from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xccfd70cf, name="functions.auth.SendCode_50")
class SendCode_50(TLObject):
    flags: Int = TLField(is_flags=True)
    allow_flashcall: bool = TLField(flag=1 << 0)
    phone_number: str = TLField()
    current_number: bool = TLField(flag=1 << 0, flag_serializable=True)
    api_id: Int = TLField()
    api_hash: str = TLField()
    lang_code: str = TLField()
