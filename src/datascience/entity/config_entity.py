from dataclasses import dataclass
from pathlib import Path

@dataclass
class DataIngestionConfig:
    root_dir: Path
    dataset_id: str  # e.g., "waqi786/mental-health-and-technology-usage-dataset"
    local_data_path: Path  # where kagglehub will download the dataset

@dataclass
class DataValidationConfig:
    root_dir: Path
    unzip_dir: Path
    STATUS_FILE: Path
    ALL_REQUIRED_FILES: list

@dataclass
class DataTransformationConfig:
    root_dir: Path
    data_path: Path  # path to the input data from data ingestion
    transformed_data_path: Path  # path to save transformed data
    target_columns: list  # columns to use as targets (Mental_Health_Status, Stress_Level)
    categorical_columns: list  # columns to encode
    drop_columns: list  # columns to drop if not useful