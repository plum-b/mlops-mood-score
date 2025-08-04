# Data Transformation Component

## Overview

The Data Transformation component is responsible for preprocessing and transforming the raw mental health dataset into a format suitable for machine learning models. It follows the same modular structure as the Data Ingestion and Data Validation components.

## Features

### 1. Automatic String Column Encoding
- **Automatically detects and encodes ALL string/categorical columns** in the dataset
- Uses `LabelEncoder` from scikit-learn for consistent encoding
- Handles missing values by filling with 'Unknown'
- Stores label encoders for later use in inference
- Encoded columns are saved with `_encoded` suffix (e.g., `Support_Systems_Access_encoded`)

### 2. Lookup Table Generation
- Creates comprehensive lookup tables in `artifacts/lookups/`
- Saves both JSON and CSV formats for each encoded column
- Provides bidirectional mapping (original → encoded, encoded → original)
- Enables easy reverse mapping for model interpretation

### 3. Custom Mood Score Generation
- Creates a composite `Mood_Score` based on weighted factors:
  - Sleep Quality (15%)
  - Exercise Frequency (10%)
  - Diet Quality (10%)
  - Work-Life Balance (15%)
  - Financial Stress (-15%, negative weight)
  - Life Satisfaction (20%)
  - Future Outlook (15%)
- Score is normalized to 0-100 range

### 4. Column Management
- Drops unnecessary columns (e.g., User_ID, Technology_Usage_Hours)
- Validates target columns exist (Mental_Health_Status, Stress_Level)
- Preserves original columns alongside encoded versions

### 5. Data Persistence
- Saves transformed data as both CSV and JSON formats
- Stores label encoder mappings for reproducibility
- All outputs saved to `artifacts/data_transformation/`
- Lookup tables saved to `artifacts/lookups/`

### 6. Directory Management
- Automatically creates all necessary directories as part of the process
- Ensures output directories exist before saving files

### 7. Physical Activity Capping
- Caps `Physical_Activity_Hours` to maximum of 6 hours
- Prevents unrealistic values from affecting the model

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

**Note**: No need to specify categorical columns - all string columns are automatically detected and encoded.

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

After transformation, the following files are created:

### In `artifacts/data_transformation/`:
1. `transformed_data.csv` - Transformed dataset in CSV format
2. `transformed_data.json` - Transformed dataset in JSON format
3. `label_encoders.json` - Mapping of original categories to encoded values

### In `artifacts/lookups/`:
1. `column_encodings.json` - Comprehensive lookup table for all encoded columns
2. `{column_name}_mapping.csv` - Individual CSV mapping files for each encoded column

## Lookup Table Structure

The lookup tables provide bidirectional mapping:

```json
{
  "Support_Systems_Access": {
    "original_values": ["Yes", "No", "Unknown"],
    "encoded_values": [0, 1, 2],
    "mapping": {"Yes": 0, "No": 1, "Unknown": 2},
    "reverse_mapping": {0: "Yes", 1: "No", 2: "Unknown"}
  }
}
```

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
│   ├── data_transformation/ # Transformed data
│   └── lookups/            # Lookup tables
├── documents/               # Documentation
├── tests/                   # Test files
├── research/                # Research notebooks
├── templates/               # Web templates
└── logs/                    # Log files
``` 