from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x7b8cc2a3, name="functions.phone.DeleteConferenceCallParticipant_202")
class DeleteConferenceCallParticipant_202(TLObject):
    call: TLObject = TLField()
    peer: TLObject = TLField()
    block: bytes = TLField()
