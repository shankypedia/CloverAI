import pandas as pd
import numpy as np
from typing import Dict, List, Union, Any
from sklearn.base import BaseEstimator
import logging
import json  # Added missing import

def generate_report(data: pd.DataFrame, model: BaseEstimator) -> Dict[str, Any]:
    """
    Generate transparency report for AI model.
    
    Args:
        data: Input DataFrame containing features and label
        model: Trained model object with feature_importances_ attribute
        
    Returns:
        Dictionary containing model information, feature importance scores,
        and predictions
        
    Raises:
        ValueError: If data format is invalid or model is not properly trained
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Validate input data
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame")
        
        if 'label' not in data.columns:
            raise ValueError("Data must contain 'label' column")
            
        # Prepare features
        features = data.drop(columns=['label'])
        
        # Get model information
        model_info = {
            'name': model.__class__.__name__,
            'n_features': features.shape[1],
            'n_samples': features.shape[0]
        }
        
        # Get feature importance scores
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importance = np.abs(model.coef_[0]) / np.sum(np.abs(model.coef_[0]))
        else:
            logger.warning("Model does not provide feature importance scores")
            importance = np.ones(features.shape[1]) / features.shape[1]
            
        # Generate predictions
        try:
            predictions = model.predict(features)
        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            raise
            
        # Construct report
        report = {
            'model': model_info,
            'feature_importance': importance.tolist(),
            'predictions': predictions.tolist()
        }
        
        # Validate report content
        issues = validate_report_content(report)
        if issues:
            logger.warning(f"Report validation issues: {issues}")
            
        return report
        
    except Exception as e:
        logger.error(f"Error generating transparency report: {str(e)}")
        raise

def validate_report_content(report: Dict[str, Any]) -> List[str]:
    """
    Validate the content of a transparency report.
    
    Args:
        report: Report dictionary to validate
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Check model information
    if not report.get('model'):
        issues.append("Missing model information")
    
    # Validate feature importance
    importance = report.get('feature_importance', [])
    if not importance:
        issues.append("Missing feature importance scores")
    elif not all(isinstance(x, (float, np.float64)) for x in importance):
        issues.append("Invalid feature importance values")
    elif not (0.99 <= sum(importance) <= 1.01):  # Allow small numerical errors
        issues.append("Feature importance scores do not sum to 1")
    
    # Validate predictions
    predictions = report.get('predictions', [])
    if not predictions:
        issues.append("Missing predictions")
    elif not all(isinstance(x, (int, np.int64)) for x in predictions):
        issues.append("Invalid prediction values")
    
    return issues

if __name__ == "__main__":
    # Example usage
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    
    # Create sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 1000),
        'feature2': np.random.normal(0, 1, 1000),
        'feature3': np.random.normal(0, 1, 1000),
        'label': np.random.binomial(1, 0.5, 1000)
    })
    
    # Train model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    X = data.drop('label', axis=1)
    y = data['label']
    model.fit(X, y)
    
    # Generate report
    report = generate_report(data, model)
    print("Generated Report:")
    print(json.dumps(report, indent=2))
    