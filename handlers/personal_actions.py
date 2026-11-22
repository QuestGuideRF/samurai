import random
import sys
import uuid
from datetime import datetime ,timedelta
import psutil
from aiogram import Router ,F
from aiogram .filters import Command
from aiogram .types import Message ,InlineKeyboardMarkup ,InlineKeyboardButton
from config import config
from filters import IsOwnerFilter ,IsAdminFilter ,InMainGroups
from services .profanity import check_for_profanity
from utils import remove_prefix ,MemberStatus
sys .path .append ("./libs")
router =Router (name ="personal_actions")
pending_messages :dict [str ,tuple [str ,datetime ]]={}
def _cleanup_old_messages ()->None :
    now =datetime .now ()
    expired =[k for k ,(_ ,ts )in pending_messages .items ()if now -ts >timedelta (minutes =5 )]
    for k in expired :
        del pending_messages [k ]
async def _build_chat_keyboard (bot ,msg_id :str )->InlineKeyboardMarkup :
    buttons =[]
    for chat_id in config .groups .main :
        try :
            chat =await bot .get_chat (chat_id )
            chat_name =chat .title or f"Chat {chat_id }"
        except Exception :
            chat_name =f"Chat {chat_id }"
        buttons .append ([InlineKeyboardButton (
        text =f"📤 {chat_name }",
        callback_data =f"msg_{msg_id }_{chat_id }"
        )])
    buttons .append ([InlineKeyboardButton (
    text ="📢 Отправить во все чаты",
    callback_data =f"msg_{msg_id }_all"
    )])
    buttons .append ([InlineKeyboardButton (
    text ="❌ Отмена",
    callback_data =f"msg_{msg_id }_cancel"
    )])
    return InlineKeyboardMarkup (inline_keyboard =buttons )
@router .message (
IsOwnerFilter (),
Command ("msg",prefix ="!/")
)
async def cmd_message_from_bot (message :Message )->None :
    _cleanup_old_messages ()
    text =remove_prefix (message .text ,"!сообщение").strip ()
    if not text :
        await message .reply (
        "<b>Использование:</b>\n"
        "<code>!msg текст сообщения</code>\n\n"
        "После ввода команды появится меню выбора чата."
        )
        return
    msg_id =uuid .uuid4 ().hex [:8 ]
    pending_messages [msg_id ]=(text ,datetime .now ())
    keyboard =await _build_chat_keyboard (message .bot ,msg_id )
    await message .reply (
    f"<b>Сообщение:</b>\n<i>{text [:500 ]}{'...'if len (text )>500 else ''}</i>\n\n"
    f"Выберите куда отправить:",
    reply_markup =keyboard
    )
@router .message (
IsOwnerFilter (),
Command ("log",prefix ="!/")
)
async def cmd_write_log_bot (message :Message )->None :
    from utils import write_log
    text =remove_prefix (message .text ,"!бревно ").strip ()
    if text :
        await write_log (message .bot ,text ,"test")
@router .message (
IsOwnerFilter (),
Command ("reload",prefix ="!/")
)
async def cmd_reload_announcements (message :Message )->None :
    from services .announcements import reload_announcements
    count =reload_announcements ()
    await message .reply (f"✅ Перезагружено {count } объявлений.")
@router .message (
IsOwnerFilter (),
Command ("chatid",prefix ="!/")
)
async def cmd_chat_id (message :Message )->None :
    chat =message .chat
    chat_type =chat .type
    chat_title =chat .title or chat .full_name or "Private"
    info =(
    f"<b>Chat ID:</b> <code>{chat .id }</code>\n"
    f"<b>Type:</b> {chat_type }\n"
    f"<b>Title:</b> {chat_title }"
    )
    print (f"\n{'='*40 }")
    print (f"CHAT ID: {chat .id }")
    print (f"Type: {chat_type }")
    print (f"Title: {chat_title }")
    print (f"{'='*40 }\n")
    await message .reply (info )
@router .message (
InMainGroups (),
IsAdminFilter (),
Command ("ping",prefix ="!")
)
async def cmd_ping_bot (message :Message )->None :
    user =await message .bot .get_chat_member (message .chat .id ,message .from_user .id )
    if user .status not in MemberStatus .admin_statuses ():
        return
    ram =psutil .virtual_memory ()
    cpu_freq =psutil .cpu_freq ().current if psutil .cpu_freq ()else 0
    reply =f"<b>{random .choice (['👊 Самурай на месте!','🫰 Нужно больше золота','🫡 Тута я, бож :3','✊ Железо говн@, но я держусь!'])}</b>\n\n"
    reply +="<b>CPU:</b> <i>{} ядер, {:.0f} MHz, загрузка {}%</i>\n".format (
    psutil .cpu_count (logical =True ),
    cpu_freq ,
    psutil .cpu_percent (interval =1 )
    )
    reply +="<b>RAM:</b> <i>{} МБ / {} МБ ({}%)</i>\n".format (
    ram .used //(1024 **2 ),
    ram .total //(1024 **2 ),
    ram .percent
    )
    reply +="<b>GPU:</b> <i>N/A</i>\n"
    disk =psutil .disk_usage ('/')
    disk_total_gb =disk .total /(1024 **3 )
    disk_used_gb =disk .used /(1024 **3 )
    reply +="<b>SSD:</b> <i>{:.2f} ГБ из {:.2f} ГБ использовано ({}% занято)</i>\n".format (
    disk_used_gb ,
    disk_total_gb ,
    int (disk .percent )
    )
    reply +="<b>Расположение сервера:</b> <i>Марс</i>\n"
    reply +=f"\n<b>Версия бота:</b> <i>{config .bot .version } codename «<b>{config .bot .version_codename }</b>»</i>"
    await message .reply (reply )
@router .message (
InMainGroups (),
IsAdminFilter (),
Command ("prof","мат",prefix ="!")
)
async def cmd_profanity_check (message :Message )->None :
    user =await message .bot .get_chat_member (message .chat .id ,message .from_user .id )
    if user .status not in MemberStatus .admin_statuses ():
        return
    text =remove_prefix (message .text ,"!проф ").strip ()
    if not text :
        text =remove_prefix (message .text ,"!мат ").strip ()
    if not text :
        await message .reply ("Укажите текст для проверки после команды.")
        return
    is_profanity_ru ,word_ru ,line_info_ru =check_for_profanity (text ,"ru")
    is_profanity_en ,word_en ,line_info_en =check_for_profanity (text ,"en")
    if is_profanity_ru or is_profanity_en :
        word =word_ru if is_profanity_ru else word_en
        pattern =line_info_ru [5 ][0 ]if is_profanity_ru else line_info_en [5 ][0 ]
        lang ="ru"if is_profanity_ru else "en"
        log_msg =f"❌ Profanity detected.\n\n"
        log_msg +=text .replace (word ,f'<u><b>{word }</b></u>')
        log_msg +=f"\nПаттерн: {pattern }"
        log_msg +=f"\nЯзык: {lang }"
        await message .reply (log_msg )
    else :
        await message .reply ("✅ Ненормативная лексика не обнаружена.")
@router .message (
F .chat .type =="private",
IsOwnerFilter (),
Command ("prof","мат",prefix ="!")
)
async def cmd_profanity_check_private (message :Message )->None :
    text =remove_prefix (message .text ,"!проф ").strip ()
    if not text :
        text =remove_prefix (message .text ,"!мат ").strip ()
    if not text :
        await message .reply ("Укажите текст для проверки после команды.")
        return
    is_profanity_ru ,word_ru ,line_info_ru =check_for_profanity (text ,"ru")
    is_profanity_en ,word_en ,line_info_en =check_for_profanity (text ,"en")
    if is_profanity_ru or is_profanity_en :
        word =word_ru if is_profanity_ru else word_en
        pattern =line_info_ru [5 ][0 ]if is_profanity_ru else line_info_en [5 ][0 ]
        lang ="ru"if is_profanity_ru else "en"
        log_msg =f"❌ Profanity detected.\n\n"
        log_msg +=text .replace (word ,f'<u><b>{word }</b></u>')
        log_msg +=f"\nПаттерн: {pattern }"
        log_msg +=f"\nЯзык: {lang }"
        await message .reply (log_msg )
    else :
        await message .reply ("✅ Ненормативная лексика не обнаружена.")