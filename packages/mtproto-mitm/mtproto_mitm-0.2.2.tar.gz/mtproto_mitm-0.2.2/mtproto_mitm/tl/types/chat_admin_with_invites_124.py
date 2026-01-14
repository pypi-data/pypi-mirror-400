from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xdfd2330f, name="types.ChatAdminWithInvites_124")
class ChatAdminWithInvites_124(TLObject):
    admin_id: Int = TLField()
    invites_count: Int = TLField()
    revoked_invites_count: Int = TLField()
