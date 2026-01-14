from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2e54dd74, name="types.Config_15")
class Config_15(TLObject):
    date: Int = TLField()
    test_mode: bool = TLField()
    this_dc: Int = TLField()
    dc_options: list[TLObject] = TLField()
    chat_size_max: Int = TLField()
    broadcast_size_max: Int = TLField()
