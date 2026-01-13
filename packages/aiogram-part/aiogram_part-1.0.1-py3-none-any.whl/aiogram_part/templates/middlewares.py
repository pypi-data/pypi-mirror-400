class MiddlewareTemplates:
    @staticmethod
    def get_class_name(name: str) -> str:
        return name.replace(".py", "").replace("_", " ").title().replace(" ", "") + "Middleware"
    
    @staticmethod
    def get_template(name: str, types: tuple = None) -> str:
        class_name = MiddlewareTemplates.get_class_name(name)
        
        type_map = {
            "message": "Message",
            "edited_message": "Message",
            "channel_post": "Message",
            "edited_channel_post": "Message",
            "callback_query": "CallbackQuery",
            "inline_query": "InlineQuery",
            "chosen_inline_result": "ChosenInlineResult",
            "shipping_query": "ShippingQuery",
            "pre_checkout_query": "PreCheckoutQuery",
            "poll": "Poll",
            "poll_answer": "PollAnswer",
            "my_chat_member": "ChatMemberUpdated",
            "chat_member": "ChatMemberUpdated",
            "chat_join_request": "ChatJoinRequest",
        }
        
        if not types or "all" in types:
            event_type = "TelegramObject"
            import_line = "from aiogram.types import TelegramObject"
        elif len(types) == 1:
            event_type = type_map.get(types[0], "TelegramObject")
            if event_type == "TelegramObject":
                import_line = "from aiogram.types import TelegramObject"
            else:
                import_line = f"from aiogram.types import {event_type}"
        else:
            event_types = list(set([type_map.get(t, "TelegramObject") for t in types]))
            if len(event_types) == 1:
                event_type = event_types[0]
                import_line = f"from aiogram.types import {event_type}"
            else:
                event_type = "TelegramObject"
                import_line = "from aiogram.types import TelegramObject"
        
        return f'''from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
{import_line}

class {class_name}(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[{event_type}, Dict[str, Any]], Awaitable[Any]],
        event: {event_type},
        data: Dict[str, Any]
    ) -> Any:
        result = await handler(event, data)
        return result
'''
