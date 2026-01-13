import math
import numpy as np
import os
import gc

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from datasets import Dataset
from utils import gen_data_iter as gen_dataIter
from utils import get_config_attr

class RuleAttentionNetwork(nn.Module):
    def __init__(self, student_emb_dim, num_rules, num_labels, dense_dropout=0.3, max_rule_seq_length=2, device="cuda"):
        super(RuleAttentionNetwork, self).__init__()
        self.num_labels = num_labels
        self.device = device
        # Define Dropout Layer
        self.dropout = nn.Dropout(p=dense_dropout)

        # Dense Layer
        self.dense = nn.Linear(student_emb_dim, 128)
        # LayerNorm is more stable than BatchNorm for small effective batch sizes
        self.layer_norm = nn.LayerNorm(128)

        # Embedding Layers
        self.rule_embed = nn.Embedding(num_rules + 1, 128, padding_idx=0)
        self.rule_bias = nn.Embedding(num_rules + 1, 1, padding_idx=0)

        # Initialization
        nn.init.xavier_uniform_(self.rule_embed.weight) # Xavier uniform initializer
        nn.init.uniform_(self.rule_bias.weight)

        # Sigmoid Activation
        self.sigmoid = nn.Sigmoid()

    def forward(self, student_embeddings, rule_ids, rule_preds_onehot):
        # Apply Dropout
        x_hidden = self.dropout(student_embeddings)
        # Dense Layer + LayerNorm
        x_hidden = self.dense(x_hidden)
        x_hidden = self.layer_norm(x_hidden)
        x_hidden = F.relu(x_hidden)
        x_hidden = self.dropout(x_hidden)

        # Embedding Layers
        rule_embeddings = self.rule_embed(rule_ids)
        rule_biases = self.rule_bias(rule_ids)

        # Attention Scores
        att_scores = torch.matmul(x_hidden.unsqueeze(2), rule_embeddings.transpose(2, 3)).squeeze(2)
        att_scores = att_scores + rule_biases.squeeze(-1)
        att_sigmoid_proba = self.sigmoid(att_scores)
        
        outputs = torch.matmul(att_sigmoid_proba.float().unsqueeze(2), rule_preds_onehot.float()).squeeze(2)
        # Normalize Outputs
        outputs = normalize_with_random_rule(outputs, att_sigmoid_proba, rule_preds_onehot)
        outputs = l1_normalize(outputs, self.num_labels)

        return outputs, att_sigmoid_proba


class RAN:
    """
    Rule Attention Network
      * Input: text embedding x, array of rule predictions
      * Output: aggregate label
    """

    def __init__(self, args, num_rules, num_labels, logger=None, name='ran'):
        self.args = args
        self.name = name
        self.logger = logger
        self.manual_seed = get_config_attr(args, 'system.seed', get_config_attr(args, 'seed', 42))
        torch.manual_seed(self.manual_seed)
        training_mode = get_config_attr(args, 'model.training_mode', get_config_attr(args, 'training_mode', 'weakly_supervised'))
        default_logdir = './experiments/ran/{}'.format(training_mode)
        self.model_dir = get_config_attr(args, 'paths.logdir', get_config_attr(args, 'logdir', default_logdir))
        self.sup_batch_size = get_config_attr(args, 'training.train_batch_size', get_config_attr(args, 'train_batch_size', 16))
        self.eval_batch_size = get_config_attr(args, 'training.eval_batch_size', get_config_attr(args, 'eval_batch_size', 128))
        self.unsup_batch_size = get_config_attr(args, 'training.unsup_batch_size', get_config_attr(args, 'unsup_batch_size', 128))
        self.sup_epochs = get_config_attr(args, 'training.num_epochs', get_config_attr(args, 'num_epochs', 10))
        self.unsup_epochs = get_config_attr(args, 'training.num_unsup_epochs', get_config_attr(args, 'num_unsup_epochs', 5))
        self.num_labels = num_labels
        self.num_rules = num_rules
        self.device = get_config_attr(args, 'system.device', get_config_attr(args, 'device', 'cuda'))
        self.use_gpu = self.device=="cuda"

        # Using Student as an extra rule
        self.num_rules += 1
        self.student_rule_id = self.num_rules
        self.hard_student_rule = get_config_attr(args, 'model.hard_student_rule', get_config_attr(args, 'hard_student_rule', False))
        self.trained = False
        self.xdim = None
        self.ignore_student = False

    def postprocess_rule_preds(self, rule_pred, student_pred=None):
        """Torch-only preprocessing on device.
        Inputs:
          - rule_pred: LongTensor [B, T, R_rules], entries in [0..num_labels-1] or -1 for no rule
          - student_pred: None or FloatTensor [B, T, num_labels] (soft) or [B, T] (hard ids)
        Returns:
          - rule_mask: FloatTensor [B, T, S] where S = R_rules (+1 if student included)
          - fired_rule_ids: LongTensor [B, T, S] with 0 as padding, student id where applicable
          - one_hot_rule_pred: FloatTensor [B, T, S, num_labels]
        """
        device = rule_pred.device
        B, T, Rrules = rule_pred.shape

        # Mask of fired rules
        rule_mask = (rule_pred != -1).to(torch.float32)  # [B, T, Rrules]

        # Fired rule ids: 1..Rrules where mask True, else 0 (padding)
        rule_indices = (torch.arange(Rrules, device=device) + 1).view(1, 1, Rrules)
        fired_rule_ids = torch.where(rule_mask.bool(), rule_indices, torch.zeros_like(rule_indices))  # [B, T, Rrules]

        # One-hot predictions per rule (zeros where -1)
        clamped = torch.clamp(rule_pred, min=0)
        oh = F.one_hot(clamped, num_classes=self.num_labels).to(torch.float32)  # [B, T, Rrules, C]
        oh = oh * rule_mask.unsqueeze(-1)

        # Optionally prepend student rule
        if student_pred is not None:
            # Align time dimension T between student and rules by cropping to min length
            T_student = student_pred.size(1) if student_pred.dim() >= 2 else T
            T_common = min(T, T_student)
            if T_common != T:
                rule_mask = rule_mask[:, :T_common, :]
                fired_rule_ids = fired_rule_ids[:, :T_common, :]
                oh = oh[:, :T_common, :, :]
                T = T_common
            if student_pred.dim() == 3:  # soft probs
                student_pred = student_pred[:, :T, :]
                student_one_hot = student_pred.to(torch.float32)
            else:
                student_pred = student_pred[:, :T]
                # hard ids -> one-hot
                student_one_hot = F.one_hot(student_pred.to(torch.long), num_classes=self.num_labels).to(torch.float32)
            if student_pred.dim() == 3:  # soft probs
                student_one_hot = student_pred.to(torch.float32)
            else:
                # hard ids -> one-hot
                student_one_hot = F.one_hot(student_pred.to(torch.long), num_classes=self.num_labels).to(torch.float32)
            student_one_hot = student_one_hot.unsqueeze(2)  # [B, T, 1, C]

            student_mask = torch.ones((B, T, 1), device=device, dtype=torch.float32)
            student_ids = torch.full((B, T, 1), fill_value=self.student_rule_id if not self.ignore_student else 0, device=device, dtype=torch.long)

            one_hot_rule_pred = torch.cat([student_one_hot, oh], dim=2)          # [B, T, 1+Rrules, C]
            rule_mask = torch.cat([student_mask, rule_mask], dim=2)              # [B, T, 1+Rrules]
            fired_rule_ids = torch.cat([student_ids, fired_rule_ids], dim=2)     # [B, T, 1+Rrules]
        else:
            one_hot_rule_pred = oh

        return rule_mask, fired_rule_ids, one_hot_rule_pred

    def init_model(self):
        if self.xdim is None:
            raise ValueError("xdim must be set before initializing the model. Call _setup_teacher_dimensions() first.")
        self.model = RuleAttentionNetwork(self.xdim,
                                          num_rules=self.num_rules,
                                          num_labels=self.num_labels,
                                          max_rule_seq_length=self.num_rules,
                                          device=self.device)
        if self.use_gpu:
            self.model = self.model.to(self.device)

    def _ensure_model_initialized(self):
        """Ensure the model is initialized before use."""
        if not hasattr(self, 'model') or self.model is None:
            self.init_model()

    def epoch_run(self, data, mode, loss_fn, optimizer=None, scheduler=None, gradient_accumulation_steps=4, scaler=None):
        # mode in ["sup_train", "unsup_train", "dev"]
        total_loss = 0
        num_batch = len(data['id'])
        
        # Initialize gradient accumulation
        if mode in ['sup_train', 'unsup_train']:
            optimizer.zero_grad()
        
        for i in range(num_batch):
            # Process one pre-batched chunk (already batched by upstream pipeline)
            with torch.amp.autocast(device_type='cuda' if self.use_gpu else 'cpu', enabled=True):
                x = torch.as_tensor(data['features'][i], dtype=torch.float32, device=self.device)
                student_pred_np = data['proba'][i]
                rule_pred_np = data['weak_labels'][i]

                # Move rule/student preds to tensors on device
                rule_pred = torch.as_tensor(rule_pred_np, dtype=torch.long, device=self.device)
                student_pred = None
                if student_pred_np is not None:
                    if isinstance(student_pred_np, np.ndarray):
                        student_pred = torch.as_tensor(student_pred_np, dtype=torch.float32, device=self.device)
                    else:
                        # assume already a tensor-like list -> convert
                        student_pred = torch.as_tensor(student_pred_np, dtype=torch.float32, device=self.device)

                rule_mask, fired_rule_ids, rule_one_hot = self.postprocess_rule_preds(rule_pred, student_pred)
                
                if mode != 'unsup_train':
                    y = torch.as_tensor(data['output_ids'][i], dtype=torch.long, device=self.device)
                
                if mode in ['sup_train', 'unsup_train']:
                    outputs, _ = self.model(x, fired_rule_ids, rule_one_hot)
                    loss = loss_fn(outputs) if mode=='unsup_train' else loss_fn(outputs.view(-1, self.num_labels), y.view(-1))
                    
                    # Scale loss for gradient accumulation
                    loss = loss / gradient_accumulation_steps
                    total_loss += loss.detach() * gradient_accumulation_steps
                    
                    if scaler is not None:
                        scaler.scale(loss).backward()
                    else:
                        loss.backward()
                    
                    # Update weights every gradient_accumulation_steps
                    if (i + 1) % gradient_accumulation_steps == 0:
                        if scaler is not None:
                            scaler.step(optimizer)
                            scaler.update()
                        else:
                            optimizer.step()
                        if scheduler:
                            scheduler.step()
                        optimizer.zero_grad(set_to_none=True)
                        
                else:
                    outputs_dev, _ = self.model(x, fired_rule_ids, rule_one_hot)
                    dev_loss = loss_fn(outputs_dev.view(-1, self.num_labels), y.view(-1))
                    total_loss += dev_loss.detach()
            
            # Clear intermediate tensors to free memory
            del x, fired_rule_ids, rule_pred, rule_mask, rule_one_hot
            if student_pred is not None:
                del student_pred
            if mode != 'unsup_train':
                del y
            if mode in ['sup_train', 'unsup_train']:
                del outputs, loss
            else:
                del outputs_dev, dev_loss
            
            # Periodic memory cleanup every 20 batches to prevent accumulation
            if (i + 1) % 20 == 0:
                if self.use_gpu:
                    torch.cuda.empty_cache()
                import gc
                gc.collect()
        if mode == 'unsup_train':
            scheduler.step()
        if mode == 'sup_train':
            scheduler.step(total_loss/num_batch)
        
        return total_loss/num_batch

    def train(self, train_data, dev_data=None, unsup_data=None, gradient_accumulation_steps=4):
        assert unsup_data is not None, "For SSL RAN you need to also provide unlabeled data... "

        self._ensure_model_initialized()
        if not self.trained:
            pass  # Model already initialized above
        
        self.logger.info("\n\n\t\t*** Training RAN ***")
        self.logger.info(f"Using gradient accumulation with {gradient_accumulation_steps} steps")

        # Log initial memory usage
        self._log_memory_usage("Before training")

        loss_fn = MinEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=1e-3, weight_decay=1e-5)  # Add weight decay
        scaler = torch.amp.GradScaler('cuda', enabled=self.use_gpu)
        scheduler = create_learning_rate_scheduler(optimizer,
                                                   max_learn_rate=1e-2,
                                                   end_learn_rate=1e-5,
                                                   warmup_epoch_count=2,
                                                   total_epoch_count=self.sup_epochs)

        # Training loop for unsupervised data
        self.model.train()
        unsup_losses = []
        for epoch in range(self.sup_epochs):
            unsup_loss = self.epoch_run(unsup_data, mode="unsup_train", loss_fn=loss_fn, optimizer=optimizer, scheduler=scheduler, gradient_accumulation_steps=gradient_accumulation_steps, scaler=scaler)
            unsup_losses.append(unsup_loss.item())
            self.logger.info("Unsupervised trainning: EPOCH {}/{} - LOSS: {}".format(epoch+1, self.sup_epochs, unsup_loss))
            
            # Memory cleanup after each epoch
            self._cleanup_epoch_memory()
            
            # Log memory usage every 3 epochs
            if (epoch + 1) % 3 == 0:
                self._log_memory_usage(f"After unsup epoch {epoch+1}")

        # Reinitialize loss function and optimizer for supervised training
        loss_fn = nn.CrossEntropyLoss(ignore_index=self.num_labels)
        optimizer = optim.Adam(self.model.parameters(), lr=1e-3, weight_decay=1e-5)  # Add weight decay
        scaler = torch.amp.GradScaler('cuda', enabled=self.use_gpu)
        scheduler = create_learning_rate_scheduler(optimizer,
                                                   max_learn_rate=1e-2,
                                                   end_learn_rate=1e-5,
                                                   warmup_epoch_count=2,
                                                   total_epoch_count=self.sup_epochs)
        
        # Training loop for supervised training
        self.trained = True
        train_losses = []
        dev_losses = []
        best_val_loss = np.inf
        for epoch in range(self.sup_epochs):
            self.model.train()
            train_loss = self.epoch_run(train_data, mode="sup_train", loss_fn=loss_fn, optimizer=optimizer, scheduler=scheduler, gradient_accumulation_steps=gradient_accumulation_steps, scaler=scaler)
            train_losses.append(train_loss.item())
            self.model.eval()
            with torch.no_grad():
                dev_loss = self.epoch_run(dev_data, mode="dev", loss_fn=loss_fn)
                dev_losses.append(dev_loss.item())
                if dev_loss < best_val_loss:
                    best_val_loss = dev_loss
                    best_model = self.model
            
            # Memory cleanup after each epoch
            self._cleanup_epoch_memory()
            
            # Log memory usage every 3 epochs
            if (epoch + 1) % 3 == 0:
                self._log_memory_usage(f"After sup epoch {epoch+1}")
                
            self.logger.info("Supervised trainning: EPOCH {}/{} - TRAIN LOSS: {} - VAL LOSS: {} - BEST VAL LOSS: {}".format(epoch+1, self.sup_epochs, train_loss, dev_loss, best_val_loss))
        self.model = best_model
        
        # Final memory cleanup
        self._cleanup_epoch_memory()
        self._log_memory_usage("After training")
        
        return {
            'unsup_loss': unsup_losses,
            'sup_loss': train_losses,
            'dev_loss': dev_losses,
            'best_dev_loss': best_val_loss.item(),
        }
    
    def _cleanup_epoch_memory(self):
        """Clean up memory after each epoch."""
        import gc
        
        # Clear GPU cache
        if self.use_gpu:
            torch.cuda.empty_cache()
        
        # Force garbage collection
        gc.collect()
        
        # Clear any cached computations
        if hasattr(self.model, 'cache'):
            delattr(self.model, 'cache')
    
    def _process_data_in_chunks(self, data, chunk_size=100):
        """Process large datasets in chunks to reduce memory usage."""
        total_size = len(data['id'])
        for start_idx in range(0, total_size, chunk_size):
            end_idx = min(start_idx + chunk_size, total_size)
            chunk = {key: data[key][start_idx:end_idx] for key in data.keys()}
            yield chunk

    def predict_ran(self, dataset, batch_size=128, inference_mode=False):
        self._ensure_model_initialized()
        
        y_preds = []
        soft_probas = []

        label = False
        if 'output_ids' in dataset:
            label=True
        num_batch = len(dataset['id'])

        self.model.eval()
        with torch.no_grad():
            for i in range(num_batch):
                # Use mixed precision for inference to save memory
                with torch.amp.autocast(device_type='cuda' if self.use_gpu else 'cpu', enabled=True):
                    x_batch = torch.as_tensor(dataset['features'][i], dtype=torch.float32, device=self.device)
                    rule_pred_batch = torch.as_tensor(dataset['weak_labels'][i], dtype=torch.long, device=self.device)
                    student_pred_np = dataset['proba'][i]

                    # Align all time dimensions to common minimum to avoid shape mismatches
                    T_feat = x_batch.shape[0]
                    T_rule = rule_pred_batch.shape[0]
                    T_student = student_pred_np.shape[0] if student_pred_np is not None else T_rule
                    T_common = min(T_feat, T_rule, T_student)
                    if T_feat != T_common:
                        x_batch = x_batch[:T_common]
                    if T_rule != T_common:
                        rule_pred_batch = rule_pred_batch[:T_common]
                    if student_pred_np is not None and T_student != T_common:
                        student_pred_np = student_pred_np[:T_common]

                    if student_pred_np is None:
                        random_pred = (rule_pred_batch != -1).sum(dim=-1) == 0  # [T_common]
                    else:
                        # Track to-mask vector per token (length T_common)
                        random_pred = torch.zeros((rule_pred_batch.shape[0],), dtype=torch.bool, device=self.device)
                    rule_mask, fired_rule_ids, rule_pred_one_hot = self.postprocess_rule_preds(rule_pred_batch, torch.as_tensor(student_pred_np, dtype=torch.float32, device=self.device) if student_pred_np is not None else None)
                
                    y_pred, att_score = self.model(x_batch, fired_rule_ids, rule_pred_one_hot)

                    preds = torch.argmax(y_pred, dim=-1, keepdim=False)  # [T_common]
                    max_proba = torch.max(y_pred, dim=-1)[0]
                    if max_proba.dim() > 1:
                        max_proba = max_proba.squeeze()
                    confidence_thres = 0.5
                    ignore_pred = (max_proba < confidence_thres)
                    # Ensure 1-D bool mask
                    if ignore_pred.dim() > 1:
                        ignore_pred = ignore_pred.reshape(-1)
                    ignore_pred = ignore_pred.to(torch.bool)
                    # Align mask and vectors to same length
                    L = min(random_pred.shape[0], ignore_pred.shape[0], preds.shape[0])
                    if random_pred.shape[0] != L:
                        random_pred = random_pred[:L]
                    if ignore_pred.shape[0] != L:
                        ignore_pred = ignore_pred[:L]
                    if preds.shape[0] != L:
                        preds = preds[:L]
                    # Use index list to avoid dimensionality issues in boolean indexing
                    idx_to_ignore = torch.nonzero(ignore_pred, as_tuple=False).view(-1)
                    if idx_to_ignore.numel() > 0:
                        random_pred[idx_to_ignore] = True
                    preds[random_pred] = -1
                if not inference_mode:
                    soft_proba = y_pred

                # Convert to CPU and store immediately to reduce GPU memory
                y_preds.append(preds.detach().cpu().numpy())
                if not inference_mode:
                    soft_probas.append(soft_proba.detach().cpu().numpy())
                
                # Clear intermediate tensors to free memory
                del x_batch, rule_pred_batch, random_pred
                del fired_rule_ids, rule_pred_one_hot, y_pred, att_score, preds, max_proba
                if not inference_mode:
                    del soft_proba
                
                # Periodic memory cleanup every 10 batches
                if (i + 1) % 10 == 0:
                    self._cleanup_epoch_memory()

        if inference_mode:
            return {
                'id': dataset['id'],
                'input_ids': dataset['input_ids'],
                'align_index': dataset['align_index'],
                'preds': y_preds,
            }

        return {
            'id': dataset['id'],
            'input_ids': dataset['input_ids'],
            'output_ids': dataset['output_ids'] if label else None,
            'align_index': dataset['align_index'],
            'preds': y_preds,
            'proba': soft_probas,
        }

    def _log_memory_usage(self, stage=""):
        """Log current memory usage for debugging."""
        if self.use_gpu and torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3  # GB
            reserved = torch.cuda.memory_reserved() / 1024**3    # GB
            self.logger.info(f"Memory usage {stage}: Allocated={allocated:.2f}GB, Reserved={reserved:.2f}GB")
        else:
            import psutil
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024**2
            self.logger.info(f"Memory usage {stage}: {memory_mb:.2f}MB")

    def load(self, savefile):
        self._ensure_model_initialized()
        self.logger.info("loading rule attention network from {}".format(savefile))
        self.model.load_state_dict(torch.load(savefile))

    def save(self, savefile):
        self._ensure_model_initialized()
        self.logger.info("Saving rule attention network at {}".format(savefile))
        torch.save(self.model.state_dict(), savefile)
        return


def MinEntropyLoss():
    def loss(y_prob):
        per_example_loss = -y_prob * torch.log(y_prob)
        return torch.mean(per_example_loss)
    return loss

def create_learning_rate_scheduler(optimizer,
                                   max_learn_rate=1e-2,
                                   end_learn_rate=1e-5,
                                   warmup_epoch_count=3,
                                   total_epoch_count=10):
    def lr_scheduler(epoch):
        if epoch < warmup_epoch_count:
            res = (max_learn_rate / warmup_epoch_count) * (epoch + 1)
        else:
            # Avoid division by zero
            decay_epochs = total_epoch_count - warmup_epoch_count
            if decay_epochs <= 0:
                # If no decay epochs, just return the max learning rate
                res = max_learn_rate
            else:
                res = max_learn_rate * math.exp(
                    math.log(end_learn_rate / max_learn_rate) * (epoch - warmup_epoch_count + 1) / decay_epochs)
        return float(res)

    learning_rate_scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lr_scheduler)

    return learning_rate_scheduler

def l1_normalize(x, num_labels):
    x = x + 1e-05  # Avoid stability issues
    l1_norm = torch.sum(x, dim=-1, keepdim=True).detach()
    l1_norm = torch.repeat_interleave(l1_norm, repeats=num_labels, dim=-1)  # Equivalent to tf.keras.backend.repeat_elements()

    return x / l1_norm

def normalize_with_random_rule(output, att_sigmoid_proba, rule_preds_onehot):
    device=output.device
    num_labels = rule_preds_onehot.shape[-1]
    sum_prob = torch.sum(rule_preds_onehot, dim=-1).detach()
    rule_mask = (sum_prob > 0).float()
    num_rules = torch.sum(sum_prob, dim=-1).float()
    masked_att_proba = att_sigmoid_proba * rule_mask
    sum_masked_att_proba = torch.sum(masked_att_proba, dim=-1)
    uniform_rule_att_proba = num_rules - sum_masked_att_proba
    uniform_vec = torch.ones((uniform_rule_att_proba.shape[0], uniform_rule_att_proba.shape[1], num_labels)) / num_labels
    uniform_vec = uniform_vec.to(device)
    uniform_pred = torch.repeat_interleave(uniform_rule_att_proba.unsqueeze(-1), repeats=num_labels, dim=-1) * uniform_vec
    output_with_uniform_rule = output + uniform_pred
    return output_with_uniform_rule
