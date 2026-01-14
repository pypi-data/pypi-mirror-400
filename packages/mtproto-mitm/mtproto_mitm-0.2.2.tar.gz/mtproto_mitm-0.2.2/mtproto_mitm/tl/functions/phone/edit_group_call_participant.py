from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa5273abf, name="functions.phone.EditGroupCallParticipant")
class EditGroupCallParticipant(TLObject):
    flags: Int = TLField(is_flags=True)
    call: TLObject = TLField()
    participant: TLObject = TLField()
    muted: bool = TLField(flag=1 << 0, flag_serializable=True)
    volume: Optional[Int] = TLField(flag=1 << 1)
    raise_hand: bool = TLField(flag=1 << 2, flag_serializable=True)
    video_stopped: bool = TLField(flag=1 << 3, flag_serializable=True)
    video_paused: bool = TLField(flag=1 << 4, flag_serializable=True)
    presentation_paused: bool = TLField(flag=1 << 5, flag_serializable=True)
