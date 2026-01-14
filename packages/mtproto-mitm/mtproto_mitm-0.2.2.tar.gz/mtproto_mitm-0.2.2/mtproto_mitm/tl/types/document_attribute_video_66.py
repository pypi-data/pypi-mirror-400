from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xef02ce6, name="types.DocumentAttributeVideo_66")
class DocumentAttributeVideo_66(TLObject):
    flags: Int = TLField(is_flags=True)
    round_message: bool = TLField(flag=1 << 0)
    duration: Int = TLField()
    w: Int = TLField()
    h: Int = TLField()
