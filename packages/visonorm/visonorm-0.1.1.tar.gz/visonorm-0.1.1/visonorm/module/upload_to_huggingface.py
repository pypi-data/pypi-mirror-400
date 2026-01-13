#!/usr/bin/env python3
"""
Script to upload trained ViSoNorm student model to Hugging Face Hub.
Supports ViSoBERT, PhoBERT, and BARTpho models.
"""

import os
import json
import argparse
import torch
from pathlib import Path
from typing import Optional, Dict, Any
from transformers import AutoTokenizer, AutoConfig
from huggingface_hub import HfApi, Repository, create_repo, hf_hub_download
import shutil

from config import Config, BaseModel, PRETRAINED_TOKENIZER_MAP
from base_model.Student import Student
from base_model.ViSoNormalizer import ViSoNormalizerTrainer


def analyze_checkpoint_weights(state_dict, base_model: str) -> dict:
    """Analyze presence of expected ViSoNorm head weights vs common alternatives.

    Returns a report dictionary with counts and example keys to help detect issues
    like missing heads or mismatched parameter names.
    """
    keys = list(state_dict.keys())

    expected_heads = [
        'cls_decoder.weight', 'cls_decoder.bias',
        'cls_dense.weight', 'cls_dense.bias',
        'cls_layer_norm.weight', 'cls_layer_norm.bias',
        'mask_n_predictor.mask_predictor_dense.weight', 'mask_n_predictor.mask_predictor_dense.bias',
        'mask_n_predictor.mask_predictor_proj.weight', 'mask_n_predictor.mask_predictor_proj.bias',
        'nsw_detector.dense.weight', 'nsw_detector.dense.bias',
        'nsw_detector.predictor.weight', 'nsw_detector.predictor.bias',
    ]

    alt_common_heads = [
        'lm_head.weight', 'lm_head.bias',
        'cls.decoder.weight', 'cls.decoder.bias',
        'cls.dense.weight', 'cls.dense.bias',
        'cls.layer_norm.weight', 'cls.layer_norm.bias',
    ]

    aux_heads = [
        'nsw_detector.', 'mask_n_predictor.',
    ]

    def present(name):
        return any(k == name or k.startswith(name) for k in keys)

    report = {
        'base_model': base_model,
        'total_params': len(keys),
        'expected_heads_present': {name: present(name) for name in expected_heads},
        'alt_common_heads_present': {name: present(name) for name in alt_common_heads},
        'aux_heads_present': {n: any(n in k for k in keys) for n in aux_heads},
        'example_keys': keys[:20],
    }

    return report


def create_model_card(model_name: str, base_model: str, performance: Dict[str, Any], 
                     training_config: Dict[str, Any]) -> str:
    """Create a model card for the uploaded model."""
    
    model_card = f"""---
    license: mit
    tags:
    - text-normalization
    - vietnamese
    - lexical-normalization
    - visonorm
    - {base_model}
    pipeline_tag: fill-mask
    ---

    # {model_name}

    This model is a Vietnamese text normalization model trained using the ViSoNorm framework with {base_model.upper()} architecture.

    ## Model Description

    This model performs lexical normalization for Vietnamese text, converting informal text to standard Vietnamese. It was trained using the ViSoNorm (Self-training with Weak Supervision) framework.

    ## Performance

    """

    if performance:
        model_card += "| Metric | Score |\n"
        model_card += "|--------|-------|\n"
        for metric, score in performance.items():
            if isinstance(score, (int, float)):
                model_card += f"| {metric} | {score:.2f}% |\n"

    model_card += f"""
        ## Training Configuration

        - **Base Model**: {base_model.upper()}
        - **Training Mode**: {training_config.get('training_mode', 'N/A')}
        - **Learning Rate**: {training_config.get('learning_rate', 'N/A')}
        - **Epochs**: {training_config.get('num_epochs', 'N/A')}
        - **Batch Size**: {training_config.get('train_batch_size', 'N/A')}

        ## Usage

        ```python
        from transformers import AutoTokenizer, AutoModelForMaskedLM

        # Load model and tokenizer
        model_repo = "your-username/your-model-name"  # Replace with your actual repo
        tokenizer = AutoTokenizer.from_pretrained(model_repo)
        model = AutoModelForMaskedLM.from_pretrained(model_repo, trust_remote_code=True)

        # Normalize text using the built-in method
        text = "sv dh gia dinh chua cho di lam :))"
        normalized_text, source_tokens, predicted_tokens = model.normalize_text(
            tokenizer, text, device='cpu'
        )

        # Output: sinh viên đại học gia đình chưa cho đi làm :))
        ```

        ## Example Outputs

        | Input | Output |
        |-------|--------|
        | `sv dh gia dinh chua cho di lam :))` | `sinh viên đại học gia đình chưa cho đi làm :))` |
        | `chúng nó bảo em là ctrai` | `chúng nó bảo em là con trai` |
        | `anh ơi em muốn đi chơi` | `anh ơi em muốn đi chơi` |

        ## Citation

        If you use this model, please cite the ViSoNorm paper:

        ```bibtex
        @article{{visonorm2024,
        title={{ViSoNorm: Self-training with Weak Supervision for Vietnamese Text Normalization}},
        author={{Your Name}},
        journal={{arXiv preprint}},
        year={{2024}}
        }}
        ```
        """
    
    return model_card


def get_model_config_from_state_dict(model_path):
    """Extract configuration parameters from the actual model file"""
    try:
        # Handle both file and directory paths
        if os.path.isfile(model_path):
            # Direct file path provided
            state_dict_path = model_path
        else:
            # Directory path provided, look for model files inside
            model_file_bin = os.path.join(model_path, "pytorch_model.bin")
            model_file_pt = os.path.join(model_path, "final_model.pt")
            if os.path.exists(model_file_bin):
                state_dict_path = model_file_bin
            elif os.path.exists(model_file_pt):
                state_dict_path = model_file_pt
            else:
                print(f"Warning: No model file found in directory {model_path}")
                return {}
        
        # Load the model state dict
        state_dict = torch.load(state_dict_path, map_location='cpu')
        
        config_info = {}
        
        
        # Look for specific embedding keys based on the actual model structure
        for key, tensor in state_dict.items():
            # ViSoBERT/PhoBERT embeddings
            if key == 'roberta.embeddings.word_embeddings.weight':
                vocab_size = tensor.shape[0]
                config_info['vocab_size'] = vocab_size
            elif key == 'roberta.embeddings.position_embeddings.weight':
                max_pos = tensor.shape[0]
                config_info['max_position_embeddings'] = max_pos
            elif key == 'roberta.embeddings.token_type_embeddings.weight':
                type_vocab_size = tensor.shape[0]
                config_info['type_vocab_size'] = type_vocab_size
            # BartPho embeddings
            elif key == 'model.shared.weight':
                vocab_size = tensor.shape[0]
                config_info['vocab_size'] = vocab_size
            elif key == 'model.encoder.embed_positions.weight':
                max_pos = tensor.shape[0]
                config_info['max_position_embeddings'] = max_pos
            elif key == 'model.decoder.embed_positions.weight':
                max_pos = tensor.shape[0]
                config_info['max_position_embeddings'] = max_pos
            # Alternative BartPho embedding keys
            elif 'shared.weight' in key and 'vocab_size' not in config_info:
                vocab_size = tensor.shape[0]
                config_info['vocab_size'] = vocab_size
            elif 'embed_positions.weight' in key and 'max_position_embeddings' not in config_info:
                max_pos = tensor.shape[0]
                config_info['max_position_embeddings'] = max_pos
            elif 'positional_embedding' in key.lower() and 'max_position_embeddings' not in config_info:
                max_pos = tensor.shape[0]
                config_info['max_position_embeddings'] = max_pos
        
        # Look for hidden size from any embedding
        for key, tensor in state_dict.items():
            if 'embedding' in key.lower() and 'weight' in key.lower() and len(tensor.shape) == 2:
                hidden_size = tensor.shape[1]
                config_info['hidden_size'] = hidden_size
                break
        
        # Fallback: if we still don't have vocab_size, try to find it from any word embedding
        if 'vocab_size' not in config_info:
            for key, tensor in state_dict.items():
                if ('word' in key.lower() or 'shared' in key.lower()) and 'weight' in key.lower() and len(tensor.shape) == 2:
                    vocab_size = tensor.shape[0]
                    config_info['vocab_size'] = vocab_size
                    break
        
        # Fallback: if we still don't have max_position_embeddings, try to find it from any position embedding
        if 'max_position_embeddings' not in config_info:
            for key, tensor in state_dict.items():
                if ('position' in key.lower() or 'pos' in key.lower()) and 'weight' in key.lower() and len(tensor.shape) == 2:
                    max_pos = tensor.shape[0]
                    config_info['max_position_embeddings'] = max_pos
                    break
        
        # Look for number of layers from transformer blocks
        layer_count = 0
        for key in state_dict.keys():
            if 'layer.' in key and 'weight' in key:
                try:
                    layer_num = int(key.split('layer.')[1].split('.')[0])
                    layer_count = max(layer_count, layer_num + 1)
                except:
                    pass
        
        if layer_count > 0:
            config_info['num_hidden_layers'] = layer_count
        
        return config_info
        
    except Exception as e:
        print(f"Error reading model file: {e}")
        return {}


def assert_heads_present(model_bin_path: str) -> dict:
    """Return a presence report for required heads and raise if missing."""
    state_dict = torch.load(model_bin_path, map_location="cpu")
    def present(prefix: str) -> int:
        return sum(1 for k in state_dict.keys() if k.startswith(prefix))
    report = {
        "cls": present("cls."),
        "mask_n_predictor": present("mask_n_predictor."),
        "nsw_detector": present("nsw_detector."),
    }
    # Require both auxiliary heads to be present for multitask inference
    if report["mask_n_predictor"] == 0 or report["nsw_detector"] == 0:
        raise RuntimeError(
            "Missing head weights in checkpoint: "
            f"mask_n_predictor={report['mask_n_predictor']}, "
            f"nsw_detector={report['nsw_detector']}. "
            "Re-export from training ensuring all heads are saved."
        )
    return report


def prepare_model_for_upload(model_path: str, base_model: str, config: Config, hf_config_json: Optional[str] = None) -> Dict[str, Any]:
    """Prepare the model files for upload to Hugging Face."""
    
    # Create temporary directory for upload (clean up any existing one)
    temp_dir = Path(f"temp_upload_{base_model}")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Copy model files (prefer pytorch_model.bin, fallback to final_model.pt)
        # Check if model_path is a file or directory
        if os.path.isfile(model_path):
            # Direct file path provided
            shutil.copy2(model_path, temp_dir / "pytorch_model.bin")
        else:
            # Directory path provided, look for model files inside
            model_file_bin = os.path.join(model_path, "pytorch_model.bin")
            model_file_pt = os.path.join(model_path, "final_model.pt")
            if os.path.exists(model_file_bin):
                shutil.copy2(model_file_bin, temp_dir / "pytorch_model.bin")
            elif os.path.exists(model_file_pt):
                shutil.copy2(model_file_pt, temp_dir / "pytorch_model.bin")
            else:
                raise FileNotFoundError(f"Model file not found: {model_file_bin} or {model_file_pt}")

        # Enforce presence of multitask heads
        head_report = assert_heads_present(str(temp_dir / "pytorch_model.bin"))
        # Persist a small JSON report for transparency
        with open(temp_dir / "state_dict_report.json", "w", encoding="utf-8") as f:
            json.dump(head_report, f, indent=2)
        
        # Create or reuse config.json (prefer provided or existing; else download base and minimally override)
        model_type_mapping = {
            'visobert': 'xlm-roberta',
            'phobert': 'roberta', 
            'bartpho': 'mbart',  # BARTpho is based on mBART architecture
            'vit5': 't5',        # ViT5 uses T5 encoder architecture
        }
        architecture_mapping = {
            'visobert': 'ViSoNormViSoBERTForMaskedLM',
            'phobert': 'RobertaForMaskedLM',
            'bartpho': 'ViSoNormBartPhoForMaskedLM',  # Use our custom class
            'vit5': 'ViSoNormViT5ForMaskedLM',        # Custom ViT5 class
        }
        standard_model_type = model_type_mapping.get(base_model.lower(), 'roberta')
        standard_architecture = architecture_mapping.get(base_model.lower(), 'RobertaForMaskedLM')
        # If explicit HF config is provided, use it
        used_existing_config = False
        if hf_config_json and os.path.exists(hf_config_json):
            shutil.copy2(hf_config_json, temp_dir / "config.json")
            used_existing_config = True
        else:
            # Try to reuse config.json from model directory
            model_dir_for_config = model_path if os.path.isdir(model_path) else os.path.dirname(model_path)
            existing_cfg = os.path.join(model_dir_for_config, "config.json")
            if os.path.exists(existing_cfg):
                shutil.copy2(existing_cfg, temp_dir / "config.json")
                used_existing_config = True

        if not used_existing_config:
            # Download base config.json from the pretrained backbone and minimally override
            pretrained_name = getattr(getattr(config, 'model', None), 'pretrained_model_name', None)
            if not pretrained_name:
                raise ValueError("pretrained_model_name must be provided in Config.model.pretrained_model_name to download base config.json")
            try:
                base_cfg_path = hf_hub_download(repo_id=pretrained_name, filename="config.json")
                with open(base_cfg_path, "r", encoding="utf-8") as f:
                    base_cfg = json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to download base config.json from {pretrained_name}: {e}. Falling back to checkpoint-derived config.")
                base_cfg = {}

            # Derive minimal necessary values from checkpoint/tokenizer
            model_config_info = get_model_config_from_state_dict(model_path)
            vocab_size = model_config_info.get('vocab_size', len(config.tokenizer) if hasattr(config, 'tokenizer') else base_cfg.get('vocab_size', 32000))

            # Merge overrides
            updated_cfg = dict(base_cfg)
            updated_cfg['vocab_size'] = int(vocab_size)
            updated_cfg['mask_n_predictor'] = True
            updated_cfg['nsw_detector'] = True
            # Ensure architectures/model_type minimally consistent if missing
            updated_cfg.setdefault('model_type', standard_model_type)
            updated_cfg.setdefault('architectures', [standard_architecture])

            with open(temp_dir / "config.json", "w", encoding="utf-8") as f:
                json.dump(updated_cfg, f, indent=2)

        # Ensure auto_map and architectures always point to our custom classes, even when reusing existing config
        try:
            with open(temp_dir / "config.json", "r", encoding="utf-8") as f:
                cfg_current = json.load(f)
        except Exception:
            cfg_current = {}

        auto_map = (
            {
                "AutoModel": "visonorm_visobert_model.ViSoNormViSoBERTForMaskedLM",
                "AutoModelForMaskedLM": "visonorm_visobert_model.ViSoNormViSoBERTForMaskedLM"
            } if base_model.lower() == 'visobert' else
            {
                "AutoModel": "visonorm_phobert_model.ViSoNormPhoBERTForMaskedLM",
                "AutoModelForMaskedLM": "visonorm_phobert_model.ViSoNormPhoBERTForMaskedLM"
            } if base_model.lower() == 'phobert' else
            {
                "AutoModel": "visonorm_bartpho_model.ViSoNormBartPhoForMaskedLM",
                "AutoModelForMaskedLM": "visonorm_bartpho_model.ViSoNormBartPhoForMaskedLM"
            } if base_model.lower() == 'bartpho' else
            {
                "AutoModel": "visonorm_vit5_model.ViSoNormViT5ForMaskedLM",
                "AutoModelForMaskedLM": "visonorm_vit5_model.ViSoNormViT5ForMaskedLM"
            } if base_model.lower() == 'vit5' else None
        )
        if auto_map is not None:
            cfg_current['auto_map'] = auto_map
            cfg_current['architectures'] = [standard_architecture]
            with open(temp_dir / "config.json", "w", encoding="utf-8") as f:
                json.dump(cfg_current, f, indent=2)
        
        # Create tokenizer config for better compatibility
        if base_model.lower() == 'bartpho':
            # BartPho requires specific tokenizer configuration
            tokenizer_config = {
                "tokenizer_class": "BartPhoTokenizer",
                "model_max_length": 512,
                "padding_side": "right",
                "truncation_side": "right",
                "pad_token": "<pad>",
                "bos_token": "<s>",
                "eos_token": "</s>",
                "unk_token": "<unk>",
                "mask_token": "<mask>",
                "additional_special_tokens": ["<pad>", "<s>", "</s>", "<unk>", "<mask>"],
                "use_fast": False,  # BartPho typically uses slow tokenizer
            }
        else:
            # Base tokenizer config - special tokens may vary by model
            additional_tokens = ["<pad>", "<s>", "</s>", "<unk>", "<mask>", "<space>"]
            
            tokenizer_config = {
                "tokenizer_class": "XLMRobertaTokenizer" if base_model.lower() == 'visobert' else 
                                  "RobertaTokenizer" if base_model.lower() == 'phobert' else 
                                  ("T5Tokenizer" if base_model.lower() == 'vit5' else "BartPhoTokenizer"),
                "model_max_length": 512,
                "padding_side": "right",
                "truncation_side": "right",
                "pad_token": "<pad>",
                "bos_token": "<s>",
                "eos_token": "</s>",
                "unk_token": "<unk>",
                "mask_token": "<mask>",
                "additional_special_tokens": additional_tokens
            }
        
        with open(temp_dir / "tokenizer_config.json", "w") as f:
            json.dump(tokenizer_config, f, indent=2)
        
        # Copy ViSoNorm custom model file based on architecture
        def get_architecture_model_file(base_model: str) -> str:
            """Get the appropriate ViSoNorm model file for the architecture."""
            base_model_lower = base_model.lower()
            if 'bartpho' in base_model_lower or 'bart' in base_model_lower:
                return "visonorm_bartpho_model.py"
            elif 'phobert' in base_model_lower or 'roberta' in base_model_lower:
                return "visonorm_phobert_model.py"
            elif 'visobert' in base_model_lower or 'xlm' in base_model_lower:
                return "visonorm_visobert_model.py"
            elif 'vit5' in base_model_lower or 't5' in base_model_lower:
                return "visonorm_vit5_model.py"
            else:
                # Default to ViSoBERT for unknown models
                return "visonorm_visobert_model.py"
        
        visonorm_model_file = get_architecture_model_file(base_model)
        if os.path.exists(visonorm_model_file):
            shutil.copy2(visonorm_model_file, temp_dir / visonorm_model_file)
        else:
            print(f"Warning: ViSoNorm model file not found: {visonorm_model_file}")
        
        # Copy README.md if it exists
        readme_file = "README.md"
        if os.path.exists(readme_file):
            shutil.copy2(readme_file, temp_dir / "README.md")
        
        # Determine model directory for tokenizer file copying
        if os.path.isfile(model_path):
            # If model_path is a file, look for tokenizer files in the parent directory
            model_dir = os.path.dirname(model_path)
        else:
            # If model_path is a directory, use it directly
            model_dir = model_path
        
        # For BartPho, we need to ensure we have the correct tokenizer files
        if base_model.lower() == 'bartpho':
            # CRITICAL: The training process modifies the tokenizer by adding special tokens like <space>
            # We MUST use the modified tokenizer files from training, not the original BartPho files
            
            # Priority 1: Use modified tokenizer files from training (these contain the <space> token)
            modified_tokenizer_files = [
                "tokenizer.json",           # Contains the full modified vocabulary
                "tokenizer_config.json",    # Contains tokenizer configuration
                "special_tokens_map.json",  # Contains special token mappings including <space>
                "added_tokens.json"        # Contains the added tokens (like <space>)
            ]
            
            # CRITICAL: Copy the BARTpho tokenization file for proper tokenizer behavior
            bartpho_tokenization_files = [
                "tokenization_bartpho.py",  # Custom BARTpho tokenizer implementation
                "bartpho_tokenization.py"   # Alternative naming
            ]
            
            tokenization_file_found = False
            for file_name in bartpho_tokenization_files:
                src_path = os.path.join(model_dir, file_name)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, temp_dir / file_name)
                    tokenization_file_found = True
                    break
            
            if not tokenization_file_found:
                print("⚠️  BARTpho tokenization file not found! Attempting to download from vinai/bartpho-syllable...")
                
                try:
                    from huggingface_hub import hf_hub_download
                    # Download the tokenization file from the original BARTpho repository
                    tokenization_file = hf_hub_download(
                        repo_id="vinai/bartpho-syllable",
                        filename="tokenization_bartpho.py",
                        local_dir=temp_dir
                    )
                    tokenization_file_found = True
                except Exception as e:
                    print(f"❌ Failed to download BARTpho tokenization file: {e}. This may cause tokenization issues when loading the model.")
            
            modified_files_found = 0
            for file_name in modified_tokenizer_files:
                src_path = os.path.join(model_dir, file_name)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, temp_dir / file_name)
                    modified_files_found += 1
                else:
                    # File missing; will rely on fallbacks below
                    pass
            # Priority 2: Copy original BartPho files as fallback (but these won't have <space> token)
            original_bartpho_files = [
                "vocab.txt",
                "monolingual_vocab.txt", 
                "dict.txt",
                "spm.model",
                "sentencepiece.bpe.model"
            ]
            
            for file_name in original_bartpho_files:
                src_path = os.path.join(model_dir, file_name)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, temp_dir / file_name)
                else:
                    # File not present; continue
                    pass
            
            # Check if we have the critical modified files
            if modified_files_found < 2:
                print("🚨 CRITICAL WARNING: Missing modified tokenizer files! The model was trained with a modified tokenizer that includes the <space> token. Without these files, the model will predict weird characters.")
        
        # Copy tokenizer files if they exist
        tokenizer_path = os.path.join(model_dir, "tokenizer")
        if os.path.exists(tokenizer_path):
            shutil.copytree(tokenizer_path, temp_dir / "tokenizer", dirs_exist_ok=True)

        # Also copy common tokenizer artifacts from model_dir root if present
        maybe_tokenizer_files = [
            "tokenizer.json",
            "tokenizer_config.json",
            "special_tokens_map.json",
            "vocab.json",
            "merges.txt",
            "sentencepiece.model",
            "sentencepiece.bpe.model",
            # BartPho specific files
            "vocab.txt",
            "monolingual_vocab.txt",
            "dict.txt",
            "spm.model",
        ]
        
        copied_files = []
        for fname in maybe_tokenizer_files:
            src = os.path.join(model_dir, fname)
            if os.path.exists(src):
                shutil.copy2(src, temp_dir / fname)
                copied_files.append(fname)
        
        if not copied_files:
            print(f"Warning: No tokenizer files found in {model_dir}")
        
        # Create training arguments
        training_args = {
            "base_model": base_model,
            "training_mode": config.model.training_mode.value,
            "learning_rate": config.model.learning_rate,
            "num_epochs": config.training.num_epochs,
            "train_batch_size": config.training.train_batch_size,
            "eval_batch_size": config.training.eval_batch_size,
            "remove_accents": config.training.remove_accents,
            "lower_case": config.training.lower_case,
        }
        
        with open(temp_dir / "training_args.json", "w") as f:
            json.dump(training_args, f, indent=2)

        # Diagnostics: analyze checkpoint for expected heads vs alternatives
        try:
            if os.path.isfile(model_path):
                sd_path = model_path
            else:
                maybe_sd = os.path.join(model_path, "pytorch_model.bin")
                sd_path = maybe_sd if os.path.exists(maybe_sd) else None
            if sd_path:
                state_dict = torch.load(sd_path, map_location='cpu')
                diag = analyze_checkpoint_weights(state_dict, base_model)
                with open(temp_dir / "state_dict_report.json", "w") as f:
                    json.dump(diag, f, indent=2)
            else:
                print(f"Warning: No state dict found at {model_path}")
        except Exception as e:
            print(f"State dict analysis failed: {e}")
        
        # Read back the config.json we prepared for reporting
        try:
            with open(temp_dir / "config.json", "r", encoding="utf-8") as f:
                prepared_cfg = json.load(f)
        except Exception:
            prepared_cfg = {}
        return {
            "temp_dir": temp_dir,
            "model_config": prepared_cfg,
            "training_args": training_args
        }
        
    except Exception as e:
        # Cleanup on error
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise e


def upload_model_to_huggingface(
    model_path: str,
    base_model: str,
    repo_name: str,
    performance: Optional[Dict[str, Any]] = None,
    config: Optional[Config] = None,
    token: Optional[str] = None,
    hf_config_json: Optional[str] = None
):
    """Upload the trained model to Hugging Face Hub."""
    
    print(f"Preparing {base_model} model for upload...")
    
    # Prepare model files
    prep_result = prepare_model_for_upload(model_path, base_model, config, hf_config_json=hf_config_json)
    temp_dir = prep_result["temp_dir"]
    model_config = prep_result["model_config"]
    training_args = prep_result["training_args"]
    
    try:
        # Create repository
        print(f"Creating repository: {repo_name}")
        create_repo(repo_id=repo_name, token=token, exist_ok=True)
        
        # Initialize repository in a clean directory
        repo_dir = Path(f"repo_{base_model}")
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
            
        repo = Repository(
            local_dir=str(repo_dir),
            clone_from=repo_name,
            token=token
        )
        
        # Copy our prepared files to the repository
        for file_path in temp_dir.glob("*"):
            if file_path.is_file():
                shutil.copy2(file_path, repo_dir / file_path.name)
            elif file_path.is_dir():
                shutil.copytree(file_path, repo_dir / file_path.name, dirs_exist_ok=True)
        
        # Create model card
        model_card = create_model_card(
            repo_name, 
            base_model, 
            performance or {}, 
            training_args
        )
        
        with open(temp_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(model_card)
        
        # Upload files
        print("Uploading model files...")
        repo.push_to_hub(commit_message="Upload ViSoNorm trained model")
        
        print(f"✅ Successfully uploaded model to: https://huggingface.co/{repo_name}")
        
    except Exception as e:
        print(f"❌ Error uploading model: {str(e)}")
        raise e
    
    finally:
        # Cleanup temporary directories
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        repo_dir = Path(f"repo_{base_model}")
        if repo_dir.exists():
            shutil.rmtree(repo_dir)


def main():
    parser = argparse.ArgumentParser(description="Upload ViSoNorm model to Hugging Face Hub")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the saved model directory (e.g., ./experiments/visobert/weakly_supervised/student_best)")
    parser.add_argument("--base_model", type=str, required=True, choices=['visobert', 'phobert', 'bartpho', 'vit5'], help="Name of the base model (backbone)")
    parser.add_argument("--repo_name", type=str, required=True, help="Hugging Face repository name (e.g., username/vietnamese-text-normalizer)")
    parser.add_argument("--performance_file", type=str, required=False, help="Path to JSON file containing model performance metrics")
    parser.add_argument("--config_file", type=str, required=False, help="Path to config file used for training")
    parser.add_argument("--token", type=str, required=False, help="Hugging Face API token (or set HF_TOKEN environment variable)")
    parser.add_argument("--hf_config_json", type=str, required=False, help="Optional path to an existing Hugging Face config.json to use for upload")
    
    args = parser.parse_args()
    
    # Load performance metrics if provided
    performance = {}
    if args.performance_file and os.path.exists(args.performance_file):
        with open(args.performance_file, "r") as f:
            performance = json.load(f)
    
    # Load config if provided
    config = None
    if args.config_file and os.path.exists(args.config_file):
        # Load config from file
        with open(args.config_file, "r") as f:
            config_dict = json.load(f)
        config = Config()
        # Update config with loaded values
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
    else:
        # Create default config
        config = Config()
        config.model.base_model = BaseModel(args.base_model)
    
    # Get token from environment if not provided
    token = args.token or os.getenv("HF_TOKEN")
    if not token:
        print("❌ Please provide Hugging Face token via --token argument or HF_TOKEN environment variable")
        return
    
    # Upload model
    upload_model_to_huggingface(
        model_path=args.model_path,
        base_model=args.base_model,
        repo_name=args.repo_name,
        performance=performance,
        config=config,
        token=token,
        hf_config_json=args.hf_config_json
    )


if __name__ == "__main__":
    main()
