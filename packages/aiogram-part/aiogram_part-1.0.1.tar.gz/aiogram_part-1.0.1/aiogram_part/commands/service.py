from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success
from aiogram_part.templates.services import ServiceTemplates

def execute(scope: str, name: str):
    base_path = Path.cwd()
    scope_folder = f"{scope}s" if scope != "common" else scope
    service_path = base_path / "services" / scope_folder / f"{name}.py"
    
    template = ServiceTemplates.get_template(name)
    FileManager.create_file(service_path, template)
    
    log_success(f"Service created: {service_path.relative_to(base_path)}")
