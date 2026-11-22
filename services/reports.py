from collections import deque
import logging
from config import config
logger =logging .getLogger (__name__ )
_recent_reports :dict [int ,deque ]={}
MAX_TRACKED_REPORTS =20
def is_already_reported (group_id :int ,message_id :int )->bool :
    if group_id not in _recent_reports :
        return False
    return message_id in _recent_reports [group_id ]
def track_report (group_id :int ,message_id :int )->None :
    if group_id not in _recent_reports :
        _recent_reports [group_id ]=deque (maxlen =MAX_TRACKED_REPORTS )
    _recent_reports [group_id ].append (message_id )
    logger .debug (f"Tracked report: group={group_id }, msg={message_id }")
def remove_report (group_id :int ,message_id :int )->None :
    if group_id not in _recent_reports :
        return
    try :
        _recent_reports [group_id ].remove (message_id )
        logger .debug (f"Removed report: group={group_id }, msg={message_id }")
    except ValueError :
        pass
def get_report_count (group_id :int )->int :
    if group_id not in _recent_reports :
        return 0
    return len (_recent_reports [group_id ])
def clear_group_reports (group_id :int )->None :
    if group_id in _recent_reports :
        _recent_reports [group_id ].clear ()