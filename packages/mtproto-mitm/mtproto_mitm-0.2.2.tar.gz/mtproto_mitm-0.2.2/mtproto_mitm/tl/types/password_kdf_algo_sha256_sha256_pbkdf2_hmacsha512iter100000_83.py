from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xb6425eaa, name="types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000_83")
class PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000_83(TLObject):
    salt1: bytes = TLField()
    salt2: bytes = TLField()
