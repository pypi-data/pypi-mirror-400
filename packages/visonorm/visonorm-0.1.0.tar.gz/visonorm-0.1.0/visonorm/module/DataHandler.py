import os
from torch.utils.data import Dataset
import numpy as np
import pandas as pd
import torch
from copy import deepcopy
from sklearn.utils import shuffle
from ast import literal_eval
from itertools import chain
from utils import add_special_tokens as add_special_token, run_strip_accents
from utils import get_config_attr
from config import MASK_TOKEN, NULL_STR


class DataHandler:
    # This module is responsible for feeding the data to teacher/student
    # If teacher is applied, then student gets the teacher-labeled data instead of ground-truth labels
    def __init__(self, args, tokenizer, logger=None):
        self.args = args
        self.logger = logger
        self.tokenizer = tokenizer
        self.datasets = {}
        self.seed = get_config_attr(args, 'system.seed', get_config_attr(args, 'seed', 42))
        np.random.seed(self.seed)

    def load_dataset(self, method='train'):
        dataset = WSDataset(self.args, method=method, tokenizer=self.tokenizer, logger=self.logger)
        self.datasets[method] = dataset
        return dataset

    def create_pseudodataset(self, wsdataset):
        dataset = PseudoDataset(self.args, wsdataset, self.logger)
        return dataset


class WSDataset(Dataset):
    # WSDataset: Dataset for Weak Supervision.
    def __init__(self, args, method, tokenizer, logger=None):
        super(WSDataset, self).__init__()
        self.args = args
        self.seed = get_config_attr(args, 'system.seed', get_config_attr(args, 'seed', 42))
        self.lower_case = get_config_attr(args, 'training.lower_case', get_config_attr(args, 'lower_case', False))
        self.remove_accents = get_config_attr(args, 'training.remove_accents', get_config_attr(args, 'remove_accents', False))
        self.rm_accent_ratio = get_config_attr(args, 'training.rm_accent_ratio', get_config_attr(args, 'rm_accent_ratio', 0.5))
        
        datapath = get_config_attr(args, 'paths.datapath', get_config_attr(args, 'datapath', './data'))
        self.datapath = os.path.join(datapath, "{}.csv".format(method))
        
        self.method = method
        self.tokenizer = tokenizer
        self.logger = logger
        self.data = {}
        self.no_accent_data = {}
        self.load_dataset()
        self.num_labels = len(self.tokenizer)
    
    def strip_accents(self, sent_list):
        new_sent_list = []
        for sent in sent_list:
            word_list = []
            for word in sent:
                new_word = run_strip_accents(word, self.rm_accent_ratio)
                word_list.append(new_word)
            new_sent_list.append(word_list)
        return new_sent_list
    
    def preprocess(self, data, strip_accents=False):
        tokenized_src_ls = []
        tokenized_tgt_ls = [] if self.method != "unlabeled" else None
        aligned_idx_ls = []
        weak_label_ls = []
        sent_len_ls = []

        ids = data['id'].tolist()
        inputs = self.strip_accents(data['input'].tolist()) if strip_accents else data['input'].tolist()
        outputs = data['output'].tolist() if self.method != "unlabeled" else None
        weak_rules = [col for col in data.columns if col.startswith("rule")]
        weak_labels = data[weak_rules].values
        num_sents = len(data)
        num_rules = weak_labels.shape[1]

        for i in range(num_sents):
            tokenized_src = []
            tokenized_tgt = []
            aligned_idx = []
            tokenized_rule_preds = []

            input_seq = inputs[i]
            output_seq = outputs[i] if self.method != "unlabeled" else None
            rule_preds = weak_labels[i]
            
            if self.lower_case:
                input_seq = [token.lower() for token in input_seq]
                output_seq = [token.lower() for token in output_seq] if self.method != "unlabeled" else None
                for j, preds in enumerate(rule_preds):
                    if preds is None:
                        continue
                    
                    # Check for None values and non-string values in preds before calling .lower()
                    filtered_preds = []
                    for k, token in enumerate(preds):
                        if token is None:
                            filtered_preds.append("")  # Replace None with empty string
                        elif not isinstance(token, str):
                            filtered_preds.append(str(token).lower())  # Convert to string first, then lowercase
                        else:
                            filtered_preds.append(token.lower())
                    rule_preds[j] = filtered_preds
            aligned = 0
            for idx, source_token in enumerate(input_seq):
                target_token = output_seq[idx] if self.method != "unlabeled" else None
                rule_pred = [pred[idx] for pred in rule_preds]
                tokenized_source = self.tokenizer.tokenize(source_token)
                tokenized_target = self.tokenizer.tokenize(target_token) if self.method != "unlabeled" else None
 
                if self.method != "unlabeled":
                    len_diff = len(tokenized_source) - len(tokenized_target)
                    if len_diff < 0:
                        tokenized_source.extend([MASK_TOKEN]*abs(len_diff))
                    elif len_diff > 0:
                        tokenized_target.extend([NULL_STR]*len_diff)
                
                tokenized_rule_pred = [self.tokenizer.tokenize(token) for token in rule_pred]
                for j, pred in enumerate(tokenized_rule_pred):
                    if len(pred) < len(tokenized_source):
                        tokenized_rule_pred[j].extend([NULL_STR]*(len(tokenized_source)-len(pred)))
                    elif len(pred) > len(tokenized_source):
                        # print("WARNING: INDEX {} - LENGTH OF WEAK LABELS {} IS LONGER THAN SOURCE TOKEN {}".format(ids[i], pred, tokenized_source))
                        tokenized_rule_pred[j] = pred[:len(tokenized_source)]

                tokenized_src.extend(tokenized_source)
                if self.method != "unlabeled":
                    tokenized_tgt.extend(tokenized_target)
                aligned_idx.extend([aligned]*len(tokenized_source))
                aligned += 1

                if not tokenized_rule_preds:
                    tokenized_rule_preds = tokenized_rule_pred
                else:
                    for j in range(num_rules):
                        tokenized_rule_preds[j].extend(tokenized_rule_pred[j])

            add_special_token(tokenized_src)
            if self.method != "unlabeled":
                add_special_token(tokenized_tgt)
            for j in range(len(tokenized_rule_preds)):
                add_special_token(tokenized_rule_preds[j])

            sent_len = len(tokenized_src)
            
            tokenized_src_ls.append(tokenized_src)
            if self.method != "unlabeled":
                tokenized_tgt_ls.append(tokenized_tgt)
            aligned_idx_ls.append(aligned_idx)
            weak_label_ls.append(tokenized_rule_preds)
            sent_len_ls.append(sent_len)

        # Converts tokens to ids
        input_ids = [self.tokenizer.convert_tokens_to_ids(sent) for sent in tokenized_src_ls]
        output_ids = [self.tokenizer.convert_tokens_to_ids(sent) for sent in tokenized_tgt_ls] if self.method != "unlabeled" else None
        for i, weak_labels in enumerate(weak_label_ls):
            weak_label_ls[i] = [self.tokenizer.convert_tokens_to_ids(sent) for sent in weak_labels]

        reshaped_weak_label = []
        for i, sent in enumerate(weak_label_ls):
            num_rules = len(sent)
            num_words = len(sent[0])
            new_sent = []
            for j in range(num_words):
                new_sent.append([rule[j] for rule in sent])
            reshaped_weak_label.append(new_sent)
        reshaped_weak_label
          
        if self.method == "unlabeled":
            preprocessed_dataset = {
                'id': ids,
                'input': inputs,
                'input_ids': input_ids,
                'align_index': aligned_idx_ls,
                'weak_labels': reshaped_weak_label,
                'sent_len': sent_len_ls,
            }
        else:
          preprocessed_dataset = {
              'id': ids,
              'input': inputs,
              'output': outputs,
              'input_ids': input_ids,
              'output_ids': output_ids,
              'align_index': aligned_idx_ls,
              'weak_labels': reshaped_weak_label,
              'sent_len': sent_len_ls,
          }
        return preprocessed_dataset

    def load_dataset(self):
        if self.method == "unlabeled":
            converters = {'input': literal_eval, 'regex_rule': literal_eval, 'dict_rule': literal_eval, 'gpt4omini_rule': literal_eval, 'gemini_rule': literal_eval}
        else:
            converters = {'input': literal_eval, 'output': literal_eval, 'regex_rule': literal_eval, 'dict_rule': literal_eval, 'gpt4omini_rule': literal_eval, 'gemini_rule': literal_eval}
        
        data = pd.read_csv(self.datapath, converters=converters)
        data.rename(columns={'regex_rule': 'rule_01', 'dict_rule': 'rule_02', 'gpt4omini_rule': 'rule_03', 'gemini_rule': 'rule_04'}, inplace=True)
        data = data.dropna(ignore_index=True)

        self.logger.info("Pre-processing {} data for student...".format(self.method))
        self.data = self.preprocess(data) # dictionary: column - list of values (each_sentence)
        if self.remove_accents and self.method != 'unlabeled':
            self.logger.info("Removing accents of {} data for student...".format(self.method))
            self.no_accent_data = self.preprocess(data, strip_accents=True)
            new_dict = {}
            for key, values in self.no_accent_data.items():
                new_dict[key] = values + self.data[key]
            self.no_accent_data = new_dict

    def __len__(self):
        return len(self.data['id'])

    def __getitem__(self, item):
        ret = {
            'id': self.data['id'][item],
            'input': self.data['input'][item],
            'output': self.data['output'][item] if 'output' in self.data else None,
            'input_ids': self.data['input_ids'][item],
            'output_ids': self.data['output_ids'][item] if 'output' in self.data else None,
            'align_index': self.data['align_index'][item],
            'weak_labels': self.data['weak_labels'][item],
            'sent_len': self.data['sent_len'][item],
            }
        return ret


class PseudoDataset(Dataset):
    # PseudoDataset: a Dataset class that provides extra functionalities for teacher-student training.
    def __init__(self, args, wsdataset, logger=None):
        super(PseudoDataset, self).__init__()
        self.args = args
        self.seed = get_config_attr(args, 'system.seed', get_config_attr(args, 'seed', 42))
        self.method = wsdataset.method
        self.logger = logger
        self.num_labels = wsdataset.num_labels
        self.logger.info("copying data from {} dataset".format(wsdataset.method))
        self.original_data = deepcopy(wsdataset.data)
        self.data = deepcopy(self.original_data)
        self.no_accent_data = deepcopy(wsdataset.no_accent_data)
        self.student_data = {}
        self.teacher_data = {}
        self.logger.info("done")

    def keep(self, keep_indices, type='teacher'):
        self.logger.info("Creating Pseudo Dataset with {} items...".format(len(list(chain.from_iterable(keep_indices)))))
        new_dict = {}
        data = self.teacher_data if type=='teacher' else self.student_data
        for key, values in data.items():
            keep_sents = []
            for i, indices in enumerate(keep_indices):
                if len(indices)==0:
                    continue
                if key in ['id', 'align_index']:
                    keep_sent = [values[i][idx] for idx in indices]
                else:
                    keep_sent = values[i][np.array(indices)]
                keep_sents.append(keep_sent)
            new_dict[key] = keep_sents
        if type=='teacher':
            self.teacher_data = new_dict
        else:
            self.student_data = new_dict

    def downsample(self, sample_size):
        N = len(self.original_data['input'])
        if sample_size > N:
            self.logger.info("[WARNING] sample size = {} > {}".format(sample_size, N))
            sample_size = N
        self.logger.info("Downsampling {} data".format(sample_size))
        self.data = {}
        keep_indices = np.random.choice(N, sample_size, replace=False)
        for key, values in self.original_data.items():
            self.data[key] = [values[i] for i in keep_indices]
    
    def inference_downsample(self, start_idx, end_idx):
        self.logger.info("Downsampling data from index {} to {}".format(start_idx, end_idx))
        for key, values in self.original_data.items():
            self.data[key] = values[start_idx:end_idx]

    def drop(self, col='teacher_labels', value=-1, type='teacher'):
        indices = []
        data = self.teacher_data if type=='teacher' else self.student_data
        for i, array in enumerate(data[col]):
            all_neg_one = np.all(array == -1, axis=1)
            keep = np.flatnonzero(~all_neg_one).tolist()
            indices.append(keep)
        
        self.keep(indices, type=type)

    def __len__(self):
        return len(self.data['id'])

    def __getitem__(self, item):
        ret = {
            'id': self.data['id'][item],
            'input': self.data['input'][item],
            'output': self.data['output'][item] if 'output' in self.data else None,
            'input_ids': self.data['input_ids'][item],
            'output_ids': self.data['output_ids'][item] if 'output' in self.data else None,
            'align_index': self.data['align_index'][item],
            'weak_labels': self.data['weak_labels'][item],
            'sent_len': self.data['sent_len'][item],
            }
        return ret