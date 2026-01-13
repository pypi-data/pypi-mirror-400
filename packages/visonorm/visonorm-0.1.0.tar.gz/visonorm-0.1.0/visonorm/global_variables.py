import os

# OpenAI
OPENAI_MODEL = "gpt-4o"
MAX_TOKENS = 500
TEMPERATURE = 0.7

# Project directories
PROJECT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__))) # ./visonorm/visonorm
ARGS_PATH = os.path.join(PROJECT_PATH, 'arguments.json')
DATASET_DIR = os.path.join(PROJECT_PATH, "dataset")
CKPT_DIR = os.path.join(os.path.dirname(PROJECT_PATH), "model_checkpoints")
LOG_DIR = os.path.join(PROJECT_PATH, "logs")
DICT_PATH = os.path.join(PROJECT_PATH, "dictionary", "dictionary.json")
GIT_DOWNLOAD_URL = "https://github.com/AnhHoang0529/visonorm/releases/download/v0.0.1"

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
}

# Student constants
SAMPLES_PER_TASK_TO_REPORT = {"normalize": ["all", "NEED_NORM", "NORMED", "PRED_NEED_NORM", "PRED_NORMED"],
                              "n_masks_pred": ["all", "n_masks_1", "n_masks_2", "n_masks_3", "n_masks_4", "n_masks_5"]}
AVAILABLE_FINE_TUNING_STRATEGY = ["standard", "flexible_lr"]
RM_ACCENTS_DICT = str.maketrans(
    "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴáàảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ",
    "A"*17 + "D" + "E"*11 + "I"*5 + "O"*17 + "U"*11 + "Y"*5 + "a"*17 + "d" + "e"*11 + "i"*5 + "o"*17 + "u"*11 + "y"*5
)

ARGS = {
    "student_name": "bartpho",
    "max_token_len": 1024,
    "teacher_name": "ran",
    "training_mode": "weakly_supervised",
    "inference_model": "student",
    "ckpt_dir": CKPT_DIR,
    "logdir": LOG_DIR,
    "metric": "f1_score",
    "num_iter": 10,
    "num_rules": 2,
    "num_epochs": 10,
    "num_unsup_epochs": 5,
    "debug": 0,
    "remove_accents": 1,
    "rm_accent_ratio": 1.0,
    "append_n_mask": 1,
    "nsw_detect": 1,
    "soft_labels": 1,
    "loss_weights": 0,
    "hard_student_rule": 1,
    "train_batch_size": 16,
    "eval_batch_size": 128,
    "unsup_batch_size": 128,
    "lowercase": 1,
    "learning_rate": 0.001,
    "fine_tuning_strategy": "flexible_lr",
    "sample_size": 8096,
    "topk": 1,
    "seed": 42,
    "downstream_task": "vihsd"
}