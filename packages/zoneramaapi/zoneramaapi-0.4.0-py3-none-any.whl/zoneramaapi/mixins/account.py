from asyncio import to_thread
from pathlib import Path

from zoneramaapi.mixins.base import AsyncBaseMixin, BaseMixin
from zoneramaapi.mixins.utils import load_image_base64
from zoneramaapi.models.account import Account
from zoneramaapi.models.aliases import AccountID
from zoneramaapi.zeep.common import raise_for_error


class AccountMixin(BaseMixin):
    def create_account(self, email: str) -> None:
        """Send a request to create an account with the provided email.
        Confirmation is sent to the address.

        Args:
            email (str): An email address for which to create the account.
        """
        response = self._api_service.CreateAccount(email)

        raise_for_error(response, "create account")

    def delete_account(self) -> None:
        """Delete the logged in account."""
        response = self._api_service.DeleteAccount()

        raise_for_error(response, "delete account")

    def reset_password(self, email: str) -> None:
        """Send a request for password reset for account with the specified email.

        Args:
            email (str): An email address for which to reset password.
        """
        response = self._api_service.ResetPwd(email)

        raise_for_error(response, "reset password")

    def update_account_settings(
        self,
        discoverable: bool,
        newsletter_features: bool,
        newsletter_photos: bool,
    ) -> None:
        """Update some account settings.

        Args:
            discoverable (bool): Make the gallery discoverable on the Internet (Google, Zonerama, etc.)
            newsletter_features (bool): Receive emails about new features.
            newsletter_photos (bool): Receive emails with the activity overview bulletin.
        """
        response = self._api_service.UpdateAccountSettings(
            discoverable, newsletter_features, newsletter_photos
        )

        raise_for_error(response, "update account settings")

    def get_account(self, id: AccountID | None = None) -> Account:
        """Get a dictionary containing various information
        about an account with the given ID.

        Args:
            id (AccountID): A Zonerama account ID.

        Returns:
            OrderedDict: Dictionary with info about the account.u
        """
        response = self._data_service.GetAccount(
            self.logged_in_as if id is None else id
        )

        raise_for_error(response, "get account")

        return Account.from_api(response.Result.__values__, timezone=self.timezone)

    def follow(self, id: AccountID) -> None:
        """Follow an account with the given ID.

        Args:
            id (AccountID): ID of the account to follow.
        """
        response = self._api_service.Like(id, 0)

        raise_for_error(response, "follow account")

    def unfollow(self, id: AccountID) -> None:
        """Unfollow an account with the given ID.

        Args:
            id (AccountID): ID of the account to unfollow.
        """
        response = self._api_service.Unlike(id, 0)

        raise_for_error(response, "unfollow account")

    def update_avatar(self, image_path: Path) -> None:
        """Update profile avatar with the given image.

        Args:
            image_path (Path): Path to the image.
        """
        response = self._api_service.UpdateAvatar(load_image_base64(image_path))

        raise_for_error(response, "update avatar")

    def delete_avatar(self) -> None:
        """Delete the avatar picture for the logged in account."""
        response = self._api_service.DeleteAvatar()

        raise_for_error(response, "delete avatar")

    def has_avatar(self) -> bool:
        """Checks whether the logged in account has an avatar."""
        response = self._api_service.ExistsAvatar()

        raise_for_error(response, "check avatar existence")

        return response.Result


class AsyncAccountMixin(AsyncBaseMixin):
    async def create_account(self, email: str) -> None:
        """Send a request to create an account with the provided email.
        Confirmation is sent to the address.

        Args:
            email (str): An email address for which to create the account.
        """
        response = await self._api_service.CreateAccount(email)

        raise_for_error(response, "create account")

    async def delete_account(self) -> None:
        """Delete the logged in account."""
        response = self._api_service.DeleteAccount()

        raise_for_error(response, "delete account")

    async def reset_password(self, email: str) -> None:
        """Send a request for password reset for account with the specified email.

        Args:
            email (str): An email address for which to reset password.
        """
        response = self._api_service.ResetPwd(email)

        raise_for_error(response, "reset password")

    async def update_account_settings(
        self,
        discoverable: bool,
        newsletter_features: bool,
        newsletter_photos: bool,
    ) -> None:
        """Update some account settings.

        Args:
            discoverable (bool): Make the gallery discoverable on the Internet (Google, Zonerama, etc.)
            newsletter_features (bool): Receive emails about new features.
            newsletter_photos (bool): Receive emails with the activity overview bulletin.
        """
        response = await self._api_service.UpdateAccountSettings(
            discoverable, newsletter_features, newsletter_photos
        )

        raise_for_error(response, "update account settings")

    async def get_account(self, id: AccountID | None = None) -> Account:
        """Get a dictionary containing various information
        about an account with the given ID.

        Args:
            id (AccountID): A Zonerama account ID.

        Returns:
            OrderedDict: Dictionary with info about the account.u
        """
        response = await self._data_service.GetAccount(
            self.logged_in_as if id is None else id
        )

        raise_for_error(response, "get account")

        return Account.from_api(response.Result.__values__, timezone=self.timezone)

    async def follow(self, id: AccountID) -> None:
        """Follow an account with the given ID.

        Args:
            id (AccountID): ID of the account to follow.
        """
        response = await self._api_service.Like(id, 0)

        raise_for_error(response, "follow account")

    async def unfollow(self, id: AccountID) -> None:
        """Unfollow an account with the given ID.

        Args:
            id (AccountID): ID of the account to unfollow.
        """
        response = await self._api_service.Unlike(id, 0)

        raise_for_error(response, "unfollow account")

    async def update_avatar(self, image_path: Path) -> None:
        """Update profile avatar with the given image.

        Args:
            image_path (Path): Path to the image.
        """
        response = await self._api_service.UpdateAvatar(
            await to_thread(load_image_base64, image_path)
        )

        raise_for_error(response, "update avatar")

    async def delete_avatar(self) -> None:
        """Delete the avatar picture for the logged in account."""
        response = await self._api_service.DeleteAvatar()

        raise_for_error(response, "delete avatar")

    async def has_avatar(self) -> bool:
        """Checks whether the logged in account has an avatar."""
        response = await self._api_service.ExistsAvatar()

        raise_for_error(response, "check avatar existence")

        return response.Result
