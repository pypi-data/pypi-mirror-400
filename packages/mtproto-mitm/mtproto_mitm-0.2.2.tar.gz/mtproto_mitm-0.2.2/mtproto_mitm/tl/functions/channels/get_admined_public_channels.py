from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf8b036af, name="functions.channels.GetAdminedPublicChannels")
class GetAdminedPublicChannels(TLObject):
    flags: Int = TLField(is_flags=True)
    by_location: bool = TLField(flag=1 << 0)
    check_limit: bool = TLField(flag=1 << 1)
    for_personal: bool = TLField(flag=1 << 2)
