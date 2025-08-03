#!/usr/bin/env python3
"""
Simple test script to verify data validation implementation
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from datascience.config.configuration import ConfigurationManager
from datascience.components.data_validation import DataValidation
from datascience.utils.common import load_json_data

def test_data_validation():
    """Test the data validation implementation"""
    try:
        print("Testing Data Validation Implementation...")
        
        # Initialize configuration
        config_manager = ConfigurationManager()
        data_validation_config = config_manager.get_data_validation_config()
        schema = config_manager.schema
        
        print(f"✅ Configuration loaded successfully")
        print(f"   - Root dir: {data_validation_config.root_dir}")
        print(f"   - Required files: {data_validation_config.ALL_REQUIRED_FILES}")
        print(f"   - Schema keys: {list(schema.get('COLUMNS', {}).keys())}")
        
        # Initialize data validation component
        data_validation = DataValidation(
            config=data_validation_config,
            schema=schema
        )
        print("✅ DataValidation component initialized")
        
        # Test file validation
        files_valid = data_validation.validate_data_files()
        print(f"✅ File validation: {'PASSED' if files_valid else 'FAILED'}")
        
        if files_valid:
            # Test data loading
            data_file_path = Path(data_validation_config.unzip_dir) / "mental_health_data.json"
            data = load_json_data(data_file_path)
            print(f"✅ Data loaded successfully. Shape: {data.shape}")
            
            # Test column validation
            columns_valid = data_validation.validate_all_columns(data)
            print(f"✅ Column validation: {'PASSED' if columns_valid else 'FAILED'}")
            
            # Test report creation
            report = data_validation.create_validation_report(data, columns_valid)
            print(f"✅ Report creation: {'SUCCESS' if report else 'FAILED'}")
            
            # Test status saving
            data_validation.save_validation_status(columns_valid, "Test validation")
            print("✅ Status saving: SUCCESS")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_validation()
    sys.exit(0 if success else 1) 