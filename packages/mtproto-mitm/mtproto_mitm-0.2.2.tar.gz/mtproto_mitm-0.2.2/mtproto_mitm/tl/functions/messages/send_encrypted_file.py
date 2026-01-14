from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5559481d, name="functions.messages.SendEncryptedFile")
class SendEncryptedFile(TLObject):
    flags: Int = TLField(is_flags=True)
    silent: bool = TLField(flag=1 << 0)
    peer: TLObject = TLField()
    random_id: Long = TLField()
    data: bytes = TLField()
    file: TLObject = TLField()
