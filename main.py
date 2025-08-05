# import datascience

# main.py
from datascience import logger
from datascience.pipeline.data_ingestion_pipeline import DataIngestionTrainingPipeline
from datascience.pipeline.data_validation_pipeline import DataValidationTrainingPipeline
from datascience.pipeline.data_transformation_pipeline import DataTransformationTrainingPipeline

STAGE_NAME = "Data Ingestion stage"
VALIDATION_STAGE_NAME = "Data Validation stage"
TRANSFORMATION_STAGE_NAME = "Data Transformation stage"

if __name__ == '__main__':
    try:
        # General Message
        logger.info(f">>>>>> Running the pipeline <<<<<<\n\n")
        # Data Ingestion Stage
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        data_ingestion = DataIngestionTrainingPipeline()
        data_ingestion.initiate_data_ingestion()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
        
        # Data Validation Stage
        logger.info(f">>>>>> stage {VALIDATION_STAGE_NAME} started <<<<<<")
        data_validation = DataValidationTrainingPipeline()
        data_validation.initiate_data_validation()
        logger.info(f">>>>>> stage {VALIDATION_STAGE_NAME} completed <<<<<<\n\nx==========x")
        
        # Data Transformation Stage
        logger.info(f">>>>>> stage {TRANSFORMATION_STAGE_NAME} started <<<<<<")
        data_transformation = DataTransformationTrainingPipeline()
        data_transformation.initiate_data_transformation()
        logger.info(f">>>>>> stage {TRANSFORMATION_STAGE_NAME} completed <<<<<<\n\nx==========x")
        
    except Exception as e:
        logger.exception(e)
        raise e
