from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x767d61eb, name="types.help.PeerColorProfileSet")
class PeerColorProfileSet(TLObject):
    palette_colors: list[Int] = TLField()
    bg_colors: list[Int] = TLField()
    story_colors: list[Int] = TLField()
