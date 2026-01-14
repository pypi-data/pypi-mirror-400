from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1142bd56, name="types.SavedPhoneContact")
class SavedPhoneContact(TLObject):
    phone: str = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
    date: Int = TLField()
