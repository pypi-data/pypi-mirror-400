import math
from collections import OrderedDict
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import CrossEntropyLoss
from transformers import XLMRobertaConfig, AutoModel
from config import NUM_LABELS_N_MASKS
from .binary_predictor import BinaryPredictor

def gelu(x):
    return x * 0.5 * (1.0 + torch.erf(x / math.sqrt(2.0)))

try:
    # apex.normalization.fused_layer_norm.FusedLayerNorm is optimized for better performance on GPU architectures compared to nn.LayerNorm
    from apex.normalization.fused_layer_norm import FusedLayerNorm as XLMRobertaLayerNorm
except ImportError:
    print("Better speed can be achieved with apex installed from https://www.github.com/nvidia/apex.")
    class XLMRobertaLayerNorm(nn.Module):
        def __init__(self, hidden_size, eps=1e-12):
            """Construct a layernorm module in the TF style (epsilon inside the square root).
            """
            super(XLMRobertaLayerNorm, self).__init__()
            self.weight = nn.Parameter(torch.ones(hidden_size))
            self.bias = nn.Parameter(torch.zeros(hidden_size))
            self.variance_epsilon = eps

        def forward(self, x):
            u = x.mean(-1, keepdim=True)
            s = (x - u).pow(2).mean(-1, keepdim=True)
            x = (x - u) / torch.sqrt(s + self.variance_epsilon)
            return self.weight * x + self.bias

class XLMRobertaLMHead(nn.Module):
    def __init__(self, config, xlmroberta_model_embedding_weights):
        super().__init__()
        # Use the actual hidden size from the pretrained model, not the config
        actual_hidden_size = xlmroberta_model_embedding_weights.size(1)
        self.dense = nn.Linear(actual_hidden_size, actual_hidden_size)
        self.layer_norm = XLMRobertaLayerNorm(actual_hidden_size, eps=1e-12)

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

class XLMRobertaForMaskedLM(nn.Module):
    def __init__(self, vocab_size, mask_n_predictor, nsw_detector, model_name='uitnlp/visobert'):
        super(XLMRobertaForMaskedLM, self).__init__()
        self.roberta = AutoModel.from_pretrained(model_name)
        self.roberta.resize_token_embeddings(vocab_size)
        self.roberta.config.vocab_size = vocab_size
        self.roberta.config.mask_n_predictor = mask_n_predictor
        self.roberta.config.nsw_detector = nsw_detector
        self.config = self.roberta.config
        # Get actual hidden size from the pretrained model
        self.actual_hidden_size = self.roberta.embeddings.word_embeddings.weight.size(1)
        
        self.cls = XLMRobertaLMHead(self.config, self.roberta.embeddings.word_embeddings.weight)
        self.mask_n_predictor = XLMRobertaMaskNPredictionHead(self.config, self.actual_hidden_size) if self.config.mask_n_predictor else None
        self.nsw_detector = BinaryPredictor(self.actual_hidden_size, dense_dim=100) if self.config.nsw_detector else None
        self.num_labels_n_mask = NUM_LABELS_N_MASKS

    def forward(self, input_ids, token_type_ids=None, attention_mask=None,
                labels=None, labels_n_masks=None, standard_labels=None, sample_weights=None,
                soft_labels=False):
        
        # Extract features
        if attention_mask is None:
            attention_mask = torch.ones_like(input_ids)
        if token_type_ids is None:
            token_type_ids = torch.zeros_like(input_ids)
        
        outputs = self.roberta(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, output_hidden_states=True)
        sequence_output = outputs.last_hidden_state

        # Calculate predictions
        prediction_scores = self.cls(sequence_output)  # (batch_size, seq_len, vocab_size)

        loss_dict = OrderedDict([("loss", None), ("loss_norm", 0), ("loss_n_masks_pred", 0), ("loss_nsw_detection", 0)])
        pred_dict = OrderedDict([("logits_norm", None), ("logits_n_masks_pred", None), ("logits_nsw_detection", None)])

        if self.mask_n_predictor is not None:
            assert self.num_labels_n_mask > 0, "ERROR  "
            logits_n_mask_prediction = self.mask_n_predictor(sequence_output)
            pred_dict["logits_n_masks_pred"] = logits_n_mask_prediction
        
        # Calculate predictions for NSW detection
        if self.nsw_detector is not None:
            standard_logits = self.nsw_detector(sequence_output)
            pred_dict["logits_nsw_detection"] = standard_logits
        
        pred_dict["logits_norm"] = prediction_scores

        # Calculate loss
        if labels is not None:
            if self.mask_n_predictor is not None:
                assert labels_n_masks is not None, "ERROR : you provided labels for normalization and self.mask_n_predictor : so you should provide labels_n_mask_prediction"
                if sample_weights is None:
                    loss_fct_masks_pred = CrossEntropyLoss(ignore_index=-1)
                    loss_dict["loss_n_masks_pred"] = loss_fct_masks_pred(logits_n_mask_prediction.view(-1, self.num_labels_n_mask), labels_n_masks.view(-1))
                else:
                    loss_fct_masks_pred = CrossEntropyLoss(ignore_index=-1, reduce='none')
                    loss_dict["loss_n_masks_pred"] = (loss_fct_masks_pred(logits_n_mask_prediction.view(-1, self.num_labels_n_mask), labels_n_masks.view(-1)) * sample_weights).mean()

            if self.nsw_detector is not None:
                assert standard_labels is not None, "ERROR : you provided labels for normalization and self.nsw_detector : so you should provide standard_labels"
                if sample_weights is None:
                    loss_fct_nsw_pred = CrossEntropyLoss(ignore_index=-1)
                    loss_dict["loss_nsw_detection"] = loss_fct_nsw_pred(standard_logits.view(-1, 2), standard_labels.view(-1))
                else:
                    loss_fct_nsw_pred = CrossEntropyLoss(ignore_index=-1, reduce='none')
                    loss_dict["loss_nsw_detection"] = (loss_fct_nsw_pred(standard_logits.view(-1, 2), standard_labels.view(-1)) * sample_weights).mean()

            # Use the actual vocabulary size from the model (not vocab_size + 1)
            num_labels = self.config.vocab_size
            masked_lm_labels = labels.view(-1, num_labels) if soft_labels else labels.view(-1)

            if sample_weights is None:
                loss_fct = CrossEntropyLoss(ignore_index=-1)
                masked_lm_loss = loss_fct(prediction_scores.view(-1, num_labels), masked_lm_labels)
            else:
                loss_fct = CrossEntropyLoss(ignore_index=-1, reduce='none')
                masked_lm_loss = (loss_fct(prediction_scores.view(-1, num_labels), masked_lm_labels)*sample_weights).mean()
            loss_dict["loss_norm"] = masked_lm_loss

        loss_dict["loss"] = loss_dict["loss_norm"] + loss_dict["loss_n_masks_pred"] + loss_dict["loss_nsw_detection"]

        return loss_dict, pred_dict, sequence_output


def get_visobert_normalizer(vocab_size, checkpoint_dir=None, mask_n_predictor=False, nsw_detector=False, model_name='uitnlp/visobert'):
    """
    Create a ViSoBERT model for text normalization.
    
    Args:
        vocab_size: Size of the vocabulary
        checkpoint_dir: Path to checkpoint file (optional)
        mask_n_predictor: Whether to include N-mask prediction head
        nsw_detector: Whether to include NSW detection head
        model_name: HuggingFace model name
        
    Returns:
        XLMRobertaForMaskedLM model instance
    """
    model = XLMRobertaForMaskedLM(
        vocab_size=vocab_size,
        mask_n_predictor=mask_n_predictor,
        nsw_detector=nsw_detector,
        model_name=model_name
    )
    
    # The model.cls.decoder is already properly initialized in XLMRobertaForMaskedLM.__init__
    # We only need to handle checkpoint loading if provided
    if checkpoint_dir is not None:
        model.load_state_dict(torch.load(checkpoint_dir, map_location=lambda storage, loc: storage))

    return model
