from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe923400d, name="types.messages.SentMessageLink_25")
class SentMessageLink_25(TLObject):
    id: Int = TLField()
    date: Int = TLField()
    pts: Int = TLField()
    pts_count: Int = TLField()
    links: list[TLObject] = TLField()
    seq: Int = TLField()
