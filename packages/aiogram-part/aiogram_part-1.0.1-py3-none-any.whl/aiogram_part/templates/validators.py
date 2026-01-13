class ValidatorTemplates:
    @staticmethod
    def get_template(name: str, validator_type: str) -> str:
        func_name = name.replace("-", "_")
        
        if validator_type == "regex":
            return ValidatorTemplates._regex_template(func_name)
        return ValidatorTemplates._custom_template(func_name)
    
    @staticmethod
    def _regex_template(name: str) -> str:
        return f'''import re
from typing import Optional

def validate_{name}(value: str) -> bool:
    """
    Validate {name} using regex pattern
    """
    pattern = r"^[a-zA-Z0-9]+$"  # Update pattern as needed
    return bool(re.match(pattern, value))

def get_{name}_error() -> str:
    """Return error message for invalid {name}"""
    return "Invalid {name} format"
'''
    
    @staticmethod
    def _custom_template(name: str) -> str:
        return f'''from typing import Optional

def validate_{name}(value: str) -> bool:
    """
    Custom validation logic for {name}
    """
    # Add your validation logic here
    return len(value) > 0

def get_{name}_error() -> str:
    """Return error message for invalid {name}"""
    return "Invalid {name}"
'''
