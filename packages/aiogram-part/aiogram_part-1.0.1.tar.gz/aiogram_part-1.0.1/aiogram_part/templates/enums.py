class EnumTemplates:
    @staticmethod
    def get_template(name: str, values: tuple) -> str:
        class_name = ''.join(word.capitalize() for word in name.split('_'))
        
        enum_values = []
        for value in values:
            value_upper = value.upper().replace('-', '_')
            enum_values.append(f'    {value_upper} = "{value}"')
        
        enum_items = '\n'.join(enum_values)
        
        return f'''from enum import Enum

class {class_name}(str, Enum):
    """Enum for {name}"""
{enum_items}
'''
