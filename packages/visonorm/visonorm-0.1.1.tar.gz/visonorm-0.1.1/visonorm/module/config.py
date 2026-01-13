"""
Configuration management for ViSoNorm project.
Centralizes all configuration parameters and constants.
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

# Project path
PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))


class TrainingMode(Enum):
    ONLY_STUDENT = "only_student"
    SELF_TRAINING = "self_training"
    WEAKLY_SUPERVISED = "weakly_supervised"


class BaseModel(Enum):
    PHOBERT = "phobert"
    VISOBERT = "visobert"
    BARTPHO = "bartpho"
    VIT5 = "vit5"


class FineTuningStrategy(Enum):
    STANDARD = "standard"
    FLEXIBLE_LR = "flexible_lr"


@dataclass
class ModelConfig:
    """Configuration for model parameters."""
    base_model: BaseModel = BaseModel.VISOBERT
    training_mode: TrainingMode = TrainingMode.WEAKLY_SUPERVISED
    inference_model: str = "student"
    
    # Model architecture
    num_rules: int = 2
    append_n_mask: bool = False
    nsw_detector: bool = False  # NSW (Non-Standard Word) detection
    soft_labels: bool = False
    loss_weights: bool = False
    hard_student_rule: bool = False
    
    # HuggingFace pretrained model name (unified for all backbones).
    # If None or empty, a sensible default will be chosen based on `base_model`:
    #   phobert -> "vinai/phobert-base"
    #   visobert -> "uitnlp/visobert"
    #   bartpho -> "vinai/bartpho-syllable"
    #   vit5    -> "VietAI/vit5-base"
    pretrained_model_name: Optional[str] = None
    
    # Multi-task training weights
    nsw_loss_weight: float = 1.0
    n_mask_loss_weight: float = 1.0
    norm_loss_weight: float = 1.0
    
    # Fine-tuning
    fine_tuning_strategy: FineTuningStrategy = FineTuningStrategy.FLEXIBLE_LR
    learning_rate: float = 1e-3
    
    # Optimizer settings
    optimizer: str = "adamw"  # "adam", "adamw"
    weight_decay: float = 0.01
    adam_betas: tuple = (0.9, 0.999)
    adam_eps: float = 1e-8
    
    # Learning rate scheduling
    use_scheduler: bool = True
    scheduler_type: str = "cosine"  # "cosine", "linear", "plateau", "none"
    warmup_epochs: int = 2
    min_lr_ratio: float = 0.1  # min_lr = learning_rate * min_lr_ratio
    
    # Gradient clipping
    max_grad_norm: float = 1.0


@dataclass
class TrainingConfig:
    """Configuration for training parameters."""
    num_epochs: int = 10
    num_unsup_epochs: int = 5
    num_iter: int = 10
    
    # Batch sizes
    train_batch_size: int = 16
    eval_batch_size: int = 128
    unsup_batch_size: int = 128
    
    # Data processing
    sample_size: int = 8096
    remove_accents: bool = False
    rm_accent_ratio: float = 0.5
    lower_case: bool = False
    
    # Evaluation
    metric: str = "f1_score"


@dataclass
class PathConfig:
    """Configuration for file paths."""
    project_path: str = os.path.dirname(os.path.realpath(__file__))
    datapath: str = os.path.join(project_path, "data")
    experiment_folder: str = os.path.join(project_path, "experiments")
    logdir: str = "./experiments/visobert"
    
    @property
    def pretrained_phobert(self) -> str:
        return os.path.join(self.project_path, "model/pretrained/phobert")
    
    @property
    def pretrained_visobert(self) -> str:
        return os.path.join(self.project_path, "model/pretrained/visobert")
    
    @property
    def sp_model(self) -> str:
        return os.path.join(self.pretrained_visobert, "sentencepiece.bpe.model")


@dataclass
class SystemConfig:
    """Configuration for system parameters."""
    seed: int = 42
    debug: bool = False
    device: Optional[str] = None
    n_gpu: int = 0


@dataclass
class Config:
    """Main configuration class combining all configs."""
    model: ModelConfig = ModelConfig()
    training: TrainingConfig = TrainingConfig()
    paths: PathConfig = PathConfig()
    system: SystemConfig = SystemConfig()
    
    def __post_init__(self):
        """Set up derived configurations after initialization."""
        self.system.logdir = os.path.join(
            self.paths.experiment_folder, 
            self.model.base_model.value, 
            self.model.training_mode.value
        )


# Tokenizer constants
MASK_TOKEN = '<mask>'
BOS_TOKEN = '<s>'
EOS_TOKEN = '</s>'
PAD_TOKEN = '<pad>'
NULL_STR = '<space>'
UNK_TOKEN = '<unk>'
NUM_LABELS_N_MASKS = 5
NULL_STR_TO_SHOW = '_'

SPECIAL_TOKEN_LS = [NULL_STR, MASK_TOKEN, BOS_TOKEN, EOS_TOKEN, UNK_TOKEN]

PRETRAINED_TOKENIZER_MAP = {
    'phobert': 'vinai/phobert-base',
    'visobert': 'uitnlp/visobert',
    'bartpho': 'vinai/bartpho-syllable',
    'vit5': 'VietAI/vit5-base',
}

# Pretrained model paths
PRETRAINED_VISOBERT = os.path.join(PROJECT_PATH, "model/pretrained/visobert")
PRETRAINED_PHOBERT = os.path.join(PROJECT_PATH, "model/pretrained/phobert")

# Accent removal dictionary
RM_ACCENTS_DICT = str.maketrans(
    "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴáàảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ",
    "A"*17 + "D" + "E"*11 + "I"*5 + "O"*17 + "U"*11 + "Y"*5 + "a"*17 + "d" + "e"*11 + "i"*5 + "o"*17 + "u"*11 + "y"*5
)

# Available fine-tuning strategies
AVAILABLE_FINE_TUNING_STRATEGY = ["standard", "flexible_lr"]

# Additional constants for backward compatibility
DATASET_DIR = os.path.join(PROJECT_PATH, "data")
SP_MODEL = os.path.join(PRETRAINED_VISOBERT, "sentencepiece.bpe.model")
NUM_RULES = 2
EXPERIMENT_DIR = os.path.join(PROJECT_PATH, "experiments")
UNLABELED_SAMPLE_SIZE = 8096

# Samples per task for reporting
SAMPLES_PER_TASK_TO_REPORT = {
    "normalize": ["all", "NEED_NORM", "NORMED", "PRED_NEED_NORM", "PRED_NORMED"],
    "n_masks_pred": ["all", "n_masks_1", "n_masks_2", "n_masks_3", "n_masks_4", "n_masks_5"]
}
