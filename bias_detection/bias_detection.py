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

def safe_divide(a: float, b: float, default: float = 1.0) -> float:
    """Safely perform division with error handling."""
    try:
        if abs(b) < 1e-10:
            return default
        return a / b
    except:
        return default

def safe_subtract(a: float, b: float, default: float = 0.0) -> float:
    """Safely perform subtraction with error handling."""
    try:
        return a - b
    except:
        return default

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
            outcome_equity = safe_subtract(
                np.mean(dataset.labels[dataset.protected_attributes[:, 0] == 1]),
                np.mean(dataset.labels[dataset.protected_attributes[:, 0] == 0])
            )
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
            service_equity = safe_subtract(
                np.mean(dataset.labels[dataset.protected_attributes[:, 0] == 1]),
                np.mean(dataset.labels[dataset.protected_attributes[:, 0] == 0])
            )
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
        
        privileged_mean = np.mean(dataset.labels[privileged_mask])
        unprivileged_mean = np.mean(dataset.labels[unprivileged_mask])
        
        return safe_subtract(privileged_mean, unprivileged_mean)

    def _calculate_diagnostic_parity(self,
                                   dataset: BinaryLabelDataset,
                                   protected_attribute: str) -> float:
        """Calculate diagnostic parity for healthcare."""
        privileged_mask = dataset.protected_attributes[:, 0] == 1
        unprivileged_mask = dataset.protected_attributes[:, 0] == 0
        
        privileged_mean = np.mean(dataset.labels[privileged_mask])
        unprivileged_mean = np.mean(dataset.labels[unprivileged_mask])
        
        return 1 - abs(safe_subtract(privileged_mean, unprivileged_mean))

    def _calculate_access_fairness(self,
                                 dataset: BinaryLabelDataset,
                                 protected_attribute: str) -> float:
        """Calculate healthcare access fairness."""
        try:
            metric = BinaryLabelDatasetMetric(
                dataset,
                unprivileged_groups=[{protected_attribute: 0}],
                privileged_groups=[{protected_attribute: 1}]
            )
            return 1 - abs(metric.disparate_impact() - 1)
        except:
            return 0.0

    def _calculate_lending_disparity(self,
                                   dataset: BinaryLabelDataset,
                                   protected_attribute: str) -> float:
        """Calculate lending disparity for finance."""
        privileged_mask = dataset.protected_attributes[:, 0] == 1
        unprivileged_mask = dataset.protected_attributes[:, 0] == 0
        
        privileged_mean = np.mean(dataset.labels[privileged_mask])
        unprivileged_mean = np.mean(dataset.labels[unprivileged_mask])
        
        return safe_subtract(privileged_mean, unprivileged_mean)

    def _calculate_risk_assessment_bias(self,
                                      dataset: BinaryLabelDataset,
                                      protected_attribute: str) -> float:
        """Calculate risk assessment bias for finance."""
        try:
            metric = BinaryLabelDatasetMetric(
                dataset,
                unprivileged_groups=[{protected_attribute: 0}],
                privileged_groups=[{protected_attribute: 1}]
            )
            return abs(metric.average_odds_difference())
        except:
            return 0.0

    def _calculate_approval_rate_parity(self,
                                      dataset: BinaryLabelDataset,
                                      protected_attribute: str) -> float:
        """Calculate approval rate parity for finance."""
        try:
            metric = BinaryLabelDatasetMetric(
                dataset,
                unprivileged_groups=[{protected_attribute: 0}],
                privileged_groups=[{protected_attribute: 1}]
            )
            return 1 - abs(metric.statistical_parity_difference())
        except:
            return 0.0

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
            # Validate inputs
            if protected_attribute not in data.columns:
                raise ValueError(f"Protected attribute {protected_attribute} not found")
                
            # Prepare dataset
            data = data.copy()
            data[protected_attribute] = data[protected_attribute].astype(float)
            if 'label' in data.columns:
                data['label'] = data['label'].astype(float)
            
            dataset = BinaryLabelDataset(
                df=data,
                label_names=['label'],
                protected_attribute_names=[protected_attribute]
            )
            
            # Calculate metrics
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
        """Calculate general fairness metrics with robust error handling."""
        try:
            # Extract privileged and unprivileged data
            privileged_mask = dataset.protected_attributes[:, 0] == 1
            unprivileged_mask = dataset.protected_attributes[:, 0] == 0
            
            privileged_outcomes = dataset.labels[privileged_mask]
            unprivileged_outcomes = dataset.labels[unprivileged_mask]
            
            # Calculate base rates with validation
            if len(privileged_outcomes) > 0 and len(unprivileged_outcomes) > 0:
                privileged_rate = np.mean(privileged_outcomes)
                unprivileged_rate = np.mean(unprivileged_outcomes)
                
                # Calculate metrics with proper bounds
                statistical_parity = privileged_rate - unprivileged_rate
                disparate_impact = (unprivileged_rate / privileged_rate 
                                if privileged_rate > 0 else 1.0)
                mean_difference = privileged_rate - unprivileged_rate
                
                return {
                    'statistical_parity': np.clip(statistical_parity, -1, 1),
                    'disparate_impact': np.clip(disparate_impact, 0, 2),
                    'mean_difference': np.clip(mean_difference, -1, 1)
                }
                
            else:
                self.logger.warning("Insufficient data for metric calculation")
                return {
                    'statistical_parity': 0.0,
                    'disparate_impact': 1.0,
                    'mean_difference': 0.0
                }
                
        except Exception as e:
            self.logger.error(f"Error calculating general metrics: {str(e)}")
            return {
                'statistical_parity': 0.0,
                'disparate_impact': 1.0,
                'mean_difference': 0.0
            }

def detect_bias(data: pd.DataFrame, protected_attribute: str, domain: str = 'general') -> Dict:
    """Main interface for bias detection."""
    detector = DomainAwareBiasDetector()
    return detector.detect_bias(data, protected_attribute, domain)

def mitigate_bias(data: pd.DataFrame, protected_attribute: str) -> pd.DataFrame:
    """Main interface for bias mitigation."""
    try:
        dataset = BinaryLabelDataset(
            df=data,
            label_names=['label'],
            protected_attribute_names=[protected_attribute]
        )
        
        reweighing = Reweighing(
            unprivileged_groups=[{protected_attribute: 0}],
            privileged_groups=[{protected_attribute: 1}]
        )
        
        mitigated_dataset = reweighing.fit_transform(dataset)
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
        data = pd.read_csv('data/data.csv')
        
        # General bias detection
        bias_metrics = detect_bias(data, 'protected_attribute')
        print("General Metrics:", bias_metrics['general_metrics'])
        
        # Domain-specific detection
        healthcare_metrics = detect_bias(data, 'protected_attribute', domain='healthcare')
        print("Healthcare Metrics:", healthcare_metrics['domain_metrics'])
        
        # Bias mitigation
        mitigated_data = mitigate_bias(data, 'protected_attribute')
        print("Mitigated Data Shape:", mitigated_data.shape)
        
    except Exception as e:
        logger.error(f"Error in example execution: {str(e)}")
        