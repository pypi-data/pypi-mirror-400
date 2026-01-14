from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x78c314e0, name="types.UpdateGroupCallMessage_217")
class UpdateGroupCallMessage_217(TLObject):
    call: TLObject = TLField()
    from_id: TLObject = TLField()
    random_id: Long = TLField()
    message: TLObject = TLField()
