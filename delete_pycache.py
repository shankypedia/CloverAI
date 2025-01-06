import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def delete_pycache(directory):
    total_deleted = 0
    total_dirs = 0
    skipped_dirs = []

    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                dir_path = os.path.join(root, dir_name)
                try:
                    for file in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, file)
                        os.remove(file_path)
                        total_deleted += 1
                    os.rmdir(dir_path)
                    total_dirs += 1
                except Exception as e:
                    skipped_dirs.append((dir_path, str(e)))

    return total_deleted, total_dirs, skipped_dirs

if __name__ == "__main__":
    directory = '.'  # Current directory
    total_deleted, total_dirs, skipped_dirs = delete_pycache(directory)

    # Display results using rich
    console.print(Panel("[bold green]CloverAI __pycache__ Deletion Report[/bold green]", title="CloverAI"))

    table = Table(title="Deletion Statistics")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Total files deleted", str(total_deleted))
    table.add_row("Total __pycache__ directories deleted", str(total_dirs))

    console.print(table)

    if skipped_dirs:
        console.print(Panel("[bold yellow]Skipped Directories[/bold yellow]", title="Skipped Directories"))
        for dir_path, error in skipped_dirs:
            console.print(f"Skipping directory: {dir_path} due to error: {error}")
            