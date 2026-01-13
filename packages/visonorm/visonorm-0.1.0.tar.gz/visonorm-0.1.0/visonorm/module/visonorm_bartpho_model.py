#!/usr/bin/env python3
"""
Custom ViSoNorm model class for BartPho-based models.
This preserves the custom heads needed for text normalization and
is loadable via auto_map without custom model_type.
"""

import math
import torch
import torch.nn as nn
from transformers import MBartModel, MBartConfig, MBartPreTrainedModel
from transformers.modeling_outputs import Seq2SeqLMOutput
# Define constants locally to avoid external dependencies
NUM_LABELS_N_MASKS = 5


def gelu(x):
    return x * 0.5 * (1.0 + torch.erf(x / math.sqrt(2.0)))


class MBartLMHead(nn.Module):
    def __init__(self, config, bart_model_embedding_weights):
        super().__init__()
        # Use the actual hidden size from the pretrained model, not the config
        actual_hidden_size = bart_model_embedding_weights.size(1)
        self.dense = nn.Linear(actual_hidden_size, actual_hidden_size)
        self.layer_norm = nn.LayerNorm(actual_hidden_size, eps=1e-12)

        num_labels = bart_model_embedding_weights.size(0)
        self.decoder = nn.Linear(actual_hidden_size, num_labels, bias=False)
        self.decoder.weight = bart_model_embedding_weights
        self.decoder.bias = nn.Parameter(torch.zeros(num_labels))

    def forward(self, features):
        x = self.dense(features)
        x = gelu(x)
        x = self.layer_norm(x)
        x = self.decoder(x)
        return x


class BartMaskNPredictionHead(nn.Module):
    def __init__(self, config, actual_hidden_size):
        super(BartMaskNPredictionHead, self).__init__()
        self.mask_predictor_dense = nn.Linear(actual_hidden_size, 50)
        self.mask_predictor_proj = nn.Linear(50, NUM_LABELS_N_MASKS)
        self.activation = gelu

    def forward(self, sequence_output):
        mask_predictor_state = self.activation(self.mask_predictor_dense(sequence_output))
        prediction_scores = self.mask_predictor_proj(mask_predictor_state)
        return prediction_scores


class BartBinaryPredictor(nn.Module):
    def __init__(self, hidden_size, dense_dim=100):
        super(BartBinaryPredictor, self).__init__()
        self.dense = nn.Linear(hidden_size, dense_dim)
        # Use 'predictor' to match the checkpoint parameter names
        self.predictor = nn.Linear(dense_dim, 2)
        self.activation = gelu

    def forward(self, sequence_output):
        state = self.activation(self.dense(sequence_output))
        prediction_scores = self.predictor(state)
        return prediction_scores


class ViSoNormBartPhoForMaskedLM(MBartPreTrainedModel):
    config_class = MBartConfig

    def __init__(self, config: MBartConfig):
        super().__init__(config)
        
        # Create MBartModel with the exact configuration from the checkpoint
        bart_config = MBartConfig(
            vocab_size=self.config.vocab_size,
            hidden_size=self.config.hidden_size,
            num_hidden_layers=self.config.num_hidden_layers,
            num_attention_heads=self.config.num_attention_heads,
            intermediate_size=self.config.intermediate_size,
            max_position_embeddings=self.config.max_position_embeddings,
            type_vocab_size=self.config.type_vocab_size,
            initializer_range=self.config.initializer_range,
            layer_norm_eps=self.config.layer_norm_eps,
            pad_token_id=self.config.pad_token_id,
            bos_token_id=self.config.bos_token_id,
            eos_token_id=self.config.eos_token_id,
            mask_token_id=self.config.mask_token_id,
        )
        
        # Use the exact same config that was used during training
        self.bart = MBartModel(self.config)
        
        # Get actual hidden size from the pretrained model
        actual_hidden_size = self.bart.shared.weight.size(1)
        
        # ViSoNorm normalization head - use exact same structure as training
        self.cls = MBartLMHead(self.config, self.bart.shared.weight)
        
        # Additional heads for ViSoNorm functionality
        self.mask_n_predictor = BartMaskNPredictionHead(self.config, actual_hidden_size)
        self.nsw_detector = BartBinaryPredictor(actual_hidden_size, dense_dim=100)
        self.num_labels_n_mask = NUM_LABELS_N_MASKS

        # Initialize per HF conventions
        self.post_init()
    
    def _load_state_dict(self, state_dict, strict=True):
        """
        Custom state dict loading that handles shape mismatches gracefully.
        """
        # Check for positional embedding mismatches
        if 'bart.encoder.embed_positions.weight' in state_dict:
            checkpoint_pos_shape = state_dict['bart.encoder.embed_positions.weight'].shape
            model_pos_shape = self.bart.encoder.embed_positions.weight.shape
            
            if checkpoint_pos_shape != model_pos_shape:
                # Resize the positional embeddings to match the checkpoint
                self.bart.encoder.embed_positions.weight.data = torch.nn.Parameter(
                    torch.zeros(checkpoint_pos_shape[0], checkpoint_pos_shape[1])
                )
                self.bart.decoder.embed_positions.weight.data = torch.nn.Parameter(
                    torch.zeros(checkpoint_pos_shape[0], checkpoint_pos_shape[1])
                )
        
        # Load the state dict with strict=False to handle any remaining mismatches
        missing_keys, unexpected_keys = self.load_state_dict(state_dict, strict=False)
        
        return missing_keys, unexpected_keys
    
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, *args, **kwargs):
        """
        Override from_pretrained to use our custom state dict loading.
        """
        # Load the config first
        config = MBartConfig.from_pretrained(pretrained_model_name_or_path)
        
        # Create the model instance
        model = cls(config)
        
        # Load the state dict manually using our custom method
        import os
        from huggingface_hub import hf_hub_download
        
        # Try to find the model file in the repository
        model_file = None
        
        # First try pytorch_model.bin
        try:
            model_file = hf_hub_download(pretrained_model_name_or_path, "pytorch_model.bin")
            state_dict = torch.load(model_file, map_location='cpu')
        except Exception:
            # Try model.safetensors
            try:
                model_file = hf_hub_download(pretrained_model_name_or_path, "model.safetensors")
                from safetensors.torch import load_file
                state_dict = load_file(model_file)
            except Exception:
                # Try local files if it's a local path
                if os.path.exists(pretrained_model_name_or_path):
                    pytorch_file = os.path.join(pretrained_model_name_or_path, "pytorch_model.bin")
                    safetensors_file = os.path.join(pretrained_model_name_or_path, "model.safetensors")
                    
                    if os.path.exists(pytorch_file):
                        state_dict = torch.load(pytorch_file, map_location='cpu')
                    elif os.path.exists(safetensors_file):
                        from safetensors.torch import load_file
                        state_dict = load_file(safetensors_file)
                    else:
                        raise FileNotFoundError(f"No model file found in {pretrained_model_name_or_path}")
                else:
                    raise FileNotFoundError(f"Model file not found for {pretrained_model_name_or_path}")
        
        # Use our custom state dict loading
        model._load_state_dict(state_dict)
        
        return model
    
    def fix_classification_head_for_tokenizer(self, tokenizer):
        """
        Fix the classification head to match the tokenizer's vocabulary size.
        This is needed when there's a vocabulary mismatch between model and tokenizer.
        """
        tokenizer_vocab_size = len(tokenizer)
        model_vocab_size = self.config.vocab_size
        
        if tokenizer_vocab_size != model_vocab_size:
            # Check if <space> token is missing
            if '<space>' not in tokenizer.get_vocab():
                # Add the <space> token
                tokenizer.add_tokens(['<space>'])
                new_vocab_size = len(tokenizer)
                
                # Update the model's embedding layer to match new tokenizer
                self.bart.resize_token_embeddings(new_vocab_size)
                
                # Initialize the new token's embedding with proper weights
                with torch.no_grad():
                    # Get the embedding for the new token (last one)
                    new_token_id = new_vocab_size - 1
                    # Initialize with the average of existing embeddings (better than random)
                    existing_embeddings = self.bart.shared.weight[:-1]  # All except the new token
                    avg_embedding = existing_embeddings.mean(dim=0)
                    self.bart.shared.weight[new_token_id] = avg_embedding
    

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        decoder_input_ids=None,
        decoder_attention_mask=None,
        head_mask=None,
        decoder_head_mask=None,
        cross_attn_head_mask=None,
        encoder_outputs=None,
        past_key_values=None,
        inputs_embeds=None,
        decoder_inputs_embeds=None,
        use_cache=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        outputs = self.bart(
            input_ids=input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            head_mask=head_mask,
            decoder_head_mask=decoder_head_mask,
            cross_attn_head_mask=cross_attn_head_mask,
            encoder_outputs=encoder_outputs,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            decoder_inputs_embeds=decoder_inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        # BartModel returns Seq2SeqModelOutput, we need the encoder last hidden state
        if return_dict:
            sequence_output = outputs.last_hidden_state
        else:
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
        
        # Handle Seq2SeqModelOutput attributes correctly
        hidden_states = getattr(outputs, 'encoder_hidden_states', None) or getattr(outputs, 'hidden_states', None)
        attentions = getattr(outputs, 'encoder_attentions', None) or getattr(outputs, 'attentions', None)
        
        return ViSoNormOutput(
            logits_norm=logits_norm,
            logits_n_masks_pred=logits_n_masks_pred,
            logits_nsw_detection=logits_nsw_detection,
            hidden_states=hidden_states,
            attentions=attentions,
        )
    
    def normalize_text(self, tokenizer, text, device='cpu'):
        """
        Normalize text using the ViSoNorm BartPho model with proper NSW detection and masking.
        
        Args:
            tokenizer: HuggingFace tokenizer (should be BartphoTokenizer)
            text: Input text to normalize
            device: Device to run inference on
        
        Returns:
            Tuple of (normalized_text, source_tokens, prediction_tokens)
        """
        # Move model to device
        self.to(device)
        
        # CRITICAL: Fix classification head for tokenizer vocabulary mismatch
        self.fix_classification_head_for_tokenizer(tokenizer)
        
        # Step 1: Preprocess text exactly like training data
        # BARTpho uses custom tokenization - handle it properly
        
        # Use the tokenizer's encode method to ensure proper tokenization
        # This handles special tokens correctly for BARTpho
        encoded = tokenizer.encode(text, add_special_tokens=True, return_tensors="pt")
        input_tokens_tensor = encoded.to(device)
        
        # Get the actual tokens for debugging
        input_tokens = tokenizer.convert_ids_to_tokens(encoded[0])
        
        # Step 2: Apply the same truncation and masking logic as training
        input_tokens_tensor, _, token_type_ids, input_mask = self._truncate_and_build_masks(input_tokens_tensor)
        
        # Step 3: Get all three prediction heads from ViSoNorm model
        # Use the same approach as training: call bart directly and get encoder_last_hidden_state
        self.eval()
        with torch.no_grad():
            bart_outputs = self.bart(input_tokens_tensor, attention_mask=input_mask, output_hidden_states=True)
            sequence_output = bart_outputs.encoder_last_hidden_state
            
            # Calculate all three prediction heads
            logits_norm = self.cls(sequence_output)
            logits_n_masks_pred = self.mask_n_predictor(sequence_output)
            logits_nsw_detection = self.nsw_detector(sequence_output)
            
            # Create outputs object with the same interface as our custom forward method
            class ViSoNormOutput:
                def __init__(self, logits_norm, logits_n_masks_pred, logits_nsw_detection):
                    self.logits = logits_norm
                    self.logits_norm = logits_norm
                    self.logits_n_masks_pred = logits_n_masks_pred
                    self.logits_nsw_detection = logits_nsw_detection
            
            outputs = ViSoNormOutput(logits_norm, logits_n_masks_pred, logits_nsw_detection)
        
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
                # Use the same approach as training: call bart directly
                bart_outputs = self.bart(input_ids_tensor, attention_mask=torch.ones_like(input_ids_tensor), output_hidden_states=True)
                sequence_output = bart_outputs.encoder_last_hidden_state
                logits = self.cls(sequence_output)
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
            # Use the same approach as training: call bart directly
            bart_outputs = self.bart(masked_input_ids, attention_mask=torch.ones_like(masked_input_ids), output_hidden_states=True)
            sequence_output = bart_outputs.encoder_last_hidden_state
            logits_final = self.cls(sequence_output)
        pred_ids = torch.argmax(logits_final, dim=-1)[0].cpu().tolist()
        
        # Build final token ids by taking predictions at positions; keep originals at specials
        final_tokens = []
        for idx, src_id in enumerate(working_ids):
            tok = tokenizer.convert_ids_to_tokens([src_id])[0]
            if tok in ['<s>', '</s>', '<pad>', '<unk>']:
                final_tokens.append(src_id)
            else:
                pred_id = pred_ids[idx] if idx < len(pred_ids) else src_id
                # Ensure predicted ID is within valid range
                if pred_id >= len(tokenizer):
                    pred_id = len(tokenizer) - 1
                final_tokens.append(pred_id)
        
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
        
        # CRITICAL: Fix classification head for tokenizer vocabulary mismatch
        self.fix_classification_head_for_tokenizer(tokenizer)
        
        # Step 1: Preprocess text exactly like normalize_text
        # Use the tokenizer's encode method to ensure proper tokenization
        # This handles special tokens correctly
        encoded = tokenizer.encode(text, add_special_tokens=True, return_tensors="pt")
        input_tokens_tensor = encoded.to(device)
        
        # Get the actual tokens for debugging
        input_tokens = tokenizer.convert_ids_to_tokens(encoded[0])
        
        # Step 2: Apply the same truncation and masking logic as normalize_text
        input_tokens_tensor, _, token_type_ids, input_mask = self._truncate_and_build_masks(input_tokens_tensor)
        
        # Step 3: Get all three prediction heads from ViSoNorm model (same as normalize_text)
        # Use the same approach as training: call bart directly and get encoder_last_hidden_state
        self.eval()
        with torch.no_grad():
            bart_outputs = self.bart(input_tokens_tensor, attention_mask=input_mask, output_hidden_states=True)
            sequence_output = bart_outputs.encoder_last_hidden_state
            
            # Calculate all three prediction heads
            logits_norm = self.cls(sequence_output)
            logits_n_masks_pred = self.mask_n_predictor(sequence_output)
            logits_nsw_detection = self.nsw_detector(sequence_output)
            
            # Create outputs object with the same interface as our custom forward method
            class ViSoNormOutput:
                def __init__(self, logits_norm, logits_n_masks_pred, logits_nsw_detection):
                    self.logits = logits_norm
                    self.logits_norm = logits_norm
                    self.logits_n_masks_pred = logits_n_masks_pred
                    self.logits_nsw_detection = logits_nsw_detection
            
            outputs = ViSoNormOutput(logits_norm, logits_n_masks_pred, logits_nsw_detection)
        
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
                # Use the same approach as training: call bart directly
                bart_outputs = self.bart(input_ids_tensor, attention_mask=torch.ones_like(input_ids_tensor), output_hidden_states=True)
                sequence_output = bart_outputs.encoder_last_hidden_state
                logits = self.cls(sequence_output)
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
            # Use the same approach as training: call bart directly
            bart_outputs = self.bart(masked_input_ids, attention_mask=torch.ones_like(masked_input_ids), output_hidden_states=True)
            sequence_output = bart_outputs.encoder_last_hidden_state
            logits_final = self.cls(sequence_output)
        pred_ids = torch.argmax(logits_final, dim=-1)[0].cpu().tolist()
        
        # No need for vocabulary mismatch handling - classification head is already fixed

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
        # BartPho specific truncation logic
        pad_id_model = 1
        input_mask = torch.ones_like(input_tokens_tensor)
        token_type_ids = None
        return input_tokens_tensor, output_tokens_tensor, token_type_ids, input_mask


__all__ = ["ViSoNormBartPhoForMaskedLM"]
