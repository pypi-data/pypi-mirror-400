from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5630281b, name="functions.stats.GetMessagePublicForwards_119")
class GetMessagePublicForwards_119(TLObject):
    channel: TLObject = TLField()
    msg_id: Int = TLField()
    offset_rate: Int = TLField()
    offset_peer: TLObject = TLField()
    offset_id: Int = TLField()
    limit: Int = TLField()
