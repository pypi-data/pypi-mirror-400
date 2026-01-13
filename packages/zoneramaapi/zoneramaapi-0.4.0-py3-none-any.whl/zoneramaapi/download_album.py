import asyncio
import logging
import re
from io import BytesIO
from pathlib import Path

from httpx import AsyncClient

from zoneramaapi._constants import ZIP_DOWNLOAD_URL, ZIP_READY_URL, ZIP_REQUEST_URL
from zoneramaapi.errors import ZoneramaError

logger = logging.getLogger(__name__)


async def request_zip_file(
    client: AsyncClient,
    album_id: int,
    *,
    secret: str | None = None,
    include_videos: bool = True,
    original: bool = False,
    av1: bool = False,
    raw: bool = False,
) -> int:
    """A coroutine which sends a request to generate a ZIP file of an album.

    Args:
        album_id (str): The Zonerama album ID.
        secret (str | None): The secret string of this album. \
            This is None for non-secret albums.
        include_videos (bool): \
            Whether videos are included or just their thumbnails. \
            Defaults to True.
        original (bool): unknown, defaults to False
        av1 (bool): Whether the av1 codec should be preferred when available. Defaults to False.
        raw (bool): Whether raw files should be included when available. Defaults to False.

    Returns:
        int: The ID of the requested ZIP file to be used in _downloadZip.
    """
    logger.info("Requesting zip file for album %s.", album_id)

    response = await client.get(
        f"{ZIP_REQUEST_URL}/{album_id}",
        params={
            "secret": secret,
            "includeVideos": include_videos,
            "original": original,
            "av1": av1,
            "raw": raw,
        },
    )
    response.raise_for_status()

    # Does not return a JSON if the album is secret
    # and no secret id was specified. Instead redirects to home page.
    if response.headers["content-type"] != "application/json; charset=utf-8":
        raise ZoneramaError("Secret ID not specified", album_id)

    json = response.json()
    return json["Id"]


async def is_zip_ready(client: AsyncClient, zip_id: int) -> bool:
    """A coroutine which checks whether the ZIP file is ready to be downloaded.

    Args:
        zip_id (int): The ID of the ZIP file.
    """
    response = await client.get(f"{ZIP_READY_URL}/{zip_id}")
    response.raise_for_status()

    if response.headers["content-type"] != "application/json; charset=utf-8":
        raise ZoneramaError("Invalid ZIP ID", zip_id)

    json = response.json()

    if json["Error"] is not None:
        raise ZoneramaError(json["Error"], zip_id)

    return json["IsReady"]


async def download_zip(client: AsyncClient, zip_id: int, destination: BytesIO) -> str:
    """A coroutine which downloads the ZIP file into the BytesIO.
        Note: Downloads an empty archive \
            if downloads are prohibited by the album's author.

    Args:
        zip_id (int): ID of the ZIP file.
        destination (BytesIO): IO into which the file is written.

    Returns:
        str: The filename of the downloaded file.
    """
    response = await client.get(f"{ZIP_DOWNLOAD_URL}/{zip_id}")
    response.raise_for_status()

    if response.headers["content-type"] == "text/html; charset=utf-8":
        match response.text:
            case "int is invalid":
                raise ZoneramaError("Invalid ZIP ID", zip_id)
            # add Zip is not ready

            case _:
                raise ZoneramaError(response.text)

    assert response.headers["content-type"] == "application/zip"

    content_disposition = response.headers["content-disposition"]
    mtch = re.match(r'attachment; filename="([^"]+)"', content_disposition)
    assert mtch is not None
    filename = mtch.group(1)

    destination.write(response.content)
    return filename


async def download_album(
    client: AsyncClient,
    album_id: int,
    *,
    secret: str | None = None,
    include_videos: bool = True,
    original: bool = False,
    av1: bool = False,
    raw: bool = False,
    destination_dir: Path = Path("."),
    sleep_for: float = 5.0,
) -> None:
    """A coroutine which downloads the Zonerama album with the provided ID as a ZIP file. \
        If the album is a secret one, secret must be specified. \
        If the author has prohibited downloads, downloads an empty archive.

    Args:
        album_id (AlbumId): The ID of the album you wish to download. \
            This is the string of numbers, \
            which can be found in the URL after Album/.
        secret (str | None, optional): The secret string for the given album. \
            Provide for secret albums, can be found in the URL for them. \
            Defaults to None.
        include_videos (bool, optional): Whether videos are included \
            or just their thumbnails. Defaults to True.
        original (bool): unknown, defaults to False
        av1 (bool): Whether the av1 codec should be preferred when available. Defaults to False.
        raw (bool): Whether raw files should be included when available. Defaults to False.
        destination_dir (Path, optional): \
            The destination folder for the ZIP file. Defaults to ".".
        sleep_for (float, optional): The time for which the function sleeps \
            while the file is not ready, in seconds. Defaults to 5.0.
    """
    zip_id = await request_zip_file(
        client,
        album_id,
        secret=secret,
        include_videos=include_videos,
        original=original,
        av1=av1,
        raw=raw,
    )

    while not await is_zip_ready(client, zip_id):
        logger.info("Waiting on zip_id: %s, %ss", zip_id, sleep_for)
        await asyncio.sleep(sleep_for)

    io = BytesIO()
    filename = await download_zip(client, zip_id, io)

    destination_dir.mkdir(parents=True, exist_ok=True)
    with open(destination_dir / f"{album_id} | {filename}", "wb") as f:
        f.write(io.getbuffer())
