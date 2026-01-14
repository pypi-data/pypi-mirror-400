from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x77d01c3b, name="types.contacts.ImportedContacts")
class ImportedContacts(TLObject):
    imported: list[TLObject] = TLField()
    popular_invites: list[TLObject] = TLField()
    retry_contacts: list[Long] = TLField()
    users: list[TLObject] = TLField()
