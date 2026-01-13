from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success
from aiogram_part.templates.tests import TestTemplates

def execute(test_type: str, name: str):
    base_path = Path.cwd()
    
    if test_type == "handler":
        test_path = base_path / "tests" / "handlers" / f"test_{name}.py"
    elif test_type == "service":
        test_path = base_path / "tests" / "services" / f"test_{name}.py"
    else:
        test_path = base_path / "tests" / f"test_{name}.py"
    
    template = TestTemplates.get_template(test_type, name)
    FileManager.create_file(test_path, template)
    
    log_success(f"Test created: {test_path.relative_to(base_path)}")
