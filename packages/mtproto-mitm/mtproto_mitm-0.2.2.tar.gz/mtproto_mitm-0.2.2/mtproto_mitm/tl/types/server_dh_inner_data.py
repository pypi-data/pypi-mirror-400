from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb5890dba, name="types.ServerDHInnerData")
class ServerDHInnerData(TLObject):
    nonce: Int128 = TLField()
    server_nonce: Int128 = TLField()
    g: Int = TLField()
    dh_prime: bytes = TLField()
    g_a: bytes = TLField()
    server_time: Int = TLField()
