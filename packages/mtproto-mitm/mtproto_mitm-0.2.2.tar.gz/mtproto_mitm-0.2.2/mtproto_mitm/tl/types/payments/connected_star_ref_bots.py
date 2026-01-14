from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x98d5ea1d, name="types.payments.ConnectedStarRefBots")
class ConnectedStarRefBots(TLObject):
    count: Int = TLField()
    connected_bots: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
