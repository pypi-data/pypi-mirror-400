from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x51a48a9a, name="types.UpdateContactLink_15")
class UpdateContactLink_15(TLObject):
    user_id: Int = TLField()
    my_link: TLObject = TLField()
    foreign_link: TLObject = TLField()
