from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x75eaea5a, name="types.GeoChat_15")
class GeoChat_15(TLObject):
    id: Int = TLField()
    access_hash: Long = TLField()
    title: str = TLField()
    address: str = TLField()
    venue: str = TLField()
    geo: TLObject = TLField()
    photo: TLObject = TLField()
    participants_count: Int = TLField()
    date: Int = TLField()
    checked_in: bool = TLField()
    version: Int = TLField()
