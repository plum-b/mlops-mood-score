import pandas as pd
import json
import os

from src.datascience import logger
from src.datascience.entity.config_entity import DataIngestionConfig

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_dataset(self):
        import kagglehub
        path = kagglehub.dataset_download(self.config.dataset_id)
        logger.info(f"Downloaded to: {path}")

        os.makedirs(self.config.local_data_path, exist_ok=True)
        os.system(f"cp -r {path}/* {self.config.local_data_path}")

    def convert_to_json(self, csv_filename: str, json_filename: str):
        """
        Converts a downloaded CSV to JSON.
        - csv_filename: name of the file inside the local_data_path folder
        - json_filename: desired name for the output JSON
        """
        csv_path = os.path.join(self.config.local_data_path, csv_filename)
        json_path = os.path.join(self.config.local_data_path, json_filename)

        df = pd.read_csv(csv_path)
        df.to_json(json_path, orient="records", indent=2)
        logger.info(f"Converted {csv_filename} to {json_filename}")