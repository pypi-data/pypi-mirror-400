from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7311ca11, name="types.WebPageNotModified")
class WebPageNotModified(TLObject):
    flags: Int = TLField(is_flags=True)
    cached_page_views: Optional[Int] = TLField(flag=1 << 0)
