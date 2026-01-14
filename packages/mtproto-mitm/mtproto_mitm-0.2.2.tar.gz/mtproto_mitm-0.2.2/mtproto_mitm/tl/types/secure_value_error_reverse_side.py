from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x868a2aa5, name="types.SecureValueErrorReverseSide")
class SecureValueErrorReverseSide(TLObject):
    type_: TLObject = TLField()
    file_hash: bytes = TLField()
    text: str = TLField()
