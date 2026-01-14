from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbe82db9c, name="types.MediaAreaVenue")
class MediaAreaVenue(TLObject):
    coordinates: TLObject = TLField()
    geo: TLObject = TLField()
    title: str = TLField()
    address: str = TLField()
    provider: str = TLField()
    venue_id: str = TLField()
    venue_type: str = TLField()
