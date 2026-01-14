from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf7d90ce0, name="types.Theme_105")
class Theme_105(TLObject):
    flags: Int = TLField(is_flags=True)
    creator: bool = TLField(flag=1 << 0)
    default: bool = TLField(flag=1 << 1)
    id: Long = TLField()
    access_hash: Long = TLField()
    slug: str = TLField()
    title: str = TLField()
    document: Optional[TLObject] = TLField(flag=1 << 2)
    installs_count: Int = TLField()
