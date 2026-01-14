from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xe0955a3c, name="types.auth.SentCodePaymentRequired")
class SentCodePaymentRequired(TLObject):
    store_product: str = TLField()
    phone_code_hash: str = TLField()
    support_email_address: str = TLField()
    support_email_subject: str = TLField()
    currency: str = TLField()
    amount: Long = TLField()
