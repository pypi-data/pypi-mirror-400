from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x18f3d0f7, name="types.StatsGroupTopPoster_116")
class StatsGroupTopPoster_116(TLObject):
    user_id: Int = TLField()
    messages: Int = TLField()
    avg_chars: Int = TLField()
