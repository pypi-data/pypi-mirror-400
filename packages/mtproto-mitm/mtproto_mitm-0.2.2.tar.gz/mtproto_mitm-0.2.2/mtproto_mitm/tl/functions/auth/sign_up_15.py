from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1b067634, name="functions.auth.SignUp_15")
class SignUp_15(TLObject):
    phone_number: str = TLField()
    phone_code_hash: str = TLField()
    phone_code: str = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
