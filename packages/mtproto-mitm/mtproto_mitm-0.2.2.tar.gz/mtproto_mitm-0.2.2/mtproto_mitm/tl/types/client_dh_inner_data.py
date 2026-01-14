from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x6643b654, name="types.ClientDHInnerData")
class ClientDHInnerData(TLObject):
    nonce: Int128 = TLField()
    server_nonce: Int128 = TLField()
    retry_id: Long = TLField()
    g_b: bytes = TLField()
