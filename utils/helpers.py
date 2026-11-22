import datetime
from typing import Optional
import psutil
from aiogram .types import Message
from aiogram .enums import ContentType
from config import config
from utils .localization import get_string
def get_message_text (message :Message )->Optional [str ]:
    if message .content_type ==ContentType .TEXT :
        return message .text
    elif message .content_type in (
    ContentType .PHOTO ,
    ContentType .DOCUMENT ,
    ContentType .VIDEO ,
    ContentType .ANIMATION ,
    ContentType .AUDIO ,
    ContentType .VOICE ,
    ContentType .VIDEO_NOTE
    ):
        return message .caption
    return None
def user_mention (from_user )->str :
    _s =from_user .full_name
    if from_user .full_name !=from_user .mention_html ():
        _s +=" ("+from_user .mention_html ()+")"
    else :
        _s +=f' (<a href="{from_user .url }">id{from_user .id }</a>)'
    return _s
def user_mention_by_id (user_id :int )->str :
    return f'<a href="tg://user?id={user_id }">{user_id }</a>'
def generate_log_message (
message :str ,
log_type :str ="default",
chat_title :Optional [str ]=None
)->str :
    now =datetime .datetime .now ()
    current_time =now .strftime ("%H:%M:%S")
    log_message =f"🕥 <i>{current_time }</i> "
    if chat_title :
        log_message +=f"[<b>{chat_title }</b>] "
    log_message +=f"<b>[{log_type .upper ()}]</b> "
    log_message +=message
    return log_message
async def write_log (
bot ,
message :str ,
log_type :str ="default",
chat_title :Optional [str ]=None
):
    return await bot .send_message (
    config .groups .logs ,
    generate_log_message (message ,log_type ,chat_title )
    )
def get_restriction_time (string :str )->Optional [int ]:
    if len (string )<2 :
        return None
    letter =string [-1 ]
    try :
        number =int (string [:-1 ])
    except (TypeError ,ValueError ):
        return None
    else :
        if letter =="m":
            return 60 *number
        elif letter =="h":
            return 3600 *number
        elif letter =="d":
            return 86400 *number
        else :
            return None
def get_report_comment (
message_date :datetime .datetime ,
message_id :int ,
chat_id :int ,
report_message :Optional [str ]=None ,
chat_title :Optional [str ]=None ,
reporter =None
)->str :
    header =""
    if chat_title :
        header =f"🟢 <b>{chat_title }</b>\n\n"
    msg =header +get_string (
    "report_message",
    date =message_date .strftime (get_string ("report_date_format")),
    chat_id =get_url_chat_id (chat_id ),
    msg_id =message_id
    )
    if reporter :
        msg +=get_string ("report_from",reporter =user_mention (reporter ))
    if report_message :
        msg +=get_string ("report_note",note =report_message )
    return msg
def get_url_chat_id (chat_id :int )->int :
    return abs (chat_id +1_000_000_000_000 )
def remove_prefix (text :str ,prefix :str )->str :
    if text .startswith (prefix ):
        return text [len (prefix ):]
    return text
def get_cpu_freq ():
    try :
        freq =psutil .cpu_freq ()
        return freq .max if freq and freq .max >0 else "N/A"
    except Exception :
        return "N/A"