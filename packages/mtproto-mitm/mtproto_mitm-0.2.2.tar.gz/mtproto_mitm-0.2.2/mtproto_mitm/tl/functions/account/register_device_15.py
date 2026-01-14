from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x446c712c, name="functions.account.RegisterDevice_15")
class RegisterDevice_15(TLObject):
    token_type: Int = TLField()
    token: str = TLField()
    device_model: str = TLField()
    system_version: str = TLField()
    app_version: str = TLField()
    app_sandbox: bool = TLField()
    lang_code: str = TLField()
