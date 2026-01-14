from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xca05d50e, name="types.InputPaymentCredentialsAndroidPay_75")
class InputPaymentCredentialsAndroidPay_75(TLObject):
    payment_token: TLObject = TLField()
    google_transaction_id: str = TLField()
