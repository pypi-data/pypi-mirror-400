from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdf1f002b, name="types.InputPeerNotifySettings_140")
class InputPeerNotifySettings_140(TLObject):
    flags: Int = TLField(is_flags=True)
    show_previews: bool = TLField(flag=1 << 0, flag_serializable=True)
    silent: bool = TLField(flag=1 << 1, flag_serializable=True)
    mute_until: Optional[Int] = TLField(flag=1 << 2)
    sound: Optional[TLObject] = TLField(flag=1 << 3)
