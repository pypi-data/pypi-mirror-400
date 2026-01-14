from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4b3b5e97, name="functions.stories.GetStoryViewsList_160")
class GetStoryViewsList_160(TLObject):
    id: Int = TLField()
    offset_date: Int = TLField()
    offset_id: Long = TLField()
    limit: Int = TLField()
