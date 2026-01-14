from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xa365df7a, name="functions.bots.SetBotInfo_155")
class SetBotInfo_155(TLObject):
    flags: Int = TLField(is_flags=True)
    lang_code: str = TLField()
    about: Optional[str] = TLField(flag=1 << 0)
    description: Optional[str] = TLField(flag=1 << 1)
