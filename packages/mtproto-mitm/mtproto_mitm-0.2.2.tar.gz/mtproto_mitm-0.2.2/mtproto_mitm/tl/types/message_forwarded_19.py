from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa367e716, name="types.MessageForwarded_19")
class MessageForwarded_19(TLObject):
    flags: Int = TLField()
    id: Int = TLField()
    fwd_from_id: Int = TLField()
    fwd_date: Int = TLField()
    from_id: Int = TLField()
    to_id: TLObject = TLField()
    date: Int = TLField()
    message: str = TLField()
    media: TLObject = TLField()
