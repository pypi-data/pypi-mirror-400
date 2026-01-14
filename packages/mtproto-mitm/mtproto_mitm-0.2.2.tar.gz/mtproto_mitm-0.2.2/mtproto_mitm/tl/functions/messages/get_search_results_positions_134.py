from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6e9583a3, name="functions.messages.GetSearchResultsPositions_134")
class GetSearchResultsPositions_134(TLObject):
    peer: TLObject = TLField()
    filter: TLObject = TLField()
    offset_id: Int = TLField()
    limit: Int = TLField()
