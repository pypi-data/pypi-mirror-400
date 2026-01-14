from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x44747e9a, name="types.auth.AuthorizationSignUpRequired")
class AuthorizationSignUpRequired(TLObject):
    flags: Int = TLField(is_flags=True)
    terms_of_service: Optional[TLObject] = TLField(flag=1 << 0)
