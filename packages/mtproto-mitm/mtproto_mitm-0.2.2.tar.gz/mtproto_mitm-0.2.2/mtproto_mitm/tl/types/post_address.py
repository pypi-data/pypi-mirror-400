from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1e8caaeb, name="types.PostAddress")
class PostAddress(TLObject):
    street_line1: str = TLField()
    street_line2: str = TLField()
    city: str = TLField()
    state: str = TLField()
    country_iso2: str = TLField()
    post_code: str = TLField()
