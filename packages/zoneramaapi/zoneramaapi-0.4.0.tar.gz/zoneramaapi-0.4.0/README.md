# Zonerama API

Unofficial Python library for the Zonerama web library's SOAP API.

## Installation

```bash
pip install zoneramaapi
```

## Usage

```python
from zoneramaapi import ZoneramaClient

with ZoneramaClient() as client:
    client.login("username", "password")
    albums = client.get_albums_in_account(client.logged_in_as)
    for album in albums:
        print(album.name)
```

### ZIP album downloader

```python
import asyncio

from httpx import AsyncClient

from zoneramaapi import download_album

client = AsyncClient()
asyncio.run(download_album(client, 42))
```
