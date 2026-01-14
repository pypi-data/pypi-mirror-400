from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7c596b46, name="types.FileLocationUnavailable_15")
class FileLocationUnavailable_15(TLObject):
    volume_id: Long = TLField()
    local_id: Int = TLField()
    secret: Long = TLField()
