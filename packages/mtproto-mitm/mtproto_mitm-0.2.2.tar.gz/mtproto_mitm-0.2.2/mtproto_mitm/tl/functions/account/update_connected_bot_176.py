from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9c2d527d, name="functions.account.UpdateConnectedBot_176")
class UpdateConnectedBot_176(TLObject):
    flags: Int = TLField(is_flags=True)
    can_reply: bool = TLField(flag=1 << 0)
    deleted: bool = TLField(flag=1 << 1)
    bot: TLObject = TLField()
    recipients: TLObject = TLField()
