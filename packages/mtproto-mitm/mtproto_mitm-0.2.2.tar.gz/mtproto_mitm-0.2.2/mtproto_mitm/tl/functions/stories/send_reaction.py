from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7fd736b2, name="functions.stories.SendReaction")
class SendReaction(TLObject):
    flags: Int = TLField(is_flags=True)
    add_to_recent: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    story_id: Int = TLField()
    reaction: TLObject = TLField()
