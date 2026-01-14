from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x87232bc7, name="types.Document_54")
class Document_54(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    date: Int = TLField()
    mime_type: str = TLField()
    size: Int = TLField()
    thumb: TLObject = TLField()
    dc_id: Int = TLField()
    version: Int = TLField()
    attributes: list[TLObject] = TLField()
