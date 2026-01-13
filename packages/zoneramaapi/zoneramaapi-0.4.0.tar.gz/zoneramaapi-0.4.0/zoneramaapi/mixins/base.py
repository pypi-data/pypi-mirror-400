import datetime

from zoneramaapi.models.aliases import AccountID
from zoneramaapi.zeep.common import AsyncServiceProxy, ServiceProxy


class BaseMixin:
    _api_service: ServiceProxy
    _data_service: ServiceProxy
    logged_in_as: AccountID | None
    timezone: datetime.tzinfo | None


class AsyncBaseMixin:
    _api_service: AsyncServiceProxy
    _data_service: AsyncServiceProxy
    logged_in_as: AccountID | None
    timezone: datetime.tzinfo | None
