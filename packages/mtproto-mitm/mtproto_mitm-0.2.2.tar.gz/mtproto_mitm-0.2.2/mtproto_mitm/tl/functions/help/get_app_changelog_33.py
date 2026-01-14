from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x5bab7fb2, name="functions.help.GetAppChangelog_33")
class GetAppChangelog_33(TLObject):
    device_model: str = TLField()
    system_version: str = TLField()
    app_version: str = TLField()
    lang_code: str = TLField()
