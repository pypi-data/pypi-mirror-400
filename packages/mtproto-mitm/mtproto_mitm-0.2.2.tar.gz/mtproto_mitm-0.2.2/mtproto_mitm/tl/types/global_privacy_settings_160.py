from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x734c4ccb, name="types.GlobalPrivacySettings_160")
class GlobalPrivacySettings_160(TLObject):
    flags: Int = TLField(is_flags=True)
    archive_and_mute_new_noncontact_peers: bool = TLField(flag=1 << 0)
    keep_archived_unmuted: bool = TLField(flag=1 << 1)
    keep_archived_folders: bool = TLField(flag=1 << 2)
