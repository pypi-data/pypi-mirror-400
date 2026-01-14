from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd712e4be, name="functions.ReqDHParams")
class ReqDHParams(TLObject):
    nonce: Int128 = TLField()
    server_nonce: Int128 = TLField()
    p: bytes = TLField()
    q: bytes = TLField()
    public_key_fingerprint: Long = TLField()
    encrypted_data: bytes = TLField()
