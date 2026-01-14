from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x95313b0c, name="types.UpdateUserPhoto_15")
class UpdateUserPhoto_15(TLObject):
    user_id: Int = TLField()
    date: Int = TLField()
    photo: TLObject = TLField()
    previous: bool = TLField()
