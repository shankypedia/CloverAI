import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Automatic data structure analyzer and processor."""
    
    # Define common patterns for attribute detection
    PROTECTED_PATTERNS = {
        'race': ['race', 'ethnicity', 'ethnic'],
        'gender': ['gender', 'sex'],
        'age': ['age', 'birth_year', 'dob'],
        'religion': ['religion', 'faith', 'belief'],
        'nationality': ['nationality', 'citizenship', 'national_origin'],
        'disability': ['disability', 'disabled', 'handicap']
    }
    
    SENSITIVE_PATTERNS = {
        'identification': ['ssn', 'social_security', 'passport', 'id_number'],
        'contact': ['email', 'phone', 'address', 'postal'],
        'financial': ['account', 'credit_card', 'salary', 'income'],
        'medical': ['diagnosis', 'condition', 'treatment', 'medication']
    }
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the data analyzer.
        
        Args:
            data: Input DataFrame to analyze
        """
        self.data = data
        self.detected_features = self._analyze_data_structure()
        
    def _analyze_data_structure(self) -> Dict[str, List[str]]:
        """
        Automatically analyze and categorize columns in the dataset.
        
        Returns:
            Dictionary of categorized features
        """
        features = {
            'categorical': [],
            'numerical': [],
            'temporal': [],
            'binary': [],
            'potential_protected': [],
            'potential_sensitive': []
        }
        
        for column in self.data.columns:
            column_lower = column.lower()
            
            # Detect protected attributes
            for category, patterns in self.PROTECTED_PATTERNS.items():
                if any(pattern in column_lower for pattern in patterns):
                    features['potential_protected'].append(column)
                    break
            
            # Detect sensitive information
            for category, patterns in self.SENSITIVE_PATTERNS.items():
                if any(pattern in column_lower for pattern in patterns):
                    features['potential_sensitive'].append(column)
                    break
            
            # Analyze data type and distribution
            dtype = self.data[column].dtype
            unique_vals = self.data[column].nunique()
            
            # Detect binary columns
            if unique_vals == 2:
                features['binary'].append(column)
                
            # Categorize by data type
            if pd.api.types.is_numeric_dtype(dtype):
                if unique_vals > 10:
                    features['numerical'].append(column)
                else:
                    features['categorical'].append(column)
            elif pd.api.types.is_datetime64_dtype(dtype):
                features['temporal'].append(column)
            else:
                features['categorical'].append(column)
                
        return features

    def suggest_protected_attributes(self) -> List[str]:
        """Get suggested protected attributes."""
        return list(set(self.detected_features['potential_protected']))
        
    def suggest_sensitive_fields(self) -> List[str]:
        """Get suggested sensitive fields."""
        return list(set(self.detected_features['potential_sensitive']))
        
    def get_feature_types(self) -> Dict[str, List[str]]:
        """Get categorized feature types."""
        return self.detected_features
        
    def analyze_data_quality(self) -> Dict[str, Any]:
        """
        Analyze data quality metrics.
        
        Returns:
            Dictionary containing data quality metrics
        """
        quality_metrics = {
            'missing_values': self.data.isnull().sum().to_dict(),
            'unique_values': self.data.nunique().to_dict(),
            'value_counts': {
                col: self.data[col].value_counts().to_dict()
                for col in self.detected_features['categorical']
            },
            'numerical_stats': self.data[self.detected_features['numerical']].describe().to_dict()
        }
        return quality_metrics

class DataProcessor:
    """Data processing and transformation handler."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the data processor.
        
        Args:
            data: Input DataFrame to process
        """
        self.data = data
        self.analyzer = DataAnalyzer(data)
        self.protected_attributes = self.analyzer.suggest_protected_attributes()
        self.sensitive_fields = self.analyzer.suggest_sensitive_fields()
        
    def prepare_for_bias_detection(self, 
                                 target_column: str,
                                 custom_protected_attrs: List[str] = None) -> Tuple[pd.DataFrame, List[str]]:
        """
        Prepare data for bias detection.
        
        Args:
            target_column: Name of the target/label column
            custom_protected_attrs: Optional list of custom protected attributes
            
        Returns:
            Tuple of (prepared_data, protected_attributes)
        """
        prepared_data = self.data.copy()
        protected_attrs = custom_protected_attrs or self.protected_attributes
        
        # Convert categorical variables to numeric
        for col in self.analyzer.detected_features['categorical']:
            if col != target_column and col not in protected_attrs:
                prepared_data[col] = pd.Categorical(prepared_data[col]).codes
                
        # Normalize numerical features
        for col in self.analyzer.detected_features['numerical']:
            if col != target_column and col not in protected_attrs:
                prepared_data[col] = (prepared_data[col] - prepared_data[col].mean()) / prepared_data[col].std()
                
        return prepared_data, protected_attrs
        
    def prepare_for_privacy_protection(self, 
                                    custom_sensitive_fields: List[str] = None) -> Tuple[pd.DataFrame, List[str]]:
        """
        Prepare data for privacy protection.
        
        Args:
            custom_sensitive_fields: Optional list of custom sensitive fields
            
        Returns:
            Tuple of (prepared_data, sensitive_fields)
        """
        sensitive_fields = custom_sensitive_fields or self.sensitive_fields
        return self.data, sensitive_fields
        
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive data summary.
        
        Returns:
            Dictionary containing data summary
        """
        summary = {
            'total_records': len(self.data),
            'features': self.analyzer.get_feature_types(),
            'protected_attributes': self.protected_attributes,
            'sensitive_fields': self.sensitive_fields,
            'data_quality': self.analyzer.analyze_data_quality(),
            'timestamp': datetime.now().isoformat()
        }
        return summary

def load_and_analyze_data(file_path: str) -> Tuple[DataProcessor, Dict[str, Any]]:
    """
    Load and analyze a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple of (DataProcessor, analysis_report)
    """
    try:
        # Load data
        data = pd.read_csv(file_path)
        
        # Create processor
        processor = DataProcessor(data)
        
        # Generate analysis report
        report = processor.get_data_summary()
        
        logger.info(f"Successfully loaded and analyzed data from {file_path}")
        return processor, report
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    try:
        # Load and analyze sample data
        processor, report = load_and_analyze_data('data/data.csv')
        
        # Print analysis results
        print("\nData Analysis Report:")
        print(f"Total Records: {report['total_records']}")
        print(f"Protected Attributes: {report['protected_attributes']}")
        print(f"Sensitive Fields: {report['sensitive_fields']}")
        
        # Prepare data for processing
        prepared_data, protected_attrs = processor.prepare_for_bias_detection('label')
        print("\nPrepared data shape:", prepared_data.shape)
        print("Protected attributes:", protected_attrs)
        
    except Exception as e:
        logger.error(f"Error in example execution: {str(e)}")