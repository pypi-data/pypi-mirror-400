"""Data models for the ChangeCrab SDK."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO format datetime string to datetime object."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _parse_bool(value: Any) -> bool:
    """Parse various representations of boolean values."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    return False


@dataclass
class Category:
    """Represents a changelog category."""

    id: int
    title: str
    colour: str
    type: str
    project: str
    is_default: bool = False
    meta: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Category":
        """Create Category from API response."""
        return cls(
            id=data["id"],
            title=data["title"],
            colour=data.get("colour", ""),
            type=data.get("type", "changelog"),
            project=data.get("project", ""),
            is_default=_parse_bool(data.get("isDefault", 0)),
            meta=data.get("meta"),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class PostCategory:
    """Represents the relationship between a post and a category."""

    id: int
    post_id: int
    category_id: int
    category: Optional[Category] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "PostCategory":
        """Create PostCategory from API response."""
        category_data = data.get("category", [])
        category = None
        if category_data and isinstance(category_data, list) and len(category_data) > 0:
            category = Category.from_api(category_data[0])
        elif isinstance(category_data, dict):
            category = Category.from_api(category_data)

        return cls(
            id=data.get("id", 0),
            post_id=data.get("logitems_id", 0),
            category_id=data.get("category_id", 0),
            category=category,
        )


@dataclass
class Post:
    """Represents a changelog post/entry."""

    id: int
    summary: str
    markdown: str
    type: str = "editor"
    project: str = ""
    creator: int = 0
    team: int = 0
    public: bool = True
    announced: bool = False
    draft: bool = False
    link: Optional[str] = None
    record: Optional[str] = None
    categories: List[PostCategory] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Post":
        """Create Post from API response."""
        categories_data = data.get("categories", [])
        categories = []
        if isinstance(categories_data, list):
            for cat_data in categories_data:
                if isinstance(cat_data, dict):
                    categories.append(PostCategory.from_api(cat_data))

        return cls(
            id=data["id"],
            summary=data.get("summary", ""),
            markdown=data.get("markdown", ""),
            type=data.get("type", "editor"),
            project=data.get("project", ""),
            creator=data.get("creator", 0),
            team=data.get("team", 0),
            public=_parse_bool(data.get("public", 1)),
            announced=_parse_bool(data.get("announced", 0)),
            draft=_parse_bool(data.get("draft", 0)),
            link=data.get("link"),
            record=data.get("record"),
            categories=categories,
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = asdict(self)
        result["categories"] = [c.category_id for c in self.categories if c.category_id]
        return {k: v for k, v in result.items() if v is not None}


@dataclass
class Changelog:
    """Represents a changelog."""

    id: int
    access_id: str
    name: str
    team: int
    team_name: str = ""
    subdomain: Optional[str] = None
    domain: Optional[str] = None
    accent: str = "#E33597"
    private: bool = False
    auto_notify: bool = True
    hide_subscriber: bool = False
    show_brand: bool = True
    subscribe_active: bool = True
    return_url: Optional[str] = None
    slack_url: Optional[str] = None
    teams_url: Optional[str] = None
    site_url: Optional[str] = None
    twitter: Optional[str] = None
    statcrab: Optional[str] = None
    robots: str = "allow"
    ga_tracking: Optional[str] = None
    logo: Optional[str] = None
    twitter_post: Optional[int] = None
    show_social: bool = True
    extra_css: Optional[str] = None
    show_creator: bool = True
    show_filters: bool = True
    suggestion_initial: Optional[int] = None
    suggestion_final: Optional[int] = None
    guest_voting: Optional[bool] = None
    guest_commenting: bool = False
    guest_creation: bool = False
    suggestion: bool = True
    approve_type: int = 0
    favicon: Optional[str] = None
    admin_suggestions_only: bool = False
    downvotes: bool = True
    discord_webhook: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Changelog":
        """Create Changelog from API response."""
        return cls(
            id=data["id"],
            access_id=data.get("accessid", ""),
            name=data.get("name", ""),
            team=data.get("team", 0),
            team_name=data.get("team_name", ""),
            subdomain=data.get("subdomain"),
            domain=data.get("domain"),
            accent=data.get("accent", "#E33597"),
            private=_parse_bool(data.get("private", 0)),
            auto_notify=_parse_bool(data.get("autonotify", 1)),
            hide_subscriber=_parse_bool(data.get("hidesubscriber", 0)),
            show_brand=_parse_bool(data.get("showbrand", 1)),
            subscribe_active=_parse_bool(data.get("subscribeactive", 1)),
            return_url=data.get("returnurl"),
            slack_url=data.get("slackurl"),
            teams_url=data.get("teamsurl"),
            site_url=data.get("siteurl"),
            twitter=data.get("twitter"),
            statcrab=data.get("statcrab"),
            robots=data.get("robots", "allow"),
            ga_tracking=data.get("gatracking"),
            logo=data.get("logo"),
            twitter_post=data.get("twitterpost"),
            show_social=_parse_bool(data.get("showsocial", 1)),
            extra_css=data.get("extracss"),
            show_creator=_parse_bool(data.get("showcreator", 1)),
            show_filters=_parse_bool(data.get("showfilters", 1)),
            suggestion_initial=data.get("suggestion_initial"),
            suggestion_final=data.get("suggestion_final"),
            guest_voting=data.get("guest_voting"),
            guest_commenting=_parse_bool(data.get("guest_commenting", 0)),
            guest_creation=_parse_bool(data.get("guest_creation", 0)),
            suggestion=_parse_bool(data.get("suggestion", 1)),
            approve_type=data.get("approve_type", 0),
            favicon=data.get("favicon"),
            admin_suggestions_only=_parse_bool(data.get("admin_suggestions_only", 0)),
            downvotes=_parse_bool(data.get("downvotes", 1)),
            discord_webhook=data.get("discord_webhook"),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {k: v for k, v in asdict(self).items() if v is not None}

