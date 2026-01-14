from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf227868c, name="types.UpdateUserPhoto_133")
class UpdateUserPhoto_133(TLObject):
    user_id: Long = TLField()
    date: Int = TLField()
    photo: TLObject = TLField()
    previous: bool = TLField()
