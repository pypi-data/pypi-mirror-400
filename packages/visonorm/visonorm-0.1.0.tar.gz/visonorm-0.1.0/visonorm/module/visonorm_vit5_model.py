#!/usr/bin/env python3
"""
Custom ViSoNorm model class for ViT5 (T5 encoder-only) based models.
This preserves the custom heads needed for text normalization and
is loadable via trust_remote_code.
"""

import math
from collections import defaultdict
import torch
import torch.nn as nn
from transformers import T5EncoderModel, T5Config, T5PreTrainedModel

# Define constants locally to avoid external dependencies
NUM_LABELS_N_MASKS = 5


def gelu(x):
    return x * 0.5 * (1.0 + torch.erf(x / math.sqrt(2.0)))


class T5LMHead(nn.Module):
    def __init__(self, config, embedding_weights: torch.Tensor):
        super().__init__()
        actual_hidden_size = embedding_weights.size(1)
        self.dense = nn.Linear(actual_hidden_size, actual_hidden_size)
        self.layer_norm = nn.LayerNorm(actual_hidden_size, eps=1e-6)
        num_labels = embedding_weights.size(0)
        self.decoder = nn.Linear(actual_hidden_size, num_labels, bias=False)
        self.decoder.weight = embedding_weights
        self.decoder.bias = nn.Parameter(torch.zeros(num_labels))

    def forward(self, features):
        x = self.dense(features)
        x = gelu(x)
        x = self.layer_norm(x)
        x = self.decoder(x)
        return x


class T5MaskNPredictionHead(nn.Module):
    def __init__(self, config, actual_hidden_size):
        super(T5MaskNPredictionHead, self).__init__()
        self.mask_predictor_dense = nn.Linear(actual_hidden_size, 50)
        self.mask_predictor_proj = nn.Linear(50, NUM_LABELS_N_MASKS)

    def forward(self, sequence_output):
        mask_predictor_state = gelu(self.mask_predictor_dense(sequence_output))
        prediction_scores = self.mask_predictor_proj(mask_predictor_state)
        return prediction_scores


class T5BinaryPredictor(nn.Module):
    def __init__(self, hidden_size, dense_dim=100):
        super(T5BinaryPredictor, self).__init__()
        self.dense = nn.Linear(hidden_size, dense_dim)
        self.predictor = nn.Linear(dense_dim, 2)

    def forward(self, sequence_output):
        state = gelu(self.dense(sequence_output))
        prediction_scores = self.predictor(state)
        return prediction_scores


class ViSoNormViT5ForMaskedLM(T5PreTrainedModel):
    config_class = T5Config

    def __init__(self, config: T5Config):
        super().__init__(config)
        self.t5 = T5EncoderModel(config)

        # Hidden size from embeddings - T5EncoderModel uses encoder.embed_tokens (not shared)
        # T5EncoderModel doesn't have shared embeddings like T5Model does
        embedding_weights = self.t5.encoder.embed_tokens.weight
        actual_hidden_size = embedding_weights.size(1)

        self.cls = T5LMHead(config, embedding_weights)
        self.mask_n_predictor = T5MaskNPredictionHead(config, actual_hidden_size)
        self.nsw_detector = T5BinaryPredictor(actual_hidden_size, dense_dim=100)
        self.num_labels_n_mask = NUM_LABELS_N_MASKS

        self.post_init()
    
    def _tie_weights(self):
        """Re-tie the decoder weights to embeddings after loading state dict."""
        # Re-tie cls.decoder.weight to embedding weights after state dict loading
        if hasattr(self.cls, 'decoder') and hasattr(self.cls.decoder, 'weight'):
            self.cls.decoder.weight = self.t5.encoder.embed_tokens.weight
    
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, *args, **kwargs):
        """Override from_pretrained to properly handle state dict loading and re-tie weights."""
        # Load the config first
        config = T5Config.from_pretrained(pretrained_model_name_or_path, *args, **kwargs)
        
        # Create the model instance
        model = cls(config)
        
        # Load the state dict
        import os
        from huggingface_hub import hf_hub_download
        
        # Try to find the model file
        model_file = None
        state_dict = None
        
        # First try pytorch_model.bin
        try:
            if os.path.exists(pretrained_model_name_or_path):
                # Local path
                pytorch_file = os.path.join(pretrained_model_name_or_path, "pytorch_model.bin")
                if os.path.exists(pytorch_file):
                    state_dict = torch.load(pytorch_file, map_location='cpu')
                else:
                    # Try safetensors
                    safetensors_file = os.path.join(pretrained_model_name_or_path, "model.safetensors")
                    if os.path.exists(safetensors_file):
                        from safetensors.torch import load_file
                        state_dict = load_file(safetensors_file)
            else:
                # Remote HuggingFace repo
                try:
                    model_file = hf_hub_download(pretrained_model_name_or_path, "pytorch_model.bin")
                    state_dict = torch.load(model_file, map_location='cpu')
                except Exception:
                    try:
                        model_file = hf_hub_download(pretrained_model_name_or_path, "model.safetensors")
                        from safetensors.torch import load_file
                        state_dict = load_file(model_file)
                    except Exception:
                        raise FileNotFoundError(f"No model file found for {pretrained_model_name_or_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load state dict: {e}")
        
        # Load state dict with strict=False to handle any mismatches
        missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
        
        # CRITICAL: Re-tie the decoder weights to embeddings after loading
        # This ensures predictions use the correct vocabulary
        model._tie_weights()
        
        return model

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        head_mask=None,
        inputs_embeds=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.t5(
            input_ids=input_ids,
            attention_mask=attention_mask,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = outputs.last_hidden_state if return_dict else outputs[0]

        logits_norm = self.cls(sequence_output)
        logits_n_masks_pred = self.mask_n_predictor(sequence_output)
        logits_nsw_detection = self.nsw_detector(sequence_output)

        if not return_dict:
            return (logits_norm, logits_n_masks_pred, logits_nsw_detection) + outputs[1:]

        class ViSoNormOutput:
            def __init__(self, logits_norm, logits_n_masks_pred, logits_nsw_detection, hidden_states=None, attentions=None):
                self.logits = logits_norm
                self.logits_norm = logits_norm
                self.logits_n_masks_pred = logits_n_masks_pred
                self.logits_nsw_detection = logits_nsw_detection
                self.hidden_states = hidden_states
                self.attentions = attentions

        return ViSoNormOutput(
            logits_norm=logits_norm,
            logits_n_masks_pred=logits_n_masks_pred,
            logits_nsw_detection=logits_nsw_detection,
            hidden_states=getattr(outputs, 'hidden_states', None),
            attentions=getattr(outputs, 'attentions', None),
        )

    # ------------------------------
    # Shared helpers for alignment
    # ------------------------------
    def _special_tokens(self, tokenizer):
        pad_token = tokenizer.pad_token if hasattr(tokenizer, 'pad_token') else '<pad>'
        unk_token = tokenizer.unk_token if hasattr(tokenizer, 'unk_token') else '<unk>'
        eos_token_val = tokenizer.eos_token if hasattr(tokenizer, 'eos_token') else '</s>'
        bos_token_val = tokenizer.bos_token if hasattr(tokenizer, 'bos_token') else None
        mask_token = tokenizer.mask_token if hasattr(tokenizer, 'mask_token') else '<mask>'
        specials = [pad_token, unk_token, eos_token_val, mask_token, '<space>']
        if bos_token_val:
            specials.append(bos_token_val)
        return specials

    def _invalid_token_strings(self):
        return [
            'Dreams', 'Monroe', 'dreams', 'monroe', 'young', 'urban', 'concert',
            'band', 'bandieu', 'icyu', 'Dreamstt', 'cttktt', 'bett', 'ttttktt',
            'duttong', 'ơmu', 'ỳ', 'ôiỳ'
        ]

    def _prepare_inputs(self, tokenizer, text, device):
        input_tokens = tokenizer.tokenize(text)
        bos_token = tokenizer.bos_token if hasattr(tokenizer, 'bos_token') else None
        eos_token = tokenizer.eos_token if hasattr(tokenizer, 'eos_token') else '</s>'
        if bos_token:
            input_tokens = [bos_token] + input_tokens + [eos_token]
        else:
            input_tokens = input_tokens + [eos_token]
        input_ids = tokenizer.convert_tokens_to_ids(input_tokens)
        input_tokens_tensor = torch.LongTensor([input_ids]).to(device)
        input_tokens_tensor, _, _, input_mask = self._truncate_and_build_masks(input_tokens_tensor)
        return input_tokens_tensor, input_tokens

    def _mask_token_id(self, tokenizer):
        try:
            mask_token_id = tokenizer.convert_tokens_to_ids('<mask>')
            if mask_token_id == tokenizer.unk_token_id:
                mask_token_id = None
        except (KeyError, ValueError, AttributeError):
            mask_token_id = None
        if mask_token_id is None:
            try:
                mask_token_id = tokenizer.convert_tokens_to_ids('<space>')
            except Exception:
                raise ValueError("Neither <mask> nor <space> found in tokenizer. Ensure tokenizer has been properly configured with special tokens.")
        return mask_token_id

    def _filter_invalid_logits(self, tokenizer, logits_row: torch.Tensor) -> torch.Tensor:
        filtered = logits_row.clone()
        pad_token_id = getattr(tokenizer, 'pad_token_id', None)
        if pad_token_id is None:
            pad_token_id = 0
        if 0 <= pad_token_id < filtered.shape[-1]:
            filtered[pad_token_id] = float('-inf')
        for invalid_tok in self._invalid_token_strings():
            invalid_id = None
            try:
                invalid_id = tokenizer.convert_tokens_to_ids(invalid_tok)
            except Exception:
                invalid_id = None
            if invalid_id is not None and 0 <= invalid_id < filtered.shape[-1]:
                filtered[invalid_id] = float('-inf')
        return filtered
    
    def _is_invalid_generated_token(self, tokenizer, token_id: int) -> bool:
        try:
            tok = tokenizer.convert_ids_to_tokens([token_id])[0]
        except Exception:
            return True
        # Special tokens or placeholders
        if tok in self._special_tokens(tokenizer) or tok in ['<pad>', '<unk>', '<mask>', '<space>']:
            return True
        # Explicit blacklist substrings
        for inv in self._invalid_token_strings():
            if inv in tok:
                return True
        return False
    
    def _pick_valid_prediction(self, tokenizer, logits_row: torch.Tensor) -> int:
        """
        Select a token id from logits by first filtering out invalid ids, then taking argmax.
        This mirrors the older behavior while preventing known bad tokens.
        """
        filtered_logits = self._filter_invalid_logits(tokenizer, logits_row)
        return int(torch.argmax(filtered_logits).item())

    def _normalize_and_collect(self, tokenizer, text, device='cpu'):
        """Single source of truth used by normalize_text and detect_nsw."""
        input_tokens_tensor, input_tokens = self._prepare_inputs(tokenizer, text, device)
        pad_id = getattr(self.config, 'pad_token_id', 0)
        input_mask = (input_tokens_tensor != pad_id).long()
        tokens = tokenizer.convert_ids_to_tokens(input_tokens_tensor[0])
        specials = self._special_tokens(tokenizer)
        vocab_size = len(tokenizer)

        self.eval()
        with torch.no_grad():
            outputs = self(
                input_ids=input_tokens_tensor,
                attention_mask=input_mask,
                return_dict=True,
            )

        logits_initial = outputs.logits_norm if hasattr(outputs, 'logits_norm') else outputs.logits
        logits_mask = getattr(outputs, 'logits_n_masks_pred', None)
        logits_nsw = getattr(outputs, 'logits_nsw_detection', None)

        initial_pred_ids = torch.argmax(logits_initial, dim=-1)[0].cpu().tolist()

        if logits_nsw is not None:
            if logits_nsw.dim() == 3:
                nsw_probs_tensor = torch.softmax(logits_nsw[0], dim=-1)[:, 1]
            else:
                nsw_probs_tensor = torch.sigmoid(logits_nsw[0])
        else:
            nsw_probs_tensor = torch.zeros(len(tokens), device=logits_initial.device)
        nsw_probs = nsw_probs_tensor.cpu().tolist()

        if logits_mask is not None:
            mask_counts_tensor = torch.argmax(logits_mask[0], dim=-1)
        else:
            mask_counts_tensor = torch.zeros(len(tokens), dtype=torch.long, device=logits_initial.device)
        mask_counts = mask_counts_tensor.cpu().tolist()

        word_spans = []
        current = []
        for idx, tok in enumerate(tokens):
            if tok in specials:
                if current:
                    word_spans.append(current)
                    current = []
                continue
            if not current or tok.startswith('▁'):
                if current:
                    word_spans.append(current)
                current = [idx]
            else:
                current.append(idx)
        if current:
            word_spans.append(current)

        token_to_span = {}
        span_info = []
        for span_idx, positions in enumerate(word_spans):
            for pos in positions:
                token_to_span[pos] = span_idx
            head = positions[0]
            mask_count = mask_counts[head] if head < len(mask_counts) else 0
            prob = max(nsw_probs[pos] if pos < len(nsw_probs) else 0.0 for pos in positions)
            changed = any(
                initial_pred_ids[pos] != int(input_tokens_tensor[0][pos].item())
                for pos in positions
            )
            # Trust NSW head for expansion only when confident; otherwise no masks
            effective_mask = 1 if (prob > 0.7 and mask_count > 0) else 0
            nsw_flag = bool(prob > 0.5 or changed)
            span_info.append({
                'positions': positions,
                'head': head,
                'mask_count': int(effective_mask),
                'nsw_prob': float(prob),
                'nsw_flag': nsw_flag,
            })

        mask_token_id = self._mask_token_id(tokenizer)
        base_ids = input_tokens_tensor[0].cpu().tolist()
        expanded_ids = []
        position_map = []
        for idx, orig_id in enumerate(base_ids):
            expanded_ids.append(orig_id)
            span_idx = token_to_span.get(idx)
            position_map.append({'span_idx': span_idx, 'token_idx': idx, 'kind': 'orig'})
            if span_idx is not None and span_info[span_idx]['head'] == idx:
                masks_to_add = span_info[span_idx]['mask_count'] if span_info[span_idx]['nsw_flag'] else 0
                masks_to_add = max(0, min(int(masks_to_add), NUM_LABELS_N_MASKS - 1))
                span_info[span_idx]['mask_applied'] = masks_to_add
                for m in range(masks_to_add):
                    expanded_ids.append(mask_token_id)
                    position_map.append({'span_idx': span_idx, 'token_idx': idx, 'kind': f'mask_{m}'})
            elif span_idx is not None and 'mask_applied' not in span_info[span_idx]:
                span_info[span_idx]['mask_applied'] = 0

        expanded_tensor = torch.tensor([expanded_ids], device=device)
        expanded_mask = torch.ones_like(expanded_tensor)
        with torch.no_grad():
            expanded_outputs = self(
                input_ids=expanded_tensor,
                attention_mask=expanded_mask,
                return_dict=True,
            )
        logits_final = expanded_outputs.logits_norm if hasattr(expanded_outputs, 'logits_norm') else expanded_outputs.logits

        final_ids = []
        for pos, meta in enumerate(position_map):
            logits_row = logits_final[0, pos]
            pred_id = self._pick_valid_prediction(tokenizer, logits_row)
            if not (0 <= pred_id < vocab_size):
                pred_id = tokenizer.unk_token_id if hasattr(tokenizer, 'unk_token_id') and tokenizer.unk_token_id is not None else 0
            orig_id = expanded_ids[pos]
            span_idx = meta['span_idx']

            if span_idx is None:
                final_ids.append(orig_id)
                continue

            token_idx = meta['token_idx']
            token_str = tokens[token_idx] if token_idx < len(tokens) else ''
            if token_str in specials:
                final_ids.append(orig_id)
                continue
            
            pred_token = tokenizer.convert_ids_to_tokens([pred_id])[0] if 0 <= pred_id < vocab_size else ''
            use_pred = span_info[span_idx]['nsw_flag'] or meta['kind'].startswith('mask_')
            if use_pred and pred_token not in specials and pred_token not in ['<pad>', '<unk>', '<mask>']:
                chosen_id = pred_id
            else:
                chosen_id = orig_id

            final_ids.append(chosen_id)

        span_pred_ids = defaultdict(list)
        for pos, meta in enumerate(position_map):
            span_idx = meta['span_idx']
            if span_idx is None:
                continue
            token_id = final_ids[pos]
            token = tokenizer.convert_ids_to_tokens([token_id])[0]
            # Skip specials, masks, and any invalid/blacklisted token
            if token in specials or token == '<mask>' or self._is_invalid_generated_token(tokenizer, token_id):
                continue
            span_pred_ids[span_idx].append(token_id)

        final_tokens = tokenizer.convert_ids_to_tokens(final_ids)
        final_tokens_clean = [tok for tok in final_tokens if tok not in specials]
        normalized_text = tokenizer.convert_tokens_to_string(final_tokens_clean).strip()
        # Post-clean any leftover blacklisted words only (do NOT remove ASCII words)
        if normalized_text:
            import re
            invalid_words = set(self._invalid_token_strings())
            # Remove standalone invalid words
            for inv in sorted(invalid_words, key=len, reverse=True):
                normalized_text = re.sub(r'\b' + re.escape(inv) + r'\b', '', normalized_text)
            normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
        if normalized_text:
            normalized_text = ' '.join(normalized_text.split())

        decoded_source = tokenizer.convert_ids_to_tokens(expanded_ids)
        decoded_pred = final_tokens

        results = []
        for span_idx, info in enumerate(span_info):
            src_ids = [int(input_tokens_tensor[0][pos].item()) for pos in info['positions']]
            src_tokens = tokenizer.convert_ids_to_tokens(src_ids)
            src_tokens_clean = [tok for tok in src_tokens if tok not in specials]
            src_text = tokenizer.convert_tokens_to_string(src_tokens_clean).strip()

            pred_ids_for_span = span_pred_ids.get(span_idx, [])
            pred_tokens = tokenizer.convert_ids_to_tokens(pred_ids_for_span)
            # Remove specials and any invalid/blacklisted token strings
            pred_tokens_clean = []
            for tok in pred_tokens:
                if tok in specials or tok == '<mask>':
                    continue
                # lightweight string-level blacklist check
                invalid = False
                for bad in self._invalid_token_strings():
                    if bad in tok:
                        invalid = True
                        break
                if not invalid:
                    pred_tokens_clean.append(tok)
            pred_text = tokenizer.convert_tokens_to_string(pred_tokens_clean).strip()

            if not pred_text:
                pred_text = src_text

            if pred_text != src_text:
                conf = info['nsw_prob'] if info['nsw_prob'] > 0 else 0.5
                results.append({
                    'index': info['head'],
                    'nsw': src_text,
                    'prediction': pred_text,
                    'confidence_score': round(min(max(conf, 0.0), 1.0), 4),
                })

        return normalized_text, results, decoded_source, decoded_pred

    def _truncate_and_build_masks(self, input_tokens_tensor, output_tokens_tensor=None):
        """Apply truncation consistent with encoder-only T5 usage."""
        pad_id_model = getattr(self.config, 'pad_token_id', 0)
        input_mask = (input_tokens_tensor != pad_id_model).long()
        return input_tokens_tensor, output_tokens_tensor, None, input_mask

    def normalize_text(self, tokenizer, text, device='cpu'):
        """
        Aligned normalization using the shared pipeline.
        Returns (normalized_text, source_tokens, prediction_tokens)
        """
        self.to(device)
        normalized_text, _, decoded_source, decoded_pred = self._normalize_and_collect(tokenizer, text, device=device)
        return normalized_text, decoded_source, decoded_pred

    def detect_nsw(self, tokenizer, text, device='cpu'):
        """
        Aligned NSW detection using the same pipeline as normalization.
        Returns a list of NSW entries with prediction and confidence.
        """
        self.to(device)
        _, results, _, _ = self._normalize_and_collect(tokenizer, text, device=device)
        return results


__all__ = ["ViSoNormViT5ForMaskedLM"]


