from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7f192d8f, name="functions.geochats.GetLocated_15")
class GetLocated_15(TLObject):
    geo_point: TLObject = TLField()
    radius: Int = TLField()
    limit: Int = TLField()
