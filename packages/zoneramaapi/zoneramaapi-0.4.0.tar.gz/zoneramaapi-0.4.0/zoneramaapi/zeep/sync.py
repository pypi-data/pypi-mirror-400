import requests
from zeep import Client
from zeep.transports import Transport

from zoneramaapi._constants import APISERVICE_WSDL_URL, DATASERVICE_WSDL_URL


class ZeepSyncClients:
    _session: requests.Session
    _transport: Transport
    api: Client
    data: Client
    _closed: bool

    def __init__(self):
        self._session = requests.Session()
        self._transport = Transport(session=self._session)

        self.api = Client(
            wsdl=APISERVICE_WSDL_URL,
            transport=self._transport,
        )

        self.data = Client(
            wsdl=DATASERVICE_WSDL_URL,
            transport=self._transport,
        )

        self._closed = False

    def close(self):
        if not self._closed:
            self._session.close()
            self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
