from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb3134d9d, name="types.contacts.Found")
class Found(TLObject):
    my_results: list[TLObject] = TLField()
    results: list[TLObject] = TLField()
    chats: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
