from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xf95f61a4, name="functions.stories.GetStoryViewsList_161")
class GetStoryViewsList_161(TLObject):
    flags: Int = TLField(is_flags=True)
    just_contacts: bool = TLField(flag=1 << 0)
    reactions_first: bool = TLField(flag=1 << 2)
    q: Optional[str] = TLField(flag=1 << 1)
    id: Int = TLField()
    offset: str = TLField()
    limit: Int = TLField()
