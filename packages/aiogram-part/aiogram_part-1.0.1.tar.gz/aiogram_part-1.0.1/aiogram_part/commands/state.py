from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success
from aiogram_part.templates.states import StateTemplates

def execute(name: str):
    base_path = Path.cwd()
    state_path = base_path / "states" / f"{name.lower()}.py"
    
    template = StateTemplates.get_template(name)
    FileManager.create_file(state_path, template)
    
    log_success(f"State created: {state_path.relative_to(base_path)}")
