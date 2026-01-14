from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5214c89d, name="types.UserForeign_15")
class UserForeign_15(TLObject):
    id: Int = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
    access_hash: Long = TLField()
    photo: TLObject = TLField()
    status: TLObject = TLField()
