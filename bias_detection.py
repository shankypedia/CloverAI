from aif360.datasets import AdultDataset
from aif360.metrics import BinaryLabelDatasetMetric

# Load UCI Adult dataset
dataset = AdultDataset()

# Define privileged (e.g., Male) and unprivileged (e.g., Female) groups
privileged_groups = [{'sex': 1}]
unprivileged_groups = [{'sex': 0}]

# Calculate Demographic Parity difference
metric = BinaryLabelDatasetMetric(dataset, unprivileged_groups=unprivileged_groups, privileged_groups=privileged_groups)
print(f"Demographic Parity Difference: {metric.mean_difference()}")
