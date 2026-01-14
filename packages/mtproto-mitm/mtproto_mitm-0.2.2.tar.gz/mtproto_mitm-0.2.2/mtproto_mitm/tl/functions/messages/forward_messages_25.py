from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xded42045, name="functions.messages.ForwardMessages_25")
class ForwardMessages_25(TLObject):
    peer: TLObject = TLField()
    id: list[Int] = TLField()
    random_id: list[Long] = TLField()
