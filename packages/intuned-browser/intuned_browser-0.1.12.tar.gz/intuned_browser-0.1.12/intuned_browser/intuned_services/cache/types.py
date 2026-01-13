from typing import Any
from typing import Optional

from pydantic import BaseModel


class CacheGetResponse(BaseModel):
    value: Optional[dict[str, Any]] = None


class CacheSetResponse(BaseModel):
    pass


class CacheSetRequest(BaseModel):
    value: Any
