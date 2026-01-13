#!/usr/bin/env python3
"""
Custom ViSoNorm model class for ViSoBERT-based models.
This preserves the custom heads needed for text normalization and
is loadable via auto_map without custom model_type.
"""

import math
import torch
import torch.nn as nn
from transformers import XLMRobertaModel, XLMRobertaConfig, XLMRobertaPreTrainedModel
from transformers.modeling_outputs import MaskedLMOutput
# Define constants locally to avoid external dependencies
NUM_LABELS_N_MASKS = 5


def gelu(x):
    return x * 0.5 * (1.0 + torch.erf(x / math.sqrt(2.0)))


class XLMRobertaLMHead(nn.Module):
    def __init__(self, config, xlmroberta_model_embedding_weights):
        super().__init__()
        # Use the actual hidden size from the pretrained model, not the config
        actual_hidden_size = xlmroberta_model_embedding_weights.size(1)
        self.dense = nn.Linear(actual_hidden_size, actual_hidden_size)
        self.layer_norm = nn.LayerNorm(actual_hidden_size, eps=1e-12)

        num_labels = xlmroberta_model_embedding_weights.size(0)
        self.decoder = nn.Linear(actual_hidden_size, num_labels, bias=False)
        self.decoder.weight = xlmroberta_model_embedding_weights
        self.decoder.bias = nn.Parameter(torch.zeros(num_labels))

    def forward(self, features):
        x = self.dense(features)
        x = gelu(x)
        x = self.layer_norm(x)
        x = self.decoder(x)
        return x


class XLMRobertaMaskNPredictionHead(nn.Module):
    def __init__(self, config, actual_hidden_size):
        super(XLMRobertaMaskNPredictionHead, self).__init__()
        self.mask_predictor_dense = nn.Linear(actual_hidden_size, 50)
        self.mask_predictor_proj = nn.Linear(50, NUM_LABELS_N_MASKS)
        self.activation = gelu

    def forward(self, sequence_output):
        mask_predictor_state = self.activation(self.mask_predictor_dense(sequence_output))
        prediction_scores = self.mask_predictor_proj(mask_predictor_state)
        return prediction_scores


class XLMRobertaBinaryPredictor(nn.Module):
    def __init__(self, hidden_size, dense_dim=100):
        super(XLMRobertaBinaryPredictor, self).__init__()
        self.dense = nn.Linear(hidden_size, dense_dim)
        # Use 'predictor' to match the checkpoint parameter names
        self.predictor = nn.Linear(dense_dim, 2)
        self.activation = gelu

    def forward(self, sequence_output):
        state = self.activation(self.dense(sequence_output))
        prediction_scores = self.predictor(state)
        return prediction_scores


class ViSoNormViSoBERTForMaskedLM(XLMRobertaPreTrainedModel):
    config_class = XLMRobertaConfig

    def __init__(self, config: XLMRobertaConfig):
        super().__init__(config)
        self.roberta = XLMRobertaModel(config)
        
        # Get actual hidden size from the pretrained model
        actual_hidden_size = self.roberta.embeddings.word_embeddings.weight.size(1)
        
        # ViSoNorm normalization head - use exact same structure as training
        self.cls = XLMRobertaLMHead(config, self.roberta.embeddings.word_embeddings.weight)
        
        # Additional heads for ViSoNorm functionality
        self.mask_n_predictor = XLMRobertaMaskNPredictionHead(config, actual_hidden_size)
        self.nsw_detector = XLMRobertaBinaryPredictor(actual_hidden_size, dense_dim=100)
        self.num_labels_n_mask = NUM_LABELS_N_MASKS

        # Initialize per HF conventions
        self.post_init()

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        token_type_ids=None,
        position_ids=None,
        head_mask=None,
        inputs_embeds=None,
        encoder_hidden_states=None,
        encoder_attention_mask=None,
        labels=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.roberta(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_attention_mask,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = outputs[0]
        
        # Calculate all three prediction heads
        logits_norm = self.cls(sequence_output)
        logits_n_masks_pred = self.mask_n_predictor(sequence_output)
        logits_nsw_detection = self.nsw_detector(sequence_output)

        if not return_dict:
            return (logits_norm, logits_n_masks_pred, logits_nsw_detection) + outputs[1:]

        # Return all prediction heads for ViSoNorm inference
        # Create a custom output object that contains all three heads
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
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
    
    def normalize_text(self, tokenizer, text, device='cpu'):
        """
        Normalize text using the ViSoNorm ViSoBERT model with proper NSW detection and masking.
        
        Args:
            tokenizer: HuggingFace tokenizer
            text: Input text to normalize
            device: Device to run inference on
        
        Returns:
            Tuple of (normalized_text, source_tokens, prediction_tokens)
        """
        # Move model to device
        self.to(device)
        
        # Step 1: Preprocess text exactly like training data
        # Tokenize the input text into tokens (not IDs yet)
        input_tokens = tokenizer.tokenize(text)
        
        # Add special tokens like in training
        input_tokens = ['<s>'] + input_tokens + ['</s>']
        
        # Convert tokens to IDs
        input_ids = tokenizer.convert_tokens_to_ids(input_tokens)
        input_tokens_tensor = torch.LongTensor([input_ids]).to(device)
        
        # Step 2: Apply the same truncation and masking logic as training
        input_tokens_tensor, _, token_type_ids, input_mask = self._truncate_and_build_masks(input_tokens_tensor)
        
        # Step 3: Get all three prediction heads from ViSoNorm model
        self.eval()
        with torch.no_grad():
            if hasattr(self, 'roberta'):
                outputs = self(input_tokens_tensor, token_type_ids, input_mask)
            else:
                outputs = self(input_tokens_tensor, input_mask)
        
        # Step 4: Use NSW detector to identify tokens that need normalization
        tokens = tokenizer.convert_ids_to_tokens(input_tokens_tensor[0])
        
        if hasattr(outputs, 'logits_nsw_detection') and outputs.logits_nsw_detection is not None:
            # Handle different output shapes
            if outputs.logits_nsw_detection.dim() == 3:  # (batch, seq_len, 2) - binary classification
                nsw_predictions = torch.argmax(outputs.logits_nsw_detection[0], dim=-1) == 1
            else:  # (batch, seq_len) - single output
                nsw_predictions = torch.sigmoid(outputs.logits_nsw_detection[0]) > 0.5
            
            tokens_need_norm = []
            for i, token in enumerate(tokens):
                # Skip special tokens
                if token in ['<s>', '</s>', '<pad>', '<unk>', '<mask>']:
                    tokens_need_norm.append(False)
                else:
                    if i < len(nsw_predictions):
                        tokens_need_norm.append(nsw_predictions[i].item())
                    else:
                        tokens_need_norm.append(False)
        else:
            # Fallback: assume all non-special tokens need checking
            tokens_need_norm = [token not in ['<s>', '</s>', '<pad>', '<unk>', '<mask>'] for token in tokens]
        
        # Update NSW tokens list (purely model-driven or generic non-special fallback)
        nsw_tokens = [tokens[i] for i, need in enumerate(tokens_need_norm) if need]
        
        # Step 5: Greedy 0/1-mask selection when heads are unusable
        # Try, per NSW position, whether adding one mask improves sequence likelihood

        def _score_sequence(input_ids_tensor: torch.Tensor) -> float:
            with torch.no_grad():
                scored = self(input_ids=input_ids_tensor, attention_mask=torch.ones_like(input_ids_tensor))
                logits = scored.logits_norm if hasattr(scored, 'logits_norm') else scored.logits
                log_probs = torch.log_softmax(logits[0], dim=-1)
                # Score by taking the max log-prob at each position (approximate sequence likelihood)
                position_scores, _ = torch.max(log_probs, dim=-1)
                return float(position_scores.mean().item())

        mask_token_id = tokenizer.convert_tokens_to_ids('<mask>')
        working_ids = input_tokens_tensor[0].detach().clone().cpu().tolist()
        nsw_indices = [i for i, need in enumerate(tokens_need_norm) if need]

        offset = 0
        for i in nsw_indices:
            pos = i + offset
            # Candidate A: no mask
            cand_a = working_ids
            score_a = _score_sequence(torch.tensor([cand_a], device=device))
            # Candidate B: add one mask after pos
            cand_b = working_ids[:pos+1] + [mask_token_id] + working_ids[pos+1:]
            score_b = _score_sequence(torch.tensor([cand_b], device=device))
            if score_b > score_a:
                working_ids = cand_b
                offset += 1

        # Final prediction on the chosen masked sequence (may be unchanged)
        masked_input_ids = torch.tensor([working_ids], device=device)
        with torch.no_grad():
            final_outputs = self(input_ids=masked_input_ids, attention_mask=torch.ones_like(masked_input_ids))
        logits_final = final_outputs.logits_norm if hasattr(final_outputs, 'logits_norm') else final_outputs.logits
        pred_ids = torch.argmax(logits_final, dim=-1)[0].cpu().tolist()

        # Build final token ids by taking predictions at positions; keep originals at specials
        final_tokens = []
        for idx, src_id in enumerate(working_ids):
            tok = tokenizer.convert_ids_to_tokens([src_id])[0]
            if tok in ['<s>', '</s>', '<pad>', '<unk>']:
                final_tokens.append(src_id)
            else:
                final_tokens.append(pred_ids[idx] if idx < len(pred_ids) else src_id)
        
        # Step 9: Convert to final text
        def remove_special_tokens(token_list):
            special_tokens = ['<s>', '</s>', '<pad>', '<unk>', '<mask>', '<space>']
            return [token for token in token_list if token not in special_tokens]
        
        def _safe_ids_to_text(token_ids):
            if not token_ids:
                return ""
            try:
                tokens = tokenizer.convert_ids_to_tokens(token_ids)
                cleaned = remove_special_tokens(tokens)
                if not cleaned:
                    return ""
                return tokenizer.convert_tokens_to_string(cleaned)
            except Exception:
                return ""
        
        # Build final normalized text
        final_tokens = [tid for tid in final_tokens if tid != -1]
        pred_str = _safe_ids_to_text(final_tokens)
        # Collapse repeated whitespace
        if pred_str:
            pred_str = ' '.join(pred_str.split())
        
        # Also return token lists for optional inspection
        decoded_source = tokenizer.convert_ids_to_tokens(working_ids)
        decoded_pred = tokenizer.convert_ids_to_tokens(final_tokens)
        
        return pred_str, decoded_source, decoded_pred
    
    def detect_nsw(self, tokenizer, text, device='cpu'):
        """
        Detect Non-Standard Words (NSW) in text and return detailed information.
        This method aligns with normalize_text to ensure consistent NSW detection.
        
        Args:
            tokenizer: HuggingFace tokenizer
            text: Input text to analyze
            device: Device to run inference on
        
        Returns:
            List of dictionaries containing NSW information:
            [{'index': int, 'start_index': int, 'end_index': int, 'nsw': str, 
              'prediction': str, 'confidence_score': float}, ...]
        """
        # Move model to device
        self.to(device)
        
        # Step 1: Preprocess text exactly like normalize_text
        input_tokens = tokenizer.tokenize(text)
        input_tokens = ['<s>'] + input_tokens + ['</s>']
        input_ids = tokenizer.convert_tokens_to_ids(input_tokens)
        input_tokens_tensor = torch.LongTensor([input_ids]).to(device)
        
        # Step 2: Apply the same truncation and masking logic as normalize_text
        input_tokens_tensor, _, token_type_ids, input_mask = self._truncate_and_build_masks(input_tokens_tensor)
        
        # Step 3: Get all three prediction heads from ViSoNorm model (same as normalize_text)
        self.eval()
        with torch.no_grad():
            if hasattr(self, 'roberta'):
                outputs = self(input_tokens_tensor, token_type_ids, input_mask)
            else:
                outputs = self(input_tokens_tensor, input_mask)
        
        # Step 4: Use NSW detector to identify tokens that need normalization (same logic as normalize_text)
        tokens = tokenizer.convert_ids_to_tokens(input_tokens_tensor[0])
        
        if hasattr(outputs, 'logits_nsw_detection') and outputs.logits_nsw_detection is not None:
            # Handle different output shapes (same as normalize_text)
            if outputs.logits_nsw_detection.dim() == 3:  # (batch, seq_len, 2) - binary classification
                nsw_predictions = torch.argmax(outputs.logits_nsw_detection[0], dim=-1) == 1
                nsw_confidence = torch.softmax(outputs.logits_nsw_detection[0], dim=-1)[:, 1]
            else:  # (batch, seq_len) - single output
                nsw_predictions = torch.sigmoid(outputs.logits_nsw_detection[0]) > 0.5
                nsw_confidence = torch.sigmoid(outputs.logits_nsw_detection[0])
            
            tokens_need_norm = []
            for i, token in enumerate(tokens):
                # Skip special tokens (same as normalize_text)
                if token in ['<s>', '</s>', '<pad>', '<unk>', '<mask>']:
                    tokens_need_norm.append(False)
                else:
                    if i < len(nsw_predictions):
                        tokens_need_norm.append(nsw_predictions[i].item())
                    else:
                        tokens_need_norm.append(False)
        else:
            # Fallback: assume all non-special tokens need checking (same as normalize_text)
            tokens_need_norm = [token not in ['<s>', '</s>', '<pad>', '<unk>', '<mask>'] for token in tokens]
        
        # Step 5: Apply the same masking strategy as normalize_text
        def _score_sequence(input_ids_tensor: torch.Tensor) -> float:
            with torch.no_grad():
                scored = self(input_ids=input_ids_tensor, attention_mask=torch.ones_like(input_ids_tensor))
                logits = scored.logits_norm if hasattr(scored, 'logits_norm') else scored.logits
                log_probs = torch.log_softmax(logits[0], dim=-1)
                position_scores, _ = torch.max(log_probs, dim=-1)
                return float(position_scores.mean().item())

        mask_token_id = tokenizer.convert_tokens_to_ids('<mask>')
        working_ids = input_tokens_tensor[0].detach().clone().cpu().tolist()
        nsw_indices = [i for i, need in enumerate(tokens_need_norm) if need]

        offset = 0
        for i in nsw_indices:
            pos = i + offset
            # Candidate A: no mask
            cand_a = working_ids
            score_a = _score_sequence(torch.tensor([cand_a], device=device))
            # Candidate B: add one mask after pos
            cand_b = working_ids[:pos+1] + [mask_token_id] + working_ids[pos+1:]
            score_b = _score_sequence(torch.tensor([cand_b], device=device))
            if score_b > score_a:
                working_ids = cand_b
                offset += 1

        # Step 6: Get final predictions using the same masked sequence as normalize_text
        masked_input_ids = torch.tensor([working_ids], device=device)
        with torch.no_grad():
            final_outputs = self(input_ids=masked_input_ids, attention_mask=torch.ones_like(masked_input_ids))
        logits_final = final_outputs.logits_norm if hasattr(final_outputs, 'logits_norm') else final_outputs.logits
        pred_ids = torch.argmax(logits_final, dim=-1)[0].cpu().tolist()

        # Step 7: Build results using the same logic as normalize_text
        # We need to identify NSW tokens by comparing original vs predicted tokens
        # This ensures we catch all tokens that were actually changed, not just those detected by NSW head
        nsw_results = []
        
        # Build final token ids by taking predictions at positions; keep originals at specials (same as normalize_text)
        final_tokens = []
        for idx, src_id in enumerate(working_ids):
            tok = tokenizer.convert_ids_to_tokens([src_id])[0]
            if tok in ['<s>', '</s>', '<pad>', '<unk>']:
                final_tokens.append(src_id)
            else:
                final_tokens.append(pred_ids[idx] if idx < len(pred_ids) else src_id)
        
        # Convert final tokens to normalized text (same as normalize_text)
        def remove_special_tokens(token_list):
            special_tokens = ['<s>', '</s>', '<pad>', '<unk>', '<mask>', '<space>']
            return [token for token in token_list if token not in special_tokens]
        
        def _safe_ids_to_text(token_ids):
            if not token_ids:
                return ""
            try:
                tokens = tokenizer.convert_ids_to_tokens(token_ids)
                cleaned = remove_special_tokens(tokens)
                if not cleaned:
                    return ""
                return tokenizer.convert_tokens_to_string(cleaned)
            except Exception:
                return ""
        
        # Build final normalized text
        final_tokens_cleaned = [tid for tid in final_tokens if tid != -1]
        normalized_text = _safe_ids_to_text(final_tokens_cleaned)
        # Collapse repeated whitespace
        if normalized_text:
            normalized_text = ' '.join(normalized_text.split())
        
        # Now compare original text tokens with normalized text tokens
        original_tokens = tokenizer.tokenize(text)
        normalized_tokens = tokenizer.tokenize(normalized_text)
        
        # Use a smarter approach that can handle multi-token expansions
        # Get the source and predicted tokens from the model
        decoded_source = tokenizer.convert_ids_to_tokens(working_ids)
        decoded_pred = tokenizer.convert_ids_to_tokens(final_tokens)
        
        # Clean the tokens (remove special tokens and ▁ prefix)
        def clean_token(token):
            if token in ['<s>', '</s>', '<pad>', '<unk>', '<mask>']:
                return None
            return token.strip().lstrip('▁')
        
        # Group consecutive predictions that form expansions
        i = 0
        while i < len(decoded_source):
            src_token = decoded_source[i]
            clean_src = clean_token(src_token)
            
            if clean_src is None:
                i += 1
                continue
            
            # Check if this token was changed
            pred_token = decoded_pred[i]
            clean_pred = clean_token(pred_token)
            
            if clean_pred is None:
                i += 1
                continue
            
            if clean_src != clean_pred:
                # This is an NSW token - check if it's part of an expansion
                expansion_tokens = [clean_pred]
                j = i + 1
                
                # Look for consecutive mask tokens that were filled
                while j < len(decoded_source) and j < len(decoded_pred):
                    next_src = decoded_source[j]
                    next_pred = decoded_pred[j]
                    
                    # If the source is a mask token, it was added for expansion
                    if next_src == '<mask>':
                        clean_next_pred = clean_token(next_pred)
                        if clean_next_pred is not None:
                            expansion_tokens.append(clean_next_pred)
                        j += 1
                    else:
                        # Check if the next source token was also changed
                        clean_next_src = clean_token(next_src)
                        clean_next_pred = clean_token(next_pred)
                        
                        if clean_next_src is not None and clean_next_pred is not None and clean_next_src != clean_next_pred:
                            # This is also a changed token, might be part of expansion
                            # But we need to be careful not to group unrelated changes
                            # For now, let's be conservative and only group mask-based expansions
                            break
                        else:
                            break
                
                # Create the expansion text
                expansion_text = ' '.join(expansion_tokens)
                
                # This is an NSW token
                start_idx = text.find(clean_src)
                end_idx = start_idx + len(clean_src) if start_idx != -1 else len(clean_src)
                
                # Calculate confidence score
                if hasattr(outputs, 'logits_nsw_detection') and outputs.logits_nsw_detection is not None:
                    # Find the corresponding position in the original token list
                    orig_pos = None
                    for k, tok in enumerate(tokens):
                        if tok.strip().lstrip('▁') == clean_src:
                            orig_pos = k
                            break
                    
                    if orig_pos is not None and orig_pos < len(nsw_confidence):
                        if outputs.logits_nsw_detection.dim() == 3:
                            nsw_conf = nsw_confidence[orig_pos].item()
                        else:
                            nsw_conf = nsw_confidence[orig_pos].item()
                    else:
                        nsw_conf = 0.5  # Default if position not found
                    
                    # Get normalization confidence
                    norm_logits = logits_final[0]  # Use final masked logits
                    norm_confidence = torch.softmax(norm_logits, dim=-1)
                    norm_conf = norm_confidence[i][final_tokens[i]].item()
                    combined_confidence = (nsw_conf + norm_conf) / 2
                else:
                    combined_confidence = 0.5  # Default confidence if no NSW detector
                
                nsw_results.append({
                    'index': i,
                    'start_index': start_idx,
                    'end_index': end_idx,
                    'nsw': clean_src,
                    'prediction': expansion_text,
                    'confidence_score': round(combined_confidence, 4)
                })
                
                # Move to the next unprocessed token
                i = j
            else:
                i += 1
        
        return nsw_results
    
    def _truncate_and_build_masks(self, input_tokens_tensor, output_tokens_tensor=None):
        """Apply the same truncation and masking logic as training."""
        if hasattr(self, 'roberta'):
            cfg_max = int(getattr(self.roberta.config, 'max_position_embeddings', input_tokens_tensor.size(1)))
            tbl_max = int(getattr(self.roberta.embeddings.position_embeddings, 'num_embeddings', cfg_max))
            max_pos = min(cfg_max, tbl_max)
            eff_max = max(1, max_pos - 2)
            if input_tokens_tensor.size(1) > eff_max:
                input_tokens_tensor = input_tokens_tensor[:, :eff_max]
                if output_tokens_tensor is not None and output_tokens_tensor.dim() == 2 and output_tokens_tensor.size(1) > eff_max:
                    output_tokens_tensor = output_tokens_tensor[:, :eff_max]
            pad_id_model = getattr(self.roberta.config, 'pad_token_id', None)
            if pad_id_model is None:
                pad_id_model = getattr(self.roberta.embeddings.word_embeddings, 'padding_idx', None)
            if pad_id_model is None:
                pad_id_model = 1  # Default pad token ID
            input_mask = (input_tokens_tensor != pad_id_model).long()
            token_type_ids = torch.zeros_like(input_tokens_tensor)
            return input_tokens_tensor, output_tokens_tensor, token_type_ids, input_mask
        # bart branch
        pad_id_model = 1
        input_mask = torch.ones_like(input_tokens_tensor)
        token_type_ids = None
        return input_tokens_tensor, output_tokens_tensor, token_type_ids, input_mask


__all__ = ["ViSoNormViSoBERTForMaskedLM"]
