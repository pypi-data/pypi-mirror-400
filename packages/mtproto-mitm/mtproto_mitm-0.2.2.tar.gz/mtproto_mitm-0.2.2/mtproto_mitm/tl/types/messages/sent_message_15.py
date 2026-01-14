from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd1f4d35c, name="types.messages.SentMessage_15")
class SentMessage_15(TLObject):
    id: Int = TLField()
    date: Int = TLField()
    pts: Int = TLField()
    seq: Int = TLField()
