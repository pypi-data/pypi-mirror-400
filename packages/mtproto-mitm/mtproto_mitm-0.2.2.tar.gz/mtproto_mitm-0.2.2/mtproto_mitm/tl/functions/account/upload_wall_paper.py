from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe39a8f03, name="functions.account.UploadWallPaper")
class UploadWallPaper(TLObject):
    flags: Int = TLField(is_flags=True)
    for_chat: bool = TLField(flag=1 << 0)
    file: TLObject = TLField()
    mime_type: str = TLField()
    settings: TLObject = TLField()
