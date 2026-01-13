from asyncio import to_thread
from pathlib import Path
from typing import Callable

from zoneramaapi.mixins.base import AsyncBaseMixin, BaseMixin
from zoneramaapi.mixins.utils import load_image_base64
from zoneramaapi.models.aliases import AlbumID, PhotoID
from zoneramaapi.models.photo import Photo
from zoneramaapi.zeep.common import raise_for_error


class PhotoMixin(BaseMixin):
    unlock_album: Callable

    def create_photo(
        self,
        album_id: AlbumID,
        image_path: Path,
        *,
        name: str | None = None,
        text: str = "",
    ) -> PhotoID:
        """Create a new photo in Zonerama by uploading one from the filesystem.

        Args:
            album_id (AlbumID): ID of an existing album.
            image_path (Path): Path to the image.
            name (str | None, optional): Name for the photo. If None, filename is used. Defaults to None.
            text (str, optional): Text description for the image. Defaults to "".

        Returns:
            PhotoID: ID of the newly created photo.
        """
        if name is None:
            name = image_path.name

        response = self._api_service.CreatePhoto(
            album_id, name, text, load_image_base64(image_path)
        )

        raise_for_error(response, "create photo")

        return response.Result

    def delete_photo(
        self,
        id: PhotoID,
    ) -> None:
        """Delete a photo with the specified ID.

        Args:
            photo_id (PhotoID): ID of the photo to delete.
        """
        response = self._api_service.DeletePhoto(id)

        raise_for_error(response, f"delete photo with ID {id}")

    def delete_photos(
        self,
        ids: list[PhotoID],
    ) -> None:
        """Delete photos with the specified IDs.

        Args:
            photo_id (PhotoID): IDs of the photos to delete.
        """
        response = self._api_service.DeletePhotos({"int": ids})

        raise_for_error(response, f"delete photos with IDs {ids}")

    def get_photo(self, id: PhotoID, *, password: str | None = None) -> Photo:
        """Get a dictionary with information about a photo.

        Args:
            id (PhotoID): ID of the photo.
            password (str | None, optional): Password to optionally unlock the photo before getting. Defaults to None.

        Returns:
            OrderedDict: Dictionary with information about the photo.
        """
        if password is not None:
            self.unlock_photo(id, password)

        response = self._data_service.GetPhoto(id)

        raise_for_error(response, f"get photo with ID {id}")

        return Photo.from_api(response.Result.__values__, timezone=self.timezone)

    def get_photos_in_album(
        self, id: AlbumID, *, password: str | None = None
    ) -> list[Photo]:
        """Get a list of dictionaries with information about photos in a given album.

        Args:
            id (PhotoID): ID of the album.
            password (str | None, optional): Password to optionally unlock the album before getting. Defaults to None.

        Returns:
            list[OrderedDict]: List of dictionaries with information about the photo.
        """
        if password is not None:
            self.unlock_album(id, password)

        response = self._data_service.GetPhotos(id)

        raise_for_error(response, f"get photos in album with ID {id}")

        if response.Result is None:
            return []

        return [Photo.from_api(photo.__values__, timezone=self.timezone) for photo in response.Result.Photo]

    def copy_photos(
        self, ids: list[PhotoID], album_id: AlbumID
    ) -> list[tuple[PhotoID, str]]:
        """Copy OWN photos to an album. Photos not owned by logged in user are not copied.

        Args:
            ids (list[PhotoID]): A list of IDs of photos to copy.
            album_id (AlbumID): A destination album.

        Returns:
            list[tuple[PhotoID, str]]: A list of tuples of new IDs and names of copied images.
        """
        response = self._api_service.CopyPhotos({"int": ids}, album_id)

        raise_for_error(response, f"copy photos to album with ID {album_id}")

        if response is None:
            return []

        return [(entry["ID"], entry["Name"]) for entry in response["Id_Name"]]

    def move_photos(
        self, ids: list[PhotoID], album_id: AlbumID
    ) -> list[tuple[PhotoID, str]]:
        """Move OWN photos to an album. Photos not owned by logged in user are not moved.

        Args:
            ids (list[PhotoID]): A list of IDs of photos to move.
            album_id (AlbumID): A destination album.

        Returns:
            list[tuple[PhotoID, str]]: A list of tuples of IDs and new names of moved images.
        """
        response = self._api_service.MovePhotos({"int": ids}, album_id)

        raise_for_error(response, f"move photos to album with ID {album_id}")

        if response is None:
            return []

        return [(entry["ID"], entry["Name"]) for entry in response["Id_Name"]]

    def unlock_photo(self, id: PhotoID, password: str) -> None:
        """This method is meant to be called prior to accessing a photo in an album protected by a password.
        Afterwards, the photo can be used as any other photo.

        Args:
            id (AlbumID): ID of the photo to unlock.
            password (str): The password to unlock this photo.
        """
        response = self._api_service.UnlockPhoto(id, password)

        raise_for_error(response, f"unlock photo with ID {id}")

    def update_photo(
        self,
        id: PhotoID,
        *,
        title: str = ...,  # type: ignore
        description: str = ...,  # type: ignore
        coordinates: tuple[float, float] = ...,  # type: ignore
        path: Path = ...,  # type: ignore
        cover_second: int = ...,  # type: ignore
    ) -> None:
        """Update a photo with the given ID.

        Args:
            id (PhotoID): ID of the photo.
            title (str, optional): A title of the photo.
            description (str, optional): Description of the photo.
            coordinates (tuple[float, float], optional): Coordinates (latitude, longitude) of the photo's location.
            path (Path, optional): Path to an image to replace the existing one with.
            cover_second (int, optional): Second of the video, of which the frame is used as the thumbnail.
        """
        if title is not ... or description is not ...:
            if title is ...:
                title = None

            if description is ...:
                description = None

            response = self._api_service.UpdatePhoto(id, title, description)

            raise_for_error(
                response, f"update title and description of photo with ID {id}"
            )

        if coordinates is not ...:
            response = self._api_service.UpdatePhotoLocation(
                id, coordinates[0], coordinates[1]
            )

            raise_for_error(response, f"update location of photo with ID {id}")

        if path is not ...:
            response = self._api_service.UpdatePhotoStream(id, load_image_base64(path))

            raise_for_error(response, f"update content of photo with ID {id}")

        if cover_second is not ...:
            response = self._api_service.UpdateVideoCover(id, f"{cover_second}.jpg")

            raise_for_error(response, f"update cover of video with ID {id}")


class AsyncPhotoMixin(AsyncBaseMixin):
    unlock_album: Callable

    async def create_photo(
        self,
        album_id: AlbumID,
        image_path: Path,
        *,
        name: str | None = None,
        text: str = "",
    ) -> PhotoID:
        """Create a new photo in Zonerama by uploading one from the filesystem.

        Args:
            album_id (AlbumID): ID of an existing album.
            image_path (Path): Path to the image.
            name (str | None, optional): Name for the photo. If None, filename is used. Defaults to None.
            text (str, optional): Text description for the image. Defaults to "".

        Returns:
            PhotoID: ID of the newly created photo.
        """
        if name is None:
            name = image_path.name

        response = await self._api_service.CreatePhoto(
            album_id, name, text, await to_thread(load_image_base64, image_path)
        )

        raise_for_error(response, "create photo")

        return response.Result

    async def delete_photo(
        self,
        id: PhotoID,
    ) -> None:
        """Delete a photo with the specified ID.

        Args:
            photo_id (PhotoID): ID of the photo to delete.
        """
        response = await self._api_service.DeletePhoto(id)

        raise_for_error(response, f"delete photo with ID {id}")

    async def delete_photos(
        self,
        ids: list[PhotoID],
    ) -> None:
        """Delete photos with the specified IDs.

        Args:
            photo_id (PhotoID): IDs of the photos to delete.
        """
        response = await self._api_service.DeletePhotos({"int": ids})

        raise_for_error(response, f"delete photos with IDs {ids}")

    async def get_photo(self, id: PhotoID, *, password: str | None = None) -> Photo:
        """Get a dictionary with information about a photo.

        Args:
            id (PhotoID): ID of the photo.
            password (str | None, optional): Password to optionally unlock the photo before getting. Defaults to None.

        Returns:
            OrderedDict: Dictionary with information about the photo.
        """
        if password is not None:
            await self.unlock_photo(id, password)

        response = await self._data_service.GetPhoto(id)

        raise_for_error(response, f"get photo with ID {id}")

        return Photo.from_api(response.Result.__values__, timezone=self.timezone)

    async def get_photos_in_album(
        self, id: AlbumID, *, password: str | None = None
    ) -> list[Photo]:
        """Get a list of dictionaries with information about photos in a given album.

        Args:
            id (PhotoID): ID of the album.
            password (str | None, optional): Password to optionally unlock the album before getting. Defaults to None.

        Returns:
            list[OrderedDict]: List of dictionaries with information about the photo.
        """
        if password is not None:
            self.unlock_album(id, password)

        response = await self._data_service.GetPhotos(id)

        raise_for_error(response, f"get photos in album with ID {id}")

        if response.Result is None:
            return []

        return [Photo.from_api(photo.__values__, timezone=self.timezone) for photo in response.Result.Photo]

    async def copy_photos(
        self, ids: list[PhotoID], album_id: AlbumID
    ) -> list[tuple[PhotoID, str]]:
        """Copy OWN photos to an album. Photos not owned by logged in user are not copied.

        Args:
            ids (list[PhotoID]): A list of IDs of photos to copy.
            album_id (AlbumID): A destination album.

        Returns:
            list[tuple[PhotoID, str]]: A list of tuples of new IDs and names of copied images.
        """
        response = await self._api_service.CopyPhotos({"int": ids}, album_id)

        raise_for_error(response, f"copy photos to album with ID {album_id}")

        if response is None:
            return []

        return [(entry["ID"], entry["Name"]) for entry in response["Id_Name"]]

    async def move_photos(
        self, ids: list[PhotoID], album_id: AlbumID
    ) -> list[tuple[PhotoID, str]]:
        """Move OWN photos to an album. Photos not owned by logged in user are not moved.

        Args:
            ids (list[PhotoID]): A list of IDs of photos to move.
            album_id (AlbumID): A destination album.

        Returns:
            list[tuple[PhotoID, str]]: A list of tuples of IDs and new names of moved images.
        """
        response = await self._api_service.MovePhotos({"int": ids}, album_id)

        raise_for_error(response, f"move photos to album with ID {album_id}")

        if response is None:
            return []

        return [(entry["ID"], entry["Name"]) for entry in response["Id_Name"]]

    async def unlock_photo(self, id: PhotoID, password: str) -> None:
        """This method is meant to be called prior to accessing a photo in an album protected by a password.
        Afterwards, the photo can be used as any other photo.

        Args:
            id (AlbumID): ID of the photo to unlock.
            password (str): The password to unlock this photo.
        """
        response = await self._api_service.UnlockPhoto(id, password)

        raise_for_error(response, f"unlock photo with ID {id}")

    async def update_photo(
        self,
        id: PhotoID,
        *,
        title: str = ...,  # type: ignore
        description: str = ...,  # type: ignore
        coordinates: tuple[float, float] = ...,  # type: ignore
        path: Path = ...,  # type: ignore
        cover_second: int = ...,  # type: ignore
    ) -> None:
        """Update a photo with the given ID.

        Args:
            id (PhotoID): ID of the photo.
            title (str, optional): A title of the photo.
            description (str, optional): Description of the photo.
            coordinates (tuple[float, float], optional): Coordinates (latitude, longitude) of the photo's location.
            path (Path, optional): Path to an image to replace the existing one with.
            cover_second (int, optional): Second of the video, of which the frame is used as the thumbnail.
        """
        if title is not ... or description is not ...:
            if title is ...:
                title = None

            if description is ...:
                description = None

            response = await self._api_service.UpdatePhoto(id, title, description)

            raise_for_error(
                response, f"update title and description of photo with ID {id}"
            )

        if coordinates is not ...:
            response = await self._api_service.UpdatePhotoLocation(
                id, coordinates[0], coordinates[1]
            )

            raise_for_error(response, f"update location of photo with ID {id}")

        if path is not ...:
            response = await self._api_service.UpdatePhotoStream(
                id, await to_thread(load_image_base64, path)
            )

            raise_for_error(response, f"update content of photo with ID {id}")

        if cover_second is not ...:
            response = await self._api_service.UpdateVideoCover(
                id, f"{cover_second}.jpg"
            )

            raise_for_error(response, f"update cover of video with ID {id}")
