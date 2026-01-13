"""
Training loop implementation for ViSoNorm.
Separates training logic from main orchestration.
"""
import logging
from typing import Dict, List, Any, Optional
import numpy as np

from config import Config
from base_model.Student import Student
from teacher.Teacher import Teacher
from core.data import DataHandler
from core.evaluation import Evaluator
from utils import evaluate_model as evaluate, write_predictions, save_and_report_results


class TrainingLoop:
    """Handles the main training loop for ViSoNorm."""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.evaluator = Evaluator(config, logger=logger)
        
        # Initialize components
        self.data_handler = None
        self.student = None
        self.teacher = None
        self.tokenizer = None
        
        # Results tracking
        self.results = {}
        self.performance_history = {
            'teacher_dev': [],
            'teacher_test': [],
            'teacher_train': [],
            'student_dev': [],
            'student_test': [],
            'student_train': []
        }
        self.student_predictions = []
    
    def initialize_components(self, tokenizer):
        """Initialize all training components."""
        self.tokenizer = tokenizer
        self.data_handler = DataHandler(self.config, tokenizer=tokenizer, logger=self.logger)
        self.student = Student(self.config, tokenizer=tokenizer, logger=self.logger)
        
        if self.config.model.training_mode.value == 'weakly_supervised':
            self.teacher = Teacher(self.config, tokenizer=tokenizer, logger=self.logger)
            self.teacher.student = self.student
            self._setup_teacher_dimensions()
    
    def _setup_teacher_dimensions(self):
        """Setup teacher model dimensions based on student model.

        Each backbone implementation exposes `actual_hidden_size`; prefer that.
        """
        model = self.student.trainer.model
        if hasattr(model, 'actual_hidden_size'):
            actual_hidden_size = model.actual_hidden_size
        else:
            # Safe fallbacks in case a model variant does not expose the attribute
            if hasattr(model, 'roberta'):
                actual_hidden_size = model.roberta.embeddings.word_embeddings.weight.size(1)
            elif hasattr(model, 'bart'):
                actual_hidden_size = model.bart.shared.weight.size(1)
            elif hasattr(model, 't5'):
                try:
                    actual_hidden_size = model.t5.encoder.embed_tokens.weight.size(1)
                except Exception:
                    actual_hidden_size = int(getattr(model.t5.config, 'd_model'))
            else:
                # Final fallback to config hidden size
                actual_hidden_size = int(getattr(getattr(model, 'config', object()), 'hidden_size', 768))
        
        self.teacher.agg_model.xdim = actual_hidden_size
        self.logger.info(f"Set RAN xdim to {actual_hidden_size} for {self.config.model.base_model.value}")
    
    def load_datasets(self):
        """Load all required datasets."""
        self.logger.info("Loading datasets")
        datasets = {}
        for split in ['train', 'dev', 'test', 'unlabeled']:
            datasets[split] = self.data_handler.load_dataset(method=split)
        
        # Create pseudo-dataset for unlabeled data
        datasets['pseudo'] = self.data_handler.create_pseudodataset(datasets['unlabeled'])
        datasets['pseudo'].downsample(self.config.training.sample_size)
        
        return datasets
    
    def train_initial_student(self, datasets: Dict[str, Any]) -> Dict[str, Any]:
        """Train student on initial labeled data."""
        self.logger.info("*** Training Student on labeled data ***")
        
        train_pseudo = self.data_handler.create_pseudodataset(datasets['train'])
        results = self.student.train(
            train_dataset=train_pseudo, 
            dev_dataset=datasets['dev'], 
            mode='train'
        )
        
        self.performance_history['student_train'].append(results)
        
        if self.config.model.training_mode.value == 'only_student':
            self.student.save('student_best')
        
        return results
    
    def evaluate_initial_student(self, datasets: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate student on dev and test sets."""
        # Dev evaluation
        self.logger.info("*** Evaluating student on dev data ***")
        dev_results = evaluate(
            self.student, datasets['dev'], self.evaluator,
            comment="student dev", 
            remove_accents=self.config.training.remove_accents
        )
        self.performance_history['student_dev'].append(dev_results)
        
        # Test evaluation
        self.logger.info("*** Evaluating student on test data ***")
        test_results, test_predictions = evaluate(
            self.student, datasets['test'], self.evaluator,
            "test", comment="student test",
            remove_accents=self.config.training.remove_accents
        )
        self.performance_history['student_test'].append(test_results)
        
        # Save predictions
        write_predictions(
            self.config, self.logger, self.tokenizer, 
            test_predictions, file_name="student_test_predictions"
        )
        
        return {
            'dev': dev_results,
            'test': test_results,
            'predictions': test_predictions
        }
    
    def initialize_teacher_results(self):
        """Initialize teacher results with zeros."""
        zero_results = {
            'precision': 0, 'recall': 0, 'f1_score': 0, 
            'accuracy': 0, 'perf': 0
        }
        self.performance_history['teacher_train'].append(zero_results)
        self.performance_history['teacher_dev'].append(zero_results)
        self.performance_history['teacher_test'].append(zero_results)
    
    def run_iteration(self, iteration: int, datasets: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single training iteration."""
        self.logger.info(f"*** Starting loop {iteration+1}/{self.config.training.num_iter} ***")
        np.random.seed(self.config.system.seed + iteration)
        
        # Downsample pseudo-dataset
        datasets['pseudo'].downsample(self.config.training.sample_size)
        
        iteration_results = {}
        
        if self.config.model.training_mode.value == 'weakly_supervised':
            iteration_results.update(self._run_teacher_iteration(datasets, iteration))
        else:
            iteration_results.update(self._run_self_training_iteration(datasets, iteration))
        
        # Re-train student on pseudo-labeled data
        self.logger.info('Re-train student on pseudo-labeled instances')
        pseudo_train_results = self.student.train(
            train_dataset=datasets['pseudo'], 
            dev_dataset=datasets['dev'], 
            mode='train_pseudo'
        )
        
        # Fine-tune student on clean labeled data
        self.logger.info('Fine-tuning the student on clean labeled data')
        train_pseudo = self.data_handler.create_pseudodataset(datasets['train'])
        finetune_results = self.student.train(
            train_dataset=train_pseudo, 
            dev_dataset=datasets['dev'], 
            mode='finetune'
        )
        
        self.performance_history['student_train'].append(finetune_results)
        
        # Evaluate student
        iteration_results.update(self._evaluate_student_iteration(datasets, iteration))
        
        # Save best model if improved
        self._save_best_model_if_improved(iteration_results['dev'])
        
        # Periodic memory cleanup to avoid RAM growth across long runs
        self._periodic_cleanup()
        
        return iteration_results
    
    def _run_teacher_iteration(self, datasets: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """Run teacher-based iteration."""
        # Train teacher
        self.teacher.train_ran(
            train_dataset=datasets['train'],
            dev_dataset=datasets['dev'],
            unlabeled_dataset=datasets['pseudo']
        )
        
        # Apply teacher on unlabeled data
        teacher_predictions = self.teacher.predict_ran(dataset=datasets['pseudo'])
        
        # Evaluate teacher
        self.logger.info("*** Evaluating teacher on dev data ***")
        teacher_dev_results, _ = evaluate(
            self.teacher, datasets['dev'], self.evaluator,
            "ran", comment=f"teacher dev iter{iteration+1}"
        )
        self.performance_history['teacher_dev'].append(teacher_dev_results)
        
        self.logger.info("*** Evaluating teacher on test data ***")
        teacher_test_results, _ = evaluate(
            self.teacher, datasets['test'], self.evaluator,
            "ran", comment=f"teacher test iter{iteration+1}"
        )
        self.performance_history['teacher_test'].append(teacher_test_results)
        
        # Update pseudo-dataset with teacher predictions
        self._update_pseudo_dataset_with_teacher(datasets['pseudo'], teacher_predictions)
        
        return {
            'teacher_dev': teacher_dev_results,
            'teacher_test': teacher_test_results
        }
    
    def _run_self_training_iteration(self, datasets: Dict[str, Any]) -> Dict[str, Any]:
        """Run self-training iteration."""
        from utils import sort_data
        
        sorted_pseudo = sort_data(datasets['pseudo'])
        student_predictions = self.student.predict(dataset=sorted_pseudo)
        
        # Update pseudo-dataset with student predictions
        self._update_pseudo_dataset_with_student(datasets['pseudo'], student_predictions)
        
        return {}
    
    def _update_pseudo_dataset_with_teacher(self, pseudo_dataset, teacher_predictions):
        """Update pseudo-dataset with teacher predictions."""
        self.logger.info("Update unlabeled data with Teacher's predictions")
        pseudo_dataset.teacher_data['id'] = teacher_predictions['id']
        pseudo_dataset.teacher_data['input_ids'] = teacher_predictions['input_ids']
        pseudo_dataset.teacher_data['align_index'] = teacher_predictions['align_index']
        pseudo_dataset.teacher_data['labels'] = teacher_predictions['preds']
        # If soft labels are required later, keep proba (downcast to float16 to save RAM);
        # otherwise, compute lightweight weights and drop proba to save memory
        if 'proba' in teacher_predictions and teacher_predictions['proba'] is not None:
            if self.config.model.soft_labels:
                pseudo_dataset.teacher_data['proba'] = [
                    arr.astype(np.float16) for arr in teacher_predictions['proba']
                ]
                pseudo_dataset.teacher_data['weights'] = [
                    np.max(arr, axis=-1) for arr in teacher_predictions['proba']
                ]
            else:
                pseudo_dataset.teacher_data['weights'] = [
                    np.max(arr, axis=-1) for arr in teacher_predictions['proba']
                ]
                teacher_predictions['proba'] = None
        else:
            pseudo_dataset.teacher_data['weights'] = None
        pseudo_dataset.drop(col='labels', value=-1, type='teacher')
    
    def _update_pseudo_dataset_with_student(self, pseudo_dataset, student_predictions):
        """Update pseudo-dataset with student predictions."""
        self.logger.info("Update unlabeled data with Student's predictions")
        pseudo_dataset.student_data['id'] = student_predictions['id']
        pseudo_dataset.student_data['input_ids'] = student_predictions['input_ids']
        pseudo_dataset.student_data['align_index'] = student_predictions['align_index']
        pseudo_dataset.student_data['labels'] = student_predictions['preds']
        # If soft labels are required later, keep proba (downcast to float16 to save RAM);
        # otherwise, compute lightweight weights and drop proba to save memory
        if 'proba' in student_predictions and student_predictions['proba'] is not None:
            if self.config.model.soft_labels:
                pseudo_dataset.student_data['proba'] = [
                    arr.astype(np.float16) for arr in student_predictions['proba']
                ]
                pseudo_dataset.student_data['weights'] = [
                    np.max(arr, axis=-1) for arr in student_predictions['proba']
                ]
            else:
                pseudo_dataset.student_data['weights'] = [
                    np.max(arr, axis=-1) for arr in student_predictions['proba']
                ]
                student_predictions['proba'] = None
        else:
            pseudo_dataset.student_data['weights'] = None
        pseudo_dataset.drop(col='labels', value=-1, type='student')
    
    def _evaluate_student_iteration(self, datasets: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """Evaluate student after iteration."""
        # Dev evaluation
        self.logger.info("*** Evaluating student on dev data ***")
        dev_results = evaluate(
            self.student, datasets['dev'], self.evaluator,
            comment=f"student dev iter{iteration+1}"
        )
        self.logger.info(f"Student Dev performance on iter {iteration}: {dev_results['perf']}")
        
        # Test evaluation
        self.logger.info("*** Evaluating student on test data ***")
        test_results, test_predictions = evaluate(
            self.student, datasets['test'], self.evaluator,
            "test", comment=f"student test iter{iteration+1}"
        )
        self.logger.info(f"Student Test performance on iter {iteration}: {test_results['perf']}")
        
        self.performance_history['student_dev'].append(dev_results)
        self.performance_history['student_test'].append(test_results)
        
        return {
            'dev': dev_results,
            'test': test_results,
            'predictions': None
        }
    
    def _save_best_model_if_improved(self, dev_results: Dict[str, Any]):
        """Save best model if performance improved."""
        if not self.performance_history['student_dev']:
            return
        
        prev_max = max([x['perf'] for x in self.performance_history['student_dev'][:-1]])
        if dev_results['perf'] > prev_max:
            self.logger.info(f"Improved dev performance from {prev_max:.2f} to {dev_results['perf']:.2f}")
            self.student.save("student_best")
            if self.config.model.training_mode.value == 'weakly_supervised':
                self.teacher.save("teacher_best")
            # Save current test predictions immediately as best snapshot
            test_snapshot, test_preds = evaluate(
                self.student, self.data_handler.load_dataset(method='test'), self.evaluator,
                "test", comment="student test best_snapshot",
                remove_accents=self.config.training.remove_accents
            )
            write_predictions(
                self.config, self.logger, self.tokenizer,
                test_preds, file_name="student_best_predictions"
            )
    
    def finalize_results(self) -> Dict[str, Any]:
        """Finalize and save all results."""
        self.logger.info("Final Results")
        
        # Log teacher performances if applicable
        if self.config.model.training_mode.value == 'weakly_supervised':
            self._log_teacher_performances()
        
        # Log student performances
        self._log_student_performances()
        
        # Find best epoch
        best_dev_epoch, best_test_epoch = self._find_best_epochs()
        
        # Compile final results
        self.results = self._compile_final_results(best_dev_epoch, best_test_epoch)
        
        # Save predictions and models
        self._save_final_artifacts(best_dev_epoch)
        
        # Clean memory-heavy fields now that artifacts are persisted
        self._cleanup_memory()
        
        return self.results
    
    def _log_teacher_performances(self):
        """Log teacher performance history."""
        teacher_dev = [self._convert_numpy_types(x['perf']) for x in self.performance_history['teacher_dev']]
        teacher_test = [self._convert_numpy_types(x['perf']) for x in self.performance_history['teacher_test']]
        teacher_perf_str = [
            f"{i}:\t{teacher_dev[i]:.2f}\t{teacher_test[i]:.2f}" 
            for i in range(len(teacher_dev))
        ]
        self.logger.info("TEACHER PERFORMANCES:\n" + "\n".join(teacher_perf_str))
    
    def _log_student_performances(self):
        """Log student performance history."""
        student_dev = [self._convert_numpy_types(x['perf']) for x in self.performance_history['student_dev']]
        student_test = [self._convert_numpy_types(x['perf']) for x in self.performance_history['student_test']]
        student_perf_str = [
            f"{i}:\t{student_dev[i]:.2f}\t{student_test[i]:.2f}" 
            for i in range(len(student_dev))
        ]
        self.logger.info("STUDENT PERFORMANCES:\n" + "\n".join(student_perf_str))
    
    def _find_best_epochs(self) -> tuple:
        """Find best dev and test epochs."""
        dev_perfs = [self._convert_numpy_types(x['perf']) for x in self.performance_history['student_dev']]
        test_perfs = [self._convert_numpy_types(x['perf']) for x in self.performance_history['student_test']]
        
        best_dev_epoch = len(dev_perfs) - np.argmax(dev_perfs[::-1]) - 1
        best_test_epoch = len(test_perfs) - np.argmax(test_perfs[::-1]) - 1
        
        self.logger.info(f"BEST DEV {self.config.training.metric} = {dev_perfs[best_dev_epoch]:.3f} for epoch {best_dev_epoch}")
        self.logger.info(f"FINAL TEST {self.config.training.metric} = {test_perfs[best_dev_epoch]:.3f} for epoch {best_dev_epoch} (max={test_perfs[best_test_epoch]:.2f} for epoch {best_test_epoch})")
        
        return best_dev_epoch, best_test_epoch
    
    def _compile_final_results(self, best_dev_epoch: int, best_test_epoch: int) -> Dict[str, Any]:
        """Compile final results dictionary with clean data types and lightweight histories."""
        results = {}
        
        # Add iteration results (store lightweight summaries only)
        results['student_train_iter'] = self._extract_lightweight_history('student_train')
        results['student_dev_iter'] = self._extract_lightweight_history('student_dev')
        results['student_test_iter'] = self._extract_lightweight_history('student_test')
        
        # Add best results
        results['student_dev'] = self._convert_numpy_types(self.performance_history['student_dev'][best_dev_epoch])
        results['student_test'] = self._convert_numpy_types(self.performance_history['student_test'][best_dev_epoch])
        
        # Add teacher results if applicable
        if self.config.model.training_mode.value == 'weakly_supervised':
            results['teacher_train_iter'] = self._extract_lightweight_history('teacher_train')
            results['teacher_dev_iter'] = self._extract_lightweight_history('teacher_dev')
            results['teacher_test_iter'] = self._extract_lightweight_history('teacher_test')
            results['teacher_dev'] = self._convert_numpy_types(self.performance_history['teacher_dev'][best_dev_epoch])
            results['teacher_test'] = self._convert_numpy_types(self.performance_history['teacher_test'][best_dev_epoch])
        
        return results

    def _extract_lightweight_history(self, key: str) -> List[Dict[str, Any]]:
        """Keep only essential metrics to minimize memory in persisted results."""
        history = self.performance_history.get(key, [])
        lightweight: List[Dict[str, Any]] = []
        for entry in history:
            if isinstance(entry, dict):
                lightweight.append({
                    'precision': self._convert_numpy_types(entry.get('precision', 0.0)),
                    'recall': self._convert_numpy_types(entry.get('recall', 0.0)),
                    'normed_recall': self._convert_numpy_types(entry.get('normed_recall', 0.0)),
                    'f1_score': self._convert_numpy_types(entry.get('f1_score', 0.0)),
                    'accuracy': self._convert_numpy_types(entry.get('accuracy', 0.0)),
                    'perf': self._convert_numpy_types(entry.get('perf', 0.0)),
                })
            else:
                lightweight.append(self._convert_numpy_types(entry))
        return lightweight

    def _periodic_cleanup(self):
        """Trim in-memory artifacts during long runs to limit CPU RAM usage."""
        # Drop predictions entirely; we now stream them to disk
        self.student_predictions = []
        
        # For train histories, keep only the last 2 entries (dev/test are already lightweight)
        for key in ['student_train', 'teacher_train']:
            if key in self.performance_history and len(self.performance_history[key]) > 2:
                self.performance_history[key] = self.performance_history[key][-2:]

    def _cleanup_memory(self):
        """Free heavy objects after finalization to release RAM."""
        import gc
        # Already dropped predictions earlier; ensure cleared
        self.student_predictions = []
        # Train histories can be large; keep only the last summary
        for key in ['student_train', 'teacher_train']:
            if key in self.performance_history and len(self.performance_history[key]) > 1:
                self.performance_history[key] = [self.performance_history[key][-1]]
        gc.collect()
    
    def _convert_numpy_types(self, obj):
        """Convert numpy types to native Python types recursively."""
        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy array
            return obj.tolist()
        else:
            return obj
    
    def _save_final_artifacts(self, best_dev_epoch: int):
        """Save final predictions and models."""
        # Best predictions were already persisted when the best model was found.
        
        # Save final models
        self.student.save("student_last")
        if self.config.model.training_mode.value == 'weakly_supervised':
            self.teacher.save("teacher_last")
        
        # Save results
        save_and_report_results(self.config, self.results, self.logger)
