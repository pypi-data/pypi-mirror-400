from zoneramaapi.mixins.base import AsyncBaseMixin, BaseMixin
from zoneramaapi.models.album import Album
from zoneramaapi.models.aliases import AccountID, AlbumID, PhotoID, TabID
from zoneramaapi.zeep.common import raise_for_error


class AlbumMixin(BaseMixin):
    def create_album(
        self,
        tab_id: TabID | None,
        name: str,
        *,
        text: str | None = None,
        password: str | None = None,
    ) -> AlbumID:
        """Create a new album in a tab.

        Args:
            tab_id (TabID | None): ID of the parent tab. If None, album is created without a tab. (Cannot be seen in UI.)
            name (str): A name of the new album.
            text (str | None, optional): Album description. Defaults to None.
            password (str | None, optional): Optional password. Defaults to None.

        Returns:
            AlbumID: ID of the newly created album.
        """
        if tab_id is None:
            response = self._api_service.CreateAlbum(name, text)
        else:
            response = self._api_service.CreateAlbumInTabAndroid(
                tab_id, name, text, password
            )

        raise_for_error(response, "create album")

        return response.Result

    def delete_album(self, id: AlbumID) -> None:
        """Delete an album with the given ID.

        Args:
            id (AlbumID): ID of the album to be deleted.
        """
        response = self._api_service.DeleteAlbum(id)

        raise_for_error(response, f"delete album with ID {id}")

    def delete_albums(self, ids: list[AlbumID]) -> None:
        """Delete albums with the given IDs.

        Args:
            ids (list[AlbumID]): IDs of the albums to be deleted.
        """
        response = self._api_service.DeleteAlbums({"int": ids})

        raise_for_error(response, f"delete albums with IDs {ids}")

    def get_album(self, id: AlbumID, *, password: str | None = None) -> Album:
        """Get a dictionary containing various information
        about an album with the given ID.

        Args:
            id (AlbumID): A Zonerama album ID.
            password (str | None, optional): Optional password.
                If provided, the album is unlocked before fetching info. Defaults to None.

        Returns:
            Album: Album object with info about the album.
        """
        if password is not None:
            self.unlock_album(id, password)

        response = self._data_service.GetAlbum(id)

        raise_for_error(response, f"get album with ID {id}")

        return Album.from_api(response.Result.__values__, timezone=self.timezone)

    def get_albums_in_account(self, id: AccountID) -> list[Album]:
        """Get a list of dictionaries containing various information
        about all albums of the user with the given ID.

        Args:
            id (AccountID): A Zonerama account ID.

        Returns:
            list[Album]: A list of Album objects with info about the albums.
        """
        response = self._data_service.GetAlbums(id)

        raise_for_error(response, f"get albums in account with ID {id}")

        # When there are no albums, the API returns None
        if response.Result is None:
            return []

        return [Album.from_api(album.__values__, timezone=self.timezone) for album in response.Result.Album]

    def get_albums_in_tab(self, id: TabID) -> list[Album]:
        """Get a list of dictionaries containing various information
        about all albums in the tab with the given ID.

        Args:
            id (TabID): A Zonerama tab ID.

        Returns:
            list[Album]: A list of Album objects with info about the albums.
        """
        response = self._data_service.GetAlbumsInTab(id)

        raise_for_error(response, f"get albums in tab with ID {id}")

        # When there are no albums, the API returns None
        if response.Result is None:
            return []

        return [Album.from_api(album.__values__, timezone=self.timezone) for album in response.Result.Album]

    def unlock_album(self, id: AlbumID, password: str) -> None:
        """This method is meant to be called prior to accessing an album protected by a password.
        Afterwards, the locked album can be used as any non-locked album.

        Args:
            id (AlbumID): ID of the album to unlock.
            password (str): The password to unlock this album.
        """
        response = self._api_service.UnlockAlbum(id, password)

        raise_for_error(response, f"unlock album with ID {id}")

    def update_album(
        self,
        id: AlbumID,
        *,
        name: str | None = None,
        text: str | None = None,
        cover_id: PhotoID | None = ...,  # type: ignore
        tab_id: TabID | None = None,
        password: str | None = ...,  # type: ignore
        # password_help: str | None = ...,
    ):
        """Update an existing album.

        Args:
            id (AlbumID): ID of the album to be updated.
            name (str | None, optional): A new name. Defaults to None.
            text (str | None, optional): A new description. Defaults to None.
            cover_id (PhotoID | None, optional): ID of a new cover image (or None to unassign cover image). Defaults to None.
            tab_id (TabID | None, optional): ID of a new parent tab. Defaults to None.
            password (str | None, optional): A new password (or None to remove existing password). Defaults to None.
        """
        if name is not None or text is not None:
            response = self._api_service.UpdateAlbum(id, name, text)
            raise_for_error(response, f"update album with ID {id}")

        if cover_id is not ...:
            response = self._api_service.UpdateAlbumCover(id, cover_id)
            raise_for_error(response, f"update album cover with ID {id}")

        if tab_id is not None:
            self.update_albums_tab([id], tab_id)

        if password is not ...:
            response = self._api_service.UpdateAlbumPwd(id, password, None)
            raise_for_error(response, f"update album password with ID {id}")

    def update_albums_tab(self, ids: list[AlbumID], tab_id: TabID) -> None:
        response = self._api_service.UpdateAlbumsTab({"int": ids}, tab_id)

        raise_for_error(response, f"update albums tab with IDs {ids}")

    def reorder_albums(self, order: list[AlbumID]) -> None:
        """Reorder albums in a tab.

        Args:
            order (list[AlbumID]): An arbitrarily ordered complete (for a tab) list of album IDs.
        """
        response = self._api_service.UpdateAlbumsRank({"int": order})

        raise_for_error(response, f"reorder albums with IDs {order}")


class AsyncAlbumMixin(AsyncBaseMixin):
    async def create_album(
        self,
        tab_id: TabID | None,
        name: str,
        *,
        text: str | None = None,
        password: str | None = None,
    ) -> AlbumID:
        """Create a new album in a tab.

        Args:
            tab_id (TabID | None): ID of the parent tab. If None, album is created without a tab. (Cannot be seen in UI.)
            name (str): A name of the new album.
            text (str | None, optional): Album description. Defaults to None.
            password (str | None, optional): Optional password. Defaults to None.

        Returns:
            AlbumID: ID of the newly created album.
        """
        if tab_id is None:
            response = await self._api_service.CreateAlbum(name, text)
        else:
            response = await self._api_service.CreateAlbumInTabAndroid(
                tab_id, name, text, password
            )

        raise_for_error(response, "create album")

        return response.Result

    async def delete_album(self, id: AlbumID) -> None:
        """Delete an album with the given ID.

        Args:
            id (AlbumID): ID of the album to be deleted.
        """
        response = await self._api_service.DeleteAlbum(id)

        raise_for_error(response, f"delete album with ID {id}")

    async def delete_albums(self, ids: list[AlbumID]) -> None:
        """Delete albums with the given IDs.

        Args:
            ids (list[AlbumID]): IDs of the albums to be deleted.
        """
        response = await self._api_service.DeleteAlbums({"int": ids})

        raise_for_error(response, f"delete albums with IDs {ids}")

    async def get_album(self, id: AlbumID, *, password: str | None = None) -> Album:
        """Get a dictionary containing various information
        about an album with the given ID.

        Args:
            id (AlbumID): A Zonerama album ID.
            password (str | None, optional): Optional password.
                If provided, the album is unlocked before fetching info. Defaults to None.

        Returns:
            Album: Album object with info about the album.
        """
        if password is not None:
            await self.unlock_album(id, password)

        response = await self._data_service.GetAlbum(id)

        raise_for_error(response, f"get album with ID {id}")

        return Album.from_api(response.Result.__values__, timezone=self.timezone)

    async def get_albums_in_account(self, id: AccountID) -> list[Album]:
        """Get a list of dictionaries containing various information
        about all albums of the user with the given ID.

        Args:
            id (AccountID): A Zonerama account ID.

        Returns:
            list[Album]: A list of Album objects with info about the albums.
        """
        response = await self._data_service.GetAlbums(id)

        raise_for_error(response, f"get albums in account with ID {id}")

        # When there are no albums, the API returns None
        if response.Result is None:
            return []

        return [Album.from_api(album.__values__, timezone=self.timezone) for album in response.Result.Album]

    async def get_albums_in_tab(self, id: TabID) -> list[Album]:
        """Get a list of dictionaries containing various information
        about all albums in the tab with the given ID.

        Args:
            id (TabID): A Zonerama tab ID.

        Returns:
            list[Album]: A list of Album objects with info about the albums.
        """
        response = await self._data_service.GetAlbumsInTab(id)

        raise_for_error(response, f"get albums in tab with ID {id}")

        # When there are no albums, the API returns None
        if response.Result is None:
            return []

        return [Album.from_api(album.__values__, timezone=self.timezone) for album in response.Result.Album]

    async def unlock_album(self, id: AlbumID, password: str) -> None:
        """This method is meant to be called prior to accessing an album protected by a password.
        Afterwards, the locked album can be used as any non-locked album.

        Args:
            id (AlbumID): ID of the album to unlock.
            password (str): The password to unlock this album.
        """
        response = await self._api_service.UnlockAlbum(id, password)

        raise_for_error(response, f"unlock album with ID {id}")

    async def update_album(
        self,
        id: AlbumID,
        *,
        name: str | None = None,
        text: str | None = None,
        cover_id: PhotoID | None = ...,  # type: ignore
        tab_id: TabID | None = None,
        password: str | None = ...,  # type: ignore
        # password_help: str | None = ...,
    ):
        """Update an existing album.

        Args:
            id (AlbumID): ID of the album to be updated.
            name (str | None, optional): A new name. Defaults to None.
            text (str | None, optional): A new description. Defaults to None.
            cover_id (PhotoID | None, optional): ID of a new cover image (or None to unassign cover image). Defaults to None.
            tab_id (TabID | None, optional): ID of a new parent tab. Defaults to None.
            password (str | None, optional): A new password (or None to remove existing password). Defaults to None.
        """
        if name is not None or text is not None:
            response = await self._api_service.UpdateAlbum(id, name, text)
            raise_for_error(response, f"update album with ID {id}")

        if cover_id is not ...:
            response = await self._api_service.UpdateAlbumCover(id, cover_id)
            raise_for_error(response, f"update album cover with ID {id}")

        if tab_id is not None:
            await self.update_albums_tab([id], tab_id)

        if password is not ...:
            response = await self._api_service.UpdateAlbumPwd(id, password, None)
            raise_for_error(response, f"update album password with ID {id}")

    async def update_albums_tab(self, ids: list[AlbumID], tab_id: TabID) -> None:
        response = await self._api_service.UpdateAlbumsTab({"int": ids}, tab_id)

        raise_for_error(response, f"update albums tab with IDs {ids}")

    async def reorder_albums(self, order: list[AlbumID]) -> None:
        """Reorder albums in a tab.

        Args:
            order (list[AlbumID]): An arbitrarily ordered complete (for a tab) list of album IDs.
        """
        response = await self._api_service.UpdateAlbumsRank({"int": order})

        raise_for_error(response, f"reorder albums with IDs {order}")
