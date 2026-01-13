from pydantic import BaseModel


class RelayModel(BaseModel):
    url: str
    namespace: str
