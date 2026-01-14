from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd0a48c4, name="functions.messages.GetCommonChats_58")
class GetCommonChats_58(TLObject):
    user_id: TLObject = TLField()
    max_id: Int = TLField()
    limit: Int = TLField()
