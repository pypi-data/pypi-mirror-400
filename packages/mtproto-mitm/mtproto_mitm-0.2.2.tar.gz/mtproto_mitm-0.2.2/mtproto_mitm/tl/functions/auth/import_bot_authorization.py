from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x67a3ff2c, name="functions.auth.ImportBotAuthorization")
class ImportBotAuthorization(TLObject):
    flags: Int = TLField()
    api_id: Int = TLField()
    api_hash: str = TLField()
    bot_auth_token: str = TLField()
