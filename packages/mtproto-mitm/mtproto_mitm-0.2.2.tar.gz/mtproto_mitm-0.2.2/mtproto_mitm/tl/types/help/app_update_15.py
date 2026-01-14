from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8987f311, name="types.help.AppUpdate_15")
class AppUpdate_15(TLObject):
    id: Int = TLField()
    critical: bool = TLField()
    url: str = TLField()
    text: str = TLField()
