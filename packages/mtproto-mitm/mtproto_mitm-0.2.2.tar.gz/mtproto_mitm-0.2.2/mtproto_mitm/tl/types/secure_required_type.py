from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x829d99da, name="types.SecureRequiredType")
class SecureRequiredType(TLObject):
    flags: Int = TLField(is_flags=True)
    native_names: bool = TLField(flag=1 << 0)
    selfie_required: bool = TLField(flag=1 << 1)
    translation_required: bool = TLField(flag=1 << 2)
    type_: TLObject = TLField()
