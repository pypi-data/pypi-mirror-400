from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x05162463, name="types.ResPQ")
class ResPQ(TLObject):
    nonce: Int128 = TLField()
    server_nonce: Int128 = TLField()
    pq: bytes = TLField()
    server_public_key_fingerprints: list[Long] = TLField()
