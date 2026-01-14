from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xaf509d20, name="types.PeerNotifySettings_79")
class PeerNotifySettings_79(TLObject):
    flags: Int = TLField(is_flags=True)
    show_previews: bool = TLField(flag=1 << 0, flag_serializable=True)
    silent: bool = TLField(flag=1 << 1, flag_serializable=True)
    mute_until: Optional[Int] = TLField(flag=1 << 2)
    sound: Optional[str] = TLField(flag=1 << 3)
