import datetime
from hashlib import sha256

from zoneramaapi.mixins.account import AccountMixin
from zoneramaapi.mixins.album import AlbumMixin
from zoneramaapi.mixins.photo import PhotoMixin
from zoneramaapi.mixins.tab import TabMixin
from zoneramaapi.models.aliases import AccountID
from zoneramaapi.zeep.common import ServiceProxy, raise_for_error
from zoneramaapi.zeep.sync import ZeepSyncClients


class ZoneramaClient(AccountMixin, AlbumMixin, PhotoMixin, TabMixin):
    _zeep: ZeepSyncClients
    logged_in_as: AccountID | None
    timezone: datetime.tzinfo | None

    def __init__(self):
        self._zeep = ZeepSyncClients()
        self.logged_in_as = None

    def __enter__(self):
        self._zeep.__enter__()
        return self

    def __exit__(self, *_):
        self.close()
        return

    def close(self):
        if self.logged_in:
            self.logout()
        self._zeep.close()

    def login(self, username: str, password: str) -> bool:
        service = self._zeep.api.service
        response = service.Login(username, sha256(bytes(password, "utf-8")).hexdigest())
        self.logged_in_as = response.Result if response.Success else None
        return response.Success

    def logout(self) -> bool:
        if not self.logged_in:
            return False

        service = self._zeep.api.service
        response = service.Logout()

        if response.Success:
            self.logged_in_as = None

        return response.Success

    def set_timezone(self, tz: datetime.tzinfo) -> None:
        """Set the timezone for the current session.

        Args:
            tz (datetime.tzinfo): The timezone as a datetime tzinfo object.
        """
        self._api_service.SetTimeZoneOffset(tz)
        self.timezone = tz

    @property
    def logged_in(self) -> bool:
        return self.logged_in_as is not None

    @property
    def _api_service(self) -> ServiceProxy:  # type: ignore
        return self._zeep.api.service

    @property
    def _data_service(self) -> ServiceProxy:  # type: ignore
        return self._zeep.data.service
