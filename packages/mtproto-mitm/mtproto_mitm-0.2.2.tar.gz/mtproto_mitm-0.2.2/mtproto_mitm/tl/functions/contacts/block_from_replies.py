from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x29a8962c, name="functions.contacts.BlockFromReplies")
class BlockFromReplies(TLObject):
    flags: Int = TLField(is_flags=True)
    delete_message: bool = TLField(flag=1 << 0)
    delete_history: bool = TLField(flag=1 << 1)
    report_spam: bool = TLField(flag=1 << 2)
    msg_id: Int = TLField()
