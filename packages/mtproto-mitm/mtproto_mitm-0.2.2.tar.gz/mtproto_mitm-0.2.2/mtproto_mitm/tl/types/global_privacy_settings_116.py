from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbea2f424, name="types.GlobalPrivacySettings_116")
class GlobalPrivacySettings_116(TLObject):
    flags: Int = TLField(is_flags=True)
    archive_and_mute_new_noncontact_peers: bool = TLField(flag=1 << 0, flag_serializable=True)
