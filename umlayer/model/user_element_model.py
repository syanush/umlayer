from pydantic import BaseModel


class UserElementModel(BaseModel):
    x: float
    y: float
