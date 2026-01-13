from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success
from aiogram_part.templates.validators import ValidatorTemplates

def execute(name: str, validator_type: str):
    base_path = Path.cwd()
    validator_path = base_path / "utils" / "validators" / f"{name}.py"
    
    template = ValidatorTemplates.get_template(name, validator_type)
    FileManager.create_file(validator_path, template)
    
    log_success(f"Validator created: {validator_path.relative_to(base_path)}")
