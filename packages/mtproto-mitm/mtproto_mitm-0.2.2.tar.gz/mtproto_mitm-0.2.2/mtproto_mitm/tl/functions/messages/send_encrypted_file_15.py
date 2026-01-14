from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9a901b66, name="functions.messages.SendEncryptedFile_15")
class SendEncryptedFile_15(TLObject):
    peer: TLObject = TLField()
    random_id: Long = TLField()
    data: bytes = TLField()
    file: TLObject = TLField()
