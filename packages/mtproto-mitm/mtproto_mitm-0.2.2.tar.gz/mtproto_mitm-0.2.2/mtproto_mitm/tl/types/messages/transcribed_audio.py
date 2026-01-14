from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcfb9d957, name="types.messages.TranscribedAudio")
class TranscribedAudio(TLObject):
    flags: Int = TLField(is_flags=True)
    pending: bool = TLField(flag=1 << 0)
    transcription_id: Long = TLField()
    text: str = TLField()
    trial_remains_num: Optional[Int] = TLField(flag=1 << 1)
    trial_remains_until_date: Optional[Int] = TLField(flag=1 << 1)
