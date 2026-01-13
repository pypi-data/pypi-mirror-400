"""
Model definitions and wrappers for ViSoNorm.
"""
from typing import Optional
import logging

from config import Config
from base_model.Student import Student
from teacher.Teacher import Teacher


class ModelFactory:
    """Factory for creating model instances."""
    
    @staticmethod
    def create_student(config: Config, tokenizer, logger: Optional[logging.Logger] = None) -> Student:
        """Create a student model instance."""
        return Student(config, tokenizer=tokenizer, logger=logger)
    
    @staticmethod
    def create_teacher(config: Config, tokenizer, logger: Optional[logging.Logger] = None) -> Teacher:
        """Create a teacher model instance."""
        return Teacher(config, tokenizer=tokenizer, logger=logger)
