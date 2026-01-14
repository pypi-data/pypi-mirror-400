from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x56e59f9c, name="functions.auth.CheckPaidAuth")
class CheckPaidAuth(TLObject):
    phone_number: str = TLField()
    phone_code_hash: str = TLField()
    form_id: Long = TLField()
