from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, PrivateAttr

from bpkio_api.models.common import NamedModel


class Tenant(NamedModel):
    id: Optional[int] = None

    # Optional to allow cases in initialisation where we create fake tenants
    email: Optional[str] = None
    # TODO - Turn to enum
    commercialPlan: str
    # TODO - Turn to enum
    state: str
    sendAnalytics: bool = False
    creationDate: datetime
    updateDate: datetime
    subscriptionDate: Optional[datetime] = None
    expirationDate: Optional[datetime] = None

    _fqdn: str = PrivateAttr()

    model_config = ConfigDict(extra="allow")
