from datetime import datetime

from pydantic import BaseModel

from bpkio_api.models.common import PropertyMixin


class LoginCredentials(BaseModel, PropertyMixin):
    email: str
    password: str


class LoginResponse(BaseModel, PropertyMixin):
    email: str
    token: str
    expirationDate: datetime
