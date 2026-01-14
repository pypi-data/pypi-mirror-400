from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe325edcf, name="types.auth.SentAppCode_19")
class SentAppCode_19(TLObject):
    phone_registered: bool = TLField()
    phone_code_hash: str = TLField()
    send_call_timeout: Int = TLField()
    is_password: bool = TLField()
