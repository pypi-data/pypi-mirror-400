from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x99622c0c, name="types.PeerNotifySettings")
class PeerNotifySettings(TLObject):
    flags: Int = TLField(is_flags=True)
    show_previews: bool = TLField(flag=1 << 0, flag_serializable=True)
    silent: bool = TLField(flag=1 << 1, flag_serializable=True)
    mute_until: Optional[Int] = TLField(flag=1 << 2)
    ios_sound: Optional[TLObject] = TLField(flag=1 << 3)
    android_sound: Optional[TLObject] = TLField(flag=1 << 4)
    other_sound: Optional[TLObject] = TLField(flag=1 << 5)
    stories_muted: bool = TLField(flag=1 << 6, flag_serializable=True)
    stories_hide_sender: bool = TLField(flag=1 << 7, flag_serializable=True)
    stories_ios_sound: Optional[TLObject] = TLField(flag=1 << 8)
    stories_android_sound: Optional[TLObject] = TLField(flag=1 << 9)
    stories_other_sound: Optional[TLObject] = TLField(flag=1 << 10)
