from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x771095da, name="types.UserFull_15")
class UserFull_15(TLObject):
    user: TLObject = TLField()
    link: TLObject = TLField()
    profile_photo: TLObject = TLField()
    notify_settings: TLObject = TLField()
    blocked: bool = TLField()
    real_first_name: str = TLField()
    real_last_name: str = TLField()
