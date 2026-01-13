"""
Refactored utility functions for ViSoNorm.
Clean, well-documented, and reusable utilities.
"""
import json
import os
import numpy as np
import unicodedata
import random
from typing import List, Dict, Any, Optional, Union
from datasets import Dataset
import torch
from transformers import PreTrainedTokenizer

from config import (
    MASK_TOKEN, PAD_TOKEN, BOS_TOKEN, EOS_TOKEN, 
    SPECIAL_TOKEN_LS, RM_ACCENTS_DICT
)


def get_config_attr(config, attr_path: str, default_value=None):
    """
    Helper function to get attributes from Config object with backward compatibility.
    
    Args:
        config: Config object or old args object
        attr_path: Dot-separated path to the attribute (e.g., 'model.base_model', 'training.metric')
        default_value: Default value if attribute is not found
        
    Returns:
        The attribute value or default_value
    """
    try:
        # Split the path and navigate through the object
        parts = attr_path.split('.')
        current = config
        
        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                return default_value
        
        # Handle enum values
        if hasattr(current, 'value'):
            return current.value
        return current
        
    except (AttributeError, TypeError):
        return default_value


def run_strip_accents(text: str, ratio: float) -> str:
    """
    Randomly strip accents from text based on given ratio.
    
    Args:
        text: Input text
        ratio: Ratio of characters to strip accents from (0.0 to 1.0)
        
    Returns:
        Text with randomly stripped accents
    """
    if not unicodedata.is_normalized("NFC", text):
        text = unicodedata.normalize("NFC", text)
    
    num_character = len(text)
    num_remove = int(ratio * num_character)
    random_indices = random.sample(range(num_character), num_remove)
    
    new_txt = ""
    for i, char in enumerate(text):
        if i in random_indices:
            char = char.translate(RM_ACCENTS_DICT)
        new_txt += char
    
    return new_txt


def sort_data(dataset: Dataset, remove_accents: bool = False) -> Dataset:
    """
    Sort dataset by sentence length.
    
    Args:
        dataset: Input dataset
        remove_accents: Whether to use accent-removed data
        
    Returns:
        Sorted dataset
    """
    if remove_accents:
        new_dataset = Dataset.from_dict(dataset.no_accent_data)
    else:
        new_dataset = Dataset.from_dict(dataset.data)
    
    return new_dataset.sort('sent_len')


def gen_data_iter(
    dataset: Dataset, 
    batch_size: int, 
    len_list: Optional[List[int]] = None, 
    shuffle: bool = False, 
    seed: Optional[int] = None
):
    """
    Generate data iterator with optional length-based batching.
    
    Args:
        dataset: Input dataset
        batch_size: Batch size
        len_list: List of sentence lengths to batch together
        shuffle: Whether to shuffle data
        seed: Random seed for shuffling
        
    Yields:
        Batches of data
    """
    if batch_size == 1:
        for batch in dataset:
            yield batch
        return
    
    if len_list is None:
        # Simple batching
        if shuffle:
            dataset = dataset.shuffle(seed=seed)
        
        num_samples = len(dataset)
        num_batches = (num_samples + batch_size - 1) // batch_size
        
        for i in range(num_batches):
            start_index = i * batch_size
            end_index = min((i + 1) * batch_size, num_samples)
            batch = dataset[start_index:end_index]
            yield batch
    else:
        # Length-based batching
        for sent_len in len_list:
            sub_dataset = dataset.filter(lambda example: example["sent_len"] == sent_len)
            
            if shuffle:
                sub_dataset = sub_dataset.shuffle(seed=seed)
            
            num_samples = len(sub_dataset)
            num_batches = (num_samples + batch_size - 1) // batch_size
            
            for i in range(num_batches):
                start_index = i * batch_size
                end_index = min((i + 1) * batch_size, num_samples)
                batch = sub_dataset[start_index:end_index]
                yield batch


def add_special_tokens(
    tokenized_sent: List[str], 
    bos_token: str = BOS_TOKEN, 
    eos_token: str = EOS_TOKEN
) -> List[str]:
    """
    Add special tokens to tokenized sentence.
    
    Args:
        tokenized_sent: List of tokens
        bos_token: Beginning of sentence token
        eos_token: End of sentence token
        
    Returns:
        Token list with special tokens added
    """
    tokenized_sent.insert(0, bos_token)
    tokenized_sent.append(eos_token)
    return tokenized_sent


def remove_special_tokens(token_list: List[str]) -> List[str]:
    """
    Remove special tokens from token list.
    
    Args:
        token_list: List of tokens
        
    Returns:
        Token list with special tokens removed
    """
    return [token for token in token_list if token not in SPECIAL_TOKEN_LS]


def merge_dicts(dict_list: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    """
    Merge list of dictionaries by extending values.
    
    Args:
        dict_list: List of dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    merged_dict = {}
    for d in dict_list:
        for key, value in d.items():
            if key in merged_dict:
                merged_dict[key].extend(value)
            else:
                merged_dict[key] = value.copy()
    return merged_dict


def convert_predictions_to_strings(
    tokenizer: PreTrainedTokenizer, 
    topk_preds: torch.Tensor, 
    topk: int
) -> List[str]:
    """
    Convert top-k predictions to strings.
    
    Args:
        tokenizer: Tokenizer instance
        topk_preds: Tensor of top-k predictions
        topk: Number of top predictions
        
    Returns:
        List of prediction strings
    """
    topk_preds_list = [
        [topk_preds[word, top].item() for word in range(topk_preds.size(0))] 
        for top in range(topk)
    ]
    
    sent_list_top = []
    for sent in topk_preds_list:
        pred = [id for id in sent if id != -1]
        decoded_pred = tokenizer.convert_ids_to_tokens(pred)
        pred_str = tokenizer.convert_tokens_to_string(remove_special_tokens(decoded_pred))
        sent_list_top.append(pred_str)
    
    return sent_list_top


def write_predictions(
    config, 
    logger, 
    tokenizer: PreTrainedTokenizer, 
    pred_dict: Dict[str, Any], 
    file_name: str = ""
) -> None:
    """
    Write predictions to JSON file with efficient chunking to avoid memory issues.
    
    Args:
        config: Configuration object
        logger: Logger instance
        tokenizer: Tokenizer instance
        pred_dict: Dictionary containing predictions
        file_name: Output file name
    """
    has_labels = 'output_ids' in pred_dict
    total_samples = len(pred_dict['id'])
    data = []
    
    # Process data in chunks to avoid memory overflow
    chunk_size = 1000
    for start_idx in range(0, total_samples, chunk_size):
        end_idx = min(start_idx + chunk_size, total_samples)
        
        # Process chunk directly without Dataset conversion for better performance
        process_chunk_direct(
            pred_dict, start_idx, end_idx, data, has_labels, tokenizer
        )
    
    # Write data to file
    write_data_to_file(data, config, logger, file_name)

def process_chunk_direct(pred_dict, start_idx, end_idx, data, has_labels, tokenizer):
    """Process a chunk of data directly without Dataset conversion for better performance."""
    for i in range(start_idx, end_idx):
        sent_id = pred_dict['id'][i]
        source = pred_dict['input_ids'][i]
        pred = pred_dict['preds'][i]
        align_index = pred_dict['align_index'][i]
        
        # Decode source - ensure it's a flat Python list of integers
        if hasattr(source, 'tolist'):
            source_list = source.tolist()
        elif hasattr(source, 'cpu'):
            source_list = source.cpu().tolist()
        else:
            source_list = list(source)
        
        # Flatten if it's nested (e.g., [[1,2,3]] -> [1,2,3])
        if isinstance(source_list, list) and len(source_list) > 0 and isinstance(source_list[0], list):
            source_list = source_list[0]
        
        decoded_source = tokenizer.convert_ids_to_tokens(source_list)
        source_str = tokenizer.convert_tokens_to_string(remove_special_tokens(decoded_source))
        
        # Decode prediction - ensure it's a flat Python list of integers
        if hasattr(pred, 'tolist'):
            pred_list = pred.tolist()
        elif hasattr(pred, 'cpu'):
            pred_list = pred.cpu().tolist()
        else:
            pred_list = list(pred)
        
        # Flatten if it's nested (e.g., [[1,2,3]] -> [1,2,3])
        if isinstance(pred_list, list) and len(pred_list) > 0 and isinstance(pred_list[0], list):
            pred_list = pred_list[0]
        
        pred_list = [id for id in pred_list if id != -1]
        decoded_pred = tokenizer.convert_ids_to_tokens(pred_list)
        pred_str = tokenizer.convert_tokens_to_string(remove_special_tokens(decoded_pred))
        
        result = {
            'id': sent_id,
            'source_text': source_str,
            'prediction_text': pred_str,
            'source_tokens': decoded_source,
            'prediction_tokens': decoded_pred,
            'aligned_index': align_index
        }
        
        # Add target if available
        if has_labels:
            target = pred_dict['output_ids'][i]
            
            # Ensure target is a flat Python list of integers
            if hasattr(target, 'tolist'):
                target_list = target.tolist()
            elif hasattr(target, 'cpu'):
                target_list = target.cpu().tolist()
            else:
                target_list = list(target)
            
            # Flatten if it's nested (e.g., [[1,2,3]] -> [1,2,3])
            if isinstance(target_list, list) and len(target_list) > 0 and isinstance(target_list[0], list):
                target_list = target_list[0]
            
            decoded_target = tokenizer.convert_ids_to_tokens(target_list)
            target_str = tokenizer.convert_tokens_to_string(remove_special_tokens(decoded_target))
            result.update({
                'target_text': target_str,
                'target_tokens': decoded_target
            })
        
        data.append(result)


def process_chunk(results, data, has_labels, tokenizer):
    """Process a chunk of results and add to data list (legacy function for backward compatibility)."""
    for i in range(len(results)):
        batch = results[i]
        sent_ids = batch['id']
        sources = batch['input_ids']
        preds = batch['preds']
        align_index = batch['align_index']
        
        if has_labels:
            targets = batch['output_ids']
        
        for idx, sent_id in enumerate(sent_ids):
            source = sources[idx]
            decoded_source = tokenizer.convert_ids_to_tokens(source)
            source_str = tokenizer.convert_tokens_to_string(remove_special_tokens(decoded_source))
            
            pred = preds[idx]
            pred = [id for id in pred if id != -1]
            decoded_pred = tokenizer.convert_ids_to_tokens(pred)
            pred_str = tokenizer.convert_tokens_to_string(remove_special_tokens(decoded_pred))
            
            result = {
                'id': sent_id,
                'source_text': source_str,
                'prediction_text': pred_str,
                'source_tokens': decoded_source,
                'prediction_tokens': decoded_pred,
                'aligned_index': align_index[idx]
            }
            
            if has_labels:
                target = targets[idx]
                decoded_target = tokenizer.convert_ids_to_tokens(target)
                target_str = tokenizer.convert_tokens_to_string(remove_special_tokens(decoded_target))
                result.update({
                    'target_text': target_str,
                    'target_tokens': decoded_target
                })
            
            data.append(result)

def write_data_to_file(data, config, logger, file_name):
    """Write processed data to JSON file."""
    json_path = os.path.join(config.paths.logdir, f"{file_name}.json")
    logger.info(f"Writing predictions to {json_path}")
    
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info("Finished writing predictions")


def save_and_report_results(config, results: Dict[str, Any], logger) -> None:
    """
    Save results to pickle file and log summary.
    
    Args:
        config: Configuration object
        results: Results dictionary
        logger: Logger instance
    """
    import joblib
    
    logger.info("*** Final Results ***")
    for res_name, values in results.items():
        logger.info(f"{res_name}:\t{values}")
    
    # Save results
    results_path = os.path.join(config.paths.logdir, 'results.pkl')
    logger.info(f'Saving results to {results_path}')
    joblib.dump(results, results_path)
    
    # Save arguments
    args_path = os.path.join(config.paths.logdir, 'args.json')
    with open(args_path, 'w') as f:
        json.dump(vars(config), f, default=str, indent=2)


def evaluate_model(
    model, 
    dataset: Dataset, 
    evaluator, 
    mode: str = "standard", 
    comment: str = "test", 
    remove_accents: bool = False
) -> Union[Dict[str, Any], tuple]:
    """
    Evaluate model on dataset.
    
    Args:
        model: Model to evaluate
        dataset: Evaluation dataset
        evaluator: Evaluator instance
        mode: Evaluation mode ("standard" or "ran")
        comment: Comment for logging
        remove_accents: Whether to remove accents
        
    Returns:
        Evaluation results (and predictions if mode != "standard")
    """
    if model.__class__.__name__ == "Student":
        dataset = sort_data(dataset, remove_accents=remove_accents)
    
    pred_dict = model.predict_ran(dataset=dataset) if mode == 'ran' else model.predict(dataset=dataset)
    
    results = evaluator.evaluate(
        preds=pred_dict['preds'],
        targets=pred_dict['output_ids'],
        sources=pred_dict['input_ids'],
        comment=comment
    )
    
    if mode == 'standard':
        return results
    else:
        return results, pred_dict


def get_optimizer(parameters, lr: float, optimizer: str = "adam", betas: Optional[tuple] = None):
    """
    Create optimizer for given parameters.
    
    Args:
        parameters: Model parameters
        lr: Learning rate
        optimizer: Optimizer type
        betas: Beta parameters for Adam
        
    Returns:
        Optimizer instance
    """
    if betas is None:
        betas = (0.9, 0.999)
    
    if optimizer.lower() == "adam":
        return torch.optim.Adam(parameters, lr=lr, eps=1e-9, betas=betas)
    else:
        raise ValueError(f"Unsupported optimizer: {optimizer}")


def apply_fine_tuning_strategy(
    fine_tuning_strategy: str, 
    model, 
    lr_init: Union[float, Dict[str, float]], 
    betas: Optional[tuple] = None, 
    append_n_mask: bool = False
) -> List[torch.optim.Optimizer]:
    """
    Apply fine-tuning strategy to create optimizers.
    
    Args:
        fine_tuning_strategy: Strategy name
        model: Model to optimize
        lr_init: Initial learning rate(s)
        betas: Beta parameters
        append_n_mask: Whether model has mask predictor
        
    Returns:
        List of optimizers
    """
    from config import AVAILABLE_FINE_TUNING_STRATEGY
    
    if fine_tuning_strategy not in AVAILABLE_FINE_TUNING_STRATEGY:
        raise ValueError(f"Strategy {fine_tuning_strategy} not in {AVAILABLE_FINE_TUNING_STRATEGY}")
    
    if fine_tuning_strategy == "standard":
        if not isinstance(lr_init, float):
            raise TypeError(f"lr_init should be float for {fine_tuning_strategy}")
        
        optimizer = [get_optimizer(model.parameters(), lr=lr_init, betas=betas)]
        print(f"TRAINING: fine tuning strategy {fine_tuning_strategy}, learning rate {lr_init}, betas {betas}")
        
    else:  # flexible_lr
        if not isinstance(lr_init, dict):
            raise TypeError(f"lr_init should be dict for {fine_tuning_strategy}")
        
        optimizer = []
        all_layers = len([a for a, _ in model.named_parameters()])
        optim_layers = 0
        
        for prefix, lr in lr_init.items():
            param_group = [param for name, param in model.named_parameters() if name.startswith(prefix)]
            optim_layers += len(param_group)
            optimizer.append(get_optimizer(param_group, lr=lr, betas=betas))
        
        if all_layers != optim_layers:
            raise ValueError(f"Missing layers in optimization: all={all_layers}, optim={optim_layers}")
    
    return optimizer


def get_label_n_masks(input_tensor: torch.Tensor, num_labels_n_masks: int) -> torch.Tensor:
    """
    Get labels for number of masks prediction.
    
    Args:
        input_tensor: Input tensor with mask positions
        num_labels_n_masks: Number of mask labels
        
    Returns:
        Tensor with mask count labels
    """
    output = torch.empty_like(input_tensor).long()
    
    for sent_idx in range(input_tensor.size(0)):
        count = 0
        for word_idx in range(input_tensor.size(1)):
            if input_tensor[sent_idx, word_idx] == 1:
                output[sent_idx, word_idx] = -1
                if count == 0:
                    ind_multi_bpe = word_idx - 1
                count += 1
            elif input_tensor[sent_idx, word_idx] == 0:
                # Reached end of multi-BPE
                if word_idx > 0 and input_tensor[sent_idx, word_idx - 1] == 1:
                    output[sent_idx, ind_multi_bpe] = min(count, num_labels_n_masks - 1)
                    count = 0
                output[sent_idx, word_idx] = 0
    
    return output
