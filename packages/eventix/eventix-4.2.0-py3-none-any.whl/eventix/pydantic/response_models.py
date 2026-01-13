from typing import List

from eventix.pydantic.pagination import PaginationResultModel
from eventix.pydantic.task import TEventixTask


class RouterTasksResponseModel(PaginationResultModel):
    data: List[TEventixTask]
