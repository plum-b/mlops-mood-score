from dataclasses import dataclass
from pathlib import Path

@dataclass
class DataIngestionConfig:
    root_dir: Path
    dataset_id: str  # e.g., "waqi786/mental-health-and-technology-usage-dataset"
    local_data_path: Path  # where kagglehub will download the dataset