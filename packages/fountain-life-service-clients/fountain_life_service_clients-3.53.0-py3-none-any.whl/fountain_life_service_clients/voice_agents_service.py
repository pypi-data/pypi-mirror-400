# This file was generated automatically. Do not edit it directly.
from typing import List, TypedDict, Unpack, cast

from fountain_life_service_clients._base_client import (
    AlphaConfig,
    AlphaResponse,
    BaseClient,
)


class Meta(TypedDict):
    description: str


class VoiceName(TypedDict):
    label: str
    id: str
    meta: Meta


class GetVoiceNamesResponse(TypedDict):
    voiceNames: List[VoiceName]


class VoiceAgentsServiceClient(BaseClient):
    def __init__(self, **cfg: Unpack[AlphaConfig]):
        kwargs = {"target": "lambda://voice-agents-service:deployed", **(cfg or {})}
        super().__init__(**kwargs)

    async def get_voice_names(self):
        res = await self.client.request(
            path="/v1/v1/voice-agents/voice-names", method="GET"
        )
        return cast(AlphaResponse[GetVoiceNamesResponse], res)
