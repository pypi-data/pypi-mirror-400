from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6014f412, name="types.StatsGroupTopAdmin_116")
class StatsGroupTopAdmin_116(TLObject):
    user_id: Int = TLField()
    deleted: Int = TLField()
    kicked: Int = TLField()
    banned: Int = TLField()
