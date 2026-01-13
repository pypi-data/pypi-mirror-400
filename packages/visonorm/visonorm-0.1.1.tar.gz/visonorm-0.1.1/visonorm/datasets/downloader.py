# downloader.py
import os
import pandas as pd
from tqdm.auto import tqdm
import requests
from visonorm.module.utils import get_logger
from .registry import DatasetRegistry

class DatasetDownloader:
    """
    Class for downloading and loading datasets with logging and caching support.
    """
    # Initialize a class-level logger
    logger = get_logger(logfile="logs/dataset_downloader.log")

    @staticmethod
    def _download_file(url: str, target_path: str):
        """
        Download a file from a URL to a target path.
        """
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        DatasetDownloader.logger.info(f"Downloading file from {url} to {target_path}...")
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        total = int(resp.headers.get('content-length', 0))
        with open(target_path, 'wb') as f, tqdm(total=total, unit='B', unit_scale=True, desc=os.path.basename(target_path)) as pbar:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        DatasetDownloader.logger.info(f"File downloaded successfully to {target_path}.")

    @staticmethod
    def load_dataset(name: str, force_download: bool = False) -> pd.DataFrame:
        """
        Download (if needed) and load a dataset as a DataFrame.
        Args:
            name (str): Dataset name.
            force_download (bool): Force re-download even if cached.
        Returns:
            pd.DataFrame: Loaded dataset.
        """
        info = DatasetRegistry.get_dataset_info(name)
        cache_path = "datasets/" + os.path.basename(info['url'])
        url = info['url']

        if force_download or not os.path.exists(cache_path):
            DatasetDownloader.logger.info(f"Downloading dataset '{name}' from {url}...")
            DatasetDownloader._download_file(url, cache_path)
        else:
            DatasetDownloader.logger.info(f"Cache found at '{cache_path}', skipping download.")

        if info['type'] == 'csv':
            DatasetDownloader.logger.info(f"Loading dataset '{name}' as CSV.")
            return pd.read_csv(cache_path)
        elif info['type'] == 'json':
            DatasetDownloader.logger.info(f"Loading dataset '{name}' as JSON.")
            return pd.read_json(cache_path)
        else:
            DatasetDownloader.logger.error(f"Unsupported file type '{info['type']}' for dataset '{name}'.")
            raise ValueError(f"Unsupported file type '{info['type']}' for dataset '{name}'.")
