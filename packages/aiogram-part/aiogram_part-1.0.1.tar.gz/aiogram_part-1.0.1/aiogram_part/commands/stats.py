from pathlib import Path
from aiogram_part.utils.logger import log_info
from rich.console import Console
from rich.table import Table

def execute():
    """Show project statistics"""
    base_path = Path.cwd()
    console = Console()
    
    # Count files
    handlers_user = len(list((base_path / "handlers" / "users").rglob("*.py"))) if (base_path / "handlers" / "users").exists() else 0
    handlers_admin = len(list((base_path / "handlers" / "admins").rglob("*.py"))) if (base_path / "handlers" / "admins").exists() else 0
    handlers_user -= len(list((base_path / "handlers" / "users").rglob("__init__.py"))) if (base_path / "handlers" / "users").exists() else 0
    handlers_admin -= len(list((base_path / "handlers" / "admins").rglob("__init__.py"))) if (base_path / "handlers" / "admins").exists() else 0
    
    models = len(list((base_path / "database" / "models").glob("*.py"))) - 1 if (base_path / "database" / "models").exists() else 0
    filters_count = len(list((base_path / "filters").rglob("*.py"))) - len(list((base_path / "filters").rglob("__init__.py"))) if (base_path / "filters").exists() else 0
    keyboards = len(list((base_path / "keyboards").rglob("*.py"))) - len(list((base_path / "keyboards").rglob("__init__.py"))) if (base_path / "keyboards").exists() else 0
    middlewares = len(list((base_path / "middlewares").rglob("*.py"))) - len(list((base_path / "middlewares").rglob("__init__.py"))) if (base_path / "middlewares").exists() else 0
    services = len(list((base_path / "services").rglob("*.py"))) - len(list((base_path / "services").rglob("__init__.py"))) if (base_path / "services").exists() else 0
    
    # Count lines of code
    total_lines = 0
    py_files = list(base_path.rglob("*.py"))
    for file in py_files:
        if "venv" not in str(file) and ".venv" not in str(file) and "__pycache__" not in str(file):
            try:
                with open(file, 'r') as f:
                    total_lines += len(f.readlines())
            except:
                pass
    
    # Create table
    table = Table(title="📊 Project Statistics", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=20)
    table.add_column("Count", justify="right", style="green")
    
    table.add_row("Handlers (User)", str(handlers_user))
    table.add_row("Handlers (Admin)", str(handlers_admin))
    table.add_row("Handlers (Total)", str(handlers_user + handlers_admin), style="bold")
    table.add_row("", "")
    table.add_row("Models", str(max(0, models)))
    table.add_row("Filters", str(filters_count))
    table.add_row("Keyboards", str(keyboards))
    table.add_row("Middlewares", str(middlewares))
    table.add_row("Services", str(services))
    table.add_row("", "")
    table.add_row("Total Python Files", str(len(py_files)))
    table.add_row("Lines of Code", str(total_lines), style="bold yellow")
    
    console.print(table)
