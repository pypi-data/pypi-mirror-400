from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbe5335be, name="functions.upload.GetFile")
class GetFile(TLObject):
    flags: Int = TLField(is_flags=True)
    precise: bool = TLField(flag=1 << 0)
    cdn_supported: bool = TLField(flag=1 << 1)
    location: TLObject = TLField()
    offset: Long = TLField()
    limit: Int = TLField()
