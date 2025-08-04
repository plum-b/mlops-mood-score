# Data Transformation Component

## Overview

The Data Transformation component is responsible for preprocessing and transforming the raw mental health dataset into a format suitable for machine learning models. It follows the same modular structure as the Data Ingestion and Data Validation components.

## Features

### 1. Categorical Variable Encoding
- Uses `LabelEncoder` from scikit-learn to encode categorical variables
- Handles missing values by filling with 'Unknown'
- Stores label encoders for later use in inference
- Encoded columns are saved with `_encoded` suffix

### 2. Custom Mood Score Generation
- Creates a composite `Mood_Score` based on weighted factors:
  - Sleep Quality (15%)
  - Exercise Frequency (10%)
  - Diet Quality (10%)
  - Work-Life Balance (15%)
  - Financial Stress (-15%, negative weight)
  - Life Satisfaction (20%)
  - Future Outlook (15%)
- Score is normalized to 0-100 range

### 3. Column Management
- Drops unnecessary columns (e.g., User_ID)
- Validates target columns exist (Mental_Health_Status, Stress_Level)
- Preserves original columns alongside encoded versions

### 4. Data Persistence
- Saves transformed data as both CSV and JSON formats
- Stores label encoder mappings for reproducibility
- All outputs saved to `artifacts/data_transformation/`

### 5. Directory Management
- Automatically creates all necessary directories as part of the process
- Ensures output directories exist before saving files

## File Structure

```
src/datascience/
├── components/
│   └── data_transformation.py          # Main transformation logic
├── pipeline/
│   └── data_transformation_pipeline.py # Pipeline orchestration
├── config/
│   └── configuration.py                # Updated with get_data_transformation_config()
├── entity/
│   └── config_entity.py               # Added DataTransformationConfig dataclass

documents/
└── DATA_TRANSFORMATION_README.md       # This documentation

tests/
└── test_data_transformation.py        # Test script for the component
```

## Configuration

The component is configured via `config/config.yaml`:

```yaml
data_transformation:
  root_dir: artifacts/data_transformation
  data_path: artifacts/data_ingestion
  transformed_data_path: artifacts/data_transformation
  target_columns: ["Mental_Health_Status", "Stress_Level"]
  categorical_columns: ["Gender", "Support_Systems_Access", ...]
  drop_columns: ["User_ID"]
```

## Usage

### Running the Full Pipeline
```bash
python main.py
```

### Running Only Data Transformation
```bash
python tests/test_data_transformation.py
```

### Direct Component Usage
```python
from src.datascience.config.configuration import ConfigurationManager
from src.datascience.components.data_transformation import DataTransformation

config_manager = ConfigurationManager()
transformation_config = config_manager.get_data_transformation_config()
transformer = DataTransformation(transformation_config)
transformed_data = transformer.transform_data()
```

## Output Files

After transformation, the following files are created in `artifacts/data_transformation/`:

1. `transformed_data.csv` - Transformed dataset in CSV format
2. `transformed_data.json` - Transformed dataset in JSON format
3. `label_encoders.json` - Mapping of original categories to encoded values

## Target Variables

The component is designed for multi-output classification with:
- **Mental_Health_Status** - Primary mental health classification
- **Stress_Level** - Stress level classification
- **Mood_Score** - Custom regression target (0-100 scale)

## Dependencies

- pandas: Data manipulation
- numpy: Numerical operations
- scikit-learn: LabelEncoder for categorical encoding
- pathlib: Path handling
- json: Encoder storage

## Error Handling

- Validates input data file existence
- Handles missing categorical columns gracefully
- Logs warnings for missing target columns
- Ensures output directories exist before saving
- Automatically creates all necessary directories

## Testing

The component can be tested using:
```bash
python tests/test_data_transformation.py
```

This will run the transformation pipeline and verify all steps complete successfully.

## Project Structure

This project follows a standardized structure:

```
mlops-mood-score/
├── src/datascience/          # Main source code
├── config/                   # Configuration files
├── artifacts/               # Generated artifacts
├── documents/               # Documentation
├── tests/                   # Test files
├── research/                # Research notebooks
├── templates/               # Web templates
└── logs/                    # Log files
``` 