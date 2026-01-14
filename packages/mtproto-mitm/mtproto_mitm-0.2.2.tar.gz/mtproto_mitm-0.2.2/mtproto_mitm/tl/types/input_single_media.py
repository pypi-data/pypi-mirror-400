from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1cc6e91f, name="types.InputSingleMedia")
class InputSingleMedia(TLObject):
    flags: Int = TLField(is_flags=True)
    media: TLObject = TLField()
    random_id: Long = TLField()
    message: str = TLField()
    entities: Optional[list[TLObject]] = TLField(flag=1 << 0)
