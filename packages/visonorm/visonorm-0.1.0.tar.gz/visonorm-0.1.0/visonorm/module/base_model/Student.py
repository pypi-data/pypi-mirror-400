import os
from base_model.ViSoNormalizer import ViSoNormalizerTrainer
from utils import sort_data
from utils import get_config_attr

supported_trainers = {
    'phobert': ViSoNormalizerTrainer,
    'visobert': ViSoNormalizerTrainer,
    'bartpho': ViSoNormalizerTrainer,
    'vit5': ViSoNormalizerTrainer,
}

class Student:
    def __init__(self, args, tokenizer, logger=None):
        self.args = args
        self.logger = logger
        self.name = get_config_attr(args, 'model.base_model', get_config_attr(args, 'base_model'))
        self.training_mode = get_config_attr(args, 'model.training_mode', get_config_attr(args, 'training_mode'))
        self.remove_accents = get_config_attr(args, 'training.remove_accents', get_config_attr(args, 'remove_accents', False))
        self.tokenizer = tokenizer
        assert self.name in supported_trainers, "Student not supported: <{}>".format(self.name)
        self.trainer_class = supported_trainers[self.name]
        self.trainer = self.trainer_class(args=self.args, tokenizer=self.tokenizer, logger=self.logger)

    def train(self, train_dataset, dev_dataset, mode='train'):
        assert mode in ['train', 'finetune', 'train_pseudo']
        if mode in ['train', 'finetune']:
            train_dataset = sort_data(train_dataset, remove_accents=self.remove_accents)
        dev_dataset = sort_data(dev_dataset, remove_accents=self.remove_accents)
        if mode == 'train':
            res = self.trainer.train(
                train_data=train_dataset,
                dev_data=dev_dataset,
            )
            return res
        if mode == 'finetune':
            res = self.trainer.finetune(
                train_data=train_dataset,
                dev_data=dev_dataset,
            )
            return res
        if mode == 'train_pseudo':
            res = self.trainer.train_pseudo(
                train_data=train_dataset.teacher_data if self.training_mode=='weakly_supervised' else train_dataset.student_data,
                dev_data=dev_dataset,
            )
            return res

    def predict(self, dataset, dataIter=None, inference_mode=False):
        res = self.trainer.predict(data=dataset, dataIter=dataIter, inference_mode=inference_mode)
        return res

    def inference(self, user_input):
        res = self.trainer.inference(user_input)
        return res

    def save(self, name='student'):
        # Handle both old args format and new Config format
        if hasattr(self.args, 'paths') and hasattr(self.args.paths, 'logdir'):
            logdir = self.args.paths.logdir
        elif hasattr(self.args, 'logdir'):
            logdir = self.args.logdir
        else:
            logdir = './experiments/student'  # fallback
        
        savefolder = os.path.join(logdir, name)
        self.logger.info('Saving {} to {}'.format(name, savefolder))
        os.makedirs(savefolder, exist_ok=True)
        self.trainer.save(savefolder)

    def load(self, name):
        # Handle both old args format and new Config format
        if hasattr(self.args, 'paths') and hasattr(self.args.paths, 'logdir'):
            logdir = self.args.paths.logdir
        elif hasattr(self.args, 'logdir'):
            logdir = self.args.logdir
        else:
            logdir = './experiments/student'  # fallback
        
        savefolder = os.path.join(logdir, name)
        if not os.path.exists(savefolder):
            raise(BaseException('Pre-trained student folder does not exist: {}'.format(savefolder)))
        self.trainer.load(savefolder)
