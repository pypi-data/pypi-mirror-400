from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x553f32eb, name="types.InputWebFileGeoMessageLocation_79")
class InputWebFileGeoMessageLocation_79(TLObject):
    peer: TLObject = TLField()
    msg_id: Int = TLField()
    w: Int = TLField()
    h: Int = TLField()
    zoom: Int = TLField()
    scale: Int = TLField()
