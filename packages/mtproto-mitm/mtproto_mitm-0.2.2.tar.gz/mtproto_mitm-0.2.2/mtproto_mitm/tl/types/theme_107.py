from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x28f1114, name="types.Theme_107")
class Theme_107(TLObject):
    flags: Int = TLField(is_flags=True)
    creator: bool = TLField(flag=1 << 0)
    default: bool = TLField(flag=1 << 1)
    id: Long = TLField()
    access_hash: Long = TLField()
    slug: str = TLField()
    title: str = TLField()
    document: Optional[TLObject] = TLField(flag=1 << 2)
    settings: Optional[TLObject] = TLField(flag=1 << 3)
    installs_count: Int = TLField()
