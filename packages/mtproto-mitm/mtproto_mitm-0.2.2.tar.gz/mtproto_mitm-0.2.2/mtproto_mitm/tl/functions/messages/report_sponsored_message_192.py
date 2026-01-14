from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1af3dbb8, name="functions.messages.ReportSponsoredMessage_192")
class ReportSponsoredMessage_192(TLObject):
    peer: TLObject = TLField()
    random_id: bytes = TLField()
    option: bytes = TLField()
