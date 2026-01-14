from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf4e096c3, name="types.InputMediaInvoice_73")
class InputMediaInvoice_73(TLObject):
    flags: Int = TLField(is_flags=True)
    title: str = TLField()
    description: str = TLField()
    photo: Optional[TLObject] = TLField(flag=1 << 0)
    invoice: TLObject = TLField()
    payload: bytes = TLField()
    provider: str = TLField()
    provider_data: TLObject = TLField()
    start_param: str = TLField()
