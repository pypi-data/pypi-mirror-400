from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe8fe0de, name="types.MessageUserVoteMultiple_109")
class MessageUserVoteMultiple_109(TLObject):
    user_id: Int = TLField()
    options: list[bytes] = TLField()
    date: Int = TLField()
