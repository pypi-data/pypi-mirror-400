from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x697102b, name="types.QuickReply")
class QuickReply(TLObject):
    shortcut_id: Int = TLField()
    shortcut: str = TLField()
    top_message: Int = TLField()
    count: Int = TLField()
