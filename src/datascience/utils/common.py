import os
import yaml
from datascience import logger
import json
import joblib
from ensure import ensure_annotations
from box import ConfigBox
from pathlib import Path
from typing import Any, Dict, List, Tuple
from box.exceptions import BoxValueError
import pandas as pd


@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """reads yaml file and returns

    Args:
        path_to_yaml (str): path like input

    Raises:
        ValueError: if yaml file is empty
        e: empty file

    Returns:
        ConfigBox: ConfigBox type
    """
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            logger.info(f"yaml file: {path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("yaml file is empty")
    except Exception as e:
        raise e
        


@ensure_annotations
def create_directories(path_to_directories: list, verbose=True):
    """create list of directories

    Args:
        path_to_directories (list): list of path of directories
        ignore_log (bool, optional): ignore if multiple dirs is to be created. Defaults to False.
    """
    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)
        if verbose:  # Print log message if verbose flag is True
            logger.info(f"created directory at: {path}")

@ensure_annotations
def save_json(path: Path, data: dict):
    """save json data

    Args:
        path (Path): path to json file
        data (dict): data to be saved in json file
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    logger.info(f"json file saved at: {path}")

@ensure_annotations
def load_json(path: Path) -> ConfigBox:
    """load json files data

    Args:
        path (Path): path to json file

    Returns:
        ConfigBox: data as class attributes instead of dict
    """
    with open(path) as f:
        content = json.load(f)

    logger.info(f"json file loaded succesfully from: {path}")
    return ConfigBox(content)

@ensure_annotations
def save_bin(data: Any, path: Path):
    """save binary file

    Args:
        data (Any): data to be saved as binary
        path (Path): path to binary file
    """
    joblib.dump(value=data, filename=path)
    logger.info(f"binary file saved at: {path}")

@ensure_annotations
def load_bin(path: Path) -> Any:
    """load binary data

    Args:
        path (Path): path to binary file

    Returns:
        Any: object stored in the file
    """
    data = joblib.load(path)
    logger.info(f"binary file loaded from: {path}")
    return data

# Data Validation Utilities
@ensure_annotations
def validate_file_exists(file_path: Path) -> bool:
    """Check if a file exists
    
    Args:
        file_path (Path): path to the file
        
    Returns:
        bool: True if file exists, False otherwise
    """
    return file_path.exists()

def validate_columns_exist(data: pd.DataFrame, expected_columns: List[str]) -> Tuple[bool, List]:
    """Validate if all expected columns exist in the dataframe
    
    Args:
        data (pd.DataFrame): dataframe to validate
        expected_columns (List[str]): list of expected column names
        
    Returns:
        Tuple[bool, List[str]]: (validation_passed, missing_columns)
    """
    missing_columns = [col for col in expected_columns if col not in data.columns]
    return len(missing_columns) == 0, missing_columns

def validate_data_types(data: pd.DataFrame, schema) -> Tuple[bool, List]:
    """Validate data types against schema
    
    Args:
        data (pd.DataFrame): dataframe to validate
        schema (Dict): schema with expected data types
        
    Returns:
        Tuple[bool, List[Dict]]: (validation_passed, type_mismatches)
    """
    expected_columns = schema.get("COLUMNS", {})
    type_mismatches = []
    
    for col_name, expected_type in expected_columns.items():
        if col_name in data.columns:
            actual_type = str(data[col_name].dtype)
            
            if actual_type != expected_type:
                type_mismatches.append({
                    'column': col_name,
                    'expected': expected_type,
                    'actual': actual_type
                })
    
    return len(type_mismatches) == 0, type_mismatches

@ensure_annotations
def load_json_data(file_path: Path) -> pd.DataFrame:
    """Load JSON data efficiently into a pandas DataFrame
    
    Args:
        file_path (Path): path to the JSON file
        
    Returns:
        pd.DataFrame: loaded data
    """
    try:
        # Load JSON data
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        
        # Convert to DataFrame efficiently
        if isinstance(json_data, list):
            df = pd.DataFrame(json_data)
        else:
            # If it's a single object, wrap it in a list
            df = pd.DataFrame([json_data])
        
        logger.info(f"JSON data loaded successfully. Shape: {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"Error loading JSON data: {e}")
        raise e

def get_data_summary(data: pd.DataFrame) -> Dict:
    """Get a summary of the dataset
    
    Args:
        data (pd.DataFrame): dataframe to summarize
        
    Returns:
        Dict: summary information
    """
    summary = {
        'shape': list(data.shape),
        'columns': list(data.columns),
        'dtypes': {col: str(dtype) for col, dtype in data.dtypes.to_dict().items()},
        'missing_values': {col: int(val) for col, val in data.isnull().sum().to_dict().items()},
        'memory_usage': int(data.memory_usage(deep=True).sum()),
        'duplicates': int(data.duplicated().sum())
    }
    
    # Add basic statistics for numerical columns
    numerical_cols = data.select_dtypes(include=['number']).columns
    if len(numerical_cols) > 0:
        # Convert numpy types to Python types for JSON serialization
        stats_dict = data[numerical_cols].describe().to_dict()
        summary['numerical_stats'] = {
            col: {stat: float(val) if isinstance(val, (int, float)) else str(val) 
                  for stat, val in stats.items()}
            for col, stats in stats_dict.items()
        }
    
    return summary

def save_validation_report(report: Dict, path: Path):
    """Save validation report to JSON file
    
    Args:
        report (Dict): validation report
        path (Path): path to save the report
    """
    save_json(path, report)
    logger.info(f"Validation report saved to: {path}")