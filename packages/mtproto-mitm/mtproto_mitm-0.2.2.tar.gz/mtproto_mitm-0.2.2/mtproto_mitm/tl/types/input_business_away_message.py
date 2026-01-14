from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x832175e0, name="types.InputBusinessAwayMessage")
class InputBusinessAwayMessage(TLObject):
    flags: Int = TLField(is_flags=True)
    offline_only: bool = TLField(flag=1 << 0)
    shortcut_id: Int = TLField()
    schedule: TLObject = TLField()
    recipients: TLObject = TLField()
