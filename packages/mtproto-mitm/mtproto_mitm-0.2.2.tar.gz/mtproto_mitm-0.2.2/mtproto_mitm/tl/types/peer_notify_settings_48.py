from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9acda4c0, name="types.PeerNotifySettings_48")
class PeerNotifySettings_48(TLObject):
    flags: Int = TLField(is_flags=True)
    show_previews: bool = TLField(flag=1 << 0)
    silent: bool = TLField(flag=1 << 1)
    mute_until: Int = TLField()
    sound: str = TLField()
