from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x57e28221, name="types.account.ContentSettings")
class ContentSettings(TLObject):
    flags: Int = TLField(is_flags=True)
    sensitive_enabled: bool = TLField(flag=1 << 0)
    sensitive_can_change: bool = TLField(flag=1 << 1)
