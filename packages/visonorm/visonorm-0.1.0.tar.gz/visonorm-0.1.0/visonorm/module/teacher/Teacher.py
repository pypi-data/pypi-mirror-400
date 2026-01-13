import os
import numpy as np
import random
import torch
from teacher.RuleAttentionNetwork import RAN
from utils import sort_data, gen_data_iter as gen_dataIter
from utils import get_config_attr

class Teacher:
    """
    Teacher:
        (1) considers multiple weak sources (1) multiple weak (heuristic) rules, (2) Student
        (2) aggregates weak sources with an aggregation model (e.g., RAN) to compute a single pseudo-label
    """

    def __init__(self, args, tokenizer, logger=None):
        # Teacher name fixed to 'ran' (teacher_name arg removed)
        self.name = 'ran'
        
        if self.name != "ran":
            raise (BaseException("Teacher not supported: {}".format(self.name)))
        
        self.args = args
        self.logger = logger
        self.seed = get_config_attr(args, 'system.seed', get_config_attr(args, 'seed', 42))
        np.random.seed(self.seed)
        self.num_labels = len(tokenizer)  # Match student model vocabulary size
        self.num_rules = get_config_attr(args, 'model.num_rules', get_config_attr(args, 'num_rules', 2))
        self.agg_model = RAN(args=self.args, num_rules=self.num_rules, num_labels=self.num_labels,
                             logger=self.logger, name=self.name)
        self.name = 'ran'
        self.student = None

    def predict(self, dataset):
        dataset = sort_data(dataset)
        res = self.aggregate_sources(dataset)
        return res

    def predict_ran(self, dataset, inference_mode=False):
        self.logger.info("Getting RAN predictions")
        dataset = sort_data(dataset)
        len_ls = list(set(dataset['sent_len']))
        dataIter = gen_dataIter(dataset, self.agg_model.unsup_batch_size, len_ls)
        data_dict = self.student.predict(dataset=None, dataIter=dataIter)
        res = self.aggregate_sources(data_dict, inference_mode=inference_mode)
        return res

    def train_ran(self, train_dataset=None, dev_dataset=None, unlabeled_dataset=None):
        train_dataset = sort_data(train_dataset) if train_dataset is not None else None
        dev_dataset = sort_data(dev_dataset) if dev_dataset is not None else None
        unlabeled_dataset = sort_data(unlabeled_dataset) if unlabeled_dataset is not None else None

        self.logger.info("Getting rule predictions")
        train_len_ls = list(set(train_dataset['sent_len']))
        trainIter = gen_dataIter(train_dataset, self.agg_model.sup_batch_size, train_len_ls, shuffle=True, seed=self.seed)
        dev_len_ls = list(set(dev_dataset['sent_len']))
        devIter = gen_dataIter(dev_dataset, self.agg_model.sup_batch_size, dev_len_ls)
        unsup_len_ls = list(set(unlabeled_dataset['sent_len']))
        unsupIter = gen_dataIter(unlabeled_dataset, self.agg_model.unsup_batch_size, unsup_len_ls)

        self.logger.info("Getting student predictions on train (and dev) dataset")
        assert self.student is not None, "To train RAN we need access to the Student"
        train_data = self.student.predict(dataset=None, dataIter=trainIter) if train_dataset is not None else {'features': None, 'proba': None}
        dev_data = self.student.predict(dataset=None, dataIter=devIter) if dev_dataset is not None else {'features': None, 'proba': None}
        unsup_data = self.student.predict(dataset=None, dataIter=unsupIter) if unlabeled_dataset is not None else {'features': None, 'proba': None}

        self.logger.info("Training Rule Attention Network")
        # Use gradient accumulation to reduce memory usage
        gradient_accumulation_steps = 4  # Adjust based on available memory
        self.agg_model.train(
            train_data=train_data,
            dev_data=dev_data,
            unsup_data=unsup_data,
            gradient_accumulation_steps=gradient_accumulation_steps
        )
        del train_data, dev_data, unsup_data
        return {}

    def aggregate_sources(self, data_dict, inference_mode=False):
        if self.name != "ran":
            raise(BaseException("Teacher method not implemented: {}".format(self.name)))
        res = self.agg_model.predict_ran(data_dict, inference_mode=inference_mode)
        return res

    def save(self, savename=None):
        # Handle both old args format and new Config format
        if hasattr(self.args, 'paths') and hasattr(self.args.paths, 'logdir'):
            logdir = self.args.paths.logdir
        elif hasattr(self.args, 'logdir'):
            logdir = self.args.logdir
        else:
            logdir = './experiments/teacher'  # fallback
        
        if savename is None:
            savefolder = os.path.join(logdir, 'teacher_best')
        else:
            savefolder = os.path.join(logdir, savename)

        self.logger.info("Saving teacher at {}".format(savefolder))
        os.makedirs(savefolder, exist_ok=True)
        # Save using HuggingFace-style filename
        model_file = os.path.join(savefolder, 'pytorch_model.bin')
        self.agg_model.save(model_file)
        return

    def load(self, name):
        # Handle both old args format and new Config format
        if hasattr(self.args, 'paths') and hasattr(self.args.paths, 'logdir'):
            logdir = self.args.paths.logdir
        elif hasattr(self.args, 'logdir'):
            logdir = self.args.logdir
        else:
            logdir = './experiments/teacher'  # fallback
        
        savefolder = os.path.join(logdir, name)
        self.logger.info("Loading teacher from {}".format(savefolder))
        # Prefer .bin, fallback to legacy .pt
        model_file_bin = os.path.join(savefolder, 'pytorch_model.bin')
        model_file_pt = os.path.join(savefolder, 'rule_attention_network.pt')
        model_file = model_file_bin if os.path.exists(model_file_bin) else model_file_pt
        self.agg_model.load(model_file)
        return
