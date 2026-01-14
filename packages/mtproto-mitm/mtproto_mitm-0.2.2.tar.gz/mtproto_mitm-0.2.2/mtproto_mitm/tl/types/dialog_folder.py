from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x71bd134c, name="types.DialogFolder")
class DialogFolder(TLObject):
    flags: Int = TLField(is_flags=True)
    pinned: bool = TLField(flag=1 << 2)
    folder: TLObject = TLField()
    peer: TLObject = TLField()
    top_message: Int = TLField()
    unread_muted_peers_count: Int = TLField()
    unread_unmuted_peers_count: Int = TLField()
    unread_muted_messages_count: Int = TLField()
    unread_unmuted_messages_count: Int = TLField()
