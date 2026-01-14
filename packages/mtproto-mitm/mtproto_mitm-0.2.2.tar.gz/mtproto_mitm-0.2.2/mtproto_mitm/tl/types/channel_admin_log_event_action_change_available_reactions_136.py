from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9cf7f76a, name="types.ChannelAdminLogEventActionChangeAvailableReactions_136")
class ChannelAdminLogEventActionChangeAvailableReactions_136(TLObject):
    prev_value: list[str] = TLField()
    new_value: list[str] = TLField()
