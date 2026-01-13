from pathlib import Path
import subprocess
import sys
from aiogram_part.utils.logger import log_success, log_error, log_info

def migrate(force: bool = False):
    """Initialize database and create first migration"""
    base_path = Path.cwd()
    
    # Check if database/ exists
    if not (base_path / "database").exists():
        log_error("Database directory not found. Initialize project with --with-db first.")
        sys.exit(1)
    
    try:
        # Check if already initialized
        pyproject_path = base_path / "pyproject.toml"
        
        if not pyproject_path.exists() or force:
            log_info("Initializing Aerich...")
            result = subprocess.run(
                ["aerich", "init", "-t", "core.configs.TORTOISE_CONFIG"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0 and not force:
                log_error(f"Aerich init failed: {result.stderr}")
                sys.exit(1)
        
        log_info("Creating initial migration...")
        result = subprocess.run(
            ["aerich", "init-db"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log_success("Database migrated successfully!")
            log_info("Migration files created in database/migrations/")
        else:
            if "already exists" in result.stderr.lower():
                log_info("Database already initialized")
            else:
                log_error(f"Migration failed: {result.stderr}")
                sys.exit(1)
                
    except FileNotFoundError:
        log_error("Aerich not found. Install: pip install aerich")
        sys.exit(1)

def update(name: str = "auto_update"):
    """Create new migration and apply it"""
    base_path = Path.cwd()
    
    if not (base_path / "database").exists():
        log_error("Database directory not found.")
        sys.exit(1)
    
    try:
        log_info(f"Creating migration: {name}")
        result = subprocess.run(
            ["aerich", "migrate", "--name", name],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            if "no changes detected" in result.stderr.lower() or "no changes detected" in result.stdout.lower():
                log_info("No changes detected in models")
            else:
                log_error(f"Migration creation failed: {result.stderr}")
                sys.exit(1)
        else:
            log_success(f"Migration '{name}' created")
        
        log_info("Applying migrations...")
        result = subprocess.run(
            ["aerich", "upgrade"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log_success("Database updated successfully!")
        else:
            log_error(f"Upgrade failed: {result.stderr}")
            sys.exit(1)
            
    except FileNotFoundError:
        log_error("Aerich not found. Install: pip install aerich")
        sys.exit(1)

def upgrade():
    """Apply pending migrations"""
    try:
        log_info("Applying pending migrations...")
        result = subprocess.run(
            ["aerich", "upgrade"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log_success("Migrations applied successfully!")
        else:
            log_error(f"Upgrade failed: {result.stderr}")
            sys.exit(1)
            
    except FileNotFoundError:
        log_error("Aerich not found. Install: pip install aerich")
        sys.exit(1)

def downgrade(version: int = -1):
    """Rollback migrations"""
    try:
        log_info(f"Rolling back {abs(version)} migration(s)...")
        result = subprocess.run(
            ["aerich", "downgrade", str(version)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log_success("Rollback successful!")
        else:
            log_error(f"Downgrade failed: {result.stderr}")
            sys.exit(1)
            
    except FileNotFoundError:
        log_error("Aerich not found. Install: pip install aerich")
        sys.exit(1)

def history():
    """Show migration history"""
    try:
        result = subprocess.run(
            ["aerich", "history"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            log_error(f"History failed: {result.stderr}")
            sys.exit(1)
            
    except FileNotFoundError:
        log_error("Aerich not found. Install: pip install aerich")
        sys.exit(1)

def heads():
    """Show current migration heads"""
    try:
        result = subprocess.run(
            ["aerich", "heads"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            log_error(f"Heads failed: {result.stderr}")
            sys.exit(1)
            
    except FileNotFoundError:
        log_error("Aerich not found. Install: pip install aerich")
        sys.exit(1)

def reset():
    """Drop all tables and reinitialize (DANGEROUS!)"""
    import click
    
    if not click.confirm("⚠️  This will DROP ALL TABLES! Continue?"):
        log_info("Reset cancelled")
        return
    
    try:
        log_info("Dropping all tables...")
        
        # Delete pyproject.toml aerich config
        pyproject_path = Path.cwd() / "pyproject.toml"
        if pyproject_path.exists():
            pyproject_path.unlink()
        
        # Delete migrations
        migrations_path = Path.cwd() / "database" / "migrations"
        if migrations_path.exists():
            import shutil
            shutil.rmtree(migrations_path)
            migrations_path.mkdir()
        
        log_info("Re-initializing database...")
        migrate(force=True)
        
        log_success("Database reset complete!")
        
    except Exception as e:
        log_error(f"Reset failed: {e}")
        sys.exit(1)

def generate_migration(name: str):
    """Generate migration without applying"""
    try:
        log_info(f"Generating migration: {name}")
        result = subprocess.run(
            ["aerich", "migrate", "--name", name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log_success(f"Migration '{name}' generated")
            log_info("Run 'aiogram-part database upgrade' to apply")
        else:
            if "no changes detected" in result.stderr.lower() or "no changes detected" in result.stdout.lower():
                log_info("No changes detected in models")
            else:
                log_error(f"Migration generation failed: {result.stderr}")
                sys.exit(1)
                
    except FileNotFoundError:
        log_error("Aerich not found. Install: pip install aerich")
        sys.exit(1)

def inspect():
    """Show current database schema"""
    try:
        log_info("Current database schema:")
        result = subprocess.run(
            ["aerich", "inspectdb"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            log_info("Schema inspection not available in current Aerich version")
            log_info("Use: aerich heads - to see current state")
            heads()
            
    except FileNotFoundError:
        log_error("Aerich not found. Install: pip install aerich")
        sys.exit(1)
