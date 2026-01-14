from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x445fc434, name="types.ChannelAdminLogEventActionChangeBackgroundEmoji_166")
class ChannelAdminLogEventActionChangeBackgroundEmoji_166(TLObject):
    prev_value: Long = TLField()
    new_value: Long = TLField()
