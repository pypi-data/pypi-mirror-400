from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x57e0a9cb, name="types.DecryptedMessageMediaAudio_15")
class DecryptedMessageMediaAudio_15(TLObject):
    duration: Int = TLField()
    mime_type: str = TLField()
    size: Int = TLField()
    key: bytes = TLField()
    iv: bytes = TLField()
