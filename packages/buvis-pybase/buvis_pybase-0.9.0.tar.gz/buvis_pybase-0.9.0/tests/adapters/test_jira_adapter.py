from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO
from buvis.pybase.adapters.jira.jira import JiraAdapter


@pytest.fixture
def mock_config() -> MagicMock:
    """Create a mock config object with default valid values."""
    config = MagicMock()
    config.get_configuration_item_or_default.side_effect = lambda key, default: {
        "server": "https://jira.example.com",
        "token": "test-token",
        "proxy": None,
    }.get(key, default)
    config.get_configuration_item.side_effect = lambda key: {
        "server": "https://jira.example.com",
        "token": "test-token",
    }[key]
    return config


@pytest.fixture
def sample_issue_dto() -> JiraIssueDTO:
    """Create a sample JiraIssueDTO for testing."""
    return JiraIssueDTO(
        project="PROJ",
        title="Test Issue",
        description="Test description",
        issue_type="Task",
        labels=["test", "automated"],
        priority="Medium",
        ticket="PARENT-123",
        feature="EPIC-456",
        assignee="testuser",
        reporter="reporter",
        team="DevTeam",
        region="US",
    )


@pytest.fixture
def mock_jira_client():
    """Create a mock JIRA client for testing."""
    with patch("buvis.pybase.adapters.jira.jira.JIRA") as mock_jira_class:
        mock_client = MagicMock()
        mock_jira_class.return_value = mock_client
        yield mock_client


class TestJiraAdapterInit:
    """Test JiraAdapter initialization."""

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_raises_when_server_missing(self, mock_jira: MagicMock) -> None:
        """Missing server raises ValueError."""
        config = MagicMock()
        config.get_configuration_item_or_default.side_effect = lambda key, default: {
            "server": None,
            "token": "test-token",
            "proxy": None,
        }.get(key, default)

        with pytest.raises(ValueError, match="Server and token must be provided"):
            JiraAdapter(config)

        mock_jira.assert_not_called()

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_raises_when_token_missing(self, mock_jira: MagicMock) -> None:
        """Missing token raises ValueError."""
        config = MagicMock()
        config.get_configuration_item_or_default.side_effect = lambda key, default: {
            "server": "https://jira.example.com",
            "token": None,
            "proxy": None,
        }.get(key, default)

        with pytest.raises(ValueError, match="Server and token must be provided"):
            JiraAdapter(config)

        mock_jira.assert_not_called()

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_creates_client_with_server_and_token(
        self, mock_jira: MagicMock, mock_config: MagicMock
    ) -> None:
        """Valid config creates JIRA client."""
        JiraAdapter(mock_config)

        mock_jira.assert_called_once_with(
            server="https://jira.example.com",
            token_auth="test-token",
        )

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_sets_proxy_when_configured(
        self, mock_jira: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Proxy config sets https_proxy env var and clears existing."""
        monkeypatch.setenv("https_proxy", "old")
        monkeypatch.setenv("http_proxy", "old")
        config = MagicMock()
        config.get_configuration_item_or_default.side_effect = lambda key, default: {
            "server": "https://jira.example.com",
            "token": "test-token",
            "proxy": "http://proxy.example.com:8080",
        }.get(key, default)
        config.get_configuration_item.side_effect = lambda key: {
            "server": "https://jira.example.com",
            "token": "test-token",
            "proxy": "http://proxy.example.com:8080",
        }[key]

        JiraAdapter(config)

        assert os.environ.get("https_proxy") == "http://proxy.example.com:8080"
        assert "http_proxy" not in os.environ


class TestJiraAdapterCreate:
    """Test JiraAdapter.create() method."""

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_creates_issue_with_correct_fields(
        self,
        mock_jira_cls: MagicMock,
        mock_config: MagicMock,
        sample_issue_dto: JiraIssueDTO,
    ) -> None:
        """create() passes correct field mapping to JIRA API."""
        mock_jira = mock_jira_cls.return_value
        mock_issue = MagicMock()
        mock_issue.key = "PROJ-123"
        mock_issue.permalink.return_value = "https://jira.example.com/browse/PROJ-123"
        mock_issue.fields.project.key = "PROJ"
        mock_issue.fields.summary = "Test Issue"
        mock_issue.fields.description = "Test description"
        mock_issue.fields.issuetype.name = "Task"
        mock_issue.fields.labels = ["test", "automated"]
        mock_issue.fields.priority.name = "Medium"
        mock_issue.fields.customfield_11502 = "PARENT-123"
        mock_issue.fields.customfield_10001 = "EPIC-456"
        mock_issue.fields.assignee.key = "testuser"
        mock_issue.fields.reporter.key = "reporter"
        mock_issue.fields.customfield_10501.value = "DevTeam"
        mock_issue.fields.customfield_12900.value = "US"
        mock_jira.create_issue.return_value = mock_issue
        mock_jira.issue.return_value = mock_issue

        adapter = JiraAdapter(mock_config)
        adapter.create(sample_issue_dto)

        mock_jira.create_issue.assert_called_once()
        call_fields = mock_jira.create_issue.call_args[1]["fields"]
        assert call_fields["project"] == {"key": "PROJ"}
        assert call_fields["summary"] == "Test Issue"
        assert call_fields["assignee"] == {"key": "testuser", "name": "testuser"}
        assert call_fields["customfield_10501"] == {"value": "DevTeam"}

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_returns_dto_with_id_and_link(
        self,
        mock_jira_cls: MagicMock,
        mock_config: MagicMock,
        sample_issue_dto: JiraIssueDTO,
    ) -> None:
        """create() returns DTO with id and link populated."""
        mock_jira = mock_jira_cls.return_value
        mock_issue = MagicMock()
        mock_issue.key = "PROJ-999"
        mock_issue.permalink.return_value = "https://jira.example.com/browse/PROJ-999"
        mock_issue.fields.project.key = "PROJ"
        mock_issue.fields.summary = "Test Issue"
        mock_issue.fields.description = "Test description"
        mock_issue.fields.issuetype.name = "Task"
        mock_issue.fields.labels = ["test", "automated"]
        mock_issue.fields.priority.name = "Medium"
        mock_issue.fields.customfield_11502 = "PARENT-123"
        mock_issue.fields.customfield_10001 = "EPIC-456"
        mock_issue.fields.assignee.key = "testuser"
        mock_issue.fields.reporter.key = "reporter"
        mock_issue.fields.customfield_10501.value = "DevTeam"
        mock_issue.fields.customfield_12900.value = "US"
        mock_jira.create_issue.return_value = mock_issue
        mock_jira.issue.return_value = mock_issue

        adapter = JiraAdapter(mock_config)
        result = adapter.create(sample_issue_dto)

        assert result.id == "PROJ-999"
        assert result.link == "https://jira.example.com/browse/PROJ-999"
        assert isinstance(result, JiraIssueDTO)

    @patch("buvis.pybase.adapters.jira.jira.JIRA")
    def test_updates_custom_fields_after_creation(
        self,
        mock_jira_cls: MagicMock,
        mock_config: MagicMock,
        sample_issue_dto: JiraIssueDTO,
    ) -> None:
        """create() updates custom fields that require post-creation update."""
        mock_jira = mock_jira_cls.return_value
        mock_created_issue = MagicMock()
        mock_created_issue.key = "PROJ-123"
        mock_fetched_issue = MagicMock()
        mock_fetched_issue.key = "PROJ-123"
        mock_fetched_issue.permalink.return_value = (
            "https://jira.example.com/browse/PROJ-123"
        )
        mock_fetched_issue.fields.project.key = "PROJ"
        mock_fetched_issue.fields.summary = "Test Issue"
        mock_fetched_issue.fields.description = "Test description"
        mock_fetched_issue.fields.issuetype.name = "Task"
        mock_fetched_issue.fields.labels = ["test", "automated"]
        mock_fetched_issue.fields.priority.name = "Medium"
        mock_fetched_issue.fields.customfield_11502 = "PARENT-123"
        mock_fetched_issue.fields.customfield_10001 = "EPIC-456"
        mock_fetched_issue.fields.assignee.key = "testuser"
        mock_fetched_issue.fields.reporter.key = "reporter"
        mock_fetched_issue.fields.customfield_10501.value = "DevTeam"
        mock_fetched_issue.fields.customfield_12900.value = "US"
        mock_jira.create_issue.return_value = mock_created_issue
        mock_jira.issue.return_value = mock_fetched_issue

        adapter = JiraAdapter(mock_config)
        adapter.create(sample_issue_dto)

        mock_jira.issue.assert_called_once_with("PROJ-123")
        assert mock_fetched_issue.update.call_count == 2
        mock_fetched_issue.update.assert_any_call(customfield_10001="EPIC-456")
        mock_fetched_issue.update.assert_any_call(customfield_12900={"value": "US"})
