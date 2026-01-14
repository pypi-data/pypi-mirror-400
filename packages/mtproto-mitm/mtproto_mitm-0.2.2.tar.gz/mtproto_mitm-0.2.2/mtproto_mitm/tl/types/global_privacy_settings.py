from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xfe41b34f, name="types.GlobalPrivacySettings")
class GlobalPrivacySettings(TLObject):
    flags: Int = TLField(is_flags=True)
    archive_and_mute_new_noncontact_peers: bool = TLField(flag=1 << 0)
    keep_archived_unmuted: bool = TLField(flag=1 << 1)
    keep_archived_folders: bool = TLField(flag=1 << 2)
    hide_read_marks: bool = TLField(flag=1 << 3)
    new_noncontact_peers_require_premium: bool = TLField(flag=1 << 4)
    display_gifts_button: bool = TLField(flag=1 << 7)
    noncontact_peers_paid_stars: Optional[Long] = TLField(flag=1 << 5)
    disallowed_gifts: Optional[TLObject] = TLField(flag=1 << 6)
