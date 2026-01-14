from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3dbc0415, name="functions.messages.AcceptEncryption")
class AcceptEncryption(TLObject):
    peer: TLObject = TLField()
    g_b: bytes = TLField()
    key_fingerprint: Long = TLField()
