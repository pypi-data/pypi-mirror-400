from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x317ceef4, name="types.Config_48")
class Config_48(TLObject):
    date: Int = TLField()
    expires: Int = TLField()
    test_mode: bool = TLField()
    this_dc: Int = TLField()
    dc_options: list[TLObject] = TLField()
    chat_size_max: Int = TLField()
    megagroup_size_max: Int = TLField()
    forwarded_count_max: Int = TLField()
    online_update_period_ms: Int = TLField()
    offline_blur_timeout_ms: Int = TLField()
    offline_idle_timeout_ms: Int = TLField()
    online_cloud_timeout_ms: Int = TLField()
    notify_cloud_delay_ms: Int = TLField()
    notify_default_delay_ms: Int = TLField()
    chat_big_size: Int = TLField()
    push_chat_period_ms: Int = TLField()
    push_chat_limit: Int = TLField()
    saved_gifs_limit: Int = TLField()
    edit_time_limit: Int = TLField()
    disabled_features: list[TLObject] = TLField()
