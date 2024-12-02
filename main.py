import os
import warnings
import logging

# Set environment variable to disable oneDNN custom operations
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Suppress TensorFlow warnings
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Suppress specific module warnings
warnings.filterwarnings("ignore", category=FutureWarning, module='inFairness')

from bias_detection import bias_detection
from privacy_protection import privacy_protection
from governance_automation import governance_automation
from real_time_monitoring import monitor_metrics
from transparency_reports import generate_report  # Updated import
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

def print_section_header(title):
    print("\n" + "="*50)
    print(f"{title:^50}")
    print("="*50)

def main():
    print("\n" + "="*50)
    print("CloverAI Governance Framework".center(50))
    print("="*50)
    
    print_section_header("Loading Data")
    # Load and process data
    data = bias_detection.load_data('data/data.csv')
    print("Data loaded successfully.")
    
    print_section_header("Running Bias Detection")
    # Bias detection and mitigation
    bias_metric = bias_detection.detect_bias(data, 'protected_attribute')
    print(f"Bias Metric: {bias_metric}")
    mitigated_data = bias_detection.mitigate_bias(data, 'protected_attribute')
    print("Mitigated Data:")
    print(mitigated_data.head())
    
    print_section_header("Running Privacy Protection")
    # Privacy protection
    key = privacy_protection.generate_key()
    encrypted_data = privacy_protection.encrypt_data(mitigated_data, key)
    print("Encrypted Data:")
    print(encrypted_data.head())
    anonymized_data = privacy_protection.anonymize_data(mitigated_data)
    print("Anonymized Data:")
    print(anonymized_data.head())
    
    print_section_header("Enforcing Governance Policy")
    # Governance automation
    governance_automation.enforce_policy('config/network_policy.yaml')
    
    print_section_header("Starting Real-Time Monitoring")
    # Real-time monitoring
    monitor_metrics(duration=10)
    
    print_section_header("Generating Transparency Report")
    # Placeholder model for transparency reports
    model = RandomForestClassifier()
    X = mitigated_data.drop(columns=['label'])
    y = mitigated_data['label']
    model.fit(X, y)
    
    report = generate_report(mitigated_data, model)  # Updated usage
    print("Transparency Report:")
    print(report)
    
    print_section_header("Program Completed")
    print("All tasks have been completed successfully.")

if __name__ == "__main__":
    main()
    