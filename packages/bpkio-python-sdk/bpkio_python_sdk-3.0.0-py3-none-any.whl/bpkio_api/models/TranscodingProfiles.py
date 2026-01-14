import json
from typing import Optional

from bpkio_api.models.common import BaseResource, NamedModel


class TranscodingProfileId(BaseResource):
    pass


class TranscodingProfileIn(NamedModel):
    content: dict
    tenantId: Optional[int] = None


class TranscodingProfile(TranscodingProfileIn, BaseResource):
    internalId: str
    
    @property
    def layers(self):
        audio_layers = [a for a in self.content["audios"].keys() if a != "common"]
        video_layers = [v for v in self.content["videos"].keys() if v != "common"]
        return f"V:{len(video_layers)} A:{len(audio_layers)}"
