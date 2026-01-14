from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe8f463d0, name="functions.contacts.AddContact_102")
class AddContact_102(TLObject):
    flags: Int = TLField(is_flags=True)
    add_phone_privacy_exception: bool = TLField(flag=1 << 0)
    id: TLObject = TLField()
    first_name: str = TLField()
    last_name: str = TLField()
    phone: str = TLField()
