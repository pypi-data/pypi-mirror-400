from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5a89ac5b, name="types.UserFull_31")
class UserFull_31(TLObject):
    user: TLObject = TLField()
    link: TLObject = TLField()
    profile_photo: TLObject = TLField()
    notify_settings: TLObject = TLField()
    blocked: bool = TLField()
    bot_info: TLObject = TLField()
