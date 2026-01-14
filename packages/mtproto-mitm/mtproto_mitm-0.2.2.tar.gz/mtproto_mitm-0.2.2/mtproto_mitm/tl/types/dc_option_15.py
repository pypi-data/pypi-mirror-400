from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2ec2a43c, name="types.DcOption_15")
class DcOption_15(TLObject):
    id: Int = TLField()
    hostname: str = TLField()
    ip_address: str = TLField()
    port: Int = TLField()
