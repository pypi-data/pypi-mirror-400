import datetime
from hashlib import sha256

from zoneramaapi.mixins.account import AsyncAccountMixin
from zoneramaapi.mixins.album import AsyncAlbumMixin
from zoneramaapi.mixins.photo import AsyncPhotoMixin
from zoneramaapi.mixins.tab import AsyncTabMixin
from zoneramaapi.models.aliases import AccountID
from zoneramaapi.zeep.async_ import ZeepAsyncClients
from zoneramaapi.zeep.common import AsyncServiceProxy, raise_for_error


class ZoneramaAsyncClient(
    AsyncAccountMixin, AsyncAlbumMixin, AsyncPhotoMixin, AsyncTabMixin
):
    _zeep: ZeepAsyncClients
    logged_in_as: AccountID | None
    timezone: datetime.tzinfo | None

    def __init__(self):
        self._zeep = ZeepAsyncClients()
        self.logged_in_as = None
        self.timezone = None

    async def __aenter__(self):
        await self._zeep.__aenter__()
        return self

    async def __aexit__(self, *_):
        await self.close()
        return

    async def close(self):
        if self.logged_in:
            await self.logout()
        await self._zeep.close()

    async def login(self, username: str, password: str) -> bool:
        service = self._zeep.api.service
        response = await service.Login(
            username, sha256(bytes(password, "utf-8")).hexdigest()
        )
        self.logged_in_as = response.Result if response.Success else None
        return response.Success

    async def logout(self) -> bool:
        if not self.logged_in:
            return False

        service = self._zeep.api.service
        response = await service.Logout()

        if response.Success:
            self.logged_in_as = None

        return response.Success

    async def set_timezone(self, tz: datetime.tzinfo) -> None:
        """Set the timezone for the current session.

        Args:
            tz (datetime.tzinfo): The timezone as a datetime tzinfo object.
        """
        await self._api_service.SetTimeZoneOffset(tz)
        self.timezone = tz

    @property
    def logged_in(self) -> bool:
        return self.logged_in_as is not None

    @property
    def _api_service(self) -> AsyncServiceProxy:  # type: ignore
        return self._zeep.api.service  # type: ignore

    @property
    def _data_service(self) -> AsyncServiceProxy:  # type: ignore
        return self._zeep.data.service  # type: ignore
