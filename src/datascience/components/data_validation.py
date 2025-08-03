import os
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, List
from src.datascience import logger
from src.datascience.entity.config_entity import DataValidationConfig


class DataValidation:
    def __init__(self, config: DataValidationConfig, schema: Dict):
        try:
            self.config = config
            self.schema = schema
            self.validation_results = {}
        except Exception as e:
            raise e

    def validate_all_columns(self, data: pd.DataFrame) -> bool:
        """
        Validates if all columns in the data match the expected schema.
        
        Args:
            data: pandas DataFrame to validate
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            logger.info("Validating data columns against schema...")
            
            # Get expected columns from schema
            expected_columns = self.schema.get("COLUMNS", {})
            
            # Check if all expected columns exist
            missing_columns = []
            for col_name in expected_columns.keys():
                if col_name not in data.columns:
                    missing_columns.append(col_name)
            
            if missing_columns:
                logger.error(f"Missing columns: {missing_columns}")
                self.validation_results["COLUMN_VALIDATION"] = {
                    "status": False,
                    "message": f"Missing columns: {missing_columns}"
                }
                return False
            
            # Check if all columns have the expected data types
            type_mismatches = []
            for col_name, expected_type in expected_columns.items():
                actual_type = str(data[col_name].dtype)
                
                # Map pandas dtypes to schema types
                type_mapping = {
                    'object': 'object',
                    'int64': 'int',
                    'float64': 'float',
                    'int32': 'int',
                    'float32': 'float',
                    'int': 'int',
                    'float': 'float'
                }
                
                actual_mapped = type_mapping.get(actual_type, actual_type)
                expected_mapped = type_mapping.get(expected_type, expected_type)
                
                if actual_mapped != expected_mapped:
                    type_mismatches.append({
                        'column': col_name,
                        'expected': expected_type,
                        'actual': actual_type
                    })
            
            if type_mismatches:
                logger.error(f"Type mismatches found: {type_mismatches}")
                self.validation_results["COLUMN_VALIDATION"] = {
                    "status": False,
                    "message": f"Type mismatches: {type_mismatches}"
                }
                return False
            
            logger.info("✅ All columns validated successfully!")
            self.validation_results["COLUMN_VALIDATION"] = {
                "status": True,
                "message": "All columns validated successfully"
            }
            return True
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            self.validation_results["COLUMN_VALIDATION"] = {
                "status": False,
                "message": f"Error during validation: {e}"
            }
            return False

    def validate_data_files(self) -> bool:
        """
        Validates if all required data files exist.
        
        Returns:
            bool: True if all files exist, False otherwise
        """
        try:
            logger.info("Validating data files...")
            
            missing_files = []
            for file_name in self.config.ALL_REQUIRED_FILES:
                file_path = Path(self.config.unzip_dir) / file_name
                if not file_path.exists():
                    missing_files.append(file_name)
            
            if missing_files:
                logger.error(f"Missing files: {missing_files}")
                self.validation_results["FILE_VALIDATION"] = {
                    "status": False,
                    "message": f"Missing files: {missing_files}"
                }
                return False
            
            logger.info("✅ All required files found!")
            self.validation_results["FILE_VALIDATION"] = {
                "status": True,
                "message": "All required files found"
            }
            return True
            
        except Exception as e:
            logger.error(f"Error during file validation: {e}")
            self.validation_results["FILE_VALIDATION"] = {
                "status": False,
                "message": f"Error during file validation: {e}"
            }
            return False

    def validate_data_quality(self, data: pd.DataFrame) -> bool:
        """
        Validates data quality aspects like missing values, duplicates, etc.
        
        Args:
            data: pandas DataFrame to validate
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            logger.info("Validating data quality...")
            
            issues = []
            
            # Check for missing values
            missing_values = data.isnull().sum()
            columns_with_missing = missing_values[missing_values > 0]
            if not columns_with_missing.empty:
                issues.append(f"Missing values in columns: {list(columns_with_missing.index)}")
            
            # Check for duplicates
            duplicate_count = data.duplicated().sum()
            if duplicate_count > 0:
                issues.append(f"Found {duplicate_count} duplicate rows")
            
            # Check for empty dataframe
            if data.empty:
                issues.append("DataFrame is empty")
            
            if issues:
                logger.warning(f"Data quality issues found: {issues}")
                self.validation_results["QUALITY_VALIDATION"] = {
                    "status": False,
                    "message": f"Quality issues: {'; '.join(issues)}"
                }
                return False
            
            logger.info("✅ Data quality validation passed!")
            self.validation_results["QUALITY_VALIDATION"] = {
                "status": True,
                "message": "Data quality validation passed"
            }
            return True
            
        except Exception as e:
            logger.error(f"Error during quality validation: {e}")
            self.validation_results["QUALITY_VALIDATION"] = {
                "status": False,
                "message": f"Error during quality validation: {e}"
            }
            return False

    def validate_data_range(self, data: pd.DataFrame) -> bool:
        """
        Validates if numerical values are within reasonable ranges.
        
        Args:
            data: pandas DataFrame to validate
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            logger.info("Validating data ranges...")
            
            issues = []
            
            # Check age range (if exists)
            if 'Age' in data.columns:
                age_min, age_max = data['Age'].min(), data['Age'].max()
                if age_min < 0 or age_max > 120:
                    issues.append(f"Age range ({age_min}-{age_max}) seems unrealistic")
            
            # Check hour-based columns (should be 0-24)
            hour_columns = ['Technology_Usage_Hours', 'Social_Media_Usage_Hours', 
                           'Gaming_Hours', 'Screen_Time_Hours', 'Sleep_Hours', 
                           'Physical_Activity_Hours']
            
            for col in hour_columns:
                if col in data.columns:
                    col_min, col_max = data[col].min(), data[col].max()
                    if col_min < 0 or col_max > 24:
                        issues.append(f"{col} range ({col_min:.2f}-{col_max:.2f}) exceeds 0-24 hours")
            
            if issues:
                logger.warning(f"Range validation issues: {issues}")
                self.validation_results["RANGE_VALIDATION"] = {
                    "status": False,
                    "message": f"Range issues: {'; '.join(issues)}"
                }
                return False
            
            logger.info("✅ Data range validation passed!")
            self.validation_results["RANGE_VALIDATION"] = {
                "status": True,
                "message": "Data range validation passed"
            }
            return True
            
        except Exception as e:
            logger.error(f"Error during range validation: {e}")
            self.validation_results["RANGE_VALIDATION"] = {
                "status": False,
                "message": f"Error during range validation: {e}"
            }
            return False

    def get_overall_validation_status(self) -> bool:
        """
        Determines the overall validation status based on all individual validations.
        
        Returns:
            bool: True if all validations passed, False otherwise
        """
        if not self.validation_results:
            return False
        
        return all(result["status"] for result in self.validation_results.values())

    def save_validation_status(self, message: str = ""):
        """
        Saves the validation status to a file with individual categories.
        
        Args:
            message: optional additional message to include
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(self.config.STATUS_FILE.parent, exist_ok=True)
            
            # Determine overall status
            overall_status = self.get_overall_validation_status()
            overall_text = "VALIDATION PASSED" if overall_status else "VALIDATION FAILED"
            
            # Build the content with individual categories
            content = f"{overall_text}\n"
            if message:
                content += f"{message}\n"
            content += "\n"
            
            # Add individual validation results
            for category, result in self.validation_results.items():
                status_icon = "✅" if result["status"] else "❌"
                content += f"{status_icon} {category}: {result['message']}\n"
            
            with open(self.config.STATUS_FILE, 'w') as f:
                f.write(content)
            
            logger.info(f"Validation status saved to {self.config.STATUS_FILE}")
            
        except Exception as e:
            logger.error(f"Error saving validation status: {e}") 