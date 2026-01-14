from __future__ import annotations

from mtproto_mitm.tl.core_types import *
from mtproto_mitm.tl.tl_object import TLObject, tl_object, TLField
from typing import Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


@tl_object(id=0x8efab953, name="types.AutoDownloadSettings_143")
class AutoDownloadSettings_143(TLObject):
    flags: Int = TLField(is_flags=True)
    disabled: bool = TLField(flag=1 << 0)
    video_preload_large: bool = TLField(flag=1 << 1)
    audio_preload_next: bool = TLField(flag=1 << 2)
    phonecalls_less_data: bool = TLField(flag=1 << 3)
    photo_size_max: Int = TLField()
    video_size_max: Long = TLField()
    file_size_max: Long = TLField()
    video_upload_maxbitrate: Int = TLField()
