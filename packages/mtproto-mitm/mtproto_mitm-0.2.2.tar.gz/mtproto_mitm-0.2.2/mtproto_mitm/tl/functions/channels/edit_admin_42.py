from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xeb7611d0, name="functions.channels.EditAdmin_42")
class EditAdmin_42(TLObject):
    channel: TLObject = TLField()
    user_id: TLObject = TLField()
    role: TLObject = TLField()
