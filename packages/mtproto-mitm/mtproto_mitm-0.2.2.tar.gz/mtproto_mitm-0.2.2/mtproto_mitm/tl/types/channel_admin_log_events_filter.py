from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xea107ae4, name="types.ChannelAdminLogEventsFilter")
class ChannelAdminLogEventsFilter(TLObject):
    flags: Int = TLField(is_flags=True)
    join: bool = TLField(flag=1 << 0)
    leave: bool = TLField(flag=1 << 1)
    invite: bool = TLField(flag=1 << 2)
    ban: bool = TLField(flag=1 << 3)
    unban: bool = TLField(flag=1 << 4)
    kick: bool = TLField(flag=1 << 5)
    unkick: bool = TLField(flag=1 << 6)
    promote: bool = TLField(flag=1 << 7)
    demote: bool = TLField(flag=1 << 8)
    info: bool = TLField(flag=1 << 9)
    settings: bool = TLField(flag=1 << 10)
    pinned: bool = TLField(flag=1 << 11)
    edit: bool = TLField(flag=1 << 12)
    delete: bool = TLField(flag=1 << 13)
    group_call: bool = TLField(flag=1 << 14)
    invites: bool = TLField(flag=1 << 15)
    send: bool = TLField(flag=1 << 16)
    forums: bool = TLField(flag=1 << 17)
    sub_extend: bool = TLField(flag=1 << 18)
