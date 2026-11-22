from aiogram .filters import Filter
from aiogram .types import Message ,CallbackQuery
from config import config
class InMainGroups (Filter ):
    async def __call__ (self ,event :Message |CallbackQuery )->bool :
        if isinstance (event ,CallbackQuery ):
            if not event .message :
                return False
            chat_id =event .message .chat .id
        else :
            chat_id =event .chat .id
        return config .groups .is_main_group (chat_id )