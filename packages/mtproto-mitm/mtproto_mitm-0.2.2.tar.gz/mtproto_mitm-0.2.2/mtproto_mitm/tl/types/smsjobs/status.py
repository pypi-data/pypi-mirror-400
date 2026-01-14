from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2aee9191, name="types.smsjobs.Status")
class Status(TLObject):
    flags: Int = TLField(is_flags=True)
    allow_international: bool = TLField(flag=1 << 0)
    recent_sent: Int = TLField()
    recent_since: Int = TLField()
    recent_remains: Int = TLField()
    total_sent: Int = TLField()
    total_since: Int = TLField()
    last_gift_slug: Optional[str] = TLField(flag=1 << 1)
    terms_url: str = TLField()
