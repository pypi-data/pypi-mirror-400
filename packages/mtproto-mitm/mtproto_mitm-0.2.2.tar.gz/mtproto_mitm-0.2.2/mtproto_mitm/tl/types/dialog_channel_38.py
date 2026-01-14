from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5b8496b2, name="types.DialogChannel_38")
class DialogChannel_38(TLObject):
    peer: TLObject = TLField()
    top_message: Int = TLField()
    top_important_message: Int = TLField()
    read_inbox_max_id: Int = TLField()
    unread_count: Int = TLField()
    unread_important_count: Int = TLField()
    notify_settings: TLObject = TLField()
    pts: Int = TLField()
