from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd9ccc4ef, name="types.UserRequest_19")
class UserRequest_19(TLObject):
    id: Int = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
    username: str = TLField()
    access_hash: Long = TLField()
    phone: str = TLField()
    photo: TLObject = TLField()
    status: TLObject = TLField()
