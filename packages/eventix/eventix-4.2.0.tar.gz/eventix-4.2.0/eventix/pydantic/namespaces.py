from typing import List

from pydantic import BaseModel


class NamespacesResponseModel(BaseModel):
    namespaces: List[str]


class NamespaceTaskTypesResponseModel(BaseModel):
    task_types: List[str]
