from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xad2e1cd8, name="types.account.AuthorizationForm")
class AuthorizationForm(TLObject):
    flags: Int = TLField(is_flags=True)
    required_types: list[TLObject] = TLField()
    values: list[TLObject] = TLField()
    errors: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
    privacy_policy_url: Optional[str] = TLField(flag=1 << 0)
