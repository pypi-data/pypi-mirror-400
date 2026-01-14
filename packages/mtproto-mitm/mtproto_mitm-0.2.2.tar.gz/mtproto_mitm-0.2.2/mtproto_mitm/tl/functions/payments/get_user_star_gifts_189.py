from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5e72c7e1, name="functions.payments.GetUserStarGifts_189")
class GetUserStarGifts_189(TLObject):
    user_id: TLObject = TLField()
    offset: str = TLField()
    limit: Int = TLField()
