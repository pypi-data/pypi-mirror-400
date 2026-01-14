from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa437c3ed, name="types.WallPaper")
class WallPaper(TLObject):
    id: Long = TLField()
    flags: Int = TLField(is_flags=True)
    creator: bool = TLField(flag=1 << 0)
    default: bool = TLField(flag=1 << 1)
    pattern: bool = TLField(flag=1 << 3)
    dark: bool = TLField(flag=1 << 4)
    access_hash: Long = TLField()
    slug: str = TLField()
    document: TLObject = TLField()
    settings: Optional[TLObject] = TLField(flag=1 << 2)
