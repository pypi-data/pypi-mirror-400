class TestTemplates:
    @staticmethod
    def get_template(test_type: str, name: str) -> str:
        if test_type == "handler":
            return TestTemplates._handler_test(name)
        elif test_type == "service":
            return TestTemplates._service_test(name)
        return TestTemplates._generic_test(name)
    
    @staticmethod
    def _handler_test(name: str) -> str:
        return f'''import pytest
from aiogram.types import Message
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_{name}_handler():
    """Test {name} handler"""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    
    # TODO: Import and test your handler
    # from handlers.users.commands.{name} import cmd_{name}
    # await cmd_{name}(message)
    
    # Assert
    # message.answer.assert_called_once()
    pass
'''
    
    @staticmethod
    def _service_test(name: str) -> str:
        return f'''import pytest

@pytest.mark.asyncio
async def test_{name}_service():
    """Test {name} service"""
    # TODO: Import and test your service
    # from services.{name} import {name.capitalize()}Service
    
    # result = await {name.capitalize()}Service.process()
    # assert result is not None
    pass
'''
    
    @staticmethod
    def _generic_test(name: str) -> str:
        return f'''import pytest

def test_{name}():
    """Test {name}"""
    # TODO: Add your tests here
    pass
'''
