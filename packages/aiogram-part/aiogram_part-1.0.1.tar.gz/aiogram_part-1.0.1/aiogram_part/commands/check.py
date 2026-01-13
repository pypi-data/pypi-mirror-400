from pathlib import Path
import sys
from aiogram_part.utils.logger import log_success, log_error, log_info, log_warning

def execute(fix: bool = False):
    """Check project environment and configuration"""
    base_path = Path.cwd()
    issues = []
    
    log_info("Checking project environment...")
    
    # Check .env file
    env_file = base_path / ".env"
    env_example = base_path / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            log_warning(".env file not found")
            if fix:
                import shutil
                shutil.copy(env_example, env_file)
                log_success("Created .env from .env.example")
            else:
                issues.append("Missing .env file (use --fix to create)")
        else:
            issues.append("Missing .env and .env.example files")
    else:
        log_success(".env file exists")
    
    # Check requirements.txt
    req_file = base_path / "requirements.txt"
    if not req_file.exists():
        issues.append("Missing requirements.txt")
    else:
        log_success("requirements.txt exists")
        
        # Check if dependencies are installed
        try:
            import aiogram
            log_success("aiogram installed")
        except ImportError:
            log_warning("aiogram not installed")
            issues.append("aiogram not installed (run: pip install -r requirements.txt)")
    
    # Check database directory
    if (base_path / "database").exists():
        log_success("Database structure exists")
        
        # Check if migrations exist
        migrations_dir = base_path / "database" / "migrations"
        if migrations_dir.exists() and list(migrations_dir.glob("*.py")):
            log_success("Database migrations found")
        else:
            log_warning("No database migrations found")
            issues.append("No migrations (run: aiogram-part database migrate)")
    
    # Check handlers
    handlers_dir = base_path / "handlers"
    if handlers_dir.exists():
        handler_files = list(handlers_dir.rglob("*.py"))
        handler_count = len([f for f in handler_files if f.name != "__init__.py"])
        log_info(f"Found {handler_count} handler(s)")
    
    # Summary
    print("\n" + "="*50)
    if issues:
        log_error(f"Found {len(issues)} issue(s):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        if not fix:
            log_info("\nRun with --fix to auto-fix some issues")
        sys.exit(1)
    else:
        log_success("✅ All checks passed!")
