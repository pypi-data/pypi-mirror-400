from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa00e67d6, name="types.Theme")
class Theme(TLObject):
    flags: Int = TLField(is_flags=True)
    creator: bool = TLField(flag=1 << 0)
    default: bool = TLField(flag=1 << 1)
    for_chat: bool = TLField(flag=1 << 5)
    id: Long = TLField()
    access_hash: Long = TLField()
    slug: str = TLField()
    title: str = TLField()
    document: Optional[TLObject] = TLField(flag=1 << 2)
    settings: Optional[list[TLObject]] = TLField(flag=1 << 3)
    emoticon: Optional[str] = TLField(flag=1 << 6)
    installs_count: Optional[Int] = TLField(flag=1 << 4)
