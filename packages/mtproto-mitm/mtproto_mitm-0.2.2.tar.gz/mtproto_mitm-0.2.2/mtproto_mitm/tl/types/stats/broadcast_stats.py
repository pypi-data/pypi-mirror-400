from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x396ca5fc, name="types.stats.BroadcastStats")
class BroadcastStats(TLObject):
    period: TLObject = TLField()
    followers: TLObject = TLField()
    views_per_post: TLObject = TLField()
    shares_per_post: TLObject = TLField()
    reactions_per_post: TLObject = TLField()
    views_per_story: TLObject = TLField()
    shares_per_story: TLObject = TLField()
    reactions_per_story: TLObject = TLField()
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
    reactions_by_emotion_graph: TLObject = TLField()
    story_interactions_graph: TLObject = TLField()
    story_reactions_by_emotion_graph: TLObject = TLField()
    recent_posts_interactions: list[TLObject] = TLField()
