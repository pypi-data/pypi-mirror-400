from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x768d5f4d, name="functions.auth.SendCode_15")
class SendCode_15(TLObject):
    phone_number: str = TLField()
    sms_type: Int = TLField()
    api_id: Int = TLField()
    api_hash: str = TLField()
    lang_code: str = TLField()
