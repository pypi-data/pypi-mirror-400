from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xad253d78, name="types.CodeSettings")
class CodeSettings(TLObject):
    flags: Int = TLField(is_flags=True)
    allow_flashcall: bool = TLField(flag=1 << 0)
    current_number: bool = TLField(flag=1 << 1)
    allow_app_hash: bool = TLField(flag=1 << 4)
    allow_missed_call: bool = TLField(flag=1 << 5)
    allow_firebase: bool = TLField(flag=1 << 7)
    unknown_number: bool = TLField(flag=1 << 9)
    logout_tokens: Optional[list[bytes]] = TLField(flag=1 << 6)
    token: Optional[str] = TLField(flag=1 << 8)
    app_sandbox: bool = TLField(flag=1 << 8, flag_serializable=True)
