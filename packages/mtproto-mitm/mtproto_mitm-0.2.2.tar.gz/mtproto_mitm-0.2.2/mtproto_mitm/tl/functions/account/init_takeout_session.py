from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8ef3eab0, name="functions.account.InitTakeoutSession")
class InitTakeoutSession(TLObject):
    flags: Int = TLField(is_flags=True)
    contacts: bool = TLField(flag=1 << 0)
    message_users: bool = TLField(flag=1 << 1)
    message_chats: bool = TLField(flag=1 << 2)
    message_megagroups: bool = TLField(flag=1 << 3)
    message_channels: bool = TLField(flag=1 << 4)
    files: bool = TLField(flag=1 << 5)
    file_max_size: Optional[Long] = TLField(flag=1 << 5)
