from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x27d69997, name="types.InputPeerPhotoFileLocation_98")
class InputPeerPhotoFileLocation_98(TLObject):
    flags: Int = TLField(is_flags=True)
    big: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    volume_id: Long = TLField()
    local_id: Int = TLField()
