from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbbf2dda0, name="types.SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000")
class SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000(TLObject):
    salt: bytes = TLField()
