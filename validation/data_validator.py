import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Data validation and preprocessing handler."""
    
    def __init__(self):
        self.validation_results: Dict[str, Any] = {}
        self.error_messages: List[str] = []

    def validate_dataset(self, 
                        data: pd.DataFrame, 
                        protected_attribute: str,
                        label_column: str = 'label') -> bool:
        """
        Validate dataset for bias analysis.
        
        Args:
            data: Input DataFrame
            protected_attribute: Name of protected attribute column
            label_column: Name of target column
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            # Reset validation results
            self.validation_results = {}
            self.error_messages = []
            
            # Basic DataFrame validation
            if not self._validate_dataframe_structure(data):
                return False
                
            # Column presence validation
            if not self._validate_required_columns(data, protected_attribute, label_column):
                return False
                
            # Data type validation
            if not self._validate_data_types(data, protected_attribute, label_column):
                return False
                
            # Value range validation
            if not self._validate_value_ranges(data, protected_attribute, label_column):
                return False
                
            # Missing value validation
            if not self._validate_missing_values(data):
                return False
                
            # Data quality validation
            if not self._validate_data_quality(data, protected_attribute, label_column):
                return False
                
            logger.info("Dataset validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            self.error_messages.append(f"Unexpected error: {str(e)}")
            return False

    def _validate_dataframe_structure(self, data: pd.DataFrame) -> bool:
        """Validate basic DataFrame structure."""
        if not isinstance(data, pd.DataFrame):
            self.error_messages.append("Input must be a pandas DataFrame")
            return False
            
        if len(data) == 0:
            self.error_messages.append("DataFrame is empty")
            return False
            
        self.validation_results['row_count'] = len(data)
        self.validation_results['column_count'] = len(data.columns)
        return True

    def _validate_required_columns(self, 
                                 data: pd.DataFrame,
                                 protected_attribute: str,
                                 label_column: str) -> bool:
        """Validate presence of required columns."""
        missing_columns = []
        
        if protected_attribute not in data.columns:
            missing_columns.append(protected_attribute)
            
        if label_column not in data.columns:
            missing_columns.append(label_column)
            
        if missing_columns:
            self.error_messages.append(
                f"Missing required columns: {', '.join(missing_columns)}"
            )
            return False
            
        self.validation_results['columns'] = list(data.columns)
        return True

    def _validate_data_types(self,
                           data: pd.DataFrame,
                           protected_attribute: str,
                           label_column: str) -> bool:
        """Validate data types of key columns."""
        invalid_types = []
        
        # Check protected attribute
        if not pd.api.types.is_numeric_dtype(data[protected_attribute]):
            invalid_types.append(
                f"{protected_attribute} must be numeric"
            )
            
        # Check label column
        if not pd.api.types.is_numeric_dtype(data[label_column]):
            invalid_types.append(
                f"{label_column} must be numeric"
            )
            
        if invalid_types:
            self.error_messages.extend(invalid_types)
            return False
            
        self.validation_results['data_types'] = {
            col: str(dtype) for col, dtype in data.dtypes.items()
        }
        return True

    def _validate_value_ranges(self,
                             data: pd.DataFrame,
                             protected_attribute: str,
                             label_column: str) -> bool:
        """Validate value ranges for key columns."""
        invalid_ranges = []
        
        # Check protected attribute is binary
        if not set(data[protected_attribute].unique()).issubset({0, 1}):
            invalid_ranges.append(
                f"{protected_attribute} must be binary (0 or 1)"
            )
            
        # Check label is binary
        if not set(data[label_column].unique()).issubset({0, 1}):
            invalid_ranges.append(
                f"{label_column} must be binary (0 or 1)"
            )
            
        if invalid_ranges:
            self.error_messages.extend(invalid_ranges)
            return False
            
        self.validation_results['value_ranges'] = {
            protected_attribute: data[protected_attribute].unique().tolist(),
            label_column: data[label_column].unique().tolist()
        }
        return True

    def _validate_missing_values(self, data: pd.DataFrame) -> bool:
        """Validate presence of missing values."""
        missing_counts = data.isnull().sum()
        
        if missing_counts.any():
            self.error_messages.append(
                "Dataset contains missing values:\n" +
                "\n".join(f"- {col}: {count}" for col, count in 
                         missing_counts[missing_counts > 0].items())
            )
            return False
            
        self.validation_results['missing_values'] = False
        return True

    def _validate_data_quality(self,
                             data: pd.DataFrame,
                             protected_attribute: str,
                             label_column: str) -> bool:
        """Validate overall data quality."""
        quality_issues = []
        
        # Check class balance
        label_balance = data[label_column].value_counts(normalize=True)
        if abs(label_balance.max() - label_balance.min()) > 0.8:  # 80% threshold
            quality_issues.append("Severe class imbalance detected")
            
        # Check protected attribute balance
        protected_balance = data[protected_attribute].value_counts(normalize=True)
        if abs(protected_balance.max() - protected_balance.min()) > 0.8:
            quality_issues.append("Severe protected attribute imbalance detected")
            
        # Store quality metrics
        self.validation_results['data_quality'] = {
            'label_balance': label_balance.to_dict(),
            'protected_balance': protected_balance.to_dict()
        }
        
        if quality_issues:
            self.error_messages.extend(quality_issues)
            return False
            
        return True

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation results."""
        return {
            'passed': len(self.error_messages) == 0,
            'results': self.validation_results,
            'errors': self.error_messages
        }

    @staticmethod
    def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data for analysis.
        
        Args:
            data: Input DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        processed = data.copy()
        
        # Convert binary columns to int
        binary_columns = [
            col for col in processed.columns
            if set(processed[col].unique()).issubset({0, 1})
        ]
        for col in binary_columns:
            processed[col] = processed[col].astype(int)
            
        # Normalize numeric columns (excluding binary)
        numeric_columns = [
            col for col in processed.columns
            if pd.api.types.is_numeric_dtype(processed[col])
            and col not in binary_columns
        ]
        for col in numeric_columns:
            processed[col] = (
                processed[col] - processed[col].mean()
            ) / processed[col].std()
            
        return processed

if __name__ == "__main__":
    # Example usage
    try:
        # Create sample data
        data = pd.DataFrame({
            'protected_attribute': [0, 1, 0, 1],
            'label': [0, 1, 1, 0],
            'feature1': [1.0, 2.0, 3.0, 4.0]
        })
        
        # Create validator
        validator = DataValidator()
        
        # Validate dataset
        is_valid = validator.validate_dataset(data, 'protected_attribute')
        
        # Get validation summary
        summary = validator.get_validation_summary()
        
        print("Validation passed:", is_valid)
        print("\nValidation summary:")
        print(summary)
        
    except Exception as e:
        print(f"Error in example: {str(e)}")
        