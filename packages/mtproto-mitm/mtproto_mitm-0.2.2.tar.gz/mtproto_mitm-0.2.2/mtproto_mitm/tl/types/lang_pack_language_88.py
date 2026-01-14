from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x651b98d, name="types.LangPackLanguage_88")
class LangPackLanguage_88(TLObject):
    flags: Int = TLField(is_flags=True)
    official: bool = TLField(flag=1 << 0)
    rtl: bool = TLField(flag=1 << 2)
    name: str = TLField()
    native_name: str = TLField()
    lang_code: str = TLField()
    base_lang_code: Optional[str] = TLField(flag=1 << 1)
    plural_code: str = TLField()
    strings_count: Int = TLField()
    translated_count: Int = TLField()
