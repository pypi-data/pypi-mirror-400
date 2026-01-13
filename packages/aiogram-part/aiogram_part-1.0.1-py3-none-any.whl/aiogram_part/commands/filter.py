from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success
from aiogram_part.templates.filters import FilterTemplates

def execute(scope: str, filter_type: str, name: str, str_params: tuple, int_params: tuple):
    base_path = Path.cwd()
    
    # filters/users/common or filters/users/callback
    scope_folder = f"{scope}s" if scope != "common" else scope
    filter_path = base_path / "filters" / scope_folder / filter_type / f"{name.replace('.py', '')}.py"
    template = FilterTemplates.get_template(filter_type, name, str_params, int_params)
    
    FileManager.create_file(filter_path, template)
    
    init_path = filter_path.parent / "__init__.py"
    class_name = FilterTemplates.get_class_name(filter_type, name)
    FileManager.update_filter_init(init_path, name.replace('.py', ''), class_name)
    
    log_success(f"Filter created: {filter_path.relative_to(base_path)}")
