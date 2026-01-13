from dataclasses import dataclass
from datetime import datetime, tzinfo

from zoneramaapi.models.aliases import AccountID, AlbumID, TabID
from zoneramaapi.models.utils import map_key, map_value

FIELD_MAP = {
    "ID": "id",
    "AlbumID": "album_id",
    "AccountID": "account_id",
    "Inserted": "created_at",
    "Changed": "changed_at",
    "Pwd": "password",
    "Public": "is_public",
    "Changed": "changed_at",
    "PathOfID": "path_of_id",
    "MD5Hash": "MD5",
}


@dataclass(slots=True)
class Photo:
    id: TabID
    album_id: AlbumID
    account_id: AccountID
    name: str
    created_at: datetime
    changed_at: datetime
    text: str | None
    password: str | None
    secret: str | None
    public_list: bool
    path_of_id: str
    path_of_name: str
    path_level: int
    protected: bool | None
    longitude: float | None
    latitude: float | None
    media_type: int
    page_url: str
    image_url: str
    image_pattern_url: str
    original_image_url: str
    is_password_protected: bool
    is_private: bool
    is_protected: bool
    is_public: bool
    is_secret: bool
    width: int
    height: int
    size: int
    timestamp: datetime
    rotate_flip: int
    browse: int
    comments: int
    like: int
    score_sum: int
    score_count: int
    score: float
    metadata: dict
    licence: dict
    MD5: str

    @classmethod
    def from_api(cls, data: dict, *, timezone: tzinfo | None = None) -> Photo:
        return cls(
            **{
                map_key(FIELD_MAP, k): map_value(v, timezone=timezone)
                for k, v in data.items()
            }
        )

    def __repr__(self) -> str:
        return f"<Photo id={self.id} name={self.name!r}>"
