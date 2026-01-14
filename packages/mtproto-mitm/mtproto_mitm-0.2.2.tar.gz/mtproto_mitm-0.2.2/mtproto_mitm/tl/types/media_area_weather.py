from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x49a6549c, name="types.MediaAreaWeather")
class MediaAreaWeather(TLObject):
    coordinates: TLObject = TLField()
    emoji: str = TLField()
    temperature_c: float = TLField()
    color: Int = TLField()
