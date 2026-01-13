from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success
from aiogram_part.templates.models import ModelTemplates

def execute(name: str, with_crud: bool):
    base_path = Path.cwd()
    
    model_path = base_path / "database" / "models" / f"{name.lower()}.py"
    model_template = ModelTemplates.get_model_template(name)
    FileManager.create_file(model_path, model_template)
    
    if with_crud:
        crud_path = base_path / "database" / "crud" / f"{name.lower()}.py"
        crud_template = ModelTemplates.get_crud_template(name)
        FileManager.create_file(crud_path, crud_template)
        log_success(f"CRUD created: {crud_path.relative_to(base_path)}")
    
    models_init = base_path / "database" / "models" / "__init__.py"
    FileManager.update_models_init(models_init, name.lower())
    
    log_success(f"Model created: {model_path.relative_to(base_path)}")
