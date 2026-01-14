from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe6df7378, name="functions.messages.StartBot")
class StartBot(TLObject):
    bot: TLObject = TLField()
    peer: TLObject = TLField()
    random_id: Long = TLField()
    start_param: str = TLField()
