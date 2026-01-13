class HandlerTemplates:
    @staticmethod
    def get_template(scope: str, handler_type: str, name: str) -> str:
        templates = {
            "command": HandlerTemplates._command_template,
            "message": HandlerTemplates._message_template,
            "callback": HandlerTemplates._callback_template,
        }
        return templates[handler_type](name, scope)
    
    @staticmethod
    def _command_template(name: str, scope: str) -> str:
        return f'''from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("{name}"))
async def cmd_{name}(message: Message):
    pass
'''
    
    @staticmethod
    def _message_template(name: str, scope: str) -> str:
        return f'''from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def handle_{name}(message: Message):
    pass
'''
    
    @staticmethod
    def _callback_template(name: str, scope: str) -> str:
        return f'''from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "{name}")
async def callback_{name}(callback: CallbackQuery):
    pass
'''
