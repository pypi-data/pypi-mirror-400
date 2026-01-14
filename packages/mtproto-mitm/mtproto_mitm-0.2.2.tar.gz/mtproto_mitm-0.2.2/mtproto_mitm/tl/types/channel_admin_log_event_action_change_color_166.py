from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3c2b247b, name="types.ChannelAdminLogEventActionChangeColor_166")
class ChannelAdminLogEventActionChangeColor_166(TLObject):
    prev_value: Int = TLField()
    new_value: Int = TLField()
