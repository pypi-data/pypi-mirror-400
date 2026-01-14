from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe7027c94, name="functions.account.AcceptAuthorization_80")
class AcceptAuthorization_80(TLObject):
    bot_id: Int = TLField()
    scope: str = TLField()
    public_key: str = TLField()
    value_hashes: list[TLObject] = TLField()
    credentials: TLObject = TLField()
