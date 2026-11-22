from aiogram import Dispatcher
from .import exceptions
from .import admin_actions
from .import user_actions
from .import personal_actions
from .import callbacks
from .import group_events
def register_all_handlers (dp :Dispatcher )->None :
    dp .include_router (exceptions .router )
    dp .include_router (admin_actions .router )
    dp .include_router (user_actions .router )
    dp .include_router (callbacks .router )
    dp .include_router (personal_actions .router )
    dp .include_router (group_events .router )
__all__ =["register_all_handlers"]