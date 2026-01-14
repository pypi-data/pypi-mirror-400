from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5b95b3d4, name="functions.phone.RequestCall_65")
class RequestCall_65(TLObject):
    user_id: TLObject = TLField()
    random_id: Int = TLField()
    g_a_hash: bytes = TLField()
    protocol: TLObject = TLField()
