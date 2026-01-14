from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x70f893ba, name="functions.channels.EditAdmin_93")
class EditAdmin_93(TLObject):
    channel: TLObject = TLField()
    user_id: TLObject = TLField()
    admin_rights: TLObject = TLField()
