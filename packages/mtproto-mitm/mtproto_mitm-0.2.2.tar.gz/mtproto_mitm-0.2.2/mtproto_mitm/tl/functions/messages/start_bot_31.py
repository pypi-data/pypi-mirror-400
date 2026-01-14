from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1b3e0ffc, name="functions.messages.StartBot_31")
class StartBot_31(TLObject):
    bot: TLObject = TLField()
    chat_id: Int = TLField()
    random_id: Long = TLField()
    start_param: str = TLField()
