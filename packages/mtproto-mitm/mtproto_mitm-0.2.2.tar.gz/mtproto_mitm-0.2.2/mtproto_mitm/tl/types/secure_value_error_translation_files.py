from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x34636dd8, name="types.SecureValueErrorTranslationFiles")
class SecureValueErrorTranslationFiles(TLObject):
    type_: TLObject = TLField()
    file_hash: list[bytes] = TLField()
    text: str = TLField()
