from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5e0fb7b9, name="types.messages.HistoryImportParsed")
class HistoryImportParsed(TLObject):
    flags: Int = TLField(is_flags=True)
    pm: bool = TLField(flag=1 << 0)
    group: bool = TLField(flag=1 << 1)
    title: Optional[str] = TLField(flag=1 << 2)
