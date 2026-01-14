from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc0944820, name="types.MessageActionTopicEdit")
class MessageActionTopicEdit(TLObject):
    flags: Int = TLField(is_flags=True)
    title: Optional[str] = TLField(flag=1 << 0)
    icon_emoji_id: Optional[Long] = TLField(flag=1 << 1)
    closed: bool = TLField(flag=1 << 2, flag_serializable=True)
    hidden: bool = TLField(flag=1 << 3, flag_serializable=True)
