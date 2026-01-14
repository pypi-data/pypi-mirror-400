from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xd7a2fcf9, name="types.auth.SentCodePaymentRequired_214")
class SentCodePaymentRequired_214(TLObject):
    store_product: str = TLField()
    phone_code_hash: str = TLField()
    support_email_address: str = TLField()
    support_email_subject: str = TLField()
