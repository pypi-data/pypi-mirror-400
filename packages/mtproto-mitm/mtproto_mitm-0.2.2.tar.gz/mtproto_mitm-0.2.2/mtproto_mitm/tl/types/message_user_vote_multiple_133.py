from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8a65e557, name="types.MessageUserVoteMultiple_133")
class MessageUserVoteMultiple_133(TLObject):
    user_id: Long = TLField()
    options: list[bytes] = TLField()
    date: Int = TLField()
