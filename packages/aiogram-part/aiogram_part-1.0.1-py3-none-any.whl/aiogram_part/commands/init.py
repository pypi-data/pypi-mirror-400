from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success, log_info
from aiogram_part.templates.project import ProjectStructure

def execute(with_db: bool, db_type: str = "sqlite"):
    base_path = Path.cwd()
    
    structure = ProjectStructure.get_full_structure(with_db, db_type)
    
    for directory in structure["directories"]:
        FileManager.create_directory(base_path / directory)
    
    for file_path, content in structure["files"].items():
        FileManager.create_file(base_path / file_path, content)
    
    log_success("Project initialized successfully!")
    if with_db:
        log_info(f"Database: {db_type.upper()}")
    log_info(f"Next steps:\n  1. cd {base_path.name}\n  2. Create .env file\n  3. pip install -r requirements.txt")
