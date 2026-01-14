from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xea52fe5a, name="types.upload.FileCdnRedirect_70")
class FileCdnRedirect_70(TLObject):
    dc_id: Int = TLField()
    file_token: bytes = TLField()
    encryption_key: bytes = TLField()
    encryption_iv: bytes = TLField()
    cdn_file_hashes: list[TLObject] = TLField()
