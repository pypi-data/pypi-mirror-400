from dataclasses import dataclass
from datetime import datetime, tzinfo

from zoneramaapi.models.aliases import AccountID, AlbumID, PhotoID, TabID
from zoneramaapi.models.utils import map_key, map_value

FIELD_MAP = {
    "ID": "id",
    "ParentID": "parent_id",
    "AccountID": "account_id",
    "PhotoID": "cover_photo_id",
    "Inserted": "created_at",
    "Changed": "changed_at",
    "Updated": "updated_at",
    "Text": "description",
    "Pwd": "password",
    "PwdHelp": "password_hint",
    "PublicList": "is_public_list",
    "PageUrl": "page_url",
    "ImageUrl": "cover_image_url",
    "ImagePatternUrl": "cover_image_pattern_url",
    "IsPasswordProtected": "is_password_protected",
    "IsPrivate": "is_private",
    "IsProtected": "is_protected",
    "IsPublic": "is_public",
    "IsSecret": "is_secret",
}


@dataclass(slots=True)
class Album:
    id: AlbumID
    parent_id: int | None
    account_id: AccountID
    cover_photo_id: PhotoID
    name: str
    created_at: datetime
    changed_at: datetime
    updated_at: datetime
    description: str
    password: str | None
    password_hint: str | None
    secret: str
    is_public_list: bool
    path_of_id: str
    path_of_name: str
    path_level: int
    protected: bool | None
    longitude: float | None
    latitude: float | None
    tab_id: TabID
    facebook_synced: int
    page_url: str
    cover_image_url: str
    cover_image_pattern_url: str
    is_password_protected: bool
    is_private: bool
    is_protected: bool
    is_public: bool
    is_secret: bool
    type: str
    albums: int
    photos: int
    size: int
    comments: int
    browse: int
    like: int

    @classmethod
    def from_api(cls, data: dict, *, timezone: tzinfo | None = None) -> Album:
        return cls(
            **{
                map_key(FIELD_MAP, k): map_value(v, timezone=timezone)
                for k, v in data.items()
            }
        )

    def __repr__(self) -> str:
        return f"<Album id={self.id} name={self.name!r}>"
