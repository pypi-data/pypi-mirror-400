from zoneramaapi.mixins.base import AsyncBaseMixin, BaseMixin
from zoneramaapi.models.aliases import AccountID, TabID
from zoneramaapi.models.tab import Tab
from zoneramaapi.zeep.common import raise_for_error


class TabMixin(BaseMixin):
    def create_tab(
        self,
        name: str,
        public: bool,
        *,
        rank: int | None = None,
        password: str | None = None,
        password_help: str | None = None,
    ) -> TabID:
        """Create a new tab (folder).

        Args:
            name (str): A name for the tab.
            public (bool): Whether it should be public or not.
            rank (int | None): The position of the new tab among other tabs.
            password (str | None): Password for password-protecting the tab.
            password_help (str | None): Help for the password.

        Returns:
            TabID: The ID of the newly created tab.
        """
        response = self._api_service.CreateTab(
            name, public, rank, password, password_help
        )

        raise_for_error(response, "create tab")

        return response.Result

    def delete_tab(self, id: TabID) -> None:
        """Delete a tab with the given ID.

        Args:
            id (TabID): ID of the tab to delete.
        """
        response = self._api_service.DeleteTab(id)

        raise_for_error(response, f"delete tab with ID {id}")

    def get_tab(self, id: TabID) -> Tab:
        """Get a dictionary containing various information
        about a tab with the given ID.

        Args:
            id (TabID): A Zonerama tab ID.

        Returns:
            OrderedDict: Dictionary with info about the tab.
        """
        response = self._data_service.GetTab(id)

        raise_for_error(response, f"get tab with ID {id}")

        return Tab.from_api(response.Result.__values__, timezone=self.timezone)

    def get_tabs(self, id: AccountID) -> list[Tab]:
        """Get a list of dictionaries containing various information
        about all tabs of the user with the given ID.

        Args:
            id (AccountID): A Zonerama account ID.

        Returns:
            list[OrderedDict]: A list of dictionaries with info about the tab.
        """
        response = self._data_service.GetTabs(id)

        raise_for_error(response, f"get tabs for account with ID {id}")

        return [Tab.from_api(tab.__values__, timezone=self.timezone) for tab in response.Result.Tab]

    def update_tab(
        self,
        id: TabID,
        *,
        name: str | None = None,
        public: bool | None = None,
        rank: int | None = None,
        password: str | None = None,
        password_help: str | None = None,
        default_order: str | None = None,
    ) -> None:
        """Update a tab.

        Args:
            id (TabID): ID of the updated tab.
            name (str | None, optional): A new name. Defaults to None.
            public (bool | None, optional): Whether tab should be public or not. Defaults to None.
            rank (int | None, optional): A new rank among other tabs. Defaults to None.
            password (str | None, optional): A new password (or None to remove existing password). Defaults to None.
            password_help (str | None, optional): A new password help. Defaults to None.
            default_order (str | None, optional): Unknown. Defaults to None.
        """
        response = self._api_service.UpdateTab(
            id,
            name,
            public,
            rank,
            password,
            password_help,
            default_order,
        )

        raise_for_error(response, f"update tab with ID {id}")

    def reorder_tabs(self, order: list[TabID]) -> None:
        """Change the order of the tabs.

        Args:
            order (list[TabID]): An arbitrarily ordered complete list of tab IDs.
        """
        response = self._api_service.UpdateTabsRank({"int": order})

        raise_for_error(response, "reorder tabs")


class AsyncTabMixin(AsyncBaseMixin):
    async def create_tab(
        self,
        name: str,
        public: bool,
        *,
        rank: int | None = None,
        password: str | None = None,
        password_help: str | None = None,
    ) -> TabID:
        """Create a new tab (folder).

        Args:
            name (str): A name for the tab.
            public (bool): Whether it should be public or not.
            rank (int | None): The position of the new tab among other tabs.
            password (str | None): Password for password-protecting the tab.
            password_help (str | None): Help for the password.

        Returns:
            TabID: The ID of the newly created tab.
        """
        response = await self._api_service.CreateTab(
            name, public, rank, password, password_help
        )

        raise_for_error(response, "create tab")

        return response.Result

    async def delete_tab(self, id: TabID) -> None:
        """Delete a tab with the given ID.

        Args:
            id (TabID): ID of the tab to delete.
        """
        response = await self._api_service.DeleteTab(id)

        raise_for_error(response, f"delete tab with ID {id}")

    async def get_tab(self, id: TabID) -> Tab:
        """Get a dictionary containing various information
        about a tab with the given ID.

        Args:
            id (TabID): A Zonerama tab ID.

        Returns:
            OrderedDict: Dictionary with info about the tab.
        """
        response = await self._data_service.GetTab(id)

        raise_for_error(response, f"get tab with ID {id}")

        return Tab.from_api(response.Result.__values__, timezone=self.timezone)

    async def get_tabs(self, id: AccountID) -> list[Tab]:
        """Get a list of dictionaries containing various information
        about all tabs of the user with the given ID.

        Args:
            id (AccountID): A Zonerama account ID.

        Returns:
            list[OrderedDict]: A list of dictionaries with info about the tab.
        """
        response = await self._data_service.GetTabs(id)

        raise_for_error(response, f"get tabs for account with ID {id}")

        return [Tab.from_api(tab.__values__, timezone=self.timezone) for tab in response.Result.Tab]

    async def update_tab(
        self,
        id: TabID,
        *,
        name: str | None = None,
        public: bool | None = None,
        rank: int | None = None,
        password: str | None = None,
        password_help: str | None = None,
        default_order: str | None = None,
    ) -> None:
        """Update a tab.

        Args:
            id (TabID): ID of the updated tab.
            name (str | None, optional): A new name. Defaults to None.
            public (bool | None, optional): Whether tab should be public or not. Defaults to None.
            rank (int | None, optional): A new rank among other tabs. Defaults to None.
            password (str | None, optional): A new password (or None to remove existing password). Defaults to None.
            password_help (str | None, optional): A new password help. Defaults to None.
            default_order (str | None, optional): Unknown. Defaults to None.
        """
        response = await self._api_service.UpdateTab(
            id,
            name,
            public,
            rank,
            password,
            password_help,
            default_order,
        )

        raise_for_error(response, f"update tab with ID {id}")

    async def reorder_tabs(self, order: list[TabID]) -> None:
        """Change the order of the tabs.

        Args:
            order (list[TabID]): An arbitrarily ordered complete list of tab IDs.
        """
        response = await self._api_service.UpdateTabsRank({"int": order})

        raise_for_error(response, "reorder tabs")
