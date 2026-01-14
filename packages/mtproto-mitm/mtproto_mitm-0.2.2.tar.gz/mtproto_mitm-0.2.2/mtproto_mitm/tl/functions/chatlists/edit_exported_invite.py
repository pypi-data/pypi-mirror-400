from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x653db63d, name="functions.chatlists.EditExportedInvite")
class EditExportedInvite(TLObject):
    flags: Int = TLField(is_flags=True)
    chatlist: TLObject = TLField()
    slug: str = TLField()
    title: Optional[str] = TLField(flag=1 << 1)
    peers: Optional[list[TLObject]] = TLField(flag=1 << 2)
