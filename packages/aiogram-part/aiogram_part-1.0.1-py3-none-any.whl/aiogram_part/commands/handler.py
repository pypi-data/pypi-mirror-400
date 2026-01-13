from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success
from aiogram_part.templates.handlers import HandlerTemplates

def execute(scope: str, handler_type: str, name: str):
    base_path = Path.cwd()
    handler_path = base_path / "handlers" / f"{scope}s" / f"{handler_type}s" / f"{name}.py"
    
    template = HandlerTemplates.get_template(scope, handler_type, name)
    FileManager.create_file(handler_path, template)
    
    init_path = handler_path.parent / "__init__.py"
    FileManager.update_init_file(init_path, name)
    
    parent_init = handler_path.parent.parent / "__init__.py"
    FileManager.update_parent_init(parent_init, f"{handler_type}s")
    
    log_success(f"Handler created: {handler_path.relative_to(base_path)}")
