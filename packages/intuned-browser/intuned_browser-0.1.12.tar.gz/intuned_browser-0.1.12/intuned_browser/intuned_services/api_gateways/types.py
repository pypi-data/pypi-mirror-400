from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Optional


class GatewayMode(Enum):
    DIRECT = "direct"
    GATEWAY = "gateway"


@dataclass
class GatewayConfig:
    functions_domain: str | None = None
    workspace_id: str | None = None
    project_id: str | None = None


@dataclass
class ModelConfig:
    model: str
    api_key: Optional[str] = None
    extra_headers: Optional[dict[str, Any]] = None
    base_url: Optional[str] = None
