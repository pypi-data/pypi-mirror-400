from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2df5fc0a, name="types.ChannelAdminLogEventActionDefaultBannedRights")
class ChannelAdminLogEventActionDefaultBannedRights(TLObject):
    prev_banned_rights: TLObject = TLField()
    new_banned_rights: TLObject = TLField()
