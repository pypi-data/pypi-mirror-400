from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x220f0b20, name="functions.phone.AcceptCall_61")
class AcceptCall_61(TLObject):
    peer: TLObject = TLField()
    g_b: bytes = TLField()
    key_fingerprint: Long = TLField()
    protocol: TLObject = TLField()
