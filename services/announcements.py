import asyncio
import json
import logging
import random
import re
import time
from collections import deque
from datetime import datetime ,timedelta ,timezone
from pathlib import Path
from config import config
logger =logging .getLogger (__name__ )
_bot =None
_announcements :list [dict ]=[]
TIMESTAMPS_FILE =Path ("data/announcement_timestamps.json")
_group_history :dict [int ,deque ]={}
def track_message (group_id :int ,is_announcement :bool =False ,announcement_idx :int |None =None )->None :
    history_size =config .announcements .history_size
    if group_id not in _group_history :
        _group_history [group_id ]=deque (maxlen =history_size )
    _group_history [group_id ].append ({
    "is_announcement":is_announcement ,
    "announcement_idx":announcement_idx
    })
def get_announcement_count_in_history (group_id :int )->int :
    if group_id not in _group_history :
        return 0
    return sum (1 for msg in _group_history [group_id ]if msg ["is_announcement"])
def is_announcement_in_recent (group_id :int ,announcement_idx :int ,lookback :int |None =None )->bool :
    if group_id not in _group_history :
        return False
    if lookback is None :
        lookback =config .announcements .avoid_duplicate_in_last
    history =list (_group_history [group_id ])
    recent =history [-lookback :]if len (history )>lookback else history
    return any (
    msg ["is_announcement"]and msg ["announcement_idx"]==announcement_idx
    for msg in recent
    )
def _parse_time (time_str :str )->tuple [int ,int ]|None :
    if not time_str :
        return None
    try :
        parts =time_str .strip ().split (":")
        return (int (parts [0 ]),int (parts [1 ]))
    except (ValueError ,IndexError ):
        logger .warning (f"Invalid time format: {time_str }")
        return None
def is_sleep_time (group_id :int )->bool :
    group_settings =config .announcements .groups .get (group_id )
    if group_settings :
        sleep_from =group_settings .sleep_from or config .announcements .sleep_from
        sleep_to =group_settings .sleep_to or config .announcements .sleep_to
        utc_offset =group_settings .utc_offset if group_settings .utc_offset is not None else config .announcements .utc_offset
    else :
        sleep_from =config .announcements .sleep_from
        sleep_to =config .announcements .sleep_to
        utc_offset =config .announcements .utc_offset
    from_time =_parse_time (sleep_from )
    to_time =_parse_time (sleep_to )
    if not from_time or not to_time :
        return False
    tz =timezone (timedelta (hours =utc_offset ))
    now =datetime .now (tz )
    current_minutes =now .hour *60 +now .minute
    from_minutes =from_time [0 ]*60 +from_time [1 ]
    to_minutes =to_time [0 ]*60 +to_time [1 ]
    if from_minutes >to_minutes :
        return current_minutes >=from_minutes or current_minutes <to_minutes
    else :
        return from_minutes <=current_minutes <to_minutes
def can_send_announcement (group_id :int ,announcement_idx :int )->tuple [bool ,str ]:
    if not config .announcements .enabled :
        return False ,"объявления отключены"
    if is_sleep_time (group_id ):
        return False ,"время сна"
    announcement_count =get_announcement_count_in_history (group_id )
    if announcement_count >=config .announcements .max_stack :
        return False ,f"max stack reached ({announcement_count })"
    if is_announcement_in_recent (group_id ,announcement_idx ):
        return False ,"дубликат в новейшей истории"
    return True ,"ok"
async def send_to_group (message :str ,group_id :int ,announcement_idx :int )->bool :
    if _bot is None :
        logger .warning ("Бот не инициализирован, пропускает объявление")
        return False
    can_send ,reason =can_send_announcement (group_id ,announcement_idx )
    if not can_send :
        logger .debug (f"Skipping announcement #{announcement_idx +1 } to {group_id }: {reason }")
        return False
    try :
        await _bot .send_message (group_id ,message )
        track_message (group_id ,is_announcement =True ,announcement_idx =announcement_idx )
        logger .debug (f"Announcement #{announcement_idx +1 } sent to {group_id }")
        return True
    except Exception as e :
        logger .error (f"Failed to send announcement to {group_id }: {e }")
        return False
def _load_timestamps ()->dict [str ,float ]:
    if not TIMESTAMPS_FILE .exists ():
        return {}
    try :
        with open (TIMESTAMPS_FILE ,'r')as f :
            data =json .load (f )
            logger .info (f"Loaded {len (data )} announcement timestamps")
            return data
    except Exception as e :
        logger .warning (f"Failed to load timestamps: {e }")
        return {}
def _save_timestamps (timestamps :dict [str ,float ])->None :
    try :
        TIMESTAMPS_FILE .parent .mkdir (parents =True ,exist_ok =True )
        with open (TIMESTAMPS_FILE ,'w')as f :
            json .dump (timestamps ,f ,indent =2 )
    except Exception as e :
        logger .error (f"Failed to save timestamps: {e }")
def _migrate_timestamps (timestamps :dict [str ,float ],announcements :list [dict ])->dict [str ,float ]:
    if not timestamps :
        return timestamps
    if any (":"in key for key in timestamps .keys ()):
        return timestamps
    if not all (key .isdigit ()for key in timestamps .keys ()):
        return timestamps
    logger .info ("Перенос меток времени из старого формата в формат для каждой группы...")
    new_timestamps ={}
    for old_key ,timestamp in timestamps .items ():
        try :
            idx =int (old_key )
            if idx <len (announcements ):
                announcement =announcements [idx ]
                target_groups =announcement .get ('groups')or config .groups .main
                for group_id in target_groups :
                    new_key =f"{idx }:{group_id }"
                    new_timestamps [new_key ]=timestamp
                logger .debug (f"Migrated key '{old_key }' to {len (target_groups )} group keys")
        except (ValueError ,IndexError )as e :
            logger .warning (f"Failed to migrate key '{old_key }': {e }")
    logger .info (f"Migration complete: {len (timestamps )} -> {len (new_timestamps )} keys")
    return new_timestamps
def _load_messages (locale :str )->dict [str ,str ]:
    messages ={}
    ftl_path =Path (f"locales/{locale }/announcements.ftl")
    if not ftl_path .exists ():
        return messages
    content =ftl_path .read_text (encoding ="utf-8")
    pattern =r'^(msg-[\w-]+)\s*=\s*\n((?:[ \t]+.+\n?)+)'
    for match in re .finditer (pattern ,content ,re .MULTILINE ):
        key =match .group (1 )
        block =match .group (2 )
        lines =[]
        for line in block .split ('\n'):
            stripped =line .strip ()
            if stripped and not stripped .startswith ('@')and not stripped .startswith ('#'):
                lines .append (line .lstrip ())
        if lines :
            messages [key ]='\n'.join (lines ).strip ()
            logger .debug (f"Loaded message: {key }")
    logger .info (f"Loaded {len (messages )} message templates")
    return messages
def load_announcements (locale :str ="ru")->list [dict ]:
    announcements =[]
    ftl_path =Path (f"locales/{locale }/announcements.ftl")
    if not ftl_path .exists ():
        logger .warning (f"Announcements file not found: {ftl_path }")
        return announcements
    content =ftl_path .read_text (encoding ="utf-8")
    messages =_load_messages (locale )
    pattern =r'^announcement-\d+\s*=\s*\n((?:[ \t]+.+\n?)+)'
    for match in re .finditer (pattern ,content ,re .MULTILINE ):
        block =match .group (1 )
        lines =block .split ('\n')
        message_lines =[]
        message_ref =None
        every_min =3600
        every_max =3600
        groups =None
        for line in lines :
            stripped =line .strip ()
            if stripped .startswith ('@каждый:'):
                every_str =stripped .replace ('@каждый:','').strip ()
                try :
                    if '-'in every_str :
                        parts =every_str .split ('-')
                        every_min =int (parts [0 ].strip ())
                        every_max =int (parts [1 ].strip ())
                        if every_min >every_max :
                            every_min ,every_max =every_max ,every_min
                    else :
                        every_min =every_max =int (every_str )
                except (ValueError ,IndexError ):
                    logger .warning (f"Invalid @every value: {stripped }")
            elif stripped .startswith ('@группы:'):
                try :
                    groups_str =stripped .replace ('@группы:','').strip ()
                    groups =[int (g .strip ())for g in groups_str .split (',')if g .strip ()]
                except ValueError :
                    logger .warning (f"Invalid @groups value: {stripped }")
            elif stripped .startswith ('@сообщение:'):
                message_ref =stripped .replace ('@сообщение:','').strip ()
            elif stripped and not stripped .startswith ('#')and not stripped .startswith ('@'):
                message_lines .append (line .lstrip ())
        message =None
        if message_ref :
            if message_ref in messages :
                message =messages [message_ref ]
            else :
                logger .warning (f"Message reference not found: {message_ref }")
        elif message_lines :
            message ='\n'.join (message_lines ).strip ()
        if message :
            announcement ={
            'message':message ,
            'every_min':every_min ,
            'every_max':every_max ,
            'message_ref':message_ref ,
            }
            if groups :
                announcement ['groups']=groups
            announcements .append (announcement )
            src =f"ref:{message_ref }"if message_ref else f"inline:{message [:30 ]}..."
            every_info =f"{every_min }-{every_max }s"if every_min !=every_max else f"{every_min }s"
            logger .debug (f"Loaded announcement ({src }, every={every_info })")
    logger .info (f"Loaded {len (announcements )} announcements from {ftl_path }")
    return announcements
async def run_scheduler ()->None :
    global _bot ,_announcements
    while _bot is None :
        await asyncio .sleep (1 )
    if not config .announcements .enabled :
        logger .info ("Объявления отключены в конфиге")
        return
    _announcements =load_announcements (config .locale .default )
    if not _announcements :
        logger .warning ("Объявления не загружены, планировщик простаивает")
        return
    logger .info (f"Scheduler started with {len (_announcements )} announcements")
    last_sent =_load_timestamps ()
    last_sent =_migrate_timestamps (last_sent ,_announcements )
    next_intervals :dict [str ,int ]={}
    current_time =time .time ()
    for i ,announcement in enumerate (_announcements ):
        every_min =announcement ['every_min']
        every_max =announcement ['every_max']
        target_groups =announcement .get ('groups')or config .groups .main
        for group_id in target_groups :
            key =f"{i }:{group_id }"
            next_intervals [key ]=random .randint (every_min ,every_max )
            if key not in last_sent :
                last_sent [key ]=current_time
                logger .debug (f"New announcement #{i +1 } for group {group_id } - will send after {next_intervals [key ]}s")
    _save_timestamps (last_sent )
    logger .info ("Объявления инициализируются с использованием временных меток для каждой группы.")
    while True :
        try :
            current_time =time .time ()
            for i ,announcement in enumerate (_announcements ):
                every_min =announcement ['every_min']
                every_max =announcement ['every_max']
                message =announcement ['message']
                target_groups =announcement .get ('groups')or config .groups .main
                for group_id in target_groups :
                    key =f"{i }:{group_id }"
                    interval =next_intervals .get (key ,every_min )
                    time_since_last =current_time -last_sent .get (key ,0 )
                    if time_since_last >=interval :
                        success =await send_to_group (message ,group_id ,i )
                        if success :
                            last_sent [key ]=current_time
                            _save_timestamps (last_sent )
                            next_intervals [key ]=random .randint (every_min ,every_max )
                            interval_info =f"{every_min }-{every_max }"if every_min !=every_max else str (every_min )
                            logger .info (f"Announcement #{i +1 } sent to {group_id } (interval: {interval_info }s, next: {next_intervals [key ]}s)")
                        else :
                            retry_delay =random .randint (60 ,300 )
                            last_sent [key ]=current_time -interval +retry_delay
            await asyncio .sleep (10 )
        except asyncio .CancelledError :
            logger .info ("Планировщик отменен")
            raise
        except Exception as e :
            logger .error (f"Scheduler error: {e }")
            await asyncio .sleep (30 )
def set_bot (bot )->None :
    global _bot
    _bot =bot
    logger .info ("Набор ботов для объявлений")
def reload_announcements (locale :str =None )->int :
    global _announcements
    _announcements =load_announcements (locale or config .locale .default )
    return len (_announcements )
def get_group_history (group_id :int )->list [dict ]:
    if group_id not in _group_history :
        return []
    return list (_group_history [group_id ])
def clear_group_history (group_id :int )->None :
    if group_id in _group_history :
        _group_history [group_id ].clear ()