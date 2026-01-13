from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success, log_info
from aiogram_part.templates.middlewares import MiddlewareTemplates

def execute(scope: str, name: str, types: tuple = None):
    base_path = Path.cwd()
    scope_folder = f"{scope}s" if scope != "common" else scope
    middleware_path = base_path / "middlewares" / scope_folder / f"{name}.py"
    
    if not types:
        types = ("all",)
    
    template = MiddlewareTemplates.get_template(name, types)
    FileManager.create_file(middleware_path, template)
    
    init_path = middleware_path.parent / "__init__.py"
    class_name = MiddlewareTemplates.get_class_name(name)
    FileManager.update_middleware_init(init_path, name, class_name, types)
    
    log_success(f"Middleware created: {middleware_path.relative_to(base_path)}")
    
    if types and types != ("all",):
        types_str = ", ".join(types)
        log_info(f"Middleware types: {types_str}")
        log_info(f"Register in bootstrap.py:")
        log_info(f"  dp.{types[0]}.middleware({class_name}())")  # First type as example
