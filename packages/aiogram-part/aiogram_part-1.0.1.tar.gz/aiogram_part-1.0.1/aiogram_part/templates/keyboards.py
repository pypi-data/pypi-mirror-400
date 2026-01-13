class KeyboardTemplates:
    @staticmethod
    def get_template(name: str, keyboard_type: str, str_params: tuple, int_params: tuple) -> str:
        class_name = ''.join(word.capitalize() for word in name.split('_')) + 'Keyboard'
        
        # Build parameters
        params = []
        if str_params:
            params.extend([f"{p}: str" for p in str_params])
        if int_params:
            params.extend([f"{p}: int" for p in int_params])
        
        param_str = ", ".join(params) if params else ""
        
        if keyboard_type == "inline":
            return KeyboardTemplates._inline_class_template(class_name, param_str, str_params, int_params)
        return KeyboardTemplates._reply_class_template(class_name, param_str, str_params, int_params)
    
    @staticmethod
    def _inline_class_template(class_name: str, params: str, str_params: tuple, int_params: tuple) -> str:
        param_usage = ""
        if str_params or int_params:
            param_usage = "\n        # Use parameters: " + ", ".join(list(str_params) + list(int_params))
        
        return f'''from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class {class_name}:
    @staticmethod
    def make({params}) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder(){param_usage}
        # builder.button(text="Button", callback_data="data")
        # builder.adjust(2)  # 2 buttons per row
        return builder.as_markup()
'''
    
    @staticmethod
    def _reply_class_template(class_name: str, params: str, str_params: tuple, int_params: tuple) -> str:
        param_usage = ""
        if str_params or int_params:
            param_usage = "\n        # Use parameters: " + ", ".join(list(str_params) + list(int_params))
        
        return f'''from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class {class_name}:
    @staticmethod
    def make({params}) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder(){param_usage}
        # builder.button(text="Button")
        # builder.adjust(2)  # 2 buttons per row
        return builder.as_markup(resize_keyboard=True)
'''
