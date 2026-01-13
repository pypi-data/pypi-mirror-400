class ServiceTemplates:
    @staticmethod
    def get_template(name: str) -> str:
        class_name = ''.join(word.capitalize() for word in name.split('_')) + 'Service'
        
        return f'''from typing import Optional, List

class {class_name}:
    """
    Business logic service for {name}
    Handles operations beyond simple CRUD
    """
    
    @staticmethod
    async def process():
        """Process business logic"""
        pass
    
    @staticmethod
    async def validate():
        """Validate data"""
        pass
'''
