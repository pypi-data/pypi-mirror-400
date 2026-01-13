from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success
from aiogram_part.templates.enums import EnumTemplates

def execute(name: str, values: tuple):
    base_path = Path.cwd()
    
    # Check if database exists
    if not (base_path / "database").exists():
        from aiogram_part.utils.logger import log_error
        log_error("Database directory not found. Initialize project with --with-db first.")
        return
    
    enum_path = base_path / "database" / "enums" / f"{name.lower()}.py"
    template = EnumTemplates.get_template(name, values)
    
    FileManager.create_file(enum_path, template)
    log_success(f"Enum created: {enum_path.relative_to(base_path)}")
