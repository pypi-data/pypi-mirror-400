from .downloader import DatasetDownloader
from .registry import DatasetRegistry

def list_datasets():
    """
    List all available datasets.
    Returns:
        list: List of dataset names.
    """
    return DatasetRegistry.list_datasets()

def load_dataset(name: str, force_download: bool = False):
    """
    Load a dataset by name.
    Args:
        name (str): Dataset name.
        force_download (bool): Force re-download even if cached.
    Returns:
        pd.DataFrame: Loaded dataset.
    """
    return DatasetDownloader.load_dataset(name, force_download)

def get_dataset_info(name: str):
    """
    Get metadata for a dataset by name.
    Args:
        name (str): Dataset name.
    Returns:
        dict: Metadata for the dataset.
    """
    return DatasetRegistry.get_dataset_info(name)

__all__ = ['list_datasets', 'load_dataset', 'get_dataset_info']