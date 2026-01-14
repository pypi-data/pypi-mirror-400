from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x92d33a0e, name="types.UrlAuthResultRequest")
class UrlAuthResultRequest(TLObject):
    flags: Int = TLField(is_flags=True)
    request_write_access: bool = TLField(flag=1 << 0)
    bot: TLObject = TLField()
    domain: str = TLField()
