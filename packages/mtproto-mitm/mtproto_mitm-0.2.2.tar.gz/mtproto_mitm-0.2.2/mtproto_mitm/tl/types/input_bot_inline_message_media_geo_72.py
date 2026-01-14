from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc1b15d65, name="types.InputBotInlineMessageMediaGeo_72")
class InputBotInlineMessageMediaGeo_72(TLObject):
    flags: Int = TLField(is_flags=True)
    geo_point: TLObject = TLField()
    period: Int = TLField()
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
