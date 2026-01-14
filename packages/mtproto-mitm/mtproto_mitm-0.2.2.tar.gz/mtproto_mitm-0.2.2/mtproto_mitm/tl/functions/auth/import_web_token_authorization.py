from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2db873a9, name="functions.auth.ImportWebTokenAuthorization")
class ImportWebTokenAuthorization(TLObject):
    api_id: Int = TLField()
    api_hash: str = TLField()
    web_auth_token: str = TLField()
