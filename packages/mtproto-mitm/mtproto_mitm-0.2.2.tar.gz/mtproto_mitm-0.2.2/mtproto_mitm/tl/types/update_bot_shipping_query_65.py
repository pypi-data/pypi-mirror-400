from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe0cdc940, name="types.UpdateBotShippingQuery_65")
class UpdateBotShippingQuery_65(TLObject):
    query_id: Long = TLField()
    user_id: Int = TLField()
    payload: bytes = TLField()
    shipping_address: TLObject = TLField()
