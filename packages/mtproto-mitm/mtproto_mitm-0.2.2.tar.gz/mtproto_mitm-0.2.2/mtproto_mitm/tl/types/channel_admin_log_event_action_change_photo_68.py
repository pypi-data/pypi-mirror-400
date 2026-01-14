from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb82f55c3, name="types.ChannelAdminLogEventActionChangePhoto_68")
class ChannelAdminLogEventActionChangePhoto_68(TLObject):
    prev_photo: TLObject = TLField()
    new_photo: TLObject = TLField()
