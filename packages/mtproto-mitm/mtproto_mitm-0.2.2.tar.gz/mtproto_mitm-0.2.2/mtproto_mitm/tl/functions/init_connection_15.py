from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x69796de9, name="functions.InitConnection_15")
class InitConnection_15(TLObject):
    api_id: Int = TLField()
    device_model: str = TLField()
    system_version: str = TLField()
    app_version: str = TLField()
    lang_code: str = TLField()
    query: TLObject = TLField()
