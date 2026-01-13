"""Tests for data models."""

from datetime import datetime

from changecrab.models import Category, Changelog, Post, PostCategory


class TestCategory:
    """Test Category model."""

    def test_from_api(self):
        """Test creating Category from API response."""
        data = {
            "id": 1,
            "title": "Bug Fixes",
            "colour": "#EF4444",
            "type": "changelog",
            "project": "abc123",
            "isDefault": 0,
        }
        category = Category.from_api(data)

        assert category.id == 1
        assert category.title == "Bug Fixes"
        assert category.colour == "#EF4444"
        assert category.is_default is False

    def test_from_api_with_default(self):
        """Test Category with isDefault set to 1."""
        data = {
            "id": 1,
            "title": "Default",
            "colour": "#000000",
            "type": "changelog",
            "project": "abc123",
            "isDefault": 1,
        }
        category = Category.from_api(data)
        assert category.is_default is True

    def test_to_dict(self):
        """Test converting Category to dictionary."""
        category = Category(
            id=1,
            title="Test",
            colour="#FF0000",
            type="changelog",
            project="abc123",
        )
        data = category.to_dict()
        assert data["id"] == 1
        assert data["title"] == "Test"


class TestPost:
    """Test Post model."""

    def test_from_api(self):
        """Test creating Post from API response."""
        data = {
            "id": 1,
            "summary": "Test Post",
            "markdown": "Content here",
            "type": "editor",
            "project": "abc123",
            "team": 1,
            "public": 1,
            "announced": 0,
            "draft": 0,
            "categories": [],
        }
        post = Post.from_api(data)

        assert post.id == 1
        assert post.summary == "Test Post"
        assert post.markdown == "Content here"
        assert post.public is True
        assert post.announced is False
        assert post.draft is False

    def test_from_api_with_categories(self):
        """Test Post with categories."""
        data = {
            "id": 1,
            "summary": "Test",
            "markdown": "Content",
            "type": "editor",
            "project": "abc123",
            "team": 1,
            "public": 1,
            "announced": 0,
            "draft": 0,
            "categories": [
                {
                    "id": 1,
                    "logitems_id": 1,
                    "category_id": 2,
                    "category": [
                        {
                            "id": 2,
                            "title": "Bug Fixes",
                            "colour": "#FF0000",
                            "type": "changelog",
                            "project": "abc123",
                        }
                    ],
                }
            ],
        }
        post = Post.from_api(data)
        assert len(post.categories) == 1
        assert post.categories[0].category_id == 2

    def test_to_dict(self):
        """Test converting Post to dictionary."""
        post = Post(
            id=1,
            summary="Test",
            markdown="Content",
            team=1,
        )
        data = post.to_dict()
        assert data["id"] == 1
        assert data["summary"] == "Test"
        assert "categories" in data


class TestChangelog:
    """Test Changelog model."""

    def test_from_api(self):
        """Test creating Changelog from API response."""
        data = {
            "id": 1,
            "accessid": "abc123",
            "name": "Test Changelog",
            "team": 1,
            "team_name": "Test Team",
            "accent": "#E33597",
            "private": 0,
            "autonotify": 1,
        }
        changelog = Changelog.from_api(data)

        assert changelog.id == 1
        assert changelog.access_id == "abc123"
        assert changelog.name == "Test Changelog"
        assert changelog.private is False
        assert changelog.auto_notify is True

    def test_from_api_with_datetime(self):
        """Test Changelog with datetime parsing."""
        data = {
            "id": 1,
            "accessid": "abc123",
            "name": "Test",
            "team": 1,
            "created_at": "2023-01-01T00:00:00.000000Z",
            "updated_at": "2023-01-02T00:00:00.000000Z",
        }
        changelog = Changelog.from_api(data)

        assert isinstance(changelog.created_at, datetime)
        assert isinstance(changelog.updated_at, datetime)

    def test_to_dict(self):
        """Test converting Changelog to dictionary."""
        changelog = Changelog(
            id=1,
            access_id="abc123",
            name="Test",
            team=1,
        )
        data = changelog.to_dict()
        assert data["id"] == 1
        assert data["name"] == "Test"


class TestPostCategory:
    """Test PostCategory model."""

    def test_from_api(self):
        """Test creating PostCategory from API response."""
        data = {
            "id": 1,
            "logitems_id": 10,
            "category_id": 5,
            "category": [
                {
                    "id": 5,
                    "title": "Feature",
                    "colour": "#00FF00",
                    "type": "changelog",
                    "project": "abc123",
                }
            ],
        }
        post_category = PostCategory.from_api(data)

        assert post_category.id == 1
        assert post_category.post_id == 10
        assert post_category.category_id == 5
        assert post_category.category is not None
        assert post_category.category.title == "Feature"

