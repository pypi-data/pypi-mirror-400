from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x831a83a2, name="functions.account.UploadRingtone")
class UploadRingtone(TLObject):
    file: TLObject = TLField()
    file_name: str = TLField()
    mime_type: str = TLField()
