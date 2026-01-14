from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa477288f, name="types.UpdateGroupCallChainBlocks")
class UpdateGroupCallChainBlocks(TLObject):
    call: TLObject = TLField()
    sub_chain_id: Int = TLField()
    blocks: list[bytes] = TLField()
    next_offset: Int = TLField()
