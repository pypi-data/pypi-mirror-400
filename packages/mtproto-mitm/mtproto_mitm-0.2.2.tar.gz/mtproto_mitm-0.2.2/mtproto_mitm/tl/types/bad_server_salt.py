from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xedab447b, name="types.BadServerSalt")
class BadServerSalt(TLObject):
    bad_msg_id: Long = TLField()
    bad_msg_seqno: Int = TLField()
    error_code: Int = TLField()
    new_server_salt: Long = TLField()
