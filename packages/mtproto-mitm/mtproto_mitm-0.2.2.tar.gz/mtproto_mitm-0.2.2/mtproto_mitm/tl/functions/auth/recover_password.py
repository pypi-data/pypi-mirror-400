from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x37096c70, name="functions.auth.RecoverPassword")
class RecoverPassword(TLObject):
    flags: Int = TLField(is_flags=True)
    code: str = TLField()
    new_settings: Optional[TLObject] = TLField(flag=1 << 0)
