from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7f9488a, name="types.UpdateBotStopped_125")
class UpdateBotStopped_125(TLObject):
    user_id: Int = TLField()
    date: Int = TLField()
    stopped: bool = TLField()
    qts: Int = TLField()
