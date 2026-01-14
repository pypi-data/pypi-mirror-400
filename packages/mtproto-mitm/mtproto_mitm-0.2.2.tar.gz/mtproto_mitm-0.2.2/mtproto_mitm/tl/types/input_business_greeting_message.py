from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x194cb3b, name="types.InputBusinessGreetingMessage")
class InputBusinessGreetingMessage(TLObject):
    shortcut_id: Int = TLField()
    recipients: TLObject = TLField()
    no_activity_days: Int = TLField()
