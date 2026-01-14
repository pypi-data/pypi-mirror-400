from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf4893d7f, name="functions.channels.CreateChannel_41")
class CreateChannel_41(TLObject):
    flags: Int = TLField(is_flags=True)
    broadcast: bool = TLField(flag=1 << 0)
    megagroup: bool = TLField(flag=1 << 1)
    title: str = TLField()
    about: str = TLField()
