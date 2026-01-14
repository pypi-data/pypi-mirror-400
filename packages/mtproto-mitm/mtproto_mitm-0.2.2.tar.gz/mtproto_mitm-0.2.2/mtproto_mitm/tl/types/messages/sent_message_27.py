from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4c3d47f3, name="types.messages.SentMessage_27")
class SentMessage_27(TLObject):
    id: Int = TLField()
    date: Int = TLField()
    media: TLObject = TLField()
    pts: Int = TLField()
    pts_count: Int = TLField()
