from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdd2a4d8f, name="functions.account.SetPassword_25")
class SetPassword_25(TLObject):
    current_password_hash: bytes = TLField()
    new_salt: bytes = TLField()
    new_password_hash: bytes = TLField()
    hint: str = TLField()
