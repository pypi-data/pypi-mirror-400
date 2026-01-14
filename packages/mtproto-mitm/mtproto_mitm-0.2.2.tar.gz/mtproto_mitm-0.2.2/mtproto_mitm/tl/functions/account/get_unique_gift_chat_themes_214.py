from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfe74ef9f, name="functions.account.GetUniqueGiftChatThemes_214")
class GetUniqueGiftChatThemes_214(TLObject):
    offset: Int = TLField()
    limit: Int = TLField()
    hash: Long = TLField()
