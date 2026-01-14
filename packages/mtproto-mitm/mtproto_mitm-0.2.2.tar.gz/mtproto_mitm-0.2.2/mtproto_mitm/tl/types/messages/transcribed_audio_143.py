from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x93752c52, name="types.messages.TranscribedAudio_143")
class TranscribedAudio_143(TLObject):
    flags: Int = TLField(is_flags=True)
    pending: bool = TLField(flag=1 << 0)
    transcription_id: Long = TLField()
    text: str = TLField()
