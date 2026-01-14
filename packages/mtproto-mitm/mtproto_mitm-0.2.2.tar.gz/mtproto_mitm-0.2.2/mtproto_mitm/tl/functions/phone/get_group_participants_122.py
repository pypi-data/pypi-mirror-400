from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc9f1d285, name="functions.phone.GetGroupParticipants_122")
class GetGroupParticipants_122(TLObject):
    call: TLObject = TLField()
    ids: list[Int] = TLField()
    sources: list[Int] = TLField()
    offset: str = TLField()
    limit: Int = TLField()
