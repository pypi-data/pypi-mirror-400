from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4d8a0299, name="types.BotInfo")
class BotInfo(TLObject):
    flags: Int = TLField(is_flags=True)
    has_preview_medias: bool = TLField(flag=1 << 6)
    user_id: Optional[Long] = TLField(flag=1 << 0)
    description: Optional[str] = TLField(flag=1 << 1)
    description_photo: Optional[TLObject] = TLField(flag=1 << 4)
    description_document: Optional[TLObject] = TLField(flag=1 << 5)
    commands: Optional[list[TLObject]] = TLField(flag=1 << 2)
    menu_button: Optional[TLObject] = TLField(flag=1 << 3)
    privacy_policy_url: Optional[str] = TLField(flag=1 << 7)
    app_settings: Optional[TLObject] = TLField(flag=1 << 8)
    verifier_settings: Optional[TLObject] = TLField(flag=1 << 9)
