from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe9723804, name="functions.phone.ToggleGroupCallSettings_217")
class ToggleGroupCallSettings_217(TLObject):
    flags: Int = TLField(is_flags=True)
    reset_invite_hash: bool = TLField(flag=1 << 1)
    call: TLObject = TLField()
    join_muted: bool = TLField(flag=1 << 0, flag_serializable=True)
    messages_enabled: bool = TLField(flag=1 << 2, flag_serializable=True)
