from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x54c01850, name="types.UpdateChatDefaultBannedRights")
class UpdateChatDefaultBannedRights(TLObject):
    peer: TLObject = TLField()
    default_banned_rights: TLObject = TLField()
    version: Int = TLField()
