from pathlib import Path
from datascience.constants import *
from datascience.utils.common import read_yaml, create_directories

from datascience.entity.config_entity import (DataIngestionConfig, DataValidationConfig, DataTransformationConfig)

class ConfigurationManager:
    def __init__(
        self,
        config_filepath=CONFIG_FILE_PATH,
        params_filepath=PARAMS_FILE_PATH,
        schema_filepath=SCHEMA_FILE_PATH,
    ):
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)

        # Create the root artifacts directory explicitly
        create_directories([self.config.artifacts_root])


    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion
        create_directories([config.root_dir])

        return DataIngestionConfig(
            root_dir=config.root_dir,
            dataset_id=config.dataset_id,
            local_data_path=config.local_data_path,
        )

    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation
        create_directories([config.root_dir])

        return DataValidationConfig(
            root_dir=config.root_dir,
            unzip_dir=config.unzip_dir,
            STATUS_FILE=Path(config.STATUS_FILE),
            ALL_REQUIRED_FILES=config.ALL_REQUIRED_FILES,
        )

    def get_data_transformation_config(self) -> DataTransformationConfig:
        config = self.config.data_transformation
        create_directories([config.root_dir, config.transformed_data_path])

        return DataTransformationConfig(
            root_dir=Path(config.root_dir),
            data_path=Path(config.data_path),
            transformed_data_path=Path(config.transformed_data_path),
            target_columns=config.target_columns,
            categorical_columns=config.categorical_columns,
            drop_columns=config.drop_columns,
        )