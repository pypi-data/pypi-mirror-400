from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xad524315, name="types.contacts.ImportedContacts_15")
class ImportedContacts_15(TLObject):
    imported: list[TLObject] = TLField()
    retry_contacts: list[Long] = TLField()
    users: list[TLObject] = TLField()
