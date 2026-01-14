from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1c3db333, name="functions.account.UploadTheme")
class UploadTheme(TLObject):
    flags: Int = TLField(is_flags=True)
    file: TLObject = TLField()
    thumb: Optional[TLObject] = TLField(flag=1 << 0)
    file_name: str = TLField()
    mime_type: str = TLField()
