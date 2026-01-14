from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xc1cd5ea9, name="functions.InitConnection")
class InitConnection(TLObject):
    flags: Int = TLField(is_flags=True)
    api_id: Int = TLField()
    device_model: str = TLField()
    system_version: str = TLField()
    app_version: str = TLField()
    system_lang_code: str = TLField()
    lang_pack: str = TLField()
    lang_code: str = TLField()
    proxy: Optional[TLObject] = TLField(flag=1 << 0)
    params: Optional[TLObject] = TLField(flag=1 << 1)
    query: TLObject = TLField()
