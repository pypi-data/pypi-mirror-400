from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x18d1cdc2, name="types.BotInlineMessageMediaContact")
class BotInlineMessageMediaContact(TLObject):
    flags: Int = TLField(is_flags=True)
    phone_number: str = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
    vcard: str = TLField()
    reply_markup: Optional[TLObject] = TLField(flag=1 << 2)
