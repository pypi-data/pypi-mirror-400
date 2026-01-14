from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x123e05e9, name="functions.channels.GetParticipants_72")
class GetParticipants_72(TLObject):
    channel: TLObject = TLField()
    filter: TLObject = TLField()
    offset: Int = TLField()
    limit: Int = TLField()
    hash: Int = TLField()
