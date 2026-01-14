from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdc0242c8, name="functions.messages.SendWebViewData")
class SendWebViewData(TLObject):
    bot: TLObject = TLField()
    random_id: Long = TLField()
    button_text: str = TLField()
    data: str = TLField()
