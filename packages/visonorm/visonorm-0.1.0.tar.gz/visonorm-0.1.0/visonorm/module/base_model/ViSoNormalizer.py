import os
import numpy as np
import torch
import torch.nn as nn
from huggingface_hub import hf_hub_download

from utils import gen_data_iter as gen_dataIter
from utils import get_config_attr
from config import (
    MASK_TOKEN, PAD_TOKEN,
    NUM_LABELS_N_MASKS, AVAILABLE_FINE_TUNING_STRATEGY,
)
from optimization_utils import (
    apply_fine_tuning_strategy_improved,
    step_optimizers
)

# Model constructors per architecture
from base_model.model_construction.phobert import get_phobert_normalizer
from base_model.model_construction.visobert import get_visobert_normalizer
from base_model.model_construction.bartpho import get_bartpho_normalizer
from base_model.model_construction.vit5 import get_vit5_normalizer


def _build_student_model(base_model, vocab_size, append_n_mask, nsw_detector, args):
    model_name = get_config_attr(args, 'model.pretrained_model_name', get_config_attr(args, 'pretrained_model_name'))
    if base_model == 'phobert':
        return get_phobert_normalizer(vocab_size, mask_n_predictor=append_n_mask, nsw_detector=nsw_detector, model_name=model_name)
    elif base_model == 'bartpho':
        return get_bartpho_normalizer(vocab_size, mask_n_predictor=append_n_mask, nsw_detector=nsw_detector, model_name=model_name)
    elif base_model == 'vit5':
        return get_vit5_normalizer(vocab_size, mask_n_predictor=append_n_mask, nsw_detector=nsw_detector, model_name=model_name)
    elif base_model == 'visobert':
        return get_visobert_normalizer(vocab_size, mask_n_predictor=append_n_mask, nsw_detector=nsw_detector, model_name=model_name)
    else:
        raise ValueError(f"Unsupported base_model: {base_model}")


def get_label_n_masks(input, num_labels_n_masks):
    output = torch.empty_like(input).long()
    for ind_sent in range(input.size(0)):
        count = 0
        for ind_word in range(input.size(1)):
            if input[ind_sent, ind_word] == 1:
                output[ind_sent, ind_word] = -1
                if count == 0:
                    ind_multi_bpe = ind_word - 1
                count += 1
            elif input[ind_sent, ind_word] == 0:
                if ind_word > 0 and input[ind_sent, ind_word -1] == 1:
                    output[ind_sent, ind_multi_bpe] = min(count, num_labels_n_masks-1)
                    count = 0
                output[ind_sent, ind_word] = 0
    return output


class ViSoNormalizerTrainer:
    def __init__(self, args, tokenizer, logger=None):
        self.args = args
        self.name = get_config_attr(args, 'model.base_model', get_config_attr(args, 'base_model'))
        self.logger = logger
        self.tokenizer = tokenizer
        self.manual_seed = get_config_attr(args, 'system.seed', get_config_attr(args, 'seed', 42))
        training_mode = get_config_attr(args, 'model.training_mode', get_config_attr(args, 'training_mode', 'weakly_supervised'))
        default_logdir = './experiments/{}/{}'.format(self.name, training_mode)
        self.model_dir = get_config_attr(args, 'paths.logdir', get_config_attr(args, 'logdir', default_logdir))
        self.sup_batch_size = get_config_attr(args, 'training.train_batch_size', get_config_attr(args, 'train_batch_size', 16))
        self.unsup_batch_size = get_config_attr(args, 'training.unsup_batch_size', get_config_attr(args, 'unsup_batch_size', 128))
        self.eval_batch_size = get_config_attr(args, 'training.eval_batch_size', get_config_attr(args, 'eval_batch_size', 128))
        self.sup_epochs = get_config_attr(args, 'training.num_epochs', get_config_attr(args, 'num_epochs', 10))
        self.unsup_epochs = get_config_attr(args, 'training.num_unsup_epochs', get_config_attr(args, 'num_unsup_epochs', 5))
        self.device = get_config_attr(args, 'system.device', get_config_attr(args, 'device', 'cuda'))
        self.use_gpu = self.device=='cuda'
        self.append_n_mask = get_config_attr(args, 'model.append_n_mask', get_config_attr(args, 'append_n_mask', False))
        self.nsw_detector = get_config_attr(args, 'model.nsw_detector', get_config_attr(args, 'nsw_detector', False))
        self.pretrained_model_name = get_config_attr(args, 'model.pretrained_model_name', get_config_attr(args, 'pretrained_model_name', None))

        self.model = _build_student_model(self.name, len(self.tokenizer), self.append_n_mask, self.nsw_detector, args)
        if self.use_gpu:
            self.model = self.model.to(self.device)
        self.fine_tuning_strategy = get_config_attr(args, 'model.fine_tuning_strategy', get_config_attr(args, 'fine_tuning_strategy', 'flexible_lr'))
        self.learning_rate = get_config_attr(args, 'model.learning_rate', get_config_attr(args, 'learning_rate', 1e-3))
        self.loss_weights = get_config_attr(args, 'model.loss_weights', get_config_attr(args, 'loss_weights', False))
        self.soft_labels = get_config_attr(args, 'model.soft_labels', get_config_attr(args, 'soft_labels', False))

    def _truncate_and_build_masks(self, input_tokens_tensor, output_tokens_tensor=None):
        if hasattr(self.model, 'roberta'):
            cfg_max = int(getattr(self.model.roberta.config, 'max_position_embeddings', input_tokens_tensor.size(1)))
            tbl_max = int(getattr(self.model.roberta.embeddings.position_embeddings, 'num_embeddings', cfg_max))
            max_pos = min(cfg_max, tbl_max)
            eff_max = max(1, max_pos - 2)
            if input_tokens_tensor.size(1) > eff_max:
                input_tokens_tensor = input_tokens_tensor[:, :eff_max]
                if output_tokens_tensor is not None and output_tokens_tensor.dim() == 2 and output_tokens_tensor.size(1) > eff_max:
                    output_tokens_tensor = output_tokens_tensor[:, :eff_max]
            pad_id_model = getattr(self.model.roberta.config, 'pad_token_id', None)
            if pad_id_model is None:
                pad_id_model = getattr(self.model.roberta.embeddings.word_embeddings, 'padding_idx', None)
            if pad_id_model is None:
                pad_id_model = self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else 1
            input_mask = (input_tokens_tensor != pad_id_model).long()
            token_type_ids = torch.zeros_like(input_tokens_tensor)
            return input_tokens_tensor, output_tokens_tensor, token_type_ids, input_mask
        # bart branch
        pad_id_model = 1
        input_mask = torch.ones_like(input_tokens_tensor)
        token_type_ids = None
        return input_tokens_tensor, output_tokens_tensor, token_type_ids, input_mask

    def epoch_run(self, batchIter, mode, epoch, n_epochs, optimizer=None, scheduler=None):
        mask_id = self.tokenizer.convert_tokens_to_ids([MASK_TOKEN])[0]
        pad_id = self.tokenizer.convert_tokens_to_ids([PAD_TOKEN])[0]

        labels_n_mask_prediction = None
        loss = 0
        loss_norm = 0
        loss_n_masks_pred = 0
        loss_nsw_detection = 0
        num_batch = 0 if mode != 'train_pseudo' else len(batchIter['id'])
        if mode != 'train_pseudo':
            while True:
                try:
                    batch = batchIter.__next__()
                    num_batch += 1
                    input_ids = batch['input_ids']
                    input_tokens_tensor = torch.LongTensor(input_ids)
                    output_ids = batch['output_ids']
                    output_tokens_tensor = torch.LongTensor(output_ids)

                    input_tokens_tensor, output_tokens_tensor, token_type_ids, input_mask = self._truncate_and_build_masks(input_tokens_tensor, output_tokens_tensor)
                    if self.use_gpu:
                        input_tokens_tensor = input_tokens_tensor.cuda()
                        output_tokens_tensor = output_tokens_tensor.cuda()
                        input_mask = input_mask.cuda()
                        if token_type_ids is not None:
                            token_type_ids = token_type_ids.cuda()

                    if hasattr(self.model, 'roberta'):
                        vocab_size = self.model.roberta.config.vocab_size
                        if torch.any(input_tokens_tensor < 0) or torch.any(input_tokens_tensor >= vocab_size):
                            unk_id = self.tokenizer.unk_token_id if self.tokenizer.unk_token_id is not None else 0
                            input_tokens_tensor = input_tokens_tensor.clamp(min=0, max=vocab_size - 1)
                            input_tokens_tensor[input_tokens_tensor >= vocab_size] = unk_id

                    if self.append_n_mask:
                        labels_n_mask_prediction = get_label_n_masks(input_tokens_tensor == mask_id, NUM_LABELS_N_MASKS)
                        assert (((input_tokens_tensor == mask_id).nonzero() == (labels_n_mask_prediction == -1).nonzero())).all()
                        labels_n_mask_prediction[input_tokens_tensor == pad_id] = -1

                    if self.nsw_detector:
                        standard_labels = (input_tokens_tensor != output_tokens_tensor).long()
                        standard_labels[input_tokens_tensor == pad_id] = -1
                    else:
                        standard_labels = None

                    feeding_the_model_with_label = output_tokens_tensor.clone()

                    if optimizer is not None:
                        portion_mask = min((1- (epoch + 1) / n_epochs), 0.6)
                        mask_normed = np.random.random() < portion_mask
                        if mask_normed:
                            feeding_the_model_with_label[input_tokens_tensor == output_tokens_tensor] = -1
                            if np.random.random() < 0.5:
                                input_tokens_tensor[input_tokens_tensor != output_tokens_tensor] = mask_id

                    if hasattr(self.model, 'roberta'):
                        loss_dic, logits, _ = self.model(input_tokens_tensor, token_type_ids, input_mask,
                                                         labels=feeding_the_model_with_label,
                                                         labels_n_masks=labels_n_mask_prediction,
                                                         standard_labels=standard_labels)
                    else:
                        loss_dic, logits, _ = self.model(input_tokens_tensor, input_mask,
                                                         labels=feeding_the_model_with_label,
                                                         labels_n_masks=labels_n_mask_prediction,
                                                         standard_labels=standard_labels)
                    _loss = loss_dic["loss"]
                    loss_norm += loss_dic["loss_norm"].detach()
                    if self.append_n_mask and not isinstance(loss_dic.get("loss_n_masks_pred", 0), int):
                        loss_n_masks_pred += loss_dic["loss_n_masks_pred"].detach()
                    if self.nsw_detector and not isinstance(loss_dic.get("loss_nsw_detection", 0), int):
                        loss_nsw_detection += loss_dic["loss_nsw_detection"].detach()

                    loss += _loss.detach()
                    if optimizer is not None:
                        _loss.backward()
                        step_optimizers(
                            optimizer,
                            scheduler=scheduler,
                            model=self.model,
                            max_grad_norm=getattr(self.args, 'model.max_grad_norm', 1.0)
                        )
                except StopIteration:
                    print("BREAKING ITERATION")
                    break
        else:
            for i in range(num_batch):
                input_ids = batchIter['input_ids'][i]
                input_tokens_tensor = torch.LongTensor(input_ids)
                output_tokens_tensor = torch.tensor(batchIter['proba'][i]) if self.soft_labels else torch.LongTensor(batchIter['labels'][i])

                input_tokens_tensor, output_tokens_tensor, token_type_ids, input_mask = self._truncate_and_build_masks(input_tokens_tensor, output_tokens_tensor)
                if self.use_gpu:
                    input_tokens_tensor = input_tokens_tensor.cuda()
                    output_tokens_tensor = output_tokens_tensor.cuda()
                    input_mask = input_mask.cuda()
                    if token_type_ids is not None:
                        token_type_ids = token_type_ids.cuda()

                if hasattr(self.model, 'roberta'):
                    vocab_size = self.model.roberta.config.vocab_size
                    if torch.any(input_tokens_tensor < 0) or torch.any(input_tokens_tensor >= vocab_size):
                        unk_id = self.tokenizer.unk_token_id if self.tokenizer.unk_token_id is not None else 0
                        input_tokens_tensor = input_tokens_tensor.clamp(min=0, max=vocab_size - 1)
                        input_tokens_tensor[input_tokens_tensor >= vocab_size] = unk_id

                if self.append_n_mask:
                    labels_n_mask_prediction = get_label_n_masks(input_tokens_tensor == mask_id, NUM_LABELS_N_MASKS)
                    assert (((input_tokens_tensor == mask_id).nonzero() == (labels_n_mask_prediction == -1).nonzero())).all()
                    labels_n_mask_prediction[input_tokens_tensor == pad_id] = -1

                if self.nsw_detector:
                    if input_tokens_tensor.shape != output_tokens_tensor.shape:
                        standard_labels = torch.zeros_like(input_tokens_tensor, dtype=torch.long)
                        standard_labels.fill_(1)
                    else:
                        standard_labels = (input_tokens_tensor != output_tokens_tensor).long()
                    standard_labels[input_tokens_tensor == pad_id] = -1
                else:
                    standard_labels = None

                feeding_the_model_with_label = output_tokens_tensor.clone()

                sample_weights = None
                if self.loss_weights:
                    sample_weights = batchIter['weight'][i]
                    sample_weights = torch.tensor(sample_weights)
                    if self.use_gpu:
                        sample_weights = sample_weights.cuda()

                if hasattr(self.model, 'roberta'):
                    loss_dic, logits, _ = self.model(input_tokens_tensor, token_type_ids, input_mask,
                                                    labels=feeding_the_model_with_label,
                                                    labels_n_masks=labels_n_mask_prediction,
                                                    standard_labels=standard_labels,
                                                    sample_weights=sample_weights,
                                                    soft_labels=self.soft_labels)
                else:
                    loss_dic, logits, _ = self.model(input_tokens_tensor, input_mask,
                                                    labels=feeding_the_model_with_label,
                                                    labels_n_masks=labels_n_mask_prediction,
                                                    standard_labels=standard_labels,
                                                    sample_weights=sample_weights,
                                                    soft_labels=self.soft_labels)
                _loss = loss_dic["loss"]
                loss_norm += loss_dic["loss_norm"].detach()
                if self.append_n_mask and not isinstance(loss_dic.get("loss_n_masks_pred", 0), int):
                    loss_n_masks_pred += loss_dic["loss_n_masks_pred"].detach()
                if self.nsw_detector and not isinstance(loss_dic.get("loss_nsw_detection", 0), int):
                    loss_nsw_detection += loss_dic["loss_nsw_detection"].detach()

                loss += _loss.detach()
                _loss.backward()
                step_optimizers(
                    optimizer,
                    scheduler=scheduler,
                    model=self.model,
                    max_grad_norm=getattr(self.args, 'model.max_grad_norm', 1.0)
                )

        return loss/num_batch

    def train(self, train_data, dev_data=None):
        train_sent_len_ls = list(set(train_data['sent_len']))
        dev_sent_len_ls = list(set(dev_data['sent_len']))
        best_val_loss = np.inf
        train_losses = []
        dev_losses = []

        optimizer, scheduler = apply_fine_tuning_strategy_improved(
            self.fine_tuning_strategy,
            self.model,
            self.learning_rate,
            self.args,
            self.append_n_mask,
            self.nsw_detector
        )

        for epoch in range(self.sup_epochs):
            trainIter = gen_dataIter(train_data, self.sup_batch_size, train_sent_len_ls, shuffle=True, seed=self.manual_seed)
            devIter = gen_dataIter(dev_data, self.sup_batch_size, dev_sent_len_ls)

            self.model.train()
            loss_train = self.epoch_run(trainIter, "train", epoch=epoch+1, n_epochs=self.sup_epochs, optimizer=optimizer, scheduler=scheduler)
            train_losses.append(loss_train.item())
            self.model.eval()
            with torch.no_grad():
                loss_dev = self.epoch_run(devIter, "dev", epoch=epoch+1, n_epochs=self.sup_epochs)
                dev_losses.append(loss_dev.item())
                if loss_dev < best_val_loss:
                    best_model = self.model
                    best_val_loss = loss_dev
                    train_loss = loss_train
            if self.logger:
                self.logger.info("EPOCH {}/{}: train_loss: {} - val_loss: {} - best_val_loss: {}".format(epoch+1, self.sup_epochs, loss_train, loss_dev, best_val_loss))
        self.model = best_model
        return {
            'train_loss': train_losses,
            'dev_loss': dev_losses,
            'best_dev_loss': best_val_loss.item()
        }

    def finetune(self, train_data, dev_data=None):
        train_sent_len_ls = list(set(train_data['sent_len']))
        dev_sent_len_ls = list(set(dev_data['sent_len']))
        best_val_loss = np.inf
        train_losses = []
        dev_losses = []

        optimizer, scheduler = apply_fine_tuning_strategy_improved(
            self.fine_tuning_strategy,
            self.model,
            self.learning_rate,
            self.args,
            self.append_n_mask,
            self.nsw_detector
        )

        for epoch in range(self.sup_epochs):
            trainIter = gen_dataIter(train_data, self.sup_batch_size, train_sent_len_ls, shuffle=True)
            devIter = gen_dataIter(dev_data, self.sup_batch_size, dev_sent_len_ls)

            self.model.train()
            loss_train = self.epoch_run(trainIter, "finetune", epoch=epoch+1, n_epochs=self.sup_epochs, optimizer=optimizer, scheduler=scheduler)
            train_losses.append(loss_train.item())
            self.model.eval()
            with torch.no_grad():
                loss_dev = self.epoch_run(devIter, "dev", epoch=epoch+1, n_epochs=self.sup_epochs)
                dev_losses.append(loss_dev.item())
                if loss_dev < best_val_loss:
                    best_model = self.model
                    best_val_loss = loss_dev
                    train_loss = loss_train
            if self.logger:
                self.logger.info("EPOCH {}/{}: train_loss: {} - val_loss: {} - best_val_loss: {}".format(epoch+1, self.sup_epochs, loss_train, loss_dev, best_val_loss))
        self.model = best_model
        return {
            'train_loss': train_losses,
            'dev_loss': dev_losses,
            'best_dev_loss': best_val_loss.item()
        }

    def train_pseudo(self, train_data, dev_data=None):
        dev_sent_len_ls = list(set(dev_data['sent_len']))
        best_val_loss = np.inf
        train_losses = []
        dev_losses = []

        optimizer, scheduler = apply_fine_tuning_strategy_improved(
            self.fine_tuning_strategy,
            self.model,
            self.learning_rate,
            self.args,
            self.append_n_mask,
            self.nsw_detector
        )

        for epoch in range(self.unsup_epochs):
            devIter = gen_dataIter(dev_data, self.unsup_batch_size, dev_sent_len_ls)
            self.model.train()
            loss_train = self.epoch_run(train_data, "train_pseudo", epoch=epoch+1, n_epochs=self.unsup_epochs, optimizer=optimizer, scheduler=scheduler)
            train_losses.append(loss_train.item())
            self.model.eval()
            with torch.no_grad():
                loss_dev = self.epoch_run(devIter, "dev", epoch=epoch+1, n_epochs=self.unsup_epochs)
                dev_losses.append(loss_dev.item())
                if loss_dev < best_val_loss:
                    best_model = self.model
                    best_val_loss = loss_dev
                    train_loss = loss_train
            if self.logger:
                self.logger.info("EPOCH {}/{}: train_loss: {} - val_loss: {} - best_val_loss: {}".format(epoch+1, self.unsup_epochs, loss_train, loss_dev, best_val_loss))
        self.model = best_model
        return {
            'train_loss': train_losses,
            'dev_loss': dev_losses,
            'best_dev_loss': best_val_loss.item()
        }

    def predict(self, data, inference_mode, dataIter=None):
        label = False
        if data is not None:
            len_ls = list(set(data['sent_len']))
            dataIter = gen_dataIter(data, batch_size=self.eval_batch_size, len_list=len_ls)
        preds = []
        probas = []
        features = []
        rule_pred = []
        sent_ids = []
        input_ids = []
        output_ids = []
        align_index = []

        while True:
            try:
                with torch.no_grad():
                    batch = dataIter.__next__()
                    input_tokens_tensor = batch['input_ids']
                    input_tokens_tensor = torch.LongTensor(input_tokens_tensor)
                    token_type_ids = torch.zeros_like(input_tokens_tensor) if hasattr(self.model, 'roberta') else None
                    input_mask = torch.ones_like(input_tokens_tensor)
                    if hasattr(self.model, 'roberta'):
                        input_tokens_tensor, _, token_type_ids, input_mask = self._truncate_and_build_masks(input_tokens_tensor)
                    if self.use_gpu:
                        input_tokens_tensor = input_tokens_tensor.cuda()
                        input_mask = input_mask.cuda()
                        if token_type_ids is not None:
                            token_type_ids = token_type_ids.cuda()
                    self.model.eval()
                    if hasattr(self.model, 'roberta'):
                        _, logits, feature = self.model(input_tokens_tensor, token_type_ids, input_mask)
                    else:
                        _, logits, feature = self.model(input_tokens_tensor, input_mask)

                    pred = torch.argmax(logits["logits_norm"], dim=-1)
                    if not inference_mode:
                        proba = torch.softmax(logits["logits_norm"], dim=-1)

                    preds.append(pred.detach().cpu().numpy())
                    if not inference_mode:
                        probas.append(proba.detach().cpu().numpy())
                        features.append(feature.detach().cpu().numpy())
                        rule_pred.append(np.array(batch['weak_labels']))
                        if 'output_ids' in batch:
                            label = True
                            output_ids.append(np.array(batch['output_ids']))
                    sent_ids.append(batch['id'])
                    input_ids.append(np.array(batch['input_ids']))
                    align_index.append(batch['align_index'])
            except StopIteration:
                print("BREAKING DATA ITERATION")
                break

        if inference_mode:
            return {
                "id": sent_ids,
                "input_ids": input_ids,
                "align_index": align_index,
                "preds":  preds,
            }

        return {
            "id": sent_ids,
            "input_ids": input_ids,
            "output_ids": output_ids if label else None,
            "align_index": align_index,
            "preds":  preds,
            "proba": probas,
            "features": features,
            "weak_labels": rule_pred,
        }

    def inference(self, user_input):
        inputs = self.tokenizer(user_input, return_tensors="pt")
        self.model.eval()
        with torch.no_grad():
            if self.use_gpu:
                input_tokens_tensor = inputs.input_ids.cuda()
                input_mask = inputs.attention_mask.cuda()
            else:
                input_tokens_tensor = inputs.input_ids
                input_mask = inputs.attention_mask
            if hasattr(self.model, 'roberta'):
                token_type_ids = torch.zeros_like(input_tokens_tensor)
                if self.use_gpu:
                    token_type_ids = token_type_ids.cuda()
                _, logits, feature = self.model(input_tokens_tensor, token_type_ids, input_mask)
            else:
                _, logits, feature = self.model(input_tokens_tensor, input_mask)
            pred = torch.argmax(logits["logits_norm"], dim=-1).squeeze()
        return pred.cpu().tolist()

    def load(self, savefolder):
        # Prefer HuggingFace convention
        model_file = os.path.join(savefolder, "pytorch_model.bin")
        if not os.path.exists(model_file):
            # Fallback to legacy filename
            model_file = os.path.join(savefolder, "final_model.pt")
        if self.logger:
            self.logger.info("Loading student from {}".format(model_file))
        self.model.load_state_dict(torch.load(model_file))
        return

    def save(self, savefolder):
        # Save using HuggingFace filename convention
        model_file = os.path.join(savefolder, "pytorch_model.bin")
        if self.logger:
            self.logger.info("Saving model at {}".format(model_file))
        torch.save(self.model.state_dict(), model_file)
        self._save_tokenizer(savefolder)
        # Save minimal HF config.json by downloading base config and applying overrides
        self._save_minimal_config(savefolder)
        
    def _save_tokenizer(self, savefolder):
        if hasattr(self, 'tokenizer') and self.tokenizer is not None:
            self.tokenizer.save_pretrained(savefolder)
        if self.logger:
            self.logger.info("Saved tokenizer at {}".format(savefolder))

    def _save_minimal_config(self, savefolder):
        try:
            os.makedirs(savefolder, exist_ok=True)
            base_cfg = {}
            if self.pretrained_model_name:
                try:
                    cfg_path = hf_hub_download(repo_id=self.pretrained_model_name, filename="config.json")
                    import json
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        base_cfg = json.load(f)
                except Exception as e:
                    if self.logger:
                        self.logger.warning("Failed to download base config.json from {}: {}".format(self.pretrained_model_name, e))

            # Apply minimal overrides
            updated = dict(base_cfg)
            updated['vocab_size'] = int(len(self.tokenizer))
            updated['mask_n_predictor'] = bool(self.append_n_mask)
            updated['nsw_detector'] = bool(self.nsw_detector)

            import json
            with open(os.path.join(savefolder, "config.json"), "w", encoding="utf-8") as f:
                json.dump(updated, f, indent=2)
            if self.logger:
                self.logger.info("Saved minimal HuggingFace config.json at {}".format(os.path.join(savefolder, "config.json")))
        except Exception as e:
            if self.logger:
                self.logger.warning("Could not save minimal config.json: {}".format(e))