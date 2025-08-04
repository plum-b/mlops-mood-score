import pandas as pd
import numpy as np
import os
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from src.datascience import logger
from src.datascience.entity.config_entity import DataTransformationConfig


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
            self.config.transformed_data_path
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

    def encode_categorical_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables using LabelEncoder"""
        logger.info("Starting categorical column encoding...")
        
        for column in self.config.categorical_columns:
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
        
        columns_to_drop = []
        for column in self.config.drop_columns:
            if column in df.columns:
                columns_to_drop.append(column)
                logger.info(f"Dropping column: {column}")
            else:
                logger.warning(f"Column {column} not found in dataset")
        
        if columns_to_drop:
            df = df.drop(columns=columns_to_drop)
            logger.info(f"Dropped {len(columns_to_drop)} columns")
        
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

    def transform_data(self):
        """Main method to perform all data transformation steps"""
        logger.info("Starting data transformation...")
        
        # Load data
        df = self.load_data()
        
        # Encode categorical columns
        df = self.encode_categorical_columns(df)
        
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