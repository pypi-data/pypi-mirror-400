from pathlib import Path
from typing import Union

class FileManager:
    @staticmethod
    def create_directory(path: Union[str, Path]):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def create_file(path: Union[str, Path], content: str):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    @staticmethod
    def update_init_file(path: Path, module_name: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if not path.exists():
            content = f'''from aiogram import Router
from .{module_name} import router as {module_name}_router

router = Router()
router.include_router({module_name}_router)
'''
            path.write_text(content)
        else:
            content = path.read_text()
            if f"from .{module_name} import" not in content:
                import_line = f"from .{module_name} import router as {module_name}_router\n"
                include_line = f"router.include_router({module_name}_router)\n"
                
                if "router = Router()" in content:
                    parts = content.split("router = Router()")
                    content = parts[0] + import_line + "router = Router()\n" + include_line + parts[1]
                else:
                    content += f"\n{import_line}{include_line}"
                
                path.write_text(content)
    
    @staticmethod
    def update_parent_init(path: Path, child_module: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if not path.exists():
            content = f'''from aiogram import Router
from .{child_module} import router as {child_module}_router

router = Router()
router.include_router({child_module}_router)
'''
            path.write_text(content)
        else:
            content = path.read_text()
            if f"from .{child_module} import" not in content:
                import_line = f"from .{child_module} import router as {child_module}_router\n"
                include_line = f"router.include_router({child_module}_router)\n"
                
                if "router = Router()" in content:
                    parts = content.split("router = Router()")
                    content = parts[0] + import_line + "router = Router()\n" + include_line + parts[1]
                else:
                    content += f"\n{import_line}{include_line}"
                
                path.write_text(content)
    
    @staticmethod
    def update_models_init(path: Path, model_name: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        
        class_name = model_name.capitalize()
        import_line = f"from .{model_name} import {class_name}\n"
        
        if not path.exists():
            path.write_text(import_line)
        else:
            content = path.read_text()
            if import_line not in content:
                path.write_text(content + import_line)
    
    @staticmethod
    def update_filter_init(path: Path, module_name: str, class_name: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        
        import_line = f"from .{module_name} import {class_name}\n"
        
        if not path.exists():
            path.write_text(import_line)
        else:
            content = path.read_text()
            if import_line not in content:
                path.write_text(content + import_line)
    
    @staticmethod
    def update_middleware_init(path: Path, module_name: str, class_name: str, types: tuple = None):
        path.parent.mkdir(parents=True, exist_ok=True)
        
        import_line = f"from .{module_name} import {class_name}\n"
        
        type_mapping = {
            "message": "message",
            "edited_message": "edited_message",
            "channel_post": "channel_post",
            "edited_channel_post": "edited_channel_post",
            "callback_query": "callback_query",
            "inline_query": "inline_query",
            "chosen_inline_result": "chosen_inline_result",
            "shipping_query": "shipping_query",
            "pre_checkout_query": "pre_checkout_query",
            "poll": "poll",
            "poll_answer": "poll_answer",
            "my_chat_member": "my_chat_member",
            "chat_member": "chat_member",
            "chat_join_request": "chat_join_request",
        }
        
        if not types or "all" in types:
            register_lines = [
                f"    dp.message.middleware({class_name}())",
                f"    dp.callback_query.middleware({class_name}())",
            ]
        else:
            register_lines = []
            for t in types:
                attr_name = type_mapping.get(t)
                if attr_name:
                    register_lines.append(f"    dp.{attr_name}.middleware({class_name}())")
        
        if not path.exists():
            content = f'''from aiogram import Dispatcher
{import_line}
def setup_middlewares(dp: Dispatcher):
{chr(10).join(register_lines)}
'''
            path.write_text(content)
        else:
            content = path.read_text()
            if import_line not in content:
                lines = content.split("\n")
                import_section = []
                rest = []
                in_imports = True
                
                for line in lines:
                    if in_imports and (line.startswith("from") or line.startswith("import") or not line.strip()):
                        import_section.append(line)
                    else:
                        in_imports = False
                        rest.append(line)
                
                import_section.append(import_line.strip())
                
                for reg_line in register_lines:
                    if reg_line.strip() not in content:
                        rest.insert(-1, reg_line)
                
                path.write_text("\n".join(import_section) + "\n" + "\n".join(rest))
