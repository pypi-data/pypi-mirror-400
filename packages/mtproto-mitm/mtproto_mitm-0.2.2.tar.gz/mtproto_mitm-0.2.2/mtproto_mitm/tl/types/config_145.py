from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x232566ac, name="types.Config_145")
class Config_145(TLObject):
    flags: Int = TLField(is_flags=True)
    phonecalls_enabled: bool = TLField(flag=1 << 1)
    default_p2p_contacts: bool = TLField(flag=1 << 3)
    preload_featured_stickers: bool = TLField(flag=1 << 4)
    ignore_phone_entities: bool = TLField(flag=1 << 5)
    revoke_pm_inbox: bool = TLField(flag=1 << 6)
    blocked_mode: bool = TLField(flag=1 << 8)
    pfs_enabled: bool = TLField(flag=1 << 13)
    force_try_ipv6: bool = TLField(flag=1 << 14)
    date: Int = TLField()
    expires: Int = TLField()
    test_mode: bool = TLField()
    this_dc: Int = TLField()
    dc_options: list[TLObject] = TLField()
    dc_txt_domain_name: str = TLField()
    chat_size_max: Int = TLField()
    megagroup_size_max: Int = TLField()
    forwarded_count_max: Int = TLField()
    online_update_period_ms: Int = TLField()
    offline_blur_timeout_ms: Int = TLField()
    offline_idle_timeout_ms: Int = TLField()
    online_cloud_timeout_ms: Int = TLField()
    notify_cloud_delay_ms: Int = TLField()
    notify_default_delay_ms: Int = TLField()
    push_chat_period_ms: Int = TLField()
    push_chat_limit: Int = TLField()
    saved_gifs_limit: Int = TLField()
    edit_time_limit: Int = TLField()
    revoke_time_limit: Int = TLField()
    revoke_pm_time_limit: Int = TLField()
    rating_e_decay: Int = TLField()
    stickers_recent_limit: Int = TLField()
    stickers_faved_limit: Int = TLField()
    channels_read_media_period: Int = TLField()
    tmp_sessions: Optional[Int] = TLField(flag=1 << 0)
    pinned_dialogs_count_max: Int = TLField()
    pinned_infolder_count_max: Int = TLField()
    call_receive_timeout_ms: Int = TLField()
    call_ring_timeout_ms: Int = TLField()
    call_connect_timeout_ms: Int = TLField()
    call_packet_timeout_ms: Int = TLField()
    me_url_prefix: str = TLField()
    autoupdate_url_prefix: Optional[str] = TLField(flag=1 << 7)
    gif_search_username: Optional[str] = TLField(flag=1 << 9)
    venue_search_username: Optional[str] = TLField(flag=1 << 10)
    img_search_username: Optional[str] = TLField(flag=1 << 11)
    static_maps_provider: Optional[str] = TLField(flag=1 << 12)
    caption_length_max: Int = TLField()
    message_length_max: Int = TLField()
    webfile_dc_id: Int = TLField()
    suggested_lang_code: Optional[str] = TLField(flag=1 << 2)
    lang_pack_version: Optional[Int] = TLField(flag=1 << 2)
    base_lang_pack_version: Optional[Int] = TLField(flag=1 << 2)
    reactions_default: Optional[TLObject] = TLField(flag=1 << 15)
