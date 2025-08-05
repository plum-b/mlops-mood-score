import pandas as pd
from pathlib import Path
from datascience import logger
from datascience.config.configuration import ConfigurationManager
from datascience.components.data_validation import DataValidation


class DataValidationTrainingPipeline:
    def __init__(self):
        self.config = ConfigurationManager()
        self.data_validation_config = self.config.get_data_validation_config()
        self.schema = self.config.schema

    def initiate_data_validation(self):
        """
        Initiates the data validation process with multiple validation categories.
        """
        try:
            logger.info("Starting data validation pipeline...")
            
            # Initialize data validation component
            data_validation = DataValidation(
                config=self.data_validation_config,
                schema=self.schema
            )
            
            # Path to the data file from data ingestion
            data_file_path = Path(self.data_validation_config.unzip_dir) / "mental_health_and_technology_usage_2024.csv"
            
            # 1. Validate that required files exist
            logger.info("=== FILE VALIDATION ===")
            files_valid = data_validation.validate_data_files()
            if not files_valid:
                logger.error("Data validation failed: Required files not found")
                data_validation.save_validation_status("File validation failed")
                return
            
            # 2. Load the data
            logger.info(f"Loading data from {data_file_path}")
            data = pd.read_csv(data_file_path)
            
            # 3. Validate columns against schema
            logger.info("=== COLUMN VALIDATION ===")
            columns_valid = data_validation.validate_all_columns(data)
            
            # 4. Validate data quality
            logger.info("=== QUALITY VALIDATION ===")
            quality_valid = data_validation.validate_data_quality(data)
            
            # 5. Validate data ranges
            logger.info("=== RANGE VALIDATION ===")
            range_valid = data_validation.validate_data_range(data)
            
            # 6. Determine overall validation status
            overall_status = data_validation.get_overall_validation_status()
            
            if overall_status:
                logger.info("✅ All validation categories passed!")
                data_validation.save_validation_status("All validations completed successfully")
            else:
                logger.error("❌ Some validation categories failed!")
                data_validation.save_validation_status("Some validation categories failed")
                
        except Exception as e:
            logger.error(f"Error in data validation pipeline: {e}")
            raise e 