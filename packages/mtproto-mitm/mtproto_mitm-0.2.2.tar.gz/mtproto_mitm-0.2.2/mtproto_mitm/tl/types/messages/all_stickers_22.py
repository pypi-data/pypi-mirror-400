from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdcef3102, name="types.messages.AllStickers_22")
class AllStickers_22(TLObject):
    hash: str = TLField()
    packs: list[TLObject] = TLField()
    documents: list[TLObject] = TLField()
