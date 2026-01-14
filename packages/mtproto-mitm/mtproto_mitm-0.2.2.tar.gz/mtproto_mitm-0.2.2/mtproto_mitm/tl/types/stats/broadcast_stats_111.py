from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0xbdf78394, name="types.stats.BroadcastStats_111")
class BroadcastStats_111(TLObject):
    period: TLObject = TLField()
    followers: TLObject = TLField()
    views_per_post: TLObject = TLField()
    shares_per_post: TLObject = TLField()
    enabled_notifications: TLObject = TLField()
    growth_graph: TLObject = TLField()
    followers_graph: TLObject = TLField()
    mute_graph: TLObject = TLField()
    top_hours_graph: TLObject = TLField()
    interactions_graph: TLObject = TLField()
    iv_interactions_graph: TLObject = TLField()
    views_by_source_graph: TLObject = TLField()
    new_followers_by_source_graph: TLObject = TLField()
    languages_graph: TLObject = TLField()
    recent_message_interactions: list[TLObject] = TLField()
