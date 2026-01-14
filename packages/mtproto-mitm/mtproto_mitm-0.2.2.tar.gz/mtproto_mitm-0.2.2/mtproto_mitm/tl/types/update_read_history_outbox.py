from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2f2f21bf, name="types.UpdateReadHistoryOutbox")
class UpdateReadHistoryOutbox(TLObject):
    peer: TLObject = TLField()
    max_id: Int = TLField()
    pts: Int = TLField()
    pts_count: Int = TLField()
