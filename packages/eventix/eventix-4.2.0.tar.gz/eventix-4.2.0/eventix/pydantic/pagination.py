from typing import Any, Dict, List

from pydantic import BaseModel


class PaginationParametersModel(BaseModel):
    skip: int | None = 0
    limit: int | None = 25
    sort: List[Dict] | None = None


class PaginationResultModel(PaginationParametersModel):
    data: Any
    max_results: int | None = 0
