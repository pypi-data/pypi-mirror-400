import math
from collections import OrderedDict
import torch
import torch.nn as nn
from torch.nn import CrossEntropyLoss
from transformers import T5Config, T5EncoderModel
from config import NUM_LABELS_N_MASKS
from .binary_predictor import BinaryPredictor


def gelu(x):
    return x * 0.5 * (1.0 + torch.erf(x / math.sqrt(2.0)))


class T5LayerNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.eps = eps

    def forward(self, x):
        variance = x.to(dtype=torch.float32).pow(2).mean(-1, keepdim=True)
        x = x * torch.rsqrt(variance + self.eps)
        if self.weight.dtype != x.dtype:
            self.weight = nn.Parameter(self.weight.to(dtype=x.dtype))
        return self.weight * x


class T5LMHead(nn.Module):
    def __init__(self, config, t5_embedding_weights: torch.Tensor):
        super().__init__()
        actual_hidden_size = t5_embedding_weights.size(1)
        self.dense = nn.Linear(actual_hidden_size, actual_hidden_size)
        self.layer_norm = T5LayerNorm(actual_hidden_size)
        num_labels = t5_embedding_weights.size(0)
        self.decoder = nn.Linear(actual_hidden_size, num_labels, bias=False)
        self.decoder.weight = t5_embedding_weights
        self.decoder.bias = nn.Parameter(torch.zeros(num_labels))

    def forward(self, features):
        x = self.dense(features)
        x = gelu(x)
        x = self.layer_norm(x)
        x = self.decoder(x)
        return x


class T5MaskNPredictionHead(nn.Module):
    def __init__(self, config, actual_hidden_size):
        super().__init__()
        self.mask_predictor_dense = nn.Linear(actual_hidden_size, 50)
        self.mask_predictor_proj = nn.Linear(50, NUM_LABELS_N_MASKS)

    def forward(self, sequence_output):
        mask_predictor_state = gelu(self.mask_predictor_dense(sequence_output))
        prediction_scores = self.mask_predictor_proj(mask_predictor_state)
        return prediction_scores


class T5ForMaskedLM(nn.Module):
    """
    T5-based normalizer following the same interface/pattern as BartPhoForMaskedLM.
    """

    def __init__(self, vocab_size, mask_n_predictor, nsw_detector, model_name='VietAI/vit5-base'):
        super().__init__()
        self.t5 = T5EncoderModel.from_pretrained(model_name)
        self.t5.resize_token_embeddings(vocab_size)
        self.t5.config.vocab_size = vocab_size
        self.t5.config.mask_n_predictor = mask_n_predictor
        self.t5.config.nsw_detector = nsw_detector
        self.config = self.t5.config

        # Hidden size and embeddings reference
        if hasattr(self.t5, 'shared') and hasattr(self.t5.shared, 'weight'):
            embedding_weights = self.t5.shared.weight
        else:
            # Fallback (should not happen for T5): create an embedding parameter
            embedding_weights = nn.Parameter(torch.empty(self.config.vocab_size, self.t5.config.d_model))
            nn.init.normal_(embedding_weights, std=0.02)

        self.actual_hidden_size = embedding_weights.size(1)

        self.cls = T5LMHead(self.config, embedding_weights)
        self.mask_n_predictor = T5MaskNPredictionHead(self.config, self.actual_hidden_size) if self.config.mask_n_predictor else None
        self.nsw_detector = BinaryPredictor(self.actual_hidden_size, dense_dim=100) if self.config.nsw_detector else None
        self.num_labels_n_mask = NUM_LABELS_N_MASKS

    def forward(self, input_ids, attention_mask=None,
                labels=None, labels_n_masks=None, standard_labels=None, sample_weights=None,
                soft_labels=False):
        if attention_mask is None:
            attention_mask = (input_ids != 0).long()

        # Encoder-only forward
        outputs = self.t5(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True)
        sequence_output = outputs.last_hidden_state

        prediction_scores = self.cls(sequence_output)

        loss_dict = OrderedDict([('loss', None), ('loss_norm', 0), ('loss_n_masks_pred', 0), ('loss_nsw_detection', 0)])
        pred_dict = OrderedDict([('logits_norm', None), ('logits_n_masks_pred', None), ('logits_nsw_detection', None)])

        if self.mask_n_predictor is not None:
            assert self.num_labels_n_mask > 0
            logits_n_mask_prediction = self.mask_n_predictor(sequence_output)
            pred_dict['logits_n_masks_pred'] = logits_n_mask_prediction

        if self.nsw_detector is not None:
            standard_logits = self.nsw_detector(sequence_output)
            pred_dict['logits_nsw_detection'] = standard_logits

        pred_dict['logits_norm'] = prediction_scores

        if labels is not None:
            if self.mask_n_predictor is not None:
                assert labels_n_masks is not None, 'labels_n_masks must be provided when mask_n_predictor is enabled'
                if sample_weights is None:
                    loss_fct_masks_pred = CrossEntropyLoss(ignore_index=-1)
                    loss_dict['loss_n_masks_pred'] = loss_fct_masks_pred(logits_n_mask_prediction.view(-1, self.num_labels_n_mask), labels_n_masks.view(-1))
                else:
                    loss_fct_masks_pred = CrossEntropyLoss(ignore_index=-1, reduce='none')
                    loss_dict['loss_n_masks_pred'] = (loss_fct_masks_pred(logits_n_mask_prediction.view(-1, self.num_labels_n_mask), labels_n_masks.view(-1)) * sample_weights).mean()

            if self.nsw_detector is not None:
                assert standard_labels is not None, 'standard_labels must be provided when nsw_detector is enabled'
                if sample_weights is None:
                    loss_fct_nsw_pred = CrossEntropyLoss(ignore_index=-1)
                    loss_dict['loss_nsw_detection'] = loss_fct_nsw_pred(standard_logits.view(-1, 2), standard_labels.view(-1))
                else:
                    loss_fct_nsw_pred = CrossEntropyLoss(ignore_index=-1, reduce='none')
                    loss_dict['loss_nsw_detection'] = (loss_fct_nsw_pred(standard_logits.view(-1, 2), standard_labels.view(-1)) * sample_weights).mean()

            num_labels = self.config.vocab_size
            masked_lm_labels = labels.view(-1, num_labels) if soft_labels else labels.view(-1)
            if sample_weights is None:
                loss_fct = CrossEntropyLoss(ignore_index=-1)
                masked_lm_loss = loss_fct(prediction_scores.view(-1, num_labels), masked_lm_labels)
            else:
                loss_fct = CrossEntropyLoss(ignore_index=-1, reduce='none')
                masked_lm_loss = (loss_fct(prediction_scores.view(-1, num_labels), masked_lm_labels) * sample_weights).mean()
            loss_dict['loss_norm'] = masked_lm_loss

        loss_dict['loss'] = loss_dict['loss_norm'] + loss_dict['loss_n_masks_pred'] + loss_dict['loss_nsw_detection']
        return loss_dict, pred_dict, sequence_output


def get_vit5_normalizer(vocab_size, checkpoint_dir=None, mask_n_predictor=False, nsw_detector=False, model_name='VietAI/vit5-base'):
    """
    Create a ViT5 model for text normalization using the same interface as other base models.
    """
    model = T5ForMaskedLM(
        vocab_size=vocab_size,
        mask_n_predictor=mask_n_predictor,
        nsw_detector=nsw_detector,
        model_name=model_name
    )
    if checkpoint_dir is not None:
        model.load_state_dict(torch.load(checkpoint_dir, map_location=lambda storage, loc: storage))
    return model