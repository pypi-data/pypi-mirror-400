from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb88cf373, name="types.BusinessBotRecipients")
class BusinessBotRecipients(TLObject):
    flags: Int = TLField(is_flags=True)
    existing_chats: bool = TLField(flag=1 << 0)
    new_chats: bool = TLField(flag=1 << 1)
    contacts: bool = TLField(flag=1 << 2)
    non_contacts: bool = TLField(flag=1 << 3)
    exclude_selected: bool = TLField(flag=1 << 5)
    users: Optional[list[Long]] = TLField(flag=1 << 4)
    exclude_users: Optional[list[Long]] = TLField(flag=1 << 6)
