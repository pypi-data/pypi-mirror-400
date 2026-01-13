from dataclasses import dataclass
from datetime import datetime, tzinfo

from zoneramaapi.models.aliases import AccountID, TabID
from zoneramaapi.models.utils import map_key, map_value

FIELD_MAP = {
    "ID": "id",
    "AccountID": "account_id",
    "Pwd": "password",
    "PwdHelp": "password_hint",
    "Public": "is_public",
    "Changed": "changed_at",
}


@dataclass(slots=True)
class Tab:
    id: TabID
    account_id: AccountID
    name: str
    rank: int
    secret: str
    password: str | None
    password_hint: str | None
    is_password_protected: bool
    is_public: bool
    changed_at: datetime
    type: str
    page_url: str

    @classmethod
    def from_api(cls, data: dict, *, timezone: tzinfo | None = None) -> Tab:
        return cls(
            **{
                map_key(FIELD_MAP, k): map_value(v, timezone=timezone)
                for k, v in data.items()
            }
        )

    def __repr__(self) -> str:
        return f"<Tab id={self.id} name={self.name!r}>"
