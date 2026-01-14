from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe8346f53, name="types.MessageGroup_38")
class MessageGroup_38(TLObject):
    min_id: Int = TLField()
    max_id: Int = TLField()
    count: Int = TLField()
    date: Int = TLField()
