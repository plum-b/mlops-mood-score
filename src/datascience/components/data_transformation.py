import pandas as pd
import numpy as np
import os
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from datascience import logger
from datascience.entity.config_entity import DataTransformationConfig


class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config
        self.label_encoders = {}
        
        # Create all necessary directories
        self._create_directories()

    def _create_directories(self):
        """Create all necessary directories for the transformation process"""
        directories_to_create = [
            self.config.root_dir,
            self.config.transformed_data_path,
            Path("artifacts/lookups")  # Add lookups directory
        ]
        
        for directory in directories_to_create:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created/verified directory: {directory}")

    def load_data(self) -> pd.DataFrame:
        """Load the data from the data ingestion stage"""
        data_file = self.config.data_path / "mental_health_and_technology_usage_2024.csv"
        logger.info(f"Loading data from {data_file}")
        
        if not data_file.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        df = pd.read_csv(data_file)
        logger.info(f"Loaded data with shape: {df.shape}")
        return df

    def encode_all_string_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode all string/categorical columns in the dataset"""
        logger.info("Starting encoding of all string columns...")
        
        # Get all columns that are object (string) type
        string_columns = df.select_dtypes(include=['object']).columns.tolist()
        logger.info(f"Found {len(string_columns)} string columns to encode: {string_columns}")
        
        for column in string_columns:
            if column in df.columns:
                # Initialize label encoder for this column
                le = LabelEncoder()
                
                # Handle missing values by filling with 'Unknown'
                df[column] = df[column].fillna('Unknown')
                
                # Fit and transform the column
                df[f"{column}_encoded"] = le.fit_transform(df[column])
                
                # Store the label encoder for later use
                self.label_encoders[column] = le
                
                logger.info(f"Encoded column: {column} -> {column}_encoded")
            else:
                logger.warning(f"Column {column} not found in dataset")
        
        return df

    def cap_physical_activity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cap physical activity to maximum of 6"""
        logger.info("Capping physical activity to maximum of 6...")
        
        if 'Physical_Activity_Hours' in df.columns:
            original_max = df['Physical_Activity_Hours'].max()
            df['Physical_Activity_Hours'] = df['Physical_Activity_Hours'].clip(upper=6)
            new_max = df['Physical_Activity_Hours'].max()
            logger.info(f"Capped Physical_Activity_Hours from {original_max} to {new_max}")
        else:
            logger.warning("Physical_Activity_Hours column not found")
        
        return df

    def create_mood_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a custom mood score based on various factors"""
        logger.info("Creating custom mood score...")
        
        # Define weights for different factors (can be adjusted based on domain knowledge)
        weights = {
            'Sleep_Quality': 0.15,
            'Exercise_Frequency': 0.10,
            'Diet_Quality': 0.10,
            'Work_Life_Balance': 0.15,
            'Financial_Stress': -0.15,  # Negative weight as higher stress = lower mood
            'Life_Satisfaction': 0.20,
            'Future_Outlook': 0.15
        }
        
        # Initialize mood score
        df['Mood_Score'] = 0.0
        
        # Calculate weighted score for each factor
        for factor, weight in weights.items():
            if f"{factor}_encoded" in df.columns:
                # Normalize the encoded values to 0-1 scale
                max_val = df[f"{factor}_encoded"].max()
                if max_val > 0:
                    normalized_values = df[f"{factor}_encoded"] / max_val
                    df['Mood_Score'] += normalized_values * weight
        
        # Scale to 0-100 range
        df['Mood_Score'] = (df['Mood_Score'] + 1) * 50  # Shift from [-1,1] to [0,100]
        df['Mood_Score'] = df['Mood_Score'].clip(0, 100)  # Ensure bounds
        
        logger.info(f"Mood score created with range: {df['Mood_Score'].min():.2f} - {df['Mood_Score'].max():.2f}")
        return df

    def drop_unnecessary_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop columns that are not useful for modeling"""
        logger.info("Dropping unnecessary columns...")
        
        # Add Technology_Usage_Hours to the drop list
        columns_to_drop = self.config.drop_columns + ["Technology_Usage_Hours"]
        
        dropped_columns = []
        for column in columns_to_drop:
            if column in df.columns:
                dropped_columns.append(column)
                logger.info(f"Dropping column: {column}")
            else:
                logger.warning(f"Column {column} not found in dataset")
        
        if dropped_columns:
            df = df.drop(columns=dropped_columns)
            logger.info(f"Dropped {len(dropped_columns)} columns: {dropped_columns}")
        
        return df

    def ensure_target_columns_exist(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure target columns exist and are properly formatted"""
        logger.info("Validating target columns...")
        
        missing_targets = []
        for target in self.config.target_columns:
            if target not in df.columns:
                missing_targets.append(target)
            else:
                logger.info(f"Target column found: {target}")
        
        if missing_targets:
            logger.warning(f"Missing target columns: {missing_targets}")
        
        return df

    def save_lookup_tables(self):
        """Save lookup tables for all encoded columns"""
        logger.info("Saving lookup tables...")
        
        lookups_dir = Path("artifacts/lookups")
        lookups_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a comprehensive lookup table
        lookup_data = {}
        
        for column, le in self.label_encoders.items():
            lookup_data[column] = {
                'original_values': le.classes_.tolist(),
                'encoded_values': list(range(len(le.classes_))),
                'mapping': dict(zip(le.classes_, range(len(le.classes_)))),
                'reverse_mapping': dict(zip(range(len(le.classes_)), le.classes_))
            }
        
        # Save as JSON
        import json
        lookup_file = lookups_dir / "column_encodings.json"
        with open(lookup_file, 'w') as f:
            json.dump(lookup_data, f, indent=2)
        logger.info(f"Saved lookup table: {lookup_file}")
        
        # Save individual CSV files for each column
        for column, le in self.label_encoders.items():
            mapping_df = pd.DataFrame({
                'original_value': le.classes_,
                'encoded_value': range(len(le.classes_))
            })
            csv_file = lookups_dir / f"{column}_mapping.csv"
            mapping_df.to_csv(csv_file, index=False)
            logger.info(f"Saved {column} mapping: {csv_file}")

    def save_transformed_data(self, df: pd.DataFrame):
        """Save the transformed dataset"""
        logger.info("Saving transformed data...")
        
        # Ensure the output directory exists
        self.config.transformed_data_path.mkdir(parents=True, exist_ok=True)
        
        # Save as CSV
        csv_path = self.config.transformed_data_path / "transformed_data.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved transformed data as CSV: {csv_path}")
        
        # Save as JSON
        json_path = self.config.transformed_data_path / "transformed_data.json"
        df.to_json(json_path, orient="records", indent=2)
        logger.info(f"Saved transformed data as JSON: {json_path}")
        
        # Save label encoders for later use
        encoders_path = self.config.transformed_data_path / "label_encoders.json"
        encoders_data = {}
        for column, le in self.label_encoders.items():
            encoders_data[column] = {
                'classes': le.classes_.tolist(),
                'n_classes': len(le.classes_)
            }
        
        import json
        with open(encoders_path, 'w') as f:
            json.dump(encoders_data, f, indent=2)
        logger.info(f"Saved label encoders: {encoders_path}")
        
        # Save lookup tables
        self.save_lookup_tables()

    def transform_data(self):
        """Main method to perform all data transformation steps"""
        logger.info("Starting data transformation...")
        
        # Load data
        df = self.load_data()
        
        # Encode all string columns
        df = self.encode_all_string_columns(df)
        
        # Cap physical activity
        df = self.cap_physical_activity(df)
        
        # Create mood score
        df = self.create_mood_score(df)
        
        # Drop unnecessary columns
        df = self.drop_unnecessary_columns(df)
        
        # Ensure target columns exist
        df = self.ensure_target_columns_exist(df)
        
        # Save transformed data
        self.save_transformed_data(df)
        
        logger.info(f"Data transformation completed. Final shape: {df.shape}")
        return df 