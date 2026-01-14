from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2ec0533f, name="types.MessageMediaVenue")
class MessageMediaVenue(TLObject):
    geo: TLObject = TLField()
    title: str = TLField()
    address: str = TLField()
    provider: str = TLField()
    venue_id: str = TLField()
    venue_type: str = TLField()
