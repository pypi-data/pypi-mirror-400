from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x50a1dfd6, name="types.ChannelParticipantBanned_126")
class ChannelParticipantBanned_126(TLObject):
    flags: Int = TLField(is_flags=True)
    left: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    kicked_by: Int = TLField()
    date: Int = TLField()
    banned_rights: TLObject = TLField()
