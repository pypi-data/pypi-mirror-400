from rich.console import Console

console = Console()

def log_success(message: str):
    console.print(f"✅ {message}", style="bold green")

def log_error(message: str):
    console.print(f"❌ {message}", style="bold red")

def log_info(message: str):
    console.print(f"ℹ️  {message}", style="bold blue")

def log_warning(message: str):
    console.print(f"⚠️  {message}", style="bold yellow")
