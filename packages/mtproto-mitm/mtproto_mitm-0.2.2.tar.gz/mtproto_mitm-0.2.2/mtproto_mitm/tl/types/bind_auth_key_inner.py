from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x75a3f765, name="types.BindAuthKeyInner")
class BindAuthKeyInner(TLObject):
    nonce: Long = TLField()
    temp_auth_key_id: Long = TLField()
    perm_auth_key_id: Long = TLField()
    temp_session_id: Long = TLField()
    expires_at: Int = TLField()
