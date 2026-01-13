"""Main client for the ChangeCrab API."""

import time
from typing import Any, Dict, List, Optional

import requests

from changecrab.exceptions import (
    AuthenticationError,
    ChangeCrabError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from changecrab.models import Category, Changelog, Post


class ChangeCrab:
    """Client for the ChangeCrab API."""

    DEFAULT_BASE_URL = "https://changecrab.com/api"
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1.0

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ) -> None:
        if not api_key:
            raise ValueError("API key is required. Get one from your ChangeCrab account settings.")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-Key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API with retry logic."""
        url = f"{self._base_url}{endpoint}"
        last_exception = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    timeout=self._timeout,
                )
                return self._handle_response(response)
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exception = e
                if attempt < self._max_retries:
                    delay = self._retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
            except requests.RequestException as e:
                raise ChangeCrabError(f"Request failed: {str(e)}")

        if last_exception:
            error_msg = (
                f"Request failed after {self._max_retries + 1} attempts: "
                f"{str(last_exception)}"
            )
            raise ChangeCrabError(error_msg)
        raise ChangeCrabError("Request failed: Unknown error")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions for errors."""
        try:
            data = response.json()
        except ValueError:
            data = {}

        if response.status_code == 401:
            error_msg = data.get("error", "Authentication failed")
            raise AuthenticationError(error_msg, response.status_code, data)

        if response.status_code == 403:
            error_msg = data.get("error", "Access forbidden")
            raise AuthenticationError(error_msg, response.status_code, data)

        if response.status_code == 404:
            error_msg = data.get("error", "Resource not found")
            raise NotFoundError(error_msg, response.status_code, data)

        if response.status_code == 422:
            error_msg = data.get("error", "Validation failed")
            errors = data.get("errors", {})
            if not isinstance(errors, dict):
                errors = {}
            raise ValidationError(error_msg, response.status_code, data, errors)

        if response.status_code == 429:
            error_msg = data.get("error", "Rate limit exceeded")
            raise RateLimitError(error_msg, response.status_code, data)

        if response.status_code >= 500:
            error_msg = data.get("error", "Server error")
            raise ServerError(error_msg, response.status_code, data)

        if not response.ok:
            error_msg = data.get("error", f"Request failed with status {response.status_code}")
            raise ChangeCrabError(error_msg, response.status_code, data)

        return data

    # -------------------------------------------------------------------------
    # Changelog Methods
    # -------------------------------------------------------------------------

    def list_changelogs(self, team_id: Optional[int] = None) -> List[Changelog]:
        """
        List all changelogs accessible to your account.

        Note: The API returns all changelogs in a single response.
        If you have a large number of changelogs, consider filtering by team_id.
        """
        params = {}
        if team_id is not None:
            params["team_id"] = team_id

        response = self._request("GET", "/changelogs", params=params or None)
        data = response.get("data", [])
        return [Changelog.from_api(item) for item in data]

    def get_changelog(self, changelog_id: str) -> Changelog:
        """Get a specific changelog by its access ID."""
        response = self._request("GET", f"/changelogs/{changelog_id}")
        return Changelog.from_api(response.get("data", {}))

    def create_changelog(
        self,
        name: str,
        team: int,
        *,
        subdomain: Optional[str] = None,
        domain: Optional[str] = None,
        accent: Optional[str] = None,
        private: Optional[bool] = None,
        auto_notify: Optional[bool] = None,
        hide_subscriber: Optional[bool] = None,
        show_brand: Optional[bool] = None,
        subscribe_active: Optional[bool] = None,
        return_url: Optional[str] = None,
        slack_url: Optional[str] = None,
        teams_url: Optional[str] = None,
        site_url: Optional[str] = None,
        twitter: Optional[str] = None,
        statcrab: Optional[str] = None,
        robots: Optional[str] = None,
        ga_tracking: Optional[str] = None,
        logo: Optional[str] = None,
        twitter_post: Optional[int] = None,
        show_social: Optional[bool] = None,
        extra_css: Optional[str] = None,
        show_creator: Optional[bool] = None,
        show_filters: Optional[bool] = None,
        suggestion_initial: Optional[int] = None,
        suggestion_final: Optional[int] = None,
        guest_voting: Optional[bool] = None,
        guest_commenting: Optional[bool] = None,
        guest_creation: Optional[bool] = None,
        suggestion: Optional[bool] = None,
        approve_type: Optional[int] = None,
        favicon: Optional[str] = None,
        admin_suggestions_only: Optional[bool] = None,
        downvotes: Optional[bool] = None,
        discord_webhook: Optional[str] = None,
    ) -> Changelog:
        """Create a new changelog. Requires name and team."""
        payload: Dict[str, Any] = {"name": name, "team": team}
        field_mapping = {
            "subdomain": subdomain,
            "domain": domain,
            "accent": accent,
            "private": private,
            "autonotify": auto_notify,
            "hidesubscriber": hide_subscriber,
            "showbrand": show_brand,
            "subscribeactive": subscribe_active,
            "returnurl": return_url,
            "slackurl": slack_url,
            "teamsurl": teams_url,
            "siteurl": site_url,
            "twitter": twitter,
            "statcrab": statcrab,
            "robots": robots,
            "gatracking": ga_tracking,
            "logo": logo,
            "twitterpost": twitter_post,
            "showsocial": show_social,
            "extracss": extra_css,
            "showcreator": show_creator,
            "showfilters": show_filters,
            "suggestion_initial": suggestion_initial,
            "suggestion_final": suggestion_final,
            "guest_voting": guest_voting,
            "guest_commenting": guest_commenting,
            "guest_creation": guest_creation,
            "suggestion": suggestion,
            "approve_type": approve_type,
            "favicon": favicon,
            "admin_suggestions_only": admin_suggestions_only,
            "downvotes": downvotes,
            "discord_webhook": discord_webhook,
        }

        for key, value in field_mapping.items():
            if value is not None:
                payload[key] = value

        response = self._request("POST", "/changelogs", json=payload)
        return Changelog.from_api(response.get("data", {}))

    def update_changelog(
        self,
        changelog_id: str,
        **kwargs: Any,
    ) -> Changelog:
        """
        Update an existing changelog.

        Accepts the same parameters as create_changelog (except team).
        """
        api_mapping = {
            "auto_notify": "autonotify",
            "hide_subscriber": "hidesubscriber",
            "show_brand": "showbrand",
            "subscribe_active": "subscribeactive",
            "return_url": "returnurl",
            "slack_url": "slackurl",
            "teams_url": "teamsurl",
            "site_url": "siteurl",
            "ga_tracking": "gatracking",
            "twitter_post": "twitterpost",
            "show_social": "showsocial",
            "extra_css": "extracss",
            "show_creator": "showcreator",
            "show_filters": "showfilters",
        }

        payload = {}
        for key, value in kwargs.items():
            if value is not None:
                api_key = api_mapping.get(key, key)
                payload[api_key] = value

        response = self._request("PUT", f"/changelogs/{changelog_id}", json=payload)
        return Changelog.from_api(response.get("data", {}))

    def delete_changelog(self, changelog_id: str) -> bool:
        """Delete a changelog."""
        response = self._request("DELETE", f"/changelogs/{changelog_id}")
        return response.get("success", False)

    # -------------------------------------------------------------------------
    # Category Methods
    # -------------------------------------------------------------------------

    def list_categories(self, changelog_id: str) -> List[Category]:
        """
        List all categories for a changelog.

        Note: The API returns all categories in a single response.
        """
        response = self._request("GET", f"/changelogs/{changelog_id}/categories")
        data = response.get("data", [])
        return [Category.from_api(item) for item in data]

    # -------------------------------------------------------------------------
    # Post Methods
    # -------------------------------------------------------------------------

    def list_posts(self, changelog_id: str) -> List[Post]:
        """
        List all posts in a changelog.

        Note: The API returns all posts in a single response.
        """
        response = self._request("GET", f"/changelogs/{changelog_id}/posts")
        data = response.get("data", [])
        return [Post.from_api(item) for item in data]

    def create_post(
        self,
        changelog_id: str,
        summary: str,
        markdown: str,
        team: int,
        *,
        public: bool = True,
        announced: bool = False,
        draft: bool = False,
        link: Optional[str] = None,
        record: Optional[str] = None,
        categories: Optional[List[int]] = None,
    ) -> Post:
        """Create a new post in a changelog."""
        payload: Dict[str, Any] = {
            "summary": summary,
            "markdown": markdown,
            "team": team,
            "public": 1 if public else 0,
            "announced": 1 if announced else 0,
            "draft": 1 if draft else 0,
        }

        if link is not None:
            payload["link"] = link
        if record is not None:
            payload["record"] = record
        if categories is not None:
            payload["categories"] = categories

        response = self._request("POST", f"/changelogs/{changelog_id}/posts", json=payload)
        return Post.from_api(response.get("data", {}))

    def update_post(
        self,
        changelog_id: str,
        post_id: int,
        markdown: str,
        team: int,
        *,
        public: bool = True,
        summary: Optional[str] = None,
        announced: Optional[bool] = None,
        draft: Optional[bool] = None,
        link: Optional[str] = None,
        record: Optional[str] = None,
        publish_date: Optional[str] = None,
        categories: Optional[List[int]] = None,
    ) -> Post:
        """Update an existing post. Requires markdown and team."""
        payload: Dict[str, Any] = {
            "markdown": markdown,
            "team": team,
            "public": 1 if public else 0,
        }

        if summary is not None:
            payload["summary"] = summary
        if announced is not None:
            payload["announced"] = 1 if announced else 0
        if draft is not None:
            payload["draft"] = 1 if draft else 0
        if link is not None:
            payload["link"] = link
        if record is not None:
            payload["record"] = record
        if publish_date is not None:
            payload["publish_date"] = publish_date
        if categories is not None:
            payload["categories"] = categories

        response = self._request(
            "PUT",
            f"/changelogs/{changelog_id}/posts/{post_id}",
            json=payload,
        )
        return Post.from_api(response.get("data", {}))

    def delete_post(self, changelog_id: str, post_id: int) -> bool:
        """Delete a post from a changelog."""
        response = self._request("DELETE", f"/changelogs/{changelog_id}/posts/{post_id}")
        return response.get("success", False)

