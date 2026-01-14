from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc9d8df1c, name="types.GlobalPrivacySettings_200")
class GlobalPrivacySettings_200(TLObject):
    flags: Int = TLField(is_flags=True)
    archive_and_mute_new_noncontact_peers: bool = TLField(flag=1 << 0)
    keep_archived_unmuted: bool = TLField(flag=1 << 1)
    keep_archived_folders: bool = TLField(flag=1 << 2)
    hide_read_marks: bool = TLField(flag=1 << 3)
    new_noncontact_peers_require_premium: bool = TLField(flag=1 << 4)
    noncontact_peers_paid_stars: Optional[Long] = TLField(flag=1 << 5)
