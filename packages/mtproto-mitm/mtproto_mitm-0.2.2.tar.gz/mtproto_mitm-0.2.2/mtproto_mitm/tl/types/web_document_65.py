from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc61acbd8, name="types.WebDocument_65")
class WebDocument_65(TLObject):
    url: str = TLField()
    access_hash: Long = TLField()
    size: Int = TLField()
    mime_type: str = TLField()
    attributes: list[TLObject] = TLField()
    dc_id: Int = TLField()
