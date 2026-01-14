from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x2000bcc3, name="functions.upload.GetCdnFile_66")
class GetCdnFile_66(TLObject):
    file_token: bytes = TLField()
    offset: Int = TLField()
    limit: Int = TLField()
