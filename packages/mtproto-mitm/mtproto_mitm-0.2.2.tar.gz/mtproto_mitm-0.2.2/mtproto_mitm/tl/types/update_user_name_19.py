from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa7332b73, name="types.UpdateUserName_19")
class UpdateUserName_19(TLObject):
    user_id: Int = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
    username: str = TLField()
