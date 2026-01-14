from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa72ded52, name="functions.channels.UpdatePinnedMessage_49")
class UpdatePinnedMessage_49(TLObject):
    flags: Int = TLField(is_flags=True)
    silent: bool = TLField(flag=1 << 0)
    channel: TLObject = TLField()
    id: Int = TLField()
