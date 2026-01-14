from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x78e41663, name="types.GroupCallParticipantVideo_129")
class GroupCallParticipantVideo_129(TLObject):
    flags: Int = TLField(is_flags=True)
    paused: bool = TLField(flag=1 << 0)
    endpoint: str = TLField()
    source_groups: list[TLObject] = TLField()
