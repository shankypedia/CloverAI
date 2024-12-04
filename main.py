import os
import warnings
import logging
from typing import Any, Dict
import pandas as pd
from datetime import datetime
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Initialize Rich console
console = Console()

# Configure logging and warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=FutureWarning, module='inFairness')
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Import components
from bias_detection import bias_detection
from privacy_protection import privacy_protection
from governance_automation import governance_automation
from real_time_monitoring import monitor_metrics
from transparency_reports import generate_report
from sklearn.ensemble import RandomForestClassifier

class CloverAI:
    """CloverAI Framework Controller"""
    
    def __init__(self):
        self.console = Console()
        self.start_time = datetime.now()

    def print_header(self):
        """Print framework header."""
        header = Panel(
            "[bold green]CloverAI Governance Framework[/bold green]\n"
            "[dim]AI Governance and Compliance Automation[/dim]",
            style="blue"
        )
        self.console.print(header)
        self.console.print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    def process_data(self, data_path: str):
        """Process data through the governance pipeline."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            # Load Data
            task = progress.add_task("[cyan]Loading data...", total=None)
            data = bias_detection.load_data(data_path)
            progress.update(task, completed=True)
            
            # Bias Detection
            task = progress.add_task("[cyan]Running bias detection...", total=None)
            bias_metrics = bias_detection.detect_bias(data, 'protected_attribute')
            self._display_bias_metrics(bias_metrics)
            progress.update(task, completed=True)
            
            # Bias Mitigation
            task = progress.add_task("[cyan]Mitigating bias...", total=None)
            mitigated_data = bias_detection.mitigate_bias(data, 'protected_attribute')
            self._display_mitigated_data(mitigated_data)
            progress.update(task, completed=True)
            
            # Privacy Protection
            task = progress.add_task("[cyan]Applying privacy protection...", total=None)
            key = privacy_protection.generate_key()
            encrypted_data = privacy_protection.encrypt_data(mitigated_data, key)
            anonymized_data = privacy_protection.anonymize_data(mitigated_data)
            self._display_privacy_results(encrypted_data, anonymized_data)
            progress.update(task, completed=True)
            
            # Governance
            task = progress.add_task("[cyan]Enforcing governance policies...", total=None)
            governance_result = governance_automation.enforce_policy('config/network_policy.yaml')
            self._display_governance_results(governance_result)
            progress.update(task, completed=True)
            
            # Monitoring
            task = progress.add_task("[cyan]Establishing monitoring...", total=None)
            monitor_metrics(duration=10)
            progress.update(task, completed=True)
            
            # Transparency
            task = progress.add_task("[cyan]Generating transparency report...", total=None)
            model = RandomForestClassifier()
            X = mitigated_data.drop(columns=['label'])
            y = mitigated_data['label']
            model.fit(X, y)
            report = generate_report(mitigated_data, model)
            self._display_transparency_report(report)
            progress.update(task, completed=True)

    def _display_bias_metrics(self, metrics: Dict[str, Any]):
        """Display bias detection metrics."""
        table = Table(title="Bias Detection Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for category, values in metrics.items():
            if isinstance(values, dict):
                for metric, value in values.items():
                    table.add_row(f"{category}.{metric}", f"{value:.4f}")
            else:
                table.add_row(category, str(values))
        
        self.console.print(table)

    def _display_mitigated_data(self, data: pd.DataFrame):
        """Display mitigated data summary."""
        self.console.print(Panel(
            f"[green]Bias Mitigation Complete[/green]\n"
            f"Processed {len(data)} records\n"
            f"Modified {len(data.columns)} features",
            title="Bias Mitigation"
        ))

    def _display_privacy_results(self, encrypted_data: pd.DataFrame, anonymized_data: pd.DataFrame):
        """Display privacy protection results."""
        self.console.print(Panel(
            f"[green]Privacy Protection Applied[/green]\n"
            f"Encrypted {len(encrypted_data)} records\n"
            f"Anonymized {len(anonymized_data)} records",
            title="Privacy Protection"
        ))

    def _display_governance_results(self, result: Dict[str, Any]):
        """Display governance enforcement results."""
        status_color = "green" if result.get('status') == 'success' else "yellow"
        self.console.print(Panel(
            f"[{status_color}]Status: {result.get('status', 'unknown')}[/{status_color}]\n"
            f"Policy Type: {result.get('policy_type', 'unknown')}\n"
            f"Namespace: {result.get('namespace', 'default')}",
            title="Governance Enforcement"
        ))

    def _display_transparency_report(self, report: Dict[str, Any]):
        """Display transparency report."""
        table = Table(title="Model Transparency Report")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        # Model info
        for key, value in report['model'].items():
            table.add_row(f"Model {key}", str(value))
        
        # Feature importance
        for i, importance in enumerate(report['feature_importance']):
            table.add_row(f"Feature {i+1} Importance", f"{importance:.4f}")
        
        self.console.print(table)

    def print_completion(self):
        """Print completion information."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.console.print(Panel(
            f"[bold green]Processing Complete[/bold green]\n"
            f"Duration: {duration:.2f} seconds\n"
            f"Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            title="Execution Summary"
        ))

def main():
    framework = CloverAI()
    framework.print_header()
    framework.process_data('data/data.csv')
    framework.print_completion()

if __name__ == "__main__":
    main()
    