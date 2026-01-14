from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe6300dba, name="functions.stats.GetBroadcastStats_112")
class GetBroadcastStats_112(TLObject):
    flags: Int = TLField(is_flags=True)
    dark: bool = TLField(flag=1 << 0)
    channel: TLObject = TLField()
    tz_offset: Int = TLField()
