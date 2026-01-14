from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x56fddf88, name="types.PQInnerDataTempDc")
class PQInnerDataTempDc(TLObject):
    pq: bytes = TLField()
    p: bytes = TLField()
    q: bytes = TLField()
    nonce: Int128 = TLField()
    server_nonce: Int128 = TLField()
    new_nonce: Int256 = TLField()
    dc: Int = TLField()
    expires_in: Int = TLField()
