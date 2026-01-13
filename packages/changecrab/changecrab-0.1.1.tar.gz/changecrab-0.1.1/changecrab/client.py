"""Main client for the ChangeCrab API."""

import json
import re
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

    # HTTP status codes that should trigger retries
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

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

    @staticmethod
    def _sanitize_response_data(data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """
        Sanitize response data to prevent leaking secrets.

        Redacts API keys and truncates large response bodies.
        """
        if not data:
            return {}
        
        # Create a deep copy to avoid modifying the original
        sanitized = json.loads(json.dumps(data))
        
        # Redact API key patterns in string values
        api_key_pattern = re.compile(
            re.escape(api_key[:8]) + r".*" if len(api_key) > 8 else re.escape(api_key),
            re.IGNORECASE
        )
        
        def redact_strings(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: redact_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [redact_strings(item) for item in obj]
            elif isinstance(obj, str):
                # Redact API key if found in string
                if api_key in obj or (len(api_key) > 8 and api_key[:8] in obj):
                    return api_key_pattern.sub("[REDACTED]", obj)
                return obj
            return obj
        
        return redact_strings(sanitized)

    @staticmethod
    def _extract_request_id(response: requests.Response) -> Optional[str]:
        """Extract request ID from response headers if present."""
        try:
            # Common header names for request IDs
            request_id_headers = [
                "X-Request-ID",
                "X-Request-Id",
                "Request-ID",
                "Request-Id",
                "X-Correlation-ID",
                "X-Correlation-Id",
            ]
            for header in request_id_headers:
                request_id = response.headers.get(header)
                if request_id and isinstance(request_id, str):
                    return request_id
        except (AttributeError, TypeError):
            # Handle cases where headers might not be a dict-like object
            pass
        return None

    @staticmethod
    def _parse_retry_after(response: requests.Response) -> float:
        """
        Parse Retry-After header from response.

        Returns delay in seconds. Supports both integer seconds and HTTP-date format.
        """
        try:
            retry_after = response.headers.get("Retry-After")
            if not retry_after:
                return 0.0
            
            # Ensure we have a string or number, not a Mock or other object
            if not isinstance(retry_after, (str, int, float)):
                return 0.0
            
            try:
                # Try parsing as integer (seconds)
                return float(retry_after)
            except ValueError:
                # Try parsing as HTTP-date (RFC 7231)
                try:
                    from email.utils import parsedate_to_datetime
                    retry_date = parsedate_to_datetime(str(retry_after))
                    if retry_date:
                        import datetime
                        now = datetime.datetime.now(datetime.timezone.utc)
                        if retry_date.tzinfo is None:
                            retry_date = retry_date.replace(tzinfo=datetime.timezone.utc)
                        delay = (retry_date - now).total_seconds()
                        return max(0.0, delay)
                except (ValueError, TypeError):
                    pass
        except (AttributeError, TypeError):
            # Handle cases where headers might not be a dict-like object
            pass
        
        return 0.0

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API with retry logic.

        Retries on:
        - Network errors (Timeout, ConnectionError)
        - HTTP 429 (Rate Limit) - respects Retry-After header
        - HTTP 5xx (Server errors: 500, 502, 503, 504)
        """
        url = f"{self._base_url}{endpoint}"
        last_exception = None
        last_response = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    timeout=self._timeout,
                )
                
                # Check if we should retry based on status code
                if response.status_code in self.RETRYABLE_STATUS_CODES:
                    last_response = response
                    
                    # Don't retry on last attempt
                    if attempt < self._max_retries:
                        # For 429, respect Retry-After header if present
                        if response.status_code == 429:
                            retry_after = self._parse_retry_after(response)
                            if retry_after > 0:
                                delay = retry_after
                            else:
                                delay = self._retry_delay * (2 ** attempt)
                        else:
                            # For 5xx errors, use exponential backoff
                            delay = self._retry_delay * (2 ** attempt)
                        
                        time.sleep(delay)
                        continue
                    else:
                        # Last attempt failed, handle the error response
                        return self._handle_response(response)
                
                # Success or non-retryable error - handle normally
                return self._handle_response(response)
                
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exception = e
                if attempt < self._max_retries:
                    delay = self._retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
            except requests.RequestException as e:
                # Non-retryable request exception
                raise ChangeCrabError(f"Request failed: {str(e)}")

        # All retries exhausted
        if last_exception:
            error_msg = (
                f"Request failed after {self._max_retries + 1} attempts: "
                f"{str(last_exception)}"
            )
            raise ChangeCrabError(error_msg)
        
        if last_response:
            # Handle the last response that triggered retries
            return self._handle_response(last_response)
        
        raise ChangeCrabError("Request failed: Unknown error")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions for errors.

        Sanitizes response data to prevent leaking secrets and includes
        request ID if available.
        """
        try:
            data = response.json()
        except ValueError:
            data = {}

        # Sanitize response data to prevent secret leaks
        sanitized_data = self._sanitize_response_data(data, self._api_key)
        request_id = self._extract_request_id(response)

        if response.status_code == 401:
            error_msg = data.get("error", "Authentication failed")
            raise AuthenticationError(
                error_msg, response.status_code, sanitized_data, request_id
            )

        if response.status_code == 403:
            error_msg = data.get("error", "Access forbidden")
            raise AuthenticationError(
                error_msg, response.status_code, sanitized_data, request_id
            )

        if response.status_code == 404:
            error_msg = data.get("error", "Resource not found")
            raise NotFoundError(
                error_msg, response.status_code, sanitized_data, request_id
            )

        if response.status_code == 422:
            error_msg = data.get("error", "Validation failed")
            errors = data.get("errors", {})
            if not isinstance(errors, dict):
                errors = {}
            raise ValidationError(
                error_msg, response.status_code, sanitized_data, errors, request_id
            )

        if response.status_code == 429:
            error_msg = data.get("error", "Rate limit exceeded")
            raise RateLimitError(
                error_msg, response.status_code, sanitized_data, request_id
            )

        if response.status_code >= 500:
            error_msg = data.get("error", "Server error")
            raise ServerError(
                error_msg, response.status_code, sanitized_data, request_id
            )

        if not response.ok:
            error_msg = data.get(
                "error", f"Request failed with status {response.status_code}"
            )
            raise ChangeCrabError(
                error_msg, response.status_code, sanitized_data, request_id
            )

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

