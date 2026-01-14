from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x9df4faad, name="functions.stats.GetBroadcastRevenueWithdrawalUrl_192")
class GetBroadcastRevenueWithdrawalUrl_192(TLObject):
    peer: TLObject = TLField()
    password: TLObject = TLField()
