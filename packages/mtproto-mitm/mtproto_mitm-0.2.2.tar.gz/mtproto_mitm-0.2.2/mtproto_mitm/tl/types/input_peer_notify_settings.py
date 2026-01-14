from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xcacb6ae2, name="types.InputPeerNotifySettings")
class InputPeerNotifySettings(TLObject):
    flags: Int = TLField(is_flags=True)
    show_previews: bool = TLField(flag=1 << 0, flag_serializable=True)
    silent: bool = TLField(flag=1 << 1, flag_serializable=True)
    mute_until: Optional[Int] = TLField(flag=1 << 2)
    sound: Optional[TLObject] = TLField(flag=1 << 3)
    stories_muted: bool = TLField(flag=1 << 6, flag_serializable=True)
    stories_hide_sender: bool = TLField(flag=1 << 7, flag_serializable=True)
    stories_sound: Optional[TLObject] = TLField(flag=1 << 8)
