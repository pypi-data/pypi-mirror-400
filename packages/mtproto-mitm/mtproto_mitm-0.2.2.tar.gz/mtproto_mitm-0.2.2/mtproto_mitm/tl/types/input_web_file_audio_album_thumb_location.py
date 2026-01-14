from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf46fe924, name="types.InputWebFileAudioAlbumThumbLocation")
class InputWebFileAudioAlbumThumbLocation(TLObject):
    flags: Int = TLField(is_flags=True)
    small: bool = TLField(flag=1 << 2)
    document: Optional[TLObject] = TLField(flag=1 << 0)
    title: Optional[str] = TLField(flag=1 << 1)
    performer: Optional[str] = TLField(flag=1 << 1)
