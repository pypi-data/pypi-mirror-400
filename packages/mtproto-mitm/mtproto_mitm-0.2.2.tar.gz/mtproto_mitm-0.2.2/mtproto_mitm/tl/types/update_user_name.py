from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa7848924, name="types.UpdateUserName")
class UpdateUserName(TLObject):
    user_id: Long = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
    usernames: list[TLObject] = TLField()
