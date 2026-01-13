import httpx
from zeep import AsyncClient
from zeep.transports import AsyncTransport

from zoneramaapi._constants import APISERVICE_WSDL_URL, DATASERVICE_WSDL_URL


class ZeepAsyncClients:
    _client: httpx.AsyncClient
    _transport: AsyncTransport
    api: AsyncClient
    data: AsyncClient
    _closed: bool

    def __init__(self):
        self._client = httpx.AsyncClient()
        self._transport = AsyncTransport(client=self._client)

        self.api = AsyncClient(
            wsdl=APISERVICE_WSDL_URL,
            transport=self._transport,
        )

        self.data = AsyncClient(
            wsdl=DATASERVICE_WSDL_URL,
            transport=self._transport,
        )

        self._closed = False

    async def close(self):
        if not self._closed:
            await self._client.aclose()
            self._closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()