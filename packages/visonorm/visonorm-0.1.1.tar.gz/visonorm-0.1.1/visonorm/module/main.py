import argparse
import os
import shutil
import torch
import numpy as np
from typing import Optional

from config import Config, TrainingMode, BaseModel, FineTuningStrategy
from core.training_loop import TrainingLoop
from core.models import ModelFactory
from Logger import get_logger, close
from transformers import AutoTokenizer
from config import NULL_STR
from datasets.utils.logging import disable_progress_bar

# Disable progress bars for cleaner output
disable_progress_bar()


def get_tokenizer(config: Config):
    """Get tokenizer using the explicitly provided pretrained model name.

    For BARTpho, use_fast=False for compatibility.
    """
    base_model = config.model.base_model.value
    hf_name = config.model.pretrained_model_name
    use_fast = False if 'bartpho' in str(hf_name).lower() or base_model == 'bartpho' else True
    tokenizer = AutoTokenizer.from_pretrained(hf_name, use_fast=use_fast)
    tokenizer.add_tokens([NULL_STR])
    return tokenizer


def setup_experiment_directory(config: Config) -> str:
    """Setup experiment directory and return log directory path."""
    logdir = os.path.join(
        config.paths.experiment_folder, 
        config.model.base_model.value, 
        config.model.training_mode.value
    )
    
    # Clean up existing directory
    if os.path.exists(logdir):
        shutil.rmtree(logdir)
    
    os.makedirs(logdir, exist_ok=True)
    return logdir


def setup_device(config: Config) -> str:
    """Setup CUDA device and return device string."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    config.system.device = device
    config.system.n_gpu = torch.cuda.device_count()
    return device


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(description="ViSoNorm: Self-training with weak supervision")
    
    # Model arguments (required)
    parser.add_argument("--base_model", type=str, required=True, choices=['phobert', 'visobert', 'bartpho', 'vit5'], help="Base model backbone")
    parser.add_argument("--pretrained_model_name", type=str, required=True, help="HuggingFace model name to use for the selected backbone")
    parser.add_argument("--training_mode", type=str, default='weakly_supervised', choices=['only_student', 'self_training', 'weakly_supervised'], help="Training mode")
    parser.add_argument("--inference_model", type=str, default='student', help="Model used for inference")
    
    # Training arguments
    parser.add_argument("--num_epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--num_unsup_epochs", type=int, default=5, help="Number of unsupervised training epochs")
    parser.add_argument("--num_iter", type=int, default=10, help="Number of self-training iterations")
    parser.add_argument("--num_rules", type=int, default=2, help="Number of rules")
    
    # Batch size arguments
    parser.add_argument("--train_batch_size", type=int, default=16, help="Training batch size")
    parser.add_argument("--eval_batch_size", type=int, default=128, help="Evaluation batch size")
    parser.add_argument("--unsup_batch_size", type=int, default=128, help="Unsupervised batch size")
    
    # Data arguments
    parser.add_argument("--datapath", type=str, default="./data", help="Path to dataset folder")
    parser.add_argument("--sample_size", type=int, default=8096, help="Number of unlabeled samples per iteration")
    parser.add_argument("--remove_accents", action="store_true", help="Remove accents in dataset")
    parser.add_argument("--rm_accent_ratio", type=float, default=0.5, help="Ratio of characters to remove accents from")
    parser.add_argument("--lower_case", action="store_true", help="Use uncased model")
    
    # Model configuration arguments
    parser.add_argument("--append_n_mask", action="store_true", help="Append mask for training Student")
    parser.add_argument("--nsw_detector", action="store_true", help="Enable NSW (Non-Standard Word) detection")
    parser.add_argument("--soft_labels", action="store_true", help="Use soft labels for training Student")
    parser.add_argument("--loss_weights", action="store_true", help="Use instance weights in loss function")
    parser.add_argument("--hard_student_rule", action="store_true", help="Use hard student labels in teacher")
    
    # Multi-task training loss weights
    parser.add_argument("--nsw_loss_weight", type=float, default=1.0, help="Weight for NSW detection loss")
    parser.add_argument("--n_mask_loss_weight", type=float, default=1.0, help="Weight for n_mask prediction loss")
    parser.add_argument("--norm_loss_weight", type=float, default=1.0, help="Weight for normalization loss")
    
    # Optimization arguments
    parser.add_argument("--learning_rate", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--fine_tuning_strategy", type=str, default='flexible_lr', choices=['standard', 'flexible_lr'], help="Fine-tuning strategy")
    
    # Optimizer arguments
    parser.add_argument("--optimizer", type=str, default='adamw', choices=['adam', 'adamw'], help="Optimizer type")
    parser.add_argument("--weight_decay", type=float, default=0.01, help="Weight decay for regularization")
    parser.add_argument("--adam_betas", type=float, nargs=2, default=[0.9, 0.999], help="Adam optimizer betas (beta1, beta2)")
    parser.add_argument("--adam_eps", type=float, default=1e-8, help="Adam optimizer epsilon")
    
    # Learning rate scheduler arguments
    parser.add_argument("--use_scheduler", action="store_true", help="Use learning rate scheduler")
    parser.add_argument("--scheduler_type", type=str, default='cosine', choices=['cosine', 'linear', 'plateau', 'none'], help="Learning rate scheduler type")
    parser.add_argument("--warmup_epochs", type=int, default=2, help="Number of warmup epochs")
    parser.add_argument("--min_lr_ratio", type=float, default=0.1, help="Minimum learning rate ratio (min_lr = lr * ratio)")
    
    # Gradient clipping arguments
    parser.add_argument("--max_grad_norm", type=float, default=1.0, help="Maximum gradient norm for clipping")
    
    # Evaluation arguments
    parser.add_argument("--metric", type=str, default='f1_score', choices=['accuracy', 'f1_score', 'precision', 'recall'], help="Evaluation metric")
    
    # System arguments
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--experiment_folder", type=str, default="./experiments", help="Experiment folder path")
    # logdir is derived from experiment folder, base_model, and training_mode
    
    return parser


def parse_args_to_config(args: argparse.Namespace) -> Config:
    """Convert parsed arguments to Config object."""
    config = Config()
    
    # Model configuration
    config.model.base_model = BaseModel(args.base_model)
    config.model.training_mode = TrainingMode(args.training_mode)
    config.model.inference_model = args.inference_model
    config.model.num_rules = args.num_rules
    config.model.append_n_mask = args.append_n_mask
    config.model.nsw_detector = args.nsw_detector
    config.model.soft_labels = args.soft_labels
    config.model.loss_weights = args.loss_weights
    config.model.hard_student_rule = args.hard_student_rule
    config.model.fine_tuning_strategy = FineTuningStrategy(args.fine_tuning_strategy)
    config.model.learning_rate = args.learning_rate
    config.model.nsw_loss_weight = args.nsw_loss_weight
    config.model.n_mask_loss_weight = args.n_mask_loss_weight
    config.model.norm_loss_weight = args.norm_loss_weight
    
    # Unified HuggingFace pretrained model name
    config.model.pretrained_model_name = args.pretrained_model_name
    
    # Optimizer settings
    config.model.optimizer = args.optimizer
    config.model.weight_decay = args.weight_decay
    config.model.adam_betas = tuple(args.adam_betas)
    config.model.adam_eps = args.adam_eps
    
    # Learning rate scheduler settings
    config.model.use_scheduler = args.use_scheduler
    config.model.scheduler_type = args.scheduler_type
    config.model.warmup_epochs = args.warmup_epochs
    config.model.min_lr_ratio = args.min_lr_ratio
    
    # Gradient clipping settings
    config.model.max_grad_norm = args.max_grad_norm
    
    # Training configuration
    config.training.num_epochs = args.num_epochs
    config.training.num_unsup_epochs = args.num_unsup_epochs
    config.training.num_iter = args.num_iter
    config.training.train_batch_size = args.train_batch_size
    config.training.eval_batch_size = args.eval_batch_size
    config.training.unsup_batch_size = args.unsup_batch_size
    config.training.sample_size = args.sample_size
    config.training.remove_accents = args.remove_accents
    config.training.rm_accent_ratio = args.rm_accent_ratio
    config.training.lower_case = args.lower_case
    config.training.metric = args.metric
    
    # Path configuration
    config.paths.datapath = args.datapath
    config.paths.experiment_folder = args.experiment_folder
    # logdir is determined later by setup_experiment_directory
    
    # System configuration
    config.system.seed = args.seed
    config.system.debug = args.debug
    
    return config


def save_and_report_results(config: Config, results: dict, logger):
    """Save and report training results."""
    logger.info("*** TRAINING RESULTS ***")
    for key, value in results.items():
        if isinstance(value, dict) and 'perf' in value:
            logger.info(f"{key}: {value['perf']:.2f}%")
        else:
            logger.info(f"{key}: {value}")


def run_visonorm(config: Config, logger) -> dict:
    """
    Main ViSoNorm training pipeline.
    
    Args:
        config: Configuration object
        logger: Logger instance
        
    Returns:
        Dictionary containing training results
    """
    try:
        # Initialize training loop
        training_loop = TrainingLoop(config, logger)
        
        # Get tokenizer
        tokenizer = get_tokenizer(config)
        
        # Initialize components
        training_loop.initialize_components(tokenizer)
        
        # Load datasets
        datasets = training_loop.load_datasets()
        
        # Train initial student
        initial_results = training_loop.train_initial_student(datasets)
        
        # Evaluate initial student
        eval_results = training_loop.evaluate_initial_student(datasets)
        
        # Early return for only_student mode
        if config.model.training_mode == TrainingMode.ONLY_STUDENT:
            results = {
                'student_train': initial_results,
                'supervised_student_dev': eval_results['dev'],
                'supervised_student_test': eval_results['test']
            }
            save_and_report_results(config, results, logger)
            return results
        
        # Initialize teacher results if needed
        if config.model.training_mode == TrainingMode.WEAKLY_SUPERVISED:
            training_loop.initialize_teacher_results()
        
        # Run training iterations
        for iteration in range(config.training.num_iter):
            training_loop.run_iteration(iteration, datasets)
        
        # Finalize results
        results = training_loop.finalize_results()
        
        return results
        
    except Exception as e:
        logger.error(f"Error in ViSoNorm training: {str(e)}")
        raise


def main():
    """Main entry point."""
    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Convert to config
    config = parse_args_to_config(args)
    
    # Set random seed
    np.random.seed(config.system.seed)
    
    # Setup experiment directory
    logdir = setup_experiment_directory(config)
    config.paths.logdir = logdir
    
    # Setup device
    device = setup_device(config)
    
    # Setup logger
    logger = get_logger(logfile=os.path.join(logdir, 'log.log'))
    
    # Log experiment start
    logger.info(f"*** NEW EXPERIMENT ***")
    logger.info(f"Device: {device}")
    logger.info(f"GPU count: {config.system.n_gpu}")
    logger.info(f"Config: {config}")
    
    try:
        # Run ViSoNorm training
        results = run_visonorm(config, logger)
        
        logger.info("*** END EXPERIMENT ***")
        return results
        
    except Exception as e:
        logger.error(f"Experiment failed: {str(e)}")
        raise
    finally:
        close(logger)


if __name__ == "__main__":
    main()
