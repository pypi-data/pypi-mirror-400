from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x4c3e069d, name="types.account.AutoSaveSettings")
class AutoSaveSettings(TLObject):
    users_settings: TLObject = TLField()
    chats_settings: TLObject = TLField()
    broadcasts_settings: TLObject = TLField()
    exceptions: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
