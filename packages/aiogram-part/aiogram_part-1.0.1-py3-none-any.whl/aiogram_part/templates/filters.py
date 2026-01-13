class FilterTemplates:
    @staticmethod
    def get_class_name(filter_type: str, name: str) -> str:
        base_name = name.replace(".py", "").replace("_", " ").title().replace(" ", "")
        if filter_type == "common":
            return base_name if base_name.startswith("Is") else f"Is{base_name}"
        return f"{base_name}Callback"
    
    @staticmethod
    def get_template(filter_type: str, name: str, str_params: tuple, int_params: tuple) -> str:
        if filter_type == "common":
            return FilterTemplates._common_template(name)
        return FilterTemplates._callback_template(name, str_params, int_params)
    
    @staticmethod
    def _common_template(name: str) -> str:
        class_name = FilterTemplates.get_class_name("common", name)
        
        return f'''from aiogram.filters import BaseFilter
from aiogram.types import Message

class {class_name}(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return True
'''
    
    @staticmethod
    def _callback_template(name: str, str_params: tuple, int_params: tuple) -> str:
        class_name = FilterTemplates.get_class_name("callback", name)
        prefix = name.replace(".py", "").replace("_callback", "")
        
        fields = []
        for param in str_params:
            fields.append(f"    {param}: str")
        for param in int_params:
            fields.append(f"    {param}: int")
        
        fields_str = "\n".join(fields) if fields else "    pass"
        
        return f'''from aiogram.filters.callback_data import CallbackData

class {class_name}(CallbackData, prefix="{prefix}"):
{fields_str}
'''
