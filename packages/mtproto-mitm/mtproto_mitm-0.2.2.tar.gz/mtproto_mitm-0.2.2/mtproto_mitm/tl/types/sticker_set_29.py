from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa7a43b17, name="types.StickerSet_29")
class StickerSet_29(TLObject):
    id: Long = TLField()
    access_hash: Long = TLField()
    title: str = TLField()
    short_name: str = TLField()
