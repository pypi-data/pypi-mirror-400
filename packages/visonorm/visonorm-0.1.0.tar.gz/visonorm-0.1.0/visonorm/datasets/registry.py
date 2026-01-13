import os
import pandas as pd
from tqdm.auto import tqdm

class DatasetRegistry:
    """
    Registry for managing dataset metadata.
    """
    _datasets = {
    'ViLexNorm': {
        'url': 'https://github.com/AnhHoang0529/visonorm/releases/download/0.0.1/ViLexNorm.csv',
        'type': 'csv'
    },
    'ViHSD': {
        'url': 'https://github.com/AnhHoang0529/visonorm/releases/download/0.0.1/ViHSD.csv',
        'type': 'csv'
    },
    'ViHOS': {
        'url': 'https://github.com/AnhHoang0529/visonorm/releases/download/0.0.1/ViHOS.csv',
        'type': 'csv'
    },
    'UIT-VSMEC': {
        'url': 'https://github.com/AnhHoang0529/visonorm/releases/download/0.0.1/VSMEC.csv',
        'type': 'csv'
    },
    'ViSpamReviews': {
        'url': 'https://github.com/AnhHoang0529/visonorm/releases/download/0.0.1/ViSpamReviews.csv',
        'type': 'csv'
    },
    'UIT-ViSFD': {
        'url': 'https://github.com/AnhHoang0529/visonorm/releases/download/0.0.1/ViSFD.csv',
        'type': 'csv'
    },
    'UIT-ViCTSD': {
        'url': 'https://github.com/AnhHoang0529/visonorm/releases/download/0.0.1/ViCTSD.csv',
        'type': 'csv'
    },
    'ViTHSD': {
        'url': 'https://github.com/AnhHoang0529/visonorm/releases/download/0.0.1/VITHSD.csv',
        'type': 'csv'
    },
    'BKEE': {
        'url': 'https://github.com/AnhHoang0529/visonorm/releases/download/0.0.1/BKEE.csv',
        'type': 'csv'
    },
    'UIT-ViQuAD': {
        'url': 'https://github.com/AnhHoang0529/visonorm/releases/download/0.0.1/UIT-ViQuAD2.0.csv',
        'type': 'csv'
    }
}

    @staticmethod
    def get_dataset_info(name: str):
        """
        Retrieve dataset metadata by name.
        Args:
            name (str): Dataset name.
        Returns:
            dict: Metadata for the dataset.
        """
        if name not in DatasetRegistry._datasets:
            raise KeyError(f"Dataset '{name}' is not registered.")
        return DatasetRegistry._datasets[name]

    @staticmethod
    def list_datasets():
        """
        List all available datasets.
        Returns:
            list: List of dataset names.
        """
        return list(DatasetRegistry._datasets.keys())