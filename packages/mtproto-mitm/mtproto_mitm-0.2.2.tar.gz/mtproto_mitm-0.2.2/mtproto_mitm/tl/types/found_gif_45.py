from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x162ecc1f, name="types.FoundGif_45")
class FoundGif_45(TLObject):
    url: str = TLField()
    thumb_url: str = TLField()
    content_url: str = TLField()
    content_type: str = TLField()
    w: Int = TLField()
    h: Int = TLField()
