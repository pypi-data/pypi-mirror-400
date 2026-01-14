from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x712c4655, name="types.stories.CanApplyBoostReplace_164")
class CanApplyBoostReplace_164(TLObject):
    current_boost: TLObject = TLField()
    chats: list[TLObject] = TLField()
