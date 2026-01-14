from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x98a12b4b, name="types.UpdateChannelMessageViews_38")
class UpdateChannelMessageViews_38(TLObject):
    channel_id: Int = TLField()
    id: Int = TLField()
    views: Int = TLField()
