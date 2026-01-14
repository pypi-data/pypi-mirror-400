from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf393aea0, name="functions.messages.DiscardEncryption")
class DiscardEncryption(TLObject):
    flags: Int = TLField(is_flags=True)
    delete_history: bool = TLField(flag=1 << 0)
    chat_id: Int = TLField()
