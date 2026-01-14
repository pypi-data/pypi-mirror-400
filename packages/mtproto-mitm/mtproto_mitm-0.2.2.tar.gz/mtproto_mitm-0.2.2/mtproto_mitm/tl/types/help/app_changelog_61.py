from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2a137e7c, name="types.help.AppChangelog_61")
class AppChangelog_61(TLObject):
    message: str = TLField()
    media: TLObject = TLField()
    entities: list[TLObject] = TLField()
