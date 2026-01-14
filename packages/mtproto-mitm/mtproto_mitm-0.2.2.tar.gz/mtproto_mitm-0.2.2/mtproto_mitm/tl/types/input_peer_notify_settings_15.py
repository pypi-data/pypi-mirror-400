from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x46a2ce98, name="types.InputPeerNotifySettings_15")
class InputPeerNotifySettings_15(TLObject):
    mute_until: Int = TLField()
    sound: str = TLField()
    show_previews: bool = TLField()
    events_mask: Int = TLField()
