from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa2bb35cb, name="types.PhoneCallProtocol_61")
class PhoneCallProtocol_61(TLObject):
    flags: Int = TLField(is_flags=True)
    udp_p2p: bool = TLField(flag=1 << 0)
    udp_reflector: bool = TLField(flag=1 << 1)
    min_layer: Int = TLField()
    max_layer: Int = TLField()
