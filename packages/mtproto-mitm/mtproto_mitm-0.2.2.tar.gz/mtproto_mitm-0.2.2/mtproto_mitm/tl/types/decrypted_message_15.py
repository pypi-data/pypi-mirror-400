from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1f814f1f, name="types.DecryptedMessage_15")
class DecryptedMessage_15(TLObject):
    random_id: Long = TLField()
    random_bytes: bytes = TLField()
    message: str = TLField()
    media: TLObject = TLField()
