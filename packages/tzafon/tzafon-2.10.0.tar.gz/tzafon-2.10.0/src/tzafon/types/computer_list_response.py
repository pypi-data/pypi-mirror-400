# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["ComputerListResponse", "ComputerListResponseItem"]


class ComputerListResponseItem(BaseModel):
    id: Optional[str] = None

    created_at: Optional[str] = None

    endpoints: Optional[Dict[str, str]] = None

    kind: Optional[str] = None

    status: Optional[str] = None


ComputerListResponse: TypeAlias = List[ComputerListResponseItem]
