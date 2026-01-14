from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xef7ff916, name="types.stats.MegagroupStats")
class MegagroupStats(TLObject):
    period: TLObject = TLField()
    members: TLObject = TLField()
    messages: TLObject = TLField()
    viewers: TLObject = TLField()
    posters: TLObject = TLField()
    growth_graph: TLObject = TLField()
    members_graph: TLObject = TLField()
    new_members_by_source_graph: TLObject = TLField()
    languages_graph: TLObject = TLField()
    messages_graph: TLObject = TLField()
    actions_graph: TLObject = TLField()
    top_hours_graph: TLObject = TLField()
    weekdays_graph: TLObject = TLField()
    top_posters: list[TLObject] = TLField()
    top_admins: list[TLObject] = TLField()
    top_inviters: list[TLObject] = TLField()
    users: list[TLObject] = TLField()
