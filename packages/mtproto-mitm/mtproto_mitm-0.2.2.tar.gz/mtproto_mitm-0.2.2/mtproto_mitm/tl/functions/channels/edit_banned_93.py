from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x72796912, name="functions.channels.EditBanned_93")
class EditBanned_93(TLObject):
    channel: TLObject = TLField()
    user_id: TLObject = TLField()
    banned_rights: TLObject = TLField()
