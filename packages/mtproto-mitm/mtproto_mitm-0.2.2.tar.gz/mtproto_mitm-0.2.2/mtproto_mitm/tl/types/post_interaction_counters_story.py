from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8a480e27, name="types.PostInteractionCountersStory")
class PostInteractionCountersStory(TLObject):
    story_id: Int = TLField()
    views: Int = TLField()
    forwards: Int = TLField()
    reactions: Int = TLField()
