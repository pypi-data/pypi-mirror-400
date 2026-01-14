from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5d8c6cc, name="types.DcOption_31")
class DcOption_31(TLObject):
    flags: Int = TLField(is_flags=True)
    id: Int = TLField()
    ip_address: str = TLField()
    port: Int = TLField()
