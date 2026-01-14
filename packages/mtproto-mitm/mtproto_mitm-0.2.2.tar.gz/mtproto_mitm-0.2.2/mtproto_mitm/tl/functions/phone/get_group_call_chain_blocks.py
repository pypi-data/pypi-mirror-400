from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xee9f88a6, name="functions.phone.GetGroupCallChainBlocks")
class GetGroupCallChainBlocks(TLObject):
    call: TLObject = TLField()
    sub_chain_id: Int = TLField()
    offset: Int = TLField()
    limit: Int = TLField()
