from aif360.datasets import BinaryLabelDataset
from aif360.metrics import BinaryLabelDatasetMetric, ClassificationMetric
from aif360.algorithms.preprocessing import Reweighing, DisparateImpactRemover
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class HealthcareMetrics:
    """Healthcare-specific fairness metrics."""
    treatment_disparity: float
    diagnostic_parity: float
    outcome_equity: float
    access_fairness: float

@dataclass
class FinanceMetrics:
    """Finance-specific fairness metrics."""
    lending_disparity: float
    risk_assessment_bias: float
    service_access_equity: float
    approval_rate_parity: float

class DomainSpecificBiasDetector:
    """Enhanced bias detection with domain-specific metrics."""
    
    def __init__(self, domain: str = 'general'):
        self.domain = domain
        self.logger = logging.getLogger(__name__)

    def calculate_healthcare_metrics(self, 
                                   dataset: BinaryLabelDataset,
                                   protected_attribute: str) -> HealthcareMetrics:
        """Calculate healthcare-specific fairness metrics."""
        try:
            metric = BinaryLabelDatasetMetric(
                dataset,
                unprivileged_groups=[{protected_attribute: 0}],
                privileged_groups=[{protected_attribute: 1}]
            )
            
            treatment_disparity = self._calculate_treatment_disparity(dataset, protected_attribute)
            diagnostic_parity = self._calculate_diagnostic_parity(dataset, protected_attribute)
            outcome_equity = metric.mean_difference()
            access_fairness = self._calculate_access_fairness(dataset, protected_attribute)
            
            return HealthcareMetrics(
                treatment_disparity=treatment_disparity,
                diagnostic_parity=diagnostic_parity,
                outcome_equity=outcome_equity,
                access_fairness=access_fairness
            )
        except Exception as e:
            self.logger.error(f"Error calculating healthcare metrics: {str(e)}")
            raise

    def calculate_finance_metrics(self,
                                dataset: BinaryLabelDataset,
                                protected_attribute: str) -> FinanceMetrics:
        """Calculate finance-specific fairness metrics."""
        try:
            metric = BinaryLabelDatasetMetric(
                dataset,
                unprivileged_groups=[{protected_attribute: 0}],
                privileged_groups=[{protected_attribute: 1}]
            )
            
            lending_disparity = self._calculate_lending_disparity(dataset, protected_attribute)
            risk_bias = self._calculate_risk_assessment_bias(dataset, protected_attribute)
            service_equity = metric.mean_difference()
            approval_parity = self._calculate_approval_rate_parity(dataset, protected_attribute)
            
            return FinanceMetrics(
                lending_disparity=lending_disparity,
                risk_assessment_bias=risk_bias,
                service_access_equity=service_equity,
                approval_rate_parity=approval_parity
            )
        except Exception as e:
            self.logger.error(f"Error calculating finance metrics: {str(e)}")
            raise

    def _calculate_treatment_disparity(self,
                                     dataset: BinaryLabelDataset,
                                     protected_attribute: str) -> float:
        """Calculate healthcare treatment disparity."""
        privileged_mask = dataset.protected_attributes[:, 0] == 1
        unprivileged_mask = dataset.protected_attributes[:, 0] == 0
        return abs(np.mean(dataset.labels[privileged_mask]) - 
                  np.mean(dataset.labels[unprivileged_mask]))

    def _calculate_diagnostic_parity(self,
                                   dataset: BinaryLabelDataset,
                                   protected_attribute: str) -> float:
        """Calculate diagnostic parity for healthcare."""
        privileged_mask = dataset.protected_attributes[:, 0] == 1
        unprivileged_mask = dataset.protected_attributes[:, 0] == 0
        return 1 - abs(np.mean(dataset.labels[privileged_mask]) - 
                      np.mean(dataset.labels[unprivileged_mask]))

    def _calculate_access_fairness(self,
                                 dataset: BinaryLabelDataset,
                                 protected_attribute: str) -> float:
        """Calculate healthcare access fairness."""
        metric = BinaryLabelDatasetMetric(
            dataset,
            unprivileged_groups=[{protected_attribute: 0}],
            privileged_groups=[{protected_attribute: 1}]
        )
        return 1 - abs(metric.disparate_impact() - 1)

    def _calculate_lending_disparity(self,
                                   dataset: BinaryLabelDataset,
                                   protected_attribute: str) -> float:
        """Calculate lending disparity for finance."""
        privileged_mask = dataset.protected_attributes[:, 0] == 1
        unprivileged_mask = dataset.protected_attributes[:, 0] == 0
        return abs(np.mean(dataset.labels[privileged_mask]) - 
                  np.mean(dataset.labels[unprivileged_mask]))

    def _calculate_risk_assessment_bias(self,
                                      dataset: BinaryLabelDataset,
                                      protected_attribute: str) -> float:
        """Calculate risk assessment bias for finance."""
        metric = BinaryLabelDatasetMetric(
            dataset,
            unprivileged_groups=[{protected_attribute: 0}],
            privileged_groups=[{protected_attribute: 1}]
        )
        return abs(metric.average_odds_difference())

    def _calculate_approval_rate_parity(self,
                                      dataset: BinaryLabelDataset,
                                      protected_attribute: str) -> float:
        """Calculate approval rate parity for finance."""
        metric = BinaryLabelDatasetMetric(
            dataset,
            unprivileged_groups=[{protected_attribute: 0}],
            privileged_groups=[{protected_attribute: 1}]
        )
        return 1 - abs(metric.statistical_parity_difference())

class DomainAwareBiasDetector:
    """Main bias detection class with domain awareness."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.domain_detector = DomainSpecificBiasDetector()

    def detect_bias(self,
                   data: pd.DataFrame,
                   protected_attribute: str,
                   domain: str = 'general') -> Dict:
        """
        Detect bias with domain-specific considerations.
        
        Args:
            data: Input DataFrame
            protected_attribute: Protected attribute name
            domain: Domain ('healthcare' or 'finance')
            
        Returns:
            Dictionary containing bias metrics
        """
        try:
            dataset = BinaryLabelDataset(
                df=data,
                label_names=['label'],
                protected_attribute_names=[protected_attribute]
            )
            
            general_metrics = self._calculate_general_metrics(dataset, protected_attribute)
            
            if domain == 'healthcare':
                domain_metrics = self.domain_detector.calculate_healthcare_metrics(
                    dataset, protected_attribute
                )
            elif domain == 'finance':
                domain_metrics = self.domain_detector.calculate_finance_metrics(
                    dataset, protected_attribute
                )
            else:
                domain_metrics = None
                
            return {
                'general_metrics': general_metrics,
                'domain_metrics': domain_metrics
            }
        except Exception as e:
            self.logger.error(f"Error in bias detection: {str(e)}")
            raise

    def _calculate_general_metrics(self,
                                    dataset: BinaryLabelDataset,
                                    protected_attribute: str) -> Dict:
            """Calculate general fairness metrics.
            
            This method computes fundamental fairness metrics using AIF360's BinaryLabelDatasetMetric:
            - Statistical parity difference: Measures the difference in selection rates
            - Disparate impact: Measures the ratio of selection rates
            - Mean difference: Measures the difference in mean predictions
            
            Args:
                dataset: The binary label dataset to analyze
                protected_attribute: Name of the protected attribute
                
            Returns:
                Dictionary containing the computed fairness metrics
            """
            metric = BinaryLabelDatasetMetric(
                dataset,
                unprivileged_groups=[{protected_attribute: 0}],
                privileged_groups=[{protected_attribute: 1}]
            )
            
            return {
                'statistical_parity': metric.statistical_parity_difference(),
                'disparate_impact': metric.disparate_impact(),
                'mean_difference': metric.mean_difference()
            }

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load and validate input data.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Pandas DataFrame containing the loaded data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If required columns are missing
    """
    try:
        data = pd.read_csv(file_path)
        required_columns = ['protected_attribute', 'label']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
        return data
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def detect_bias(data: pd.DataFrame, 
                protected_attribute: str,
                domain: str = 'general') -> Dict:
    """
    Detect bias with domain-specific considerations.
    
    Args:
        data: Input DataFrame
        protected_attribute: Name of protected attribute column
        domain: Optional domain specification ('healthcare' or 'finance')
        
    Returns:
        Dictionary containing bias metrics
    """
    detector = DomainAwareBiasDetector()
    return detector.detect_bias(data, protected_attribute, domain)

def mitigate_bias(data: pd.DataFrame, protected_attribute: str) -> pd.DataFrame:
    """
    Mitigate detected bias in the dataset using reweighing technique.
    
    This implementation focuses on the reweighing approach, which adjusts instance weights
    to ensure fairness while preserving the ability to learn accurate predictor downstream.
    
    Args:
        data: Input DataFrame containing features and protected attributes
        protected_attribute: Name of the protected attribute column
        
    Returns:
        DataFrame with mitigated bias through instance reweighing
    """
    try:
        # Convert to AIF360 dataset format
        dataset = BinaryLabelDataset(
            df=data,
            label_names=['label'],
            protected_attribute_names=[protected_attribute]
        )
        
        # Initialize and apply reweighing
        reweighing = Reweighing(
            unprivileged_groups=[{protected_attribute: 0}],
            privileged_groups=[{protected_attribute: 1}]
        )
        
        # Transform the dataset
        mitigated_dataset = reweighing.fit_transform(dataset)
        
        # Convert back to DataFrame and preserve instance weights
        mitigated_data = mitigated_dataset.convert_to_dataframe()[0]
        mitigated_data['instance_weights'] = mitigated_dataset.instance_weights
        
        logger.info("Bias mitigation completed successfully")
        return mitigated_data
        
    except Exception as e:
        logger.error(f"Error in bias mitigation: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Example usage
        data = load_data('data/data.csv')
        
        # General bias detection
        bias_metrics = detect_bias(data, 'protected_attribute')
        print("General Bias Metrics:", bias_metrics['general_metrics'])
        
        # Healthcare-specific detection
        healthcare_metrics = detect_bias(data, 'protected_attribute', domain='healthcare')
        print("Healthcare Metrics:", healthcare_metrics['domain_metrics'])
        
        # Bias mitigation
        mitigated_data = mitigate_bias(data, 'protected_attribute')
        print("Mitigated Data Shape:", mitigated_data.shape)
        
    except Exception as e:
        logger.error(f"Error in example execution: {str(e)}")
        