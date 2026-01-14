from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5f3b8a00, name="types.RequestPeerTypeUser")
class RequestPeerTypeUser(TLObject):
    flags: Int = TLField(is_flags=True)
    bot: bool = TLField(flag=1 << 0, flag_serializable=True)
    premium: bool = TLField(flag=1 << 1, flag_serializable=True)
