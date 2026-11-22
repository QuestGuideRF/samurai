import asyncio
from dataclasses import dataclass
from functools import wraps
from typing import Optional
import ormar
from cachetools import TTLCache ,LRUCache
from config import config
from db .models import Member
from services .gender import detect_gender as _detect_gender ,Gender
@dataclass
class MemberData :
    id :int
    user_id :int
    messages_count :int
    reputation_points :int
    violations_count_profanity :int
    violations_count_spam :int
    halloween_sweets :int
    halloween_golden_tickets :int
    @classmethod
    def from_orm (cls ,member :Member )->"MemberData":
        return cls (
        id =member .id ,
        user_id =member .user_id ,
        messages_count =member .messages_count ,
        reputation_points =member .reputation_points ,
        violations_count_profanity =member .violations_count_profanity ,
        violations_count_spam =member .violations_count_spam ,
        halloween_sweets =member .halloween_sweets ,
        halloween_golden_tickets =member .halloween_golden_tickets ,
        )
members_cache :TTLCache =TTLCache (
maxsize =config .cache .members_maxsize ,
ttl =config .cache .members_ttl
)
tgmembers_cache :TTLCache =TTLCache (
maxsize =config .cache .tgmembers_maxsize ,
ttl =config .cache .tgmembers_ttl
)
gender_detections_cache :LRUCache =LRUCache (
maxsize =config .cache .gender_maxsize
)
nsfw_results_cache :TTLCache =TTLCache (
maxsize =config .cache .nsfw_maxsize ,
ttl =config .cache .nsfw_ttl
)
_pending_updates :dict [int ,dict [str ,int ]]={}
_batch_lock =asyncio .Lock ()
_flush_task :Optional [asyncio .Task ]=None
async def queue_member_update (user_id :int ,**changes :int )->None :
    async with _batch_lock :
        if user_id not in _pending_updates :
            _pending_updates [user_id ]={}
        for field ,delta in changes .items ():
            current =_pending_updates [user_id ].get (field ,0 )
            _pending_updates [user_id ][field ]=current +delta
async def flush_member_updates ()->int :
    async with _batch_lock :
        if not _pending_updates :
            return 0
        updates_copy =dict (_pending_updates )
        _pending_updates .clear ()
    count =0
    for user_id ,changes in updates_copy .items ():
        try :
            member =await Member .objects .get (user_id =user_id )
            for field ,delta in changes .items ():
                current_value =getattr (member ,field ,0 )
                setattr (member ,field ,current_value +delta )
            await member .update ()
            count +=1
            invalidate_member_cache (user_id )
        except ormar .NoMatch :
            pass
        except Exception :
            pass
    return count
async def _periodic_flush (interval :int )->None :
    while True :
        await asyncio .sleep (interval )
        await flush_member_updates ()
def start_batch_flush_task (interval :Optional [int ]=None )->asyncio .Task :
    global _flush_task
    if interval is None :
        interval =config .cache .batch_flush_interval
    if _flush_task is None or _flush_task .done ():
        _flush_task =asyncio .create_task (_periodic_flush (interval ))
    return _flush_task
def stop_batch_flush_task ()->None :
    global _flush_task
    if _flush_task and not _flush_task .done ():
        _flush_task .cancel ()
        _flush_task =None
def cache_gender_detection (func ):
    @wraps (func )
    def wrapper (name :str )->Gender :
        if name in gender_detections_cache :
            return gender_detections_cache [name ]
        result =func (name )
        gender_detections_cache [name ]=result
        return result
    return wrapper
@cache_gender_detection
def detect_gender (name :str )->Gender :
    return _detect_gender (name )
async def retrieve_tgmember (bot ,chat_id :int ,user_id :int ):
    cache_key =(chat_id ,user_id )
    if cache_key in tgmembers_cache :
        return tgmembers_cache [cache_key ]
    result =await bot .get_chat_member (chat_id ,user_id )
    tgmembers_cache [cache_key ]=result
    return result
def invalidate_tgmember_cache (chat_id :int ,user_id :int )->None :
    cache_key =(chat_id ,user_id )
    if cache_key in tgmembers_cache :
        del tgmembers_cache [cache_key ]
def invalidate_tgmember_cache_all (user_id :int )->None :
    keys_to_delete =[k for k in tgmembers_cache .keys ()if k [1 ]==user_id ]
    for key in keys_to_delete :
        del tgmembers_cache [key ]
async def retrieve_or_create_member (user_id :int )->MemberData :
    if user_id in members_cache :
        return members_cache [user_id ]
    try :
        member =await Member .objects .get (user_id =user_id )
    except ormar .NoMatch :
        try :
            member =await Member .objects .create (user_id =user_id ,messages_count =1 )
        except Exception :
            member =await Member .objects .get (user_id =user_id )
    member_data =MemberData .from_orm (member )
    members_cache [user_id ]=member_data
    return member_data
async def get_member_orm (user_id :int )->Member :
    try :
        return await Member .objects .get (user_id =user_id )
    except ormar .NoMatch :
        try :
            return await Member .objects .create (user_id =user_id ,messages_count =1 )
        except Exception :
            return await Member .objects .get (user_id =user_id )
def invalidate_member_cache (user_id :int )->None :
    if user_id in members_cache :
        del members_cache [user_id ]
def update_member_cache (user_id :int ,member :Member )->None :
    members_cache [user_id ]=MemberData .from_orm (member )
def get_cached_nsfw_result (user_id :int ,photo_file_unique_id :str )->Optional [bool ]:
    cache_key =(user_id ,photo_file_unique_id )
    return nsfw_results_cache .get (cache_key )
def cache_nsfw_result (user_id :int ,photo_file_unique_id :str ,is_nsfw :bool )->None :
    cache_key =(user_id ,photo_file_unique_id )
    nsfw_results_cache [cache_key ]=is_nsfw
def invalidate_nsfw_cache (user_id :int )->None :
    keys_to_delete =[k for k in nsfw_results_cache .keys ()if k [0 ]==user_id ]
    for key in keys_to_delete :
        del nsfw_results_cache [key ]
def is_trusted_user (member :MemberData )->bool :
    return member .messages_count >=config .cache .trusted_user_messages
def clear_all_caches ()->None :
    members_cache .clear ()
    tgmembers_cache .clear ()
    gender_detections_cache .clear ()
    nsfw_results_cache .clear ()