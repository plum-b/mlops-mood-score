#!/usr/bin/env python3
"""
Test script for the Data Transformation component
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.datascience import logger
from src.datascience.pipeline.data_transformation_pipeline import DataTransformationTrainingPipeline

def test_data_transformation():
    """Test the data transformation pipeline"""
    try:
        logger.info("Testing Data Transformation Pipeline...")
        
        # Initialize the pipeline
        pipeline = DataTransformationTrainingPipeline()
        
        # Run the transformation
        pipeline.initiate_data_transformation()
        
        logger.info("Data Transformation test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Data Transformation test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_data_transformation()
    if success:
        print("✅ Data Transformation test passed!")
    else:
        print("❌ Data Transformation test failed!")
        sys.exit(1) 