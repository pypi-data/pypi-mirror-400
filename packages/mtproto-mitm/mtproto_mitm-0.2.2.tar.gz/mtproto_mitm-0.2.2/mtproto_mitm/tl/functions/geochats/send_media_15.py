from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb8f0deff, name="functions.geochats.SendMedia_15")
class SendMedia_15(TLObject):
    peer: TLObject = TLField()
    media: TLObject = TLField()
    random_id: Long = TLField()
