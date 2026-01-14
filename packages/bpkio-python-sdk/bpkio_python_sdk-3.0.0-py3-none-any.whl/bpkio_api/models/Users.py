from datetime import datetime
from typing import Optional

from bpkio_api.models.common import BaseResource
from pydantic import ConfigDict


class User(BaseResource):
    firstName: str
    lastName: str
    email: str
    tenantId: Optional[int] = None

    creationDate: datetime
    updateDate: datetime

    model_config = ConfigDict(extra="allow")

    @property
    def name(self):
        return "{} {}".format(self.firstName, self.lastName)
