from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xab3a99ac, name="types.Dialog_15")
class Dialog_15(TLObject):
    peer: TLObject = TLField()
    top_message: Int = TLField()
    unread_count: Int = TLField()
    notify_settings: TLObject = TLField()
