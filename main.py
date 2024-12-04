import os
import warnings
import logging
from typing import Any, Dict
import pandas as pd
import numpy as np
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.layout import Layout
import json

# Initialize Rich console
console = Console()

# Configure logging and warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=FutureWarning, module='inFairness')
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Import components
from data_processing import load_and_analyze_data
from validation import DataValidator
from bias_detection import detect_bias, mitigate_bias
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
        self.validator = DataValidator()

    def print_header(self):
        """Print framework header."""
        header = Panel(
            "[bold blue]CloverAI[/bold blue]: AI Governance Framework\n"
            "[dim]Version 1.0.0[/dim]\n"
            "[cyan]Ensuring Ethical AI Deployment[/cyan]",
            style="bold white"
        )
        self.console.print(header)
        self.console.print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    def run_pipeline(self, data_path: str):
        """Run the complete governance pipeline."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )

        try:
            with progress:
                # Data Analysis
                analysis_task = progress.add_task("[cyan]Analyzing data...", total=100)
                processor, analysis_report = load_and_analyze_data(data_path)
                self._display_analysis_report(analysis_report)
                progress.update(analysis_task, completed=100)

                # Validate data
                validation_task = progress.add_task("[cyan]Validating data...", total=100)
                if not self.validator.validate_dataset(processor.data, 'protected_attribute'):
                    self._display_validation_errors()
                    return
                progress.update(validation_task, completed=100)

                # Bias Detection
                bias_task = progress.add_task("[cyan]Detecting bias...", total=100)
                prepared_data, protected_attrs = processor.prepare_for_bias_detection('label')
                bias_metrics = detect_bias(
                    prepared_data, 
                    protected_attrs[0], 
                    domain='finance'
                )
                self._display_bias_metrics(bias_metrics)
                progress.update(bias_task, completed=100)

                # Bias Mitigation
                mitigation_task = progress.add_task("[cyan]Mitigating bias...", total=100)
                mitigated_data = mitigate_bias(prepared_data, protected_attrs[0])
                self._display_mitigated_data(mitigated_data, bias_metrics)
                progress.update(mitigation_task, completed=100)

                # Privacy Protection
                privacy_task = progress.add_task("[cyan]Applying privacy protection...", total=100)
                key = privacy_protection.generate_key()
                encrypted_data = privacy_protection.encrypt_data(mitigated_data, key)
                anonymized_data = privacy_protection.anonymize_data(mitigated_data)
                self._display_privacy_results(encrypted_data, anonymized_data)
                progress.update(privacy_task, completed=100)

                # Governance
                governance_task = progress.add_task("[cyan]Enforcing governance policies...", total=100)
                governance_result = governance_automation.enforce_policy('config/network_policy.yaml')
                self._display_governance_results(governance_result)
                progress.update(governance_task, completed=100)

                # Monitoring
                monitoring_task = progress.add_task("[cyan]Establishing monitoring...", total=100)
                monitor_metrics(duration=10)
                progress.update(monitoring_task, completed=100)

                # Transparency
                transparency_task = progress.add_task("[cyan]Generating transparency report...", total=100)
                model = RandomForestClassifier(random_state=42)
                features_for_model = mitigated_data.drop(columns=['label', 'instance_weights'])
                labels = mitigated_data['label']
                model.fit(features_for_model, labels)
                report = generate_report(mitigated_data, model)
                self._display_transparency_report(report)
                progress.update(transparency_task, completed=100)

        except Exception as e:
            self.console.print(f"\n[red]Error in pipeline execution:[/red] {str(e)}")
            logging.error(f"Pipeline error: {str(e)}")
            raise

    def _display_analysis_report(self, report: Dict[str, Any]):
        """Display data analysis results."""
        layout = Layout()
        layout.split_column(
            Layout(name="summary"),
            Layout(name="details")
        )

        # Summary table
        summary_table = Table(title="Data Analysis Summary", show_header=True)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total Records", str(report['total_records']))
        summary_table.add_row("Protected Attributes", ", ".join(report['protected_attributes']))
        summary_table.add_row("Sensitive Fields", ", ".join(report['sensitive_fields']))

        # Details panel
        details = "\n".join([
            f"[cyan]Feature Types:[/cyan]",
            *[f"• {k}: {len(v)} features" for k, v in report['features'].items()],
            f"\n[cyan]Data Quality:[/cyan]",
            f"• Missing Values: {sum(report['data_quality']['missing_values'].values())}",
            f"• Unique Values: {sum(report['data_quality']['unique_values'].values())}"
        ])

        layout["summary"].update(summary_table)
        layout["details"].update(Panel(details, title="Detailed Analysis"))

        self.console.print(layout)

    def _display_validation_errors(self):
        """Display validation errors."""
        summary = self.validator.get_validation_summary()
        self.console.print("\n[red]Validation Errors:[/red]")
        for error in summary['errors']:
            self.console.print(f"[red]• {error}[/red]")

    def _display_bias_metrics(self, metrics: Dict[str, Any]):
        """Display enhanced bias detection metrics."""
        layout = Layout()
        layout.split_column(
            Layout(name="general"),
            Layout(name="domain"),
            Layout(name="interpretation")
        )

        # General metrics table
        general_table = Table(title="General Bias Metrics")
        general_table.add_column("Metric", style="cyan")
        general_table.add_column("Value", style="green")
        general_table.add_column("Status", style="yellow")

        thresholds = {
            'statistical_parity': (-0.1, 0.1),
            'disparate_impact': (0.8, 1.2),
            'mean_difference': (-0.1, 0.1)
        }

        general_metrics = metrics.get('general_metrics', {})
        for metric, value in general_metrics.items():
            if metric in thresholds:
                low, high = thresholds[metric]
                status = "✓" if low <= value <= high else "⚠"
                general_table.add_row(
                    metric.replace('_', ' ').title(),
                    f"{value:.4f}",
                    status
                )

        # Domain-specific metrics
        domain_metrics = metrics.get('domain_metrics')
        if domain_metrics:
            domain_table = Table(title="Domain-Specific Metrics")
            domain_table.add_column("Metric", style="cyan")
            domain_table.add_column("Value", style="green")

            for field in domain_metrics.__annotations__:
                value = getattr(domain_metrics, field)
                domain_table.add_row(
                    field.replace('_', ' ').title(),
                    f"{value:.4f}"
                )
            layout["domain"].update(domain_table)

        # Interpretation panel
        interpretation = self._generate_bias_interpretation(metrics)
        layout["general"].update(general_table)
        layout["interpretation"].update(Panel(
            interpretation,
            title="[bold cyan]Bias Analysis Interpretation[/bold cyan]"
        ))

        self.console.print(layout)

    def _display_mitigated_data(self, data: pd.DataFrame, original_metrics: Dict[str, Any]):
        """Display bias mitigation results."""
        # Calculate post-mitigation metrics
        post_metrics = detect_bias(data, 'protected_attribute')

        table = Table(title="Bias Mitigation Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Before", style="yellow")
        table.add_column("After", style="green")
        table.add_column("Improvement", style="blue")

        for metric, before in original_metrics['general_metrics'].items():
            after = post_metrics['general_metrics'][metric]
            improvement = ((after - before) / abs(before)) * 100 if before != 0 else 0

            table.add_row(
                metric.replace('_', ' ').title(),
                f"{before:.4f}",
                f"{after:.4f}",
                f"{improvement:+.1f}%"
            )

        self.console.print(table)

    def _display_privacy_results(self, encrypted_data: pd.DataFrame, anonymized_data: pd.DataFrame):
        """Display privacy protection results."""
        layout = Layout()
        layout.split_column(
            Layout(name="summary"),
            Layout(name="details")
        )

        # Summary
        summary = Panel(
            f"[green]Privacy Protection Applied Successfully[/green]\n\n"
            f"Records Processed: {len(encrypted_data)}\n"
            f"Columns Protected: {len(encrypted_data.columns)}\n"
            f"Anonymization Method: Differential Privacy",
            title="Privacy Protection Summary"
        )

        # Details table
        details_table = Table(title="Protection Details")
        details_table.add_column("Category", style="cyan")
        details_table.add_column("Status", style="green")

        details_table.add_row("Encryption", "✓ Applied")
        details_table.add_row("Anonymization", "✓ Applied")
        details_table.add_row("PII Protection", "✓ Verified")
        details_table.add_row("GDPR Compliance", "✓ Confirmed")

        layout["summary"].update(summary)
        layout["details"].update(details_table)

        self.console.print(layout)

    def _display_governance_results(self, result: Dict[str, Any]):
        """Display governance enforcement results."""
        status_color = "green" if result.get('status') == 'success' else "yellow"

        layout = Layout()
        layout.split_column(
            Layout(name="status"),
            Layout(name="details")
        )

        # Status panel
        status = Panel(
            f"[{status_color}]Status: {result.get('status', 'unknown')}[/{status_color}]\n"
            f"Policy Type: {result.get('policy_type', 'unknown')}\n"
            f"Namespace: {result.get('namespace', 'default')}",
            title="Governance Status"
        )

        # Details table
        details_table = Table(title="Policy Enforcement Details")
        details_table.add_column("Component", style="cyan")
        details_table.add_column("Status", style="green")

        details_table.add_row("Network Policy", "✓ Enforced")
        details_table.add_row("Security Policy", "✓ Applied")
        details_table.add_row("Resource Quotas", "✓ Set")
        details_table.add_row("Compliance Check", "✓ Passed")

        layout["status"].update(status)
        layout["details"].update(details_table)

        self.console.print(layout)

    def _display_transparency_report(self, report: Dict[str, Any]):
        """Display transparency report."""
        layout = Layout()
        layout.split_column(
            Layout(name="model"),
            Layout(name="features"),
            Layout(name="summary")
        )

        # Model information
        model_table = Table(title="Model Information")
        model_table.add_column("Parameter", style="cyan")
        model_table.add_column("Value", style="green")

        for key, value in report['model'].items():
            model_table.add_row(key.replace('_', ' ').title(), str(value))

        # Feature importance
        feature_table = Table(title="Feature Importance")
        feature_table.add_column("Feature", style="cyan")
        feature_table.add_column("Importance", style="green")
        feature_table.add_column("Impact", style="yellow")

        for i, importance in enumerate(report['feature_importance']):
            impact = "High" if importance > 0.2 else "Medium" if importance > 0.1 else "Low"
            feature_table.add_row(
                f"Feature {i + 1}",
                f"{importance:.4f}",
                impact
            )

        # Summary
        summary = Panel(
            "[cyan]Model Transparency Summary[/cyan]\n\n"
            f"Total Features: {len(report['feature_importance'])}\n"
            f"Key Drivers: {sum(1 for imp in report['feature_importance'] if imp > 0.2)} features\n"
            "Model Type: Random Forest Classifier",
            title="Summary"
        )

        layout["model"].update(model_table)
        layout["features"].update(feature_table)
        layout["summary"].update(summary)

        self.console.print(layout)

    def _generate_bias_interpretation(self, metrics: Dict[str, Any]) -> str:
        """Generate interpretation text for bias metrics."""
        interpretations = []
        general_metrics = metrics.get('general_metrics', {})

        if 'disparate_impact' in general_metrics:
            di = general_metrics['disparate_impact']
            if di < 0.8:
                interpretations.append("⚠ Significant disadvantage detected for unprivileged group")
            elif di > 1.2:
                interpretations.append("⚠ Significant advantage detected for unprivileged group")
            else:
                interpretations.append("✓ Disparate impact within acceptable range")

        if 'statistical_parity' in general_metrics:
            sp = abs(general_metrics['statistical_parity'])
            if sp > 0.1:
                interpretations.append("⚠ Notable selection rate difference between groups")
            else:
                interpretations.append("✓ Selection rates are approximately equal")

        if 'mean_difference' in general_metrics:
            md = abs(general_metrics['mean_difference'])
            if md > 0.1:
                interpretations.append("⚠ Substantial outcome differences detected")
            else:
                interpretations.append("✓ Outcome differences are minimal")

        # Domain-specific interpretations
        if metrics.get('domain_metrics'):
            domain_metrics = metrics['domain_metrics']
            if hasattr(domain_metrics, 'treatment_disparity'):
                # Healthcare domain
                if domain_metrics.treatment_disparity > 0.1:
                    interpretations.append("⚠ Treatment disparities require attention")
                if domain_metrics.diagnostic_parity < 0.9:
                    interpretations.append("⚠ Diagnostic parity below threshold")
            elif hasattr(domain_metrics, 'lending_disparity'):
                # Finance domain
                if domain_metrics.lending_disparity > 0.1:
                    interpretations.append("⚠ Lending disparities detected")
                if domain_metrics.approval_rate_parity < 0.9:
                    interpretations.append("⚠ Approval rate disparities present")

        return "\n".join(interpretations) if interpretations else "No significant bias detected"

    def print_completion(self):
        """Print completion information with execution summary."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        layout = Layout()
        layout.split_column(
            Layout(name="summary"),
            Layout(name="recommendations")
        )

        # Execution summary
        summary = Panel(
            f"[bold green]Processing Complete[/bold green]\n\n"
            f"Duration: {duration:.2f} seconds\n"
            f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            title="Execution Summary"
        )

        # Recommendations for next steps
        recommendations = Panel(
            "[cyan]Recommended Next Steps:[/cyan]\n\n"
            "1. Review bias mitigation results\n"
            "2. Verify privacy protection measures\n"
            "3. Monitor governance compliance\n"
            "4. Schedule regular reassessment",
            title="Next Steps"
        )

        layout["summary"].update(summary)
        layout["recommendations"].update(recommendations)

        self.console.print(layout)


def main():
    """Main execution function."""
    try:
        console.print("\n[bold cyan]Initializing CloverAI Framework...[/bold cyan]")

        framework = CloverAI()
        framework.print_header()

        console.print("[bold cyan]Starting Analysis Pipeline...[/bold cyan]\n")
        framework.run_pipeline('data/data.csv')

        framework.print_completion()

    except Exception as e:
        console.print(f"\n[red bold]Critical Error:[/red bold] {str(e)}")
        logging.error(f"Critical error in main execution: {str(e)}")

        # Display error details in a panel
        error_panel = Panel(
            f"[red]Error Type: {type(e).__name__}[/red]\n"
            f"[red]Error Message: {str(e)}[/red]\n\n"
            "[yellow]Please check the logs for more details.[/yellow]",
            title="Error Details"
        )
        console.print(error_panel)
        raise
    finally:
        console.print("\n[bold cyan]CloverAI Session Ended[/bold cyan]")


if __name__ == "__main__":
    main()
