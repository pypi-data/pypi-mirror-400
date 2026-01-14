from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbb32d7c0, name="functions.updates.GetChannelDifference_38")
class GetChannelDifference_38(TLObject):
    channel: TLObject = TLField()
    filter: TLObject = TLField()
    pts: Int = TLField()
    limit: Int = TLField()
