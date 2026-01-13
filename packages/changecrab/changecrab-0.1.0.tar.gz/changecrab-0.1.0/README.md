# ChangeCrab Python SDK

The official Python client for the [ChangeCrab](https://changecrab.com) API. Manage your changelogs and release notes programmatically.

[![CI](https://github.com/changecrab/python_sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/changecrab/python_sdk/actions/workflows/ci.yml)

For complete API documentation, see the [ChangeCrab API Overview](https://changecrab.com/knowledge-base/integrations/api-overview).

## Installation

```bash
pip install changecrab
```

Or install from source:

```bash
git clone https://github.com/changecrab/python_sdk.git
cd python_sdk
pip install .
```

## Quick Start

```python
from changecrab import ChangeCrab

# Initialize the client with your API key
client = ChangeCrab(api_key="your_api_key_here")

# List all your changelogs
changelogs = client.list_changelogs()
for changelog in changelogs:
    print(f"{changelog.name} ({changelog.access_id})")

# Create a new post
post = client.create_post(
    changelog_id="abc123def4",
    summary="🚀 New Feature: Dark Mode",
    markdown="We've added dark mode support! Toggle it in your settings.",
    team=1,
    public=True
)
print(f"Created post #{post.id}")
```

## Authentication

Get your API key from your [ChangeCrab account settings](https://changecrab.com/api-keys). All API requests require authentication.

For detailed authentication information, see the [ChangeCrab API Overview](https://changecrab.com/knowledge-base/integrations/api-overview).

```python
from changecrab import ChangeCrab

client = ChangeCrab(api_key="your_api_key_here")
```

You can also configure the client with custom settings:

```python
client = ChangeCrab(
    api_key="your_api_key_here",
    base_url="https://changecrab.com/api",  # Custom API URL (optional)
    timeout=60,  # Request timeout in seconds (default: 30)
    max_retries=3,  # Max retry attempts for transient errors (default: 3)
    retry_delay=1.0,  # Initial retry delay in seconds (default: 1.0, exponential backoff)
)
```

### Retry Logic

The SDK automatically retries requests on transient errors (timeouts, connection errors) with exponential backoff:
- Default: 3 retries with delays of 1s, 2s, 4s
- Only retries on `Timeout` and `ConnectionError` exceptions
- Non-retryable errors (authentication, validation, etc.) are raised immediately

## Usage Guide

### Changelogs

#### List Changelogs

Retrieve all changelogs accessible to your account:

```python
# Get all changelogs
changelogs = client.list_changelogs()

# Filter by team ID
team_changelogs = client.list_changelogs(team_id=123)
```

#### Get a Changelog

Retrieve a specific changelog by its access ID:

```python
changelog = client.get_changelog("abc123def4")
print(f"Name: {changelog.name}")
print(f"Subdomain: {changelog.subdomain}")
print(f"Created: {changelog.created_at}")
```

#### Create a Changelog

```python
changelog = client.create_changelog(
    name="My Product Changelog",
    team=1,
    subdomain="myproduct",
    accent="#007bff",
    auto_notify=True,
    show_social=True
)
print(f"Created: {changelog.access_id}")
```

All available options:

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | **Required.** Name of the changelog |
| `team` | int | **Required.** Team ID that owns the changelog |
| `subdomain` | str | Subdomain (e.g., "myapp" for myapp.changecrab.com) |
| `domain` | str | Custom domain |
| `accent` | str | Accent color in hex format (e.g., "#E33597") |
| `private` | bool | Whether the changelog is private |
| `auto_notify` | bool | Auto-notify subscribers of new posts |
| `hide_subscriber` | bool | Hide subscriber count |
| `show_brand` | bool | Show ChangeCrab branding |
| `subscribe_active` | bool | Enable subscriptions |
| `return_url` | str | Return URL for your site |
| `slack_url` | str | Slack webhook URL |
| `teams_url` | str | Microsoft Teams webhook URL |
| `discord_webhook` | str | Discord webhook URL |
| `site_url` | str | Your main website URL |
| `twitter` | str | Twitter handle |
| `ga_tracking` | str | Google Analytics tracking ID |
| `logo` | str | Logo URL |
| `favicon` | str | Favicon URL |
| `extra_css` | str | Custom CSS |
| `show_creator` | bool | Show post creator names |
| `show_filters` | bool | Show category filters |
| `suggestion` | bool | Enable suggestions |
| `guest_voting` | bool | Allow guest voting |
| `guest_commenting` | bool | Allow guest comments |
| `guest_creation` | bool | Allow guest suggestions |
| `downvotes` | bool | Enable downvoting |

#### Update a Changelog

```python
changelog = client.update_changelog(
    "abc123def4",
    name="Updated Changelog Name",
    accent="#ff5722",
    auto_notify=False
)
```

#### Delete a Changelog

```python
client.delete_changelog("abc123def4")
```

---

### Categories

Categories help organize posts within a changelog. Retrieve them to get category IDs for tagging posts.

```python
categories = client.list_categories("abc123def4")
for cat in categories:
    print(f"{cat.title} (ID: {cat.id}, Color: {cat.colour})")
```

---

### Posts

#### List Posts

```python
posts = client.list_posts("abc123def4")
for post in posts:
    status = "Draft" if post.draft else "Published"
    print(f"[{status}] {post.summary}")
```

#### Create a Post

```python
post = client.create_post(
    changelog_id="abc123def4",
    summary="Bug Fix: Login Issue Resolved",
    markdown="""
## What's Fixed

We've resolved an issue where some users couldn't log in using social authentication.

### Details
- Fixed OAuth callback handling
- Improved error messages for failed logins
- Added retry logic for transient failures

Thanks to everyone who reported this issue!
    """,
    team=1,
    public=True,
    announced=True,  # Notify subscribers
    categories=[1, 2]  # Category IDs from list_categories()
)
```

All available options:

| Parameter | Type | Description |
|-----------|------|-------------|
| `changelog_id` | str | **Required.** Changelog access ID |
| `summary` | str | **Required.** Title/summary (max 2555 chars) |
| `markdown` | str | **Required.** Content in Markdown format |
| `team` | int | **Required.** Team ID |
| `public` | bool | Public visibility (default: True) |
| `announced` | bool | Notify subscribers (default: False) |
| `draft` | bool | Save as draft (default: False) |
| `link` | str | Related URL |
| `record` | str | Record identifier (single char) |
| `categories` | list[int] | Category IDs to tag the post |

#### Update a Post

```python
post = client.update_post(
    changelog_id="abc123def4",
    post_id=123,
    markdown="Updated content here with more details.",
    team=1,
    summary="Updated Title",
    announced=True,  # Announce to subscribers
    publish_date="2024-01-15",
    categories=[1, 3]
)
```

#### Delete a Post

```python
client.delete_post("abc123def4", post_id=123)
```

---

## Error Handling

The SDK provides specific exception classes for different error scenarios:

```python
from changecrab import (
    ChangeCrab,
    ChangeCrabError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)

client = ChangeCrab(api_key="your_api_key")

try:
    post = client.create_post(
        changelog_id="abc123def4",
        summary="",  # Empty summary will fail validation
        markdown="Content here",
        team=1
    )
except ValidationError as e:
    # Handle validation errors with field-level details
    print(f"Validation failed: {e.message}")
    for field, messages in e.errors.items():
        print(f"  {field}: {', '.join(messages)}")

except AuthenticationError as e:
    # Invalid or missing API key
    print(f"Auth failed: {e.message}")

except NotFoundError as e:
    # Resource doesn't exist
    print(f"Not found: {e.message}")

except RateLimitError as e:
    # Too many requests - implement backoff
    print("Rate limited. Waiting before retry...")

except ServerError as e:
    # ChangeCrab server error - retry may help
    print(f"Server error: {e.message}")

except ChangeCrabError as e:
    # Catch-all for any SDK error
    print(f"Error: {e.message} (status: {e.status_code})")
```

### Exception Hierarchy

```
ChangeCrabError (base)
├── AuthenticationError  # 401, 403
├── NotFoundError        # 404
├── ValidationError      # 422 (includes field errors)
├── RateLimitError       # 429
└── ServerError          # 5xx
```

---

## Data Models

The SDK returns typed dataclass objects for easy access to resource properties:

### Changelog

```python
changelog = client.get_changelog("abc123def4")

# Access properties directly
print(changelog.id)           # Numeric ID
print(changelog.access_id)    # String ID used in API URLs
print(changelog.name)         # Display name
print(changelog.team)         # Team ID
print(changelog.subdomain)    # Subdomain
print(changelog.accent)       # Accent color
print(changelog.created_at)   # datetime object

# Convert to dictionary
data = changelog.to_dict()
```

### Post

```python
post = client.list_posts("abc123def4")[0]

print(post.id)           # Numeric ID
print(post.summary)      # Title
print(post.markdown)     # Content
print(post.public)       # bool
print(post.announced)    # bool
print(post.draft)        # bool
print(post.categories)   # List of PostCategory objects
print(post.created_at)   # datetime object
```

### Category

```python
category = client.list_categories("abc123def4")[0]

print(category.id)       # Numeric ID
print(category.title)    # Display name
print(category.colour)   # Hex color code
```

---

## Environment Variables

You can set your API key as an environment variable:

```bash
export CHANGECRAB_API_KEY="your_api_key_here"
```

Then initialize the client:

```python
import os
from changecrab import ChangeCrab

client = ChangeCrab(api_key=os.environ["CHANGECRAB_API_KEY"])
```

---

## Type Hints

This SDK includes full type annotations and a `py.typed` marker for static type checkers like mypy:

```python
from typing import Optional
from changecrab import ChangeCrab, Changelog, Post

def get_latest_post(client: ChangeCrab, changelog_id: str) -> Optional[Post]:
    posts = client.list_posts(changelog_id)
    return posts[0] if posts else None
```

---

## Testing

The SDK includes a comprehensive test suite. To run tests:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=changecrab --cov-report=term

# Run specific test file
pytest tests/test_client.py
```

The test suite includes:
- Unit tests for all client methods (with mocked API responses)
- Model tests for data parsing and conversion
- Exception handling tests
- Error scenario tests

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Install dev dependencies (`pip install -e ".[dev]"`)
4. Make your changes
5. Run tests (`pytest`)
6. Run linting (`ruff check .`)
7. Run type checking (`mypy changecrab`)
8. Commit your changes
9. Push to the branch
10. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

- **API Documentation:** [ChangeCrab API Overview](https://changecrab.com/knowledge-base/integrations/api-overview)
- **Issues:** [GitHub Issues](https://github.com/changecrab/python_sdk/issues)
- **Email:** support@changecrab.com
