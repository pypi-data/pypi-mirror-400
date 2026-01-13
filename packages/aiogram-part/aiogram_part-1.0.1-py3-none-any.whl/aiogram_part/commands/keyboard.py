from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success
from aiogram_part.templates.keyboards import KeyboardTemplates

def execute(scope: str, name: str, keyboard_type: str, str_params: tuple, int_params: tuple):
    base_path = Path.cwd()
    # Fix: use correct scope folder name (user/admin/common, not users/admins/commons)
    scope_folder = f"{scope}s" if scope in ["user", "admin"] else scope
    keyboard_path = base_path / "keyboards" / scope_folder / f"{name}.py"
    
    template = KeyboardTemplates.get_template(name, keyboard_type, str_params, int_params)
    
    FileManager.create_file(keyboard_path, template)
    
    log_success(f"Keyboard class created: {keyboard_path.relative_to(base_path)}")
