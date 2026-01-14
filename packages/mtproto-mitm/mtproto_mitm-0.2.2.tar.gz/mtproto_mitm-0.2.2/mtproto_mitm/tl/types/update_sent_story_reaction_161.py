from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe3a73d20, name="types.UpdateSentStoryReaction_161")
class UpdateSentStoryReaction_161(TLObject):
    user_id: Long = TLField()
    story_id: Int = TLField()
    reaction: TLObject = TLField()
