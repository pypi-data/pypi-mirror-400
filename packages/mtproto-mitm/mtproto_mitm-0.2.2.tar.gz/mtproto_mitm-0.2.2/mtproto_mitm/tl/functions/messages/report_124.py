from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8953ab4e, name="functions.messages.Report_124")
class Report_124(TLObject):
    peer: TLObject = TLField()
    id: list[Int] = TLField()
    reason: TLObject = TLField()
    message: str = TLField()
