from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentHubConfig:
    base_url: str
    attp_url: str
    agt_key: str
    organization_id: int


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name, default)
    return value.strip() or default


def load_agenthub_config() -> AgentHubConfig:
    base_url = _get_env("AGENTHUB__BASE_URL", "http://localhost:8000")
    attp_url = _get_env("AGENTHUB__ATTP_URL", "attp://localhost:6563")
    agt_key = _get_env("AGENTHUB__AGT_KEY", "agt_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvcmdhbml6YXRpb25faWQiOjEsInBlcm1pc3Npb25zIjpbIioiXSwiZXhwaXJlc19hdF90aW1lc3RhbXAiOm51bGwsInV1aWQiOiJkMjQwYzI3ZC04ODRjLTQ3Y2UtOWEyOC1jZWM3NTgzZTJmYjciLCJhZG1pbmlzdHJhdGl2ZSI6dHJ1ZX0.hRL3zgVMZqvo43IPT3ZTLixLVsiayJ618bJW4DZ3kYs")
    org_raw = _get_env("AGENTHUB__ORGANIZATION_ID", "1")
    try:
        organization_id = int(org_raw)
    except ValueError:
        organization_id = 1
    return AgentHubConfig(
        base_url=base_url,
        attp_url=attp_url,
        agt_key=agt_key,
        organization_id=organization_id,
    )
