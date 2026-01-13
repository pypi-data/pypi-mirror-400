from dataclasses import dataclass
from datetime import datetime, tzinfo

from zoneramaapi.models.aliases import AccountID
from zoneramaapi.models.utils import map_key, map_value

FIELD_MAP = {
    "ID": "id",
    "ZAID": "zoner_account_id",
    "EMail": "email",
    "Inserted": "created_at",
    "LastAccess": "last_accessed_at",
    "Changed": "changed_at",
    "ChangeAvatar": "changed_avatar_at",
}


@dataclass(slots=True)
class Account:
    id: AccountID
    zoner_account_id: int
    email: str
    name: str
    domain: str
    full_name: str
    language: str
    country: str
    text: str | None
    created_at: datetime
    last_accessed_at: datetime
    changed_at: datetime
    changed_avatar_at: datetime
    page_url: str
    avatar_url: str
    profile_photo_url: str
    max_albums: int
    max_photos: int
    max_size: int
    albums: int
    photos: int
    size: int
    likes: int

    @classmethod
    def from_api(cls, data: dict, *, timezone: tzinfo | None = None) -> Account:
        return cls(
            **{
                map_key(FIELD_MAP, k): map_value(v, timezone=timezone)
                for k, v in data.items()
            }
        )

    def __repr__(self) -> str:
        return f"<Account id={self.id} email={self.email!r}>"
