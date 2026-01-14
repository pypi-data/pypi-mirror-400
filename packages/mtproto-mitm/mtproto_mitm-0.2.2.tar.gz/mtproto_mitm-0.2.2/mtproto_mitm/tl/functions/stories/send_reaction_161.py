from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x49aaa9b3, name="functions.stories.SendReaction_161")
class SendReaction_161(TLObject):
    flags: Int = TLField(is_flags=True)
    add_to_recent: bool = TLField(flag=1 << 0)
    user_id: TLObject = TLField()
    story_id: Int = TLField()
    reaction: TLObject = TLField()
