"""
Optimization utilities for ViSoNorm training.
Includes improved optimizer, learning rate scheduling, and gradient clipping.
"""

import torch
import math
from typing import List, Optional, Union, Dict, Any
from torch.optim import Optimizer
from torch.optim.lr_scheduler import _LRScheduler


def get_optimizer(parameters: List[torch.nn.Parameter], 
                  lr: float, 
                  optimizer_type: str = "adamw",
                  weight_decay: float = 0.01,
                  betas: tuple = (0.9, 0.999),
                  eps: float = 1e-8) -> Optimizer:
    """
    Create optimizer with improved settings.
    
    Args:
        parameters: Model parameters to optimize
        lr: Learning rate
        optimizer_type: Type of optimizer ("adam" or "adamw")
        weight_decay: Weight decay for regularization
        betas: Adam optimizer betas
        eps: Adam optimizer epsilon
        
    Returns:
        Configured optimizer
    """
    if optimizer_type.lower() == "adamw":
        return torch.optim.AdamW(
            parameters, 
            lr=lr, 
            betas=betas, 
            eps=eps, 
            weight_decay=weight_decay
        )
    elif optimizer_type.lower() == "adam":
        return torch.optim.Adam(
            parameters, 
            lr=lr, 
            betas=betas, 
            eps=eps, 
            weight_decay=weight_decay
        )
    else:
        raise ValueError(f"Unsupported optimizer type: {optimizer_type}")


def create_learning_rate_scheduler(optimizer: Optimizer,
                                 scheduler_type: str = "cosine",
                                 total_epochs: int = 10,
                                 warmup_epochs: int = 2,
                                 min_lr_ratio: float = 0.1,
                                 **kwargs) -> Optional[_LRScheduler]:
    """
    Create learning rate scheduler with warmup and decay.
    
    Args:
        optimizer: Optimizer to schedule
        scheduler_type: Type of scheduler ("cosine", "linear", "plateau", "none")
        total_epochs: Total number of training epochs
        warmup_epochs: Number of warmup epochs
        min_lr_ratio: Minimum learning rate ratio (min_lr = base_lr * ratio)
        **kwargs: Additional scheduler-specific arguments
        
    Returns:
        Configured scheduler or None
    """
    if scheduler_type.lower() == "none":
        return None
    
    # Validate parameters
    if total_epochs <= 0:
        raise ValueError(f"total_epochs must be positive, got {total_epochs}")
    if warmup_epochs < 0:
        raise ValueError(f"warmup_epochs must be non-negative, got {warmup_epochs}")
    if warmup_epochs >= total_epochs:
        print(f"Warning: warmup_epochs ({warmup_epochs}) >= total_epochs ({total_epochs}). "
              f"Consider reducing warmup_epochs or increasing total_epochs.")
    
    base_lr = optimizer.param_groups[0]['lr']
    min_lr = base_lr * min_lr_ratio
    
    if scheduler_type.lower() == "cosine":
        # Ensure T_0 is at least 1
        T_0 = max(1, total_epochs - warmup_epochs)
        return torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer,
            T_0=T_0,
            T_mult=1,
            eta_min=min_lr,
            last_epoch=-1
        )
    
    elif scheduler_type.lower() == "linear":
        def lr_lambda(epoch):
            if epoch < warmup_epochs:
                return epoch / max(1, warmup_epochs)  # Avoid division by zero
            else:
                # Handle case where warmup_epochs >= total_epochs
                if warmup_epochs >= total_epochs:
                    return 1.0
                progress = (epoch - warmup_epochs) / (total_epochs - warmup_epochs)
                return max(min_lr_ratio, 1.0 - progress)
        
        return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
    
    elif scheduler_type.lower() == "plateau":
        return torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.5,
            patience=kwargs.get('patience', 2),
            verbose=True,
            min_lr=min_lr
        )
    
    else:
        raise ValueError(f"Unsupported scheduler type: {scheduler_type}")


def apply_fine_tuning_strategy_improved(fine_tuning_strategy: str, 
                                      model: torch.nn.Module, 
                                      lr_init: Union[float, Dict[str, float]],
                                      config: Any,
                                      append_n_mask: bool = False, 
                                      nsw_detector: bool = False) -> tuple:
    """
    Apply improved fine-tuning strategy with better optimizer and scheduler.
    
    Args:
        fine_tuning_strategy: Strategy type ("standard" or "flexible_lr")
        model: Model to optimize
        lr_init: Initial learning rate(s)
        config: Configuration object with optimizer and scheduler settings
        append_n_mask: Whether model has mask predictor
        nsw_detector: Whether model has NSW detector
        
    Returns:
        Tuple of (optimizer, scheduler)
    """
    from config import AVAILABLE_FINE_TUNING_STRATEGY
    
    assert fine_tuning_strategy in AVAILABLE_FINE_TUNING_STRATEGY, \
        f"{fine_tuning_strategy} not in {AVAILABLE_FINE_TUNING_STRATEGY}"
    
    if fine_tuning_strategy == "standard":
        assert isinstance(lr_init, float), f"lr_init should be float for {fine_tuning_strategy}"
        
        optimizer = get_optimizer(
            model.parameters(),
            lr=lr_init,
            optimizer_type=config.model.optimizer,
            weight_decay=config.model.weight_decay,
            betas=config.model.adam_betas,
            eps=config.model.adam_eps
        )
        
        scheduler = create_learning_rate_scheduler(
            optimizer,
            scheduler_type=config.model.scheduler_type if config.model.use_scheduler else "none",
            total_epochs=config.training.num_epochs,
            warmup_epochs=min(config.model.warmup_epochs, config.training.num_epochs - 1),
            min_lr_ratio=config.model.min_lr_ratio
        )
        
        print(f"TRAINING: fine tuning strategy {fine_tuning_strategy} : "
              f"optimizer {config.model.optimizer}, lr {lr_init}, "
              f"weight_decay {config.model.weight_decay}, scheduler {config.model.scheduler_type}")
        
        return [optimizer], scheduler
    
    else:  # fine_tuning_strategy == "flexible_lr"
        # Decide LRs based on the actual HuggingFace model variant (base vs large)
        # Priority: use model name from config; fallback to hidden size
        base_model = getattr(getattr(config, 'model', None), 'base_model', None)
        if hasattr(base_model, 'value'):
            base_model = base_model.value

        # Resolve HF model name provided on CLI for the selected architecture
        hf_model_name = getattr(config.model, 'pretrained_model_name', None)

        # Detect model size by explicit mapping of known variants first, then fallbacks
        is_large_by_name = False
        if isinstance(hf_model_name, str):
            name_l = hf_model_name.lower()
            if base_model == 'phobert':
                if 'phobert-large' in name_l:
                    is_large_by_name = True
                elif ('phobert-base' in name_l) or ('phobert-base-v2' in name_l):
                    is_large_by_name = False
            elif base_model == 'bartpho':
                # bartpho-syllable is large; bartpho-syllable-base is base
                if 'bartpho-syllable-base' in name_l:
                    is_large_by_name = False
                elif 'bartpho-syllable' in name_l:
                    is_large_by_name = True
            elif base_model == 'visobert':
                # only one version; treat as base
                is_large_by_name = False
            else:
                # generic fallback: contains 'large'
                is_large_by_name = ('large' in name_l)
        # Hidden size from the instantiated model
        hidden_size = None
        try:
            if hasattr(model, 'roberta'):
                hidden_size = model.roberta.embeddings.word_embeddings.weight.size(1)
            elif hasattr(model, 'bart'):
                hidden_size = model.bart.shared.weight.size(1)
            elif hasattr(model, 't5'):
                # T5 encoder-only backbone (vit5)
                hidden_size = model.t5.encoder.embed_tokens.weight.size(1)
        except Exception:
            hidden_size = None

        is_large_by_dim = (hidden_size is not None and hidden_size >= 1000)
        is_large = is_large_by_name or is_large_by_dim

        # Choose conservative LRs for large models
        if is_large:
            lr_emb = 5e-6
            lr_encoder = 1e-5
            lr_head = 1e-5
        else:
            lr_emb = 1e-5
            lr_encoder = 2e-5
            lr_head = 2e-5

        # Define learning rates for different model components by architecture
        if hasattr(model, 'roberta'):  # PhoBERT / ViSoBERT
            lr_dict = {
                "roberta.embeddings": lr_emb,
                "roberta.encoder": lr_encoder,
                "roberta.pooler": lr_head,
                "cls": lr_head,
            }
        elif hasattr(model, 'bart'):  # BARTpho
            lr_dict = {
                "bart.shared": lr_emb,
                "bart.encoder": lr_encoder,
                "bart.decoder": lr_encoder,
                "cls": lr_head,
            }
        elif hasattr(model, 't5'):  # ViT5 (T5 encoder-only)
            # T5EncoderModel ties embeddings to t5.shared; include final layer norm
            lr_dict = {
                "t5.shared": lr_emb,
                "t5.encoder.block": lr_encoder,
                "t5.encoder.final_layer_norm": lr_head,
                "cls": lr_head,
            }
        else:
            # Fallback: apply single head rate to all params
            lr_dict = {"": lr_head}
        
        if append_n_mask:
            lr_dict["mask_n_predictor"] = lr_head
        if nsw_detector:
            lr_dict["nsw_detector"] = lr_head
        
        # Create parameter groups
        param_groups = []
        n_all_layers = len([a for a, _ in model.named_parameters()])
        n_optim_layer = 0
        
        for prefix, lr in lr_dict.items():
            param_group = [param for name, param in model.named_parameters() if name.startswith(prefix)] if prefix != "" else [p for _, p in model.named_parameters()]
            if param_group:  # Only add if parameters exist
                param_groups.append({
                    'params': param_group,
                    'lr': lr
                })
                n_optim_layer += len(param_group)
        
        # Check if all parameters are covered
        if n_all_layers != n_optim_layer:
            print(f"WARNING: Not all layers covered in optimization. "
                  f"All layers: {n_all_layers}, Optimized layers: {n_optim_layer}")
        
        # Create optimizer for each parameter group
        optimizers = []
        for param_group in param_groups:
            optimizer = get_optimizer(
                param_group['params'],
                lr=param_group['lr'],
                optimizer_type=config.model.optimizer,
                weight_decay=config.model.weight_decay,
                betas=config.model.adam_betas,
                eps=config.model.adam_eps
            )
            optimizers.append(optimizer)
        
        # Create scheduler for the first optimizer (main model)
        scheduler = create_learning_rate_scheduler(
            optimizers[0],
            scheduler_type=config.model.scheduler_type if config.model.use_scheduler else "none",
            total_epochs=config.training.num_epochs,
            warmup_epochs=min(config.model.warmup_epochs, config.training.num_epochs - 1),
            min_lr_ratio=config.model.min_lr_ratio
        )
        
        print(f"TRAINING: fine tuning strategy {fine_tuning_strategy} : "
              f"optimizer {config.model.optimizer}, lr_dict {lr_dict}, "
              f"weight_decay {config.model.weight_decay}, scheduler {config.model.scheduler_type}")
        
        return optimizers, scheduler


def clip_gradients(model: torch.nn.Module, max_grad_norm: float = 1.0) -> float:
    """
    Clip gradients to prevent exploding gradients.
    
    Args:
        model: Model whose gradients to clip
        max_grad_norm: Maximum gradient norm
        
    Returns:
        Gradient norm before clipping
    """
    return torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_grad_norm)


def step_optimizers(optimizers: List[Optimizer], 
                   scheduler: Optional[_LRScheduler] = None,
                   model: Optional[torch.nn.Module] = None,
                   max_grad_norm: float = 1.0) -> Dict[str, float]:
    """
    Step optimizers with gradient clipping and scheduler update.
    
    Args:
        optimizers: List of optimizers to step
        scheduler: Learning rate scheduler (optional)
        model: Model for gradient clipping (optional)
        max_grad_norm: Maximum gradient norm for clipping
        
    Returns:
        Dictionary with gradient norm and learning rates
    """
    results = {}
    
    # Clip gradients if model is provided
    if model is not None:
        grad_norm = clip_gradients(model, max_grad_norm)
        results['grad_norm'] = grad_norm.item()
    
    # Step all optimizers
    for i, optimizer in enumerate(optimizers):
        optimizer.step()
        optimizer.zero_grad()
        
        # Get current learning rate
        current_lr = optimizer.param_groups[0]['lr']
        results[f'optimizer_{i}_lr'] = current_lr
    
    # Step scheduler if provided
    if scheduler is not None:
        if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
            # For ReduceLROnPlateau, we need to pass the loss value
            # This should be called separately with the loss value
            pass
        else:
            scheduler.step()
            results['scheduler_lr'] = scheduler.get_last_lr()[0]
    
    return results
