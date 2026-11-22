from contextlib import suppress
from datetime import datetime ,timedelta ,timezone
from aiogram import Router ,F
from aiogram .types import CallbackQuery ,ChatPermissions
from aiogram .exceptions import TelegramBadRequest
from config import config
from db .models import Member ,Spam
from services .reports import remove_report
from services .cache import queue_member_update
from utils import get_string ,_random
from handlers .personal_actions import pending_messages
router =Router (name ="callbacks")
@router .callback_query (F .data .startswith ("msg_"))
async def callback_msg_send (call :CallbackQuery )->None :
    if call .from_user .id !=config .bot .owner :
        await call .answer ("⛔ Только для владельца",show_alert =True )
        return
    parts =call .data .split ("_")
    if len (parts )<3 :
        await call .answer ("❌ Ошибка данных",show_alert =True )
        return
    msg_id =parts [1 ]
    target ="_".join (parts [2 :])
    if msg_id not in pending_messages :
        await call .message .edit_text ("❌ Сообщение устарело. Отправьте команду заново.")
        await call .answer ()
        return
    text ,_ =pending_messages [msg_id ]
    if target =="cancel":
        del pending_messages [msg_id ]
        await call .message .edit_text ("❌ Отменено.")
        await call .answer ()
        return
    if target =="all":
        sent =0
        failed =0
        for chat_id in config .groups .main :
            try :
                await call .bot .send_message (chat_id ,text )
                sent +=1
            except Exception :
                failed +=1
        del pending_messages [msg_id ]
        await call .message .edit_text (
        f"✅ <b>Отправлено во все чаты</b>\n\n"
        f"Успешно: {sent }\n"
        f"Ошибок: {failed }"
        )
        await call .answer ("Отправлено!")
    else :
        try :
            chat_id =int (target )
            await call .bot .send_message (chat_id ,text )
            try :
                chat =await call .bot .get_chat (chat_id )
                chat_name =chat .title or f"Chat {chat_id }"
            except Exception :
                chat_name =f"Chat {chat_id }"
            del pending_messages [msg_id ]
            await call .message .edit_text (f"✅ <b>Отправлено в:</b> {chat_name }")
            await call .answer ("Отправлено!")
        except ValueError :
            await call .answer ("❌ Неверный ID чата",show_alert =True )
        except Exception as e :
            await call .answer (f"❌ Ошибка: {str (e )[:100 ]}",show_alert =True )
async def _update_bot_reply (bot ,chat_id :int ,bot_reply_id :int )->None :
    with suppress (TelegramBadRequest ):
        await bot .edit_message_text (
        chat_id =chat_id ,
        message_id =bot_reply_id ,
        text =_random ("report-completed"),
        parse_mode ="HTML"
        )
async def _reward_reporter (reporter_id :int ,points :int )->None :
    await queue_member_update (reporter_id ,reputation_points =points )
@router .callback_query (F .data .startswith ("rdel_"))
async def callback_report_delete (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    reporter_id =int (parts [3 ])
    bot_reply_id =int (parts [4 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    remove_report (chat_id ,message_id )
    await _reward_reporter (reporter_id ,10 )
    await _update_bot_reply (call .bot ,chat_id ,bot_reply_id )
    await call .message .edit_text (
    call .message .text +"\n\n"+get_string ("action_deleted")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("rdelban_"))
async def callback_report_delete_and_ban (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    user_id =int (parts [3 ])
    reporter_id =int (parts [4 ])
    bot_reply_id =int (parts [5 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    await call .bot .ban_chat_member (chat_id =chat_id ,user_id =user_id )
    remove_report (chat_id ,message_id )
    await _reward_reporter (reporter_id ,20 )
    await _update_bot_reply (call .bot ,chat_id ,bot_reply_id )
    await call .message .edit_text (
    call .message .text +"\n\n"+get_string ("action_deleted_banned")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("rmute_"))
async def callback_report_delete_and_mute_24h (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    user_id =int (parts [3 ])
    reporter_id =int (parts [4 ])
    bot_reply_id =int (parts [5 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    await call .bot .restrict_chat_member (
    chat_id =chat_id ,
    user_id =user_id ,
    permissions =ChatPermissions (can_send_messages =False ),
    until_date =datetime .now (timezone .utc )+timedelta (hours =24 )
    )
    remove_report (chat_id ,message_id )
    await _reward_reporter (reporter_id ,10 )
    await _update_bot_reply (call .bot ,chat_id ,bot_reply_id )
    await call .message .edit_text (
    call .message .text +"\n\n"+get_string ("action_deleted_readonly")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("rmute2_"))
async def callback_report_delete_and_mute_7d (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    user_id =int (parts [3 ])
    reporter_id =int (parts [4 ])
    bot_reply_id =int (parts [5 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    await call .bot .restrict_chat_member (
    chat_id =chat_id ,
    user_id =user_id ,
    permissions =ChatPermissions (can_send_messages =False ),
    until_date =datetime .now (timezone .utc )+timedelta (days =7 )
    )
    remove_report (chat_id ,message_id )
    await _reward_reporter (reporter_id ,15 )
    await _update_bot_reply (call .bot ,chat_id ,bot_reply_id )
    await call .message .edit_text (
    call .message .text +"\n\n"+get_string ("action_deleted_readonly2")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("rdismiss_"))
async def callback_report_dismiss (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    bot_reply_id =int (parts [5 ])
    remove_report (chat_id ,message_id )
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,bot_reply_id )
    await call .message .edit_text (
    call .message .text +"\n\n"+get_string ("action_dismissed")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("rdismiss2_"))
async def callback_report_dismiss_mute_reporter_1d (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    reporter_id =int (parts [4 ])
    bot_reply_id =int (parts [5 ])
    remove_report (chat_id ,message_id )
    await call .bot .restrict_chat_member (
    chat_id =chat_id ,
    user_id =reporter_id ,
    permissions =ChatPermissions (can_send_messages =False ),
    until_date =datetime .now (timezone .utc )+timedelta (days =1 )
    )
    await queue_member_update (reporter_id ,reputation_points =-10 )
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,bot_reply_id )
    await call .message .edit_text (
    call .message .text +"\n\n"+get_string ("action_deleted_dismissed2")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("rdismiss3_"))
async def callback_report_dismiss_mute_reporter_7d (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    reporter_id =int (parts [4 ])
    bot_reply_id =int (parts [5 ])
    remove_report (chat_id ,message_id )
    await call .bot .restrict_chat_member (
    chat_id =chat_id ,
    user_id =reporter_id ,
    permissions =ChatPermissions (can_send_messages =False ),
    until_date =datetime .now (timezone .utc )+timedelta (days =7 )
    )
    await queue_member_update (reporter_id ,reputation_points =-20 )
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,bot_reply_id )
    await call .message .edit_text (
    call .message .text +"\n\n"+get_string ("action_deleted_dismissed3")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("rdismiss4_"))
async def callback_report_dismiss_ban_reporter (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    reporter_id =int (parts [4 ])
    bot_reply_id =int (parts [5 ])
    remove_report (chat_id ,message_id )
    await call .bot .ban_chat_member (chat_id =chat_id ,user_id =reporter_id )
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,bot_reply_id )
    await call .message .edit_text (
    call .message .text +"\n\n"+get_string ("action_deleted_dismissed4")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("del_"))
async def callback_delete (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    await call .message .edit_text (
    call .message .text +get_string ("action_deleted")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("delban_"))
async def callback_delete_and_ban (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    user_id =int (parts [3 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    await call .bot .ban_chat_member (chat_id =chat_id ,user_id =user_id )
    await call .message .edit_text (
    call .message .text +get_string ("action_deleted_banned")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("mute_"))
async def callback_delete_and_mute_24h (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    user_id =int (parts [3 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    await call .bot .restrict_chat_member (
    chat_id =chat_id ,
    user_id =user_id ,
    permissions =ChatPermissions (can_send_messages =False ),
    until_date =datetime .now (timezone .utc )+timedelta (hours =24 )
    )
    await call .message .edit_text (
    call .message .text +get_string ("action_deleted_readonly")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("mute2_"))
async def callback_delete_and_mute_7d (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    user_id =int (parts [3 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    await call .bot .restrict_chat_member (
    chat_id =chat_id ,
    user_id =user_id ,
    permissions =ChatPermissions (can_send_messages =False ),
    until_date =datetime .now (timezone .utc )+timedelta (days =7 )
    )
    await call .message .edit_text (
    call .message .text +get_string ("action_deleted_readonly2")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("dismiss_"))
async def callback_dismiss (call :CallbackQuery )->None :
    await call .message .edit_text (
    call .message .text +get_string ("action_dismissed")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("dismiss2_"))
async def callback_dismiss_mute_reporter_1d (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    user_id =int (parts [3 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    await call .bot .restrict_chat_member (
    chat_id =chat_id ,
    user_id =user_id ,
    permissions =ChatPermissions (can_send_messages =False ),
    until_date =datetime .now (timezone .utc )+timedelta (days =1 )
    )
    await call .message .edit_text (
    call .message .text +get_string ("action_deleted_dismissed2")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("dismiss3_"))
async def callback_dismiss_mute_reporter_7d (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    user_id =int (parts [3 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    await call .bot .restrict_chat_member (
    chat_id =chat_id ,
    user_id =user_id ,
    permissions =ChatPermissions (can_send_messages =False ),
    until_date =datetime .now (timezone .utc )+timedelta (days =7 )
    )
    await call .message .edit_text (
    call .message .text +get_string ("action_deleted_dismissed3")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("dismiss4_"))
async def callback_dismiss_ban_reporter (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    chat_id =int (parts [1 ])
    message_id =int (parts [2 ])
    user_id =int (parts [3 ])
    with suppress (TelegramBadRequest ):
        await call .bot .delete_message (chat_id ,message_id )
    await call .bot .ban_chat_member (chat_id =chat_id ,user_id =user_id )
    await call .message .edit_text (
    call .message .text +get_string ("action_deleted_dismissed4")
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("spam_test_"))
async def callback_spam_test (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    spam_id =int (parts [2 ])
    member_id =int (parts [3 ])
    try :
        await Spam .objects .delete (id =spam_id )
    except Exception :
        pass
    try :
        member =await Member .objects .get (id =member_id )
        member .messages_count +=1
        await member .update ()
    except Exception :
        pass
    await call .message .edit_text (
    call .message .text +"\n\n<b>Удалено из базы, вероятно тест.</b>"
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("spam_ban_"))
async def callback_spam_ban (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    spam_id =int (parts [2 ])
    user_id =int (parts [3 ])
    try :
        spam_rec =await Spam .objects .get (id =spam_id )
        chat_id =spam_rec .chat_id
        with suppress (TelegramBadRequest ):
            await call .bot .ban_chat_member (chat_id =chat_id ,user_id =user_id )
        spam_rec .is_blocked =True
        await spam_rec .update ()
    except Exception :
        pass
    await call .message .edit_text (
    call .message .text +"\n\n❌ <b>Юзер забанен, сообщение помечено как спам</b>"
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("spam_invert_"))
async def callback_spam_not_spam (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    spam_id =int (parts [2 ])
    member_id =int (parts [3 ])if len (parts )>3 else None
    try :
        spam_rec =await Spam .objects .get (id =spam_id )
        spam_rec .is_spam =False
        await spam_rec .update ()
    except Exception :
        pass
    if member_id :
        try :
            member =await Member .objects .get (id =member_id )
            member .messages_count +=1
            member .reputation_points +=10
            await member .update ()
        except Exception :
            pass
    await call .message .edit_text (
    call .message .text +"\n\n❎ <b>Сообщение помечено как НЕ СПАМ</b>"
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("nsfw_ban_"))
async def callback_nsfw_ban (call :CallbackQuery )->None :
    parts =call .data .split ("_")
    user_id =int (parts [2 ])
    chat_id =int (parts [3 ])if len (parts )>3 else None
    if chat_id :
        with suppress (TelegramBadRequest ):
            await call .bot .ban_chat_member (chat_id =chat_id ,user_id =user_id )
    await call .message .edit_text (
    call .message .text +"\n\n❌ <b>Юзер забанен за NSFW изображение профиля.</b>"
    )
    await call .answer (text ="Done")
@router .callback_query (F .data .startswith ("nsfw_safe_"))
async def callback_nsfw_safe (call :CallbackQuery )->None :
    member_id =int (call .data .split ("_")[2 ])
    try :
        member =await Member .objects .get (id =member_id )
        member .messages_count +=1
        member .reputation_points +=10
        await member .update ()
    except Exception :
        pass
    await call .message .edit_text (
    call .message .text +"\n\n❎ <b>Сообщение помечено как не содержащее NSFW.</b>"
    )
    await call .answer (text ="Done")