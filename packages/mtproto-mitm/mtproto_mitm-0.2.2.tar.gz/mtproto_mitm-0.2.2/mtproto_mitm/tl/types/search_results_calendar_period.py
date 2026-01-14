from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc9b0539f, name="types.SearchResultsCalendarPeriod")
class SearchResultsCalendarPeriod(TLObject):
    date: Int = TLField()
    min_msg_id: Int = TLField()
    max_msg_id: Int = TLField()
    count: Int = TLField()
