from enum import Enum
class MemberStatus (str ,Enum ):
    CREATOR ="creator"
    ADMINISTRATOR ="administrator"
    MEMBER ="member"
    RESTRICTED ="restricted"
    LEFT ="left"
    KICKED ="kicked"
    @classmethod
    def is_admin (cls ,status :str )->bool :
        return status in (cls .ADMINISTRATOR ,cls .CREATOR )
    @classmethod
    def admin_statuses (cls )->tuple :
        return (cls .ADMINISTRATOR .value ,cls .CREATOR .value )