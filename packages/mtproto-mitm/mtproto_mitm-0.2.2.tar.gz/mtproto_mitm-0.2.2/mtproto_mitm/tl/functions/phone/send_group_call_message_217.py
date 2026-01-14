from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x87893014, name="functions.phone.SendGroupCallMessage_217")
class SendGroupCallMessage_217(TLObject):
    call: TLObject = TLField()
    random_id: Long = TLField()
    message: TLObject = TLField()
