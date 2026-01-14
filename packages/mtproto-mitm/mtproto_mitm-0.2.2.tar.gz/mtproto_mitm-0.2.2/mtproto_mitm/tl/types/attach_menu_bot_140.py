from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe93cb772, name="types.AttachMenuBot_140")
class AttachMenuBot_140(TLObject):
    flags: Int = TLField(is_flags=True)
    inactive: bool = TLField(flag=1 << 0)
    bot_id: Long = TLField()
    short_name: str = TLField()
    icons: list[TLObject] = TLField()
