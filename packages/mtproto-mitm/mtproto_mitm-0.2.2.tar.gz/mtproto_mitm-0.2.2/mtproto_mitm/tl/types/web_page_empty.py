from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x211a1788, name="types.WebPageEmpty")
class WebPageEmpty(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Long = TLField()
    url: Optional[str] = TLField(flag=1 << 0)
