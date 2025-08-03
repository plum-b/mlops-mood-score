import pandas as pd
import numpy as np
from pathlib import Path
import shutil

def create_test_data_with_errors():
    """
    Creates test datasets with various data quality issues to test validation.
    """
    # Original data path
    original_path = Path("artifacts/data_ingestion/mental_health_and_technology_usage_2024.csv")
    
    if not original_path.exists():
        print("❌ Original data file not found. Please run data ingestion first.")
        return
    
    # Load original data
    df = pd.read_csv(original_path)
    print(f"✅ Loaded original data: {df.shape}")
    
    # Create test directory
    test_dir = Path("artifacts/data_ingestion/test_validation")
    test_dir.mkdir(exist_ok=True)
    
    # Test 1: Missing columns
    print("\n🧪 Test 1: Missing columns")
    df_missing_cols = df.drop(columns=['Age', 'Gender'])
    df_missing_cols.to_csv(test_dir / "missing_columns.csv", index=False)
    print("Created: missing_columns.csv (missing Age and Gender columns)")
    
    # Test 2: Wrong data types
    print("\n🧪 Test 2: Wrong data types")
    df_wrong_types = df.copy()
    df_wrong_types['Age'] = df_wrong_types['Age'].astype(str)  # Age as string
    df_wrong_types['Technology_Usage_Hours'] = df_wrong_types['Technology_Usage_Hours'].astype(str)  # Hours as string
    df_wrong_types.to_csv(test_dir / "wrong_types.csv", index=False)
    print("Created: wrong_types.csv (Age and Technology_Usage_Hours as strings)")
    
    # Test 3: Missing values
    print("\n🧪 Test 3: Missing values")
    df_missing_values = df.copy()
    # Add some missing values
    df_missing_values.loc[df_missing_values.sample(frac=0.1).index, 'Age'] = np.nan
    df_missing_values.loc[df_missing_values.sample(frac=0.05).index, 'Mental_Health_Status'] = None
    df_missing_values.to_csv(test_dir / "missing_values.csv", index=False)
    print("Created: missing_values.csv (10% missing Age, 5% missing Mental_Health_Status)")
    
    # Test 4: Out of range values
    print("\n🧪 Test 4: Out of range values")
    df_out_of_range = df.copy()
    # Add unrealistic values
    df_out_of_range.loc[df_out_of_range.sample(frac=0.02).index, 'Age'] = 150  # Impossible age
    df_out_of_range.loc[df_out_of_range.sample(frac=0.03).index, 'Technology_Usage_Hours'] = 30  # More than 24 hours
    df_out_of_range.loc[df_out_of_range.sample(frac=0.01).index, 'Sleep_Hours'] = -5  # Negative sleep hours
    df_out_of_range.to_csv(test_dir / "out_of_range.csv", index=False)
    print("Created: out_of_range.csv (unrealistic values)")
    
    # Test 5: Duplicate rows
    print("\n🧪 Test 5: Duplicate rows")
    df_duplicates = df.copy()
    # Add some duplicate rows
    duplicate_rows = df.sample(frac=0.05)  # 5% duplicate rows
    df_duplicates = pd.concat([df_duplicates, duplicate_rows], ignore_index=True)
    df_duplicates.to_csv(test_dir / "duplicates.csv", index=False)
    print("Created: duplicates.csv (5% duplicate rows)")
    
    # Test 6: Invalid categorical values
    print("\n🧪 Test 6: Invalid categorical values")
    df_invalid_cats = df.copy()
    # Add invalid values to categorical columns
    df_invalid_cats.loc[df_invalid_cats.sample(frac=0.02).index, 'Gender'] = 'Invalid_Gender'
    df_invalid_cats.loc[df_invalid_cats.sample(frac=0.03).index, 'Mental_Health_Status'] = 'Invalid_Status'
    df_invalid_cats.to_csv(test_dir / "invalid_categorical.csv", index=False)
    print("Created: invalid_categorical.csv (invalid categorical values)")
    
    # Test 7: Mixed data types in same column
    print("\n🧪 Test 7: Mixed data types")
    df_mixed_types = df.copy()
    # Mix string and numeric in numeric column
    df_mixed_types.loc[df_mixed_types.sample(frac=0.01).index, 'Age'] = 'Invalid_Age'
    df_mixed_types.to_csv(test_dir / "mixed_types.csv", index=False)
    print("Created: mixed_types.csv (mixed data types in Age column)")
    
    print(f"\n✅ All test files created in: {test_dir}")
    print("\n📋 Test files summary:")
    print("1. missing_columns.csv - Missing required columns")
    print("2. wrong_types.csv - Incorrect data types")
    print("3. missing_values.csv - Missing values")
    print("4. out_of_range.csv - Values outside expected range")
    print("5. duplicates.csv - Duplicate rows")
    print("6. invalid_categorical.csv - Invalid categorical values")
    print("7. mixed_types.csv - Mixed data types in same column")
    
    return test_dir

def test_validation_with_file(test_file_path):
    """
    Tests the validation pipeline with a specific test file.
    """
    print(f"\n🔍 Testing validation with: {test_file_path}")
    
    # Temporarily replace the original file
    original_path = Path("artifacts/data_ingestion/mental_health_and_technology_usage_2024.csv")
    backup_path = Path("artifacts/data_ingestion/mental_health_and_technology_usage_2024_backup.csv")
    
    # Backup original file
    if original_path.exists():
        shutil.copy2(original_path, backup_path)
    
    # Replace with test file
    shutil.copy2(test_file_path, original_path)
    
    try:
        # Run validation
        from src.datascience.pipeline.data_validation_pipeline import DataValidationTrainingPipeline
        
        validation_pipeline = DataValidationTrainingPipeline()
        validation_pipeline.initiate_data_validation()
        
        # Check validation status
        status_file = Path("artifacts/data_validation/status.txt")
        if status_file.exists():
            with open(status_file, 'r') as f:
                status = f.read()
            print(f"Validation Status:\n{status}")
        else:
            print("❌ No validation status file found")
            
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
    
    finally:
        # Restore original file
        if backup_path.exists():
            shutil.copy2(backup_path, original_path)
            backup_path.unlink()

def run_all_validation_tests():
    """
    Runs validation tests on all created test files.
    """
    test_dir = create_test_data_with_errors()
    
    if not test_dir:
        return
    
    test_files = [
        "missing_columns.csv",
        "wrong_types.csv", 
        "missing_values.csv",
        "out_of_range.csv",
        "duplicates.csv",
        "invalid_categorical.csv",
        "mixed_types.csv"
    ]
    
    print("\n" + "="*60)
    print("🧪 RUNNING ALL VALIDATION TESTS")
    print("="*60)
    
    for test_file in test_files:
        test_file_path = test_dir / test_file
        if test_file_path.exists():
            test_validation_with_file(test_file_path)
            print("-" * 40)
        else:
            print(f"❌ Test file not found: {test_file}")

if __name__ == "__main__":
    print("🧪 Data Validation Testing Script")
    print("="*40)
    
    # Create test data with errors
    create_test_data_with_errors()
    
    # Ask user which test to run
    print("\n" + "="*40)
    print("Choose a test to run:")
    print("1. missing_columns.csv")
    print("2. wrong_types.csv")
    print("3. missing_values.csv")
    print("4. out_of_range.csv")
    print("5. duplicates.csv")
    print("6. invalid_categorical.csv")
    print("7. mixed_types.csv")
    print("8. Run all tests")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-8): ")
    
    test_dir = Path("artifacts/data_ingestion/test_validation")
    
    if choice == "0":
        print("👋 Exiting...")
    elif choice == "8":
        run_all_validation_tests()
    elif choice in ["1", "2", "3", "4", "5", "6", "7"]:
        test_files = [
            "missing_columns.csv",
            "wrong_types.csv", 
            "missing_values.csv",
            "out_of_range.csv",
            "duplicates.csv",
            "invalid_categorical.csv",
            "mixed_types.csv"
        ]
        test_file = test_files[int(choice) - 1]
        test_file_path = test_dir / test_file
        if test_file_path.exists():
            test_validation_with_file(test_file_path)
        else:
            print(f"❌ Test file not found: {test_file}")
    else:
        print("❌ Invalid choice") 