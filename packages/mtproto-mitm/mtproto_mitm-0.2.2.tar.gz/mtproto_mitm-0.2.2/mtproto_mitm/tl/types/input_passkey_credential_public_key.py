from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x3c27b78f, name="types.InputPasskeyCredentialPublicKey")
class InputPasskeyCredentialPublicKey(TLObject):
    id: str = TLField()
    raw_id: str = TLField()
    response: TLObject = TLField()
