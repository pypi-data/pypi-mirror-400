import json
import re
import os
import numpy as np
import joblib
import unicodedata
import random
from datasets import Dataset
import torch
import attridict
from transformers import AutoTokenizer
from visonorm.global_variables import (
    SPECIAL_TOKEN_LS, BOS_TOKEN, EOS_TOKEN, RM_ACCENTS_DICT,
    PRETRAINED_TOKENIZER_MAP, NULL_STR,
    PROJECT_PATH, DATASET_DIR, LOG_DIR, ARGS_PATH, CKPT_DIR
)
import contextlib

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

def get_arguments():
    import chardet
    import json

    with open(ARGS_PATH, 'rb') as f:
        # Detect file encoding
        raw_data = f.read()
        detected_encoding = chardet.detect(raw_data)['encoding']
    
    # Fallback to the detected encoding (default to UTF-8 if detection fails)
    encoding = detected_encoding if detected_encoding else 'utf-8'

    with open(ARGS_PATH, 'r', encoding=encoding) as f:
        args = json.load(f)
        args = attridict(args)
        args.datapath = DATASET_DIR
        args.ckpt_dir = CKPT_DIR
        args.logdir = LOG_DIR
    return args


def get_tokenizer(model_name):
    tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_TOKENIZER_MAP[model_name])
    tokenizer.add_tokens([NULL_STR])
    return tokenizer

def bold(text):
    trans = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
        "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
    )
    return text.translate(trans)

def run_strip_accents(txt, ratio):
    if not unicodedata.is_normalized("NFC", txt):
        txt = unicodedata.normalize("NFC", txt)
    num_character = len(txt)
    num_remove = int(ratio*num_character)
    random_indices = random.sample(np.arange(num_character).tolist(), num_remove)
    new_txt = ""
    for i in range(num_character):
        c = txt[i]
        if i in random_indices:
            c = c.translate(RM_ACCENTS_DICT)
        new_txt += c
    return new_txt

def sort_data(dataset, remove_accents=False):
    if remove_accents:
        new_dataset = Dataset.from_dict(dataset.no_accent_data)
    else:
        new_dataset = Dataset.from_dict(dataset.data)
    sorted_dataset = new_dataset.sort('sent_len')
    return sorted_dataset

def gen_dataIter(dataset, batch_size, len_list=None, shuffle=False, seed=None):
    if batch_size==1:
        for batch in dataset:
            yield batch
    else:
        if len_list is None:
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

def evaluate(model, dataset, evaluator, mode="standard", comment="test", remove_accents=False):
    if model.__class__.__name__ == "Student":
        dataset = sort_data(dataset, remove_accents=remove_accents)
    pred_dict = model.predict_ran(dataset=dataset) if mode=='ran' else model.predict(dataset=dataset)
    # pred_dict = {'id', 'sources', 'targets', 'preds', 'aligned_index'}
    res = evaluator.evaluate(preds=pred_dict['preds'],
                             targets=pred_dict['output_ids'],
                             sources=pred_dict['input_ids'],
                             comment=comment)
    if mode=='standard':
        return res
    else:
        return res, pred_dict

def add_special_token(tokenized_sent, bos_token=BOS_TOKEN, eos_token=EOS_TOKEN):
    tokenized_sent.insert(0, bos_token)
    tokenized_sent.append(eos_token)

def delete_special_tokens(token_lst):
    filtered_tokens = []
    original_indices = []
    
    for idx, token in enumerate(token_lst):
        if token not in SPECIAL_TOKEN_LS:
            filtered_tokens.append(token)
            original_indices.append(idx)
    
    return filtered_tokens, original_indices


def post_process(sent):
    sent = sent.capitalize()
    sent = re.sub(r'\s+([,\.])', r'\1', sent)
    if not sent.endswith('.'):
        sent += '.'
    return sent

def merge_dicts(dict_list):
    merged_dict = {}
    for d in dict_list:
        for key, value in d.items():
            if key in merged_dict:
                merged_dict[key].extend(value)
            else:
                merged_dict[key] = value.copy()
    return merged_dict

def write_predictions(args, logger, tokenizer, pred_dict, file_name=""):
    label = False
    if 'output_ids' in pred_dict:
        label = True
    results = Dataset.from_dict(pred_dict)
    data = []
    for i in range(len(results)):
        batch = results[i]
        sent_ids = batch['id']
        sources = batch['input_ids']
        if label:
            targets = batch['output_ids']
        preds = batch['preds']
        align_index = batch['align_index']
        is_nsw = batch['is_nsw']
        if args.nsw_detect:
            assert is_nsw, "ERROR: is_nsw must not be empty in NSW detection mode."
        for idx, sent_id in enumerate(sent_ids):
            source = sources[idx]
            decoded_source = tokenizer.convert_ids_to_tokens(source)
            decoded_source, _ = delete_special_tokens(decoded_source)
            source_str = tokenizer.convert_tokens_to_string(decoded_source)
            if label:
                target = targets[idx]
                decoded_target = tokenizer.convert_ids_to_tokens(target)
                decoded_target, _ = delete_special_tokens(decoded_target)
                target_str = tokenizer.convert_tokens_to_string(decoded_target)
            if is_nsw:
                norm_or_not = is_nsw[idx]
            pred = preds[idx]
            pred = [id for id in pred if id != -1]
            decoded_pred = tokenizer.convert_ids_to_tokens(pred)
            decoded_pred, _ = delete_special_tokens(decoded_pred)
            pred_str = tokenizer.convert_tokens_to_string(decoded_pred)
            if label:
                res = {
                    'id': sent_id,
                    'source_text': post_process(source_str),
                    'target_text': post_process(target_str),
                    'prediction_text': post_process(pred_str),
                    'source_tokens': decoded_source,
                    'target_tokens': decoded_target,
                    'prediction_tokens': decoded_pred,
                    'aligned_index': align_index[idx],
                    'is_nsw': norm_or_not
                }
            else:
                res = {
                    'id': sent_id,
                    'source_text': post_process(source_str),
                    'prediction_text': post_process(pred_str),
                    'source_tokens': decoded_source,
                    'prediction_tokens': decoded_pred,
                    'aligned_index': align_index[idx],
                    'is_nsw': norm_or_not
                }
            data.append(res)
    
    json_path = os.path.join(args.logdir, "{}.json".format(file_name))
    logger.info("Writing predictions to json file at {}".format(json_path))
    with open(json_path, "w") as final:
        json.dump(data, final)
    logger.info("Finish")
                       

def save_and_report_results(args, results, logger):
    logger.info("\t*** Final Results ***")
    for res, values in results.items():
        logger.info("\n{}:\t{}".format(res, values))
    savepath = os.path.join(args.logdir, 'results.pkl')
    logger.info('Saving results at {}'.format(savepath))
    joblib.dump(results, savepath)

    args_savepath = os.path.join(args.logdir, 'args.json')
    with open(args_savepath, 'w') as f:
        json.dump(vars(args), f)
    return


def clear_console():
    try:
        from IPython.display import clear_output as _ip_clear
        _ip_clear(wait=True)
    except Exception:
        os.system('cls' if os.name == 'nt' else 'clear')

@contextlib.contextmanager
def suppress_output():
    import sys
    import logging
    try:
        from transformers.utils import logging as tf_logging
    except Exception:
        tf_logging = None
    try:
        from huggingface_hub import logging as hub_logging
    except Exception:
        hub_logging = None

    prev_tf_level = None
    prev_hub_level = None
    if tf_logging:
        prev_tf_level = tf_logging.get_verbosity()
        tf_logging.set_verbosity_error()
    if hub_logging and hasattr(hub_logging, 'set_verbosity_error'):
        try:
            prev_hub_level = hub_logging.get_verbosity()
        except Exception:
            prev_hub_level = None
        hub_logging.set_verbosity_error()

    prev_env = {
        'HF_HUB_DISABLE_PROGRESS_BARS': os.environ.get('HF_HUB_DISABLE_PROGRESS_BARS'),
        'TRANSFORMERS_VERBOSITY': os.environ.get('TRANSFORMERS_VERBOSITY')
    }
    os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
    os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

    devnull = open(os.devnull, 'w')
    with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
        try:
            yield
        finally:
            devnull.close()
            if tf_logging and prev_tf_level is not None:
                tf_logging.set_verbosity(prev_tf_level)
            if hub_logging and prev_hub_level is not None and hasattr(hub_logging, 'set_verbosity'):
                try:
                    hub_logging.set_verbosity(prev_hub_level)
                except Exception:
                    pass
            for k, v in prev_env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

