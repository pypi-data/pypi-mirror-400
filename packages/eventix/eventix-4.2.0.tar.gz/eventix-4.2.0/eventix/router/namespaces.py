import logging

from fastapi import APIRouter

from eventix.pydantic.namespaces import NamespacesResponseModel, NamespaceTaskTypesResponseModel
from eventix.functions.namespace import list_namespaces

log = logging.getLogger(__name__)

router = APIRouter(tags=["tasks"])


@router.get("/namespaces")
async def router_namespaces_get() -> NamespacesResponseModel:
    namespaces = list_namespaces()
    return NamespacesResponseModel(namespaces=namespaces)


@router.get("/namespace/{namespace}/task_types")
async def router_namespace_task_types_get(
    namespace: str,
) -> NamespaceTaskTypesResponseModel:
    raise NotImplementedError()
    # return NamespaceTaskTypesResponseModel(task_types=[])
