from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x1508485a, name="types.upload.FileCdnRedirect_66")
class FileCdnRedirect_66(TLObject):
    dc_id: Int = TLField()
    file_token: bytes = TLField()
    encryption_key: bytes = TLField()
    encryption_iv: bytes = TLField()
