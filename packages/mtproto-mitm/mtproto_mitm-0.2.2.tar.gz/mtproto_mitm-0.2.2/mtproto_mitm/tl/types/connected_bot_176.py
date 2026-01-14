from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe7e999e7, name="types.ConnectedBot_176")
class ConnectedBot_176(TLObject):
    flags: Int = TLField(is_flags=True)
    can_reply: bool = TLField(flag=1 << 0)
    bot_id: Long = TLField()
    recipients: TLObject = TLField()
