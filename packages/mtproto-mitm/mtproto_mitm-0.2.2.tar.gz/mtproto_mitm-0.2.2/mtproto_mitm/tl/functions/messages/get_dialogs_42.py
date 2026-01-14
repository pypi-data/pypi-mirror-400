from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6b47f94d, name="functions.messages.GetDialogs_42")
class GetDialogs_42(TLObject):
    offset_date: Int = TLField()
    offset_id: Int = TLField()
    offset_peer: TLObject = TLField()
    limit: Int = TLField()
