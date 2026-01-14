from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9a0b48b8, name="types.InputInvoiceStarGiftPrepaidUpgrade")
class InputInvoiceStarGiftPrepaidUpgrade(TLObject):
    peer: TLObject = TLField()
    hash: str = TLField()
