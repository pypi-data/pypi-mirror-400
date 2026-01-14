from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf3ed4c73, name="functions.account.AcceptAuthorization")
class AcceptAuthorization(TLObject):
    bot_id: Long = TLField()
    scope: str = TLField()
    public_key: str = TLField()
    value_hashes: list[TLObject] = TLField()
    credentials: TLObject = TLField()
