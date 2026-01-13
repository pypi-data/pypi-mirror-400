"""JIRA REST API adapter for issue creation.

Provides JiraAdapter for creating JIRA issues with custom field support.
"""

import os
from typing import Any

from jira import JIRA

from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO


class JiraAdapter:
    """JIRA REST API adapter for issue creation.

    Requirements:
        Config must provide `server` and `token`.

    Optional:
        Set `proxy` in the config to route requests through a proxy server.

    Example:
        >>> cfg = MyConfig()  # provides server, token
        >>> jira = JiraAdapter(cfg)
        >>> issue = JiraIssueDTO(project='PROJ', title='Bug', ...)
        >>> created = jira.create(issue)
        >>> print(created.link)
    """

    def __init__(self: "JiraAdapter", cfg: Any) -> None:
        """Initialize JIRA connection.

        Args:
            cfg: Configuration object with methods:
                - get_configuration_item(key) -> str
                - get_configuration_item_or_default(key, default) -> str | None

                Required keys: 'server' (JIRA URL), 'token' (API token).
                Optional keys: 'proxy' (HTTP proxy URL).

        Raises:
            ValueError: If server or token not provided in cfg.

        Note:
            Proxy handling clears existing `https_proxy` and `http_proxy` before
            setting the configured proxy.
        """
        self._cfg = cfg
        if self._cfg.get_configuration_item_or_default("proxy", None):
            os.environ.pop("https_proxy", None)
            os.environ.pop("http_proxy", None)
            os.environ["https_proxy"] = str(self._cfg.get_configuration_item("proxy"))
        if not self._cfg.get_configuration_item_or_default(
            "server",
            None,
        ) or not self._cfg.get_configuration_item_or_default(
            "token",
            None,
        ):
            msg = "Server and token must be provided"
            raise ValueError(msg)
        self._jira = JIRA(
            server=str(self._cfg.get_configuration_item("server")),
            token_auth=str(self._cfg.get_configuration_item("token")),
        )

    def create(self, issue: JiraIssueDTO) -> JiraIssueDTO:
        """Create a JIRA issue via the REST API.

        Args:
            issue (JiraIssueDTO): containing all required fields.

        Returns:
            JiraIssueDTO: populated with server-assigned id and link.

        Custom Field Mappings:
            ticket -> customfield_11502 (parent ticket reference)
            team -> customfield_10501 (team selector)
            feature -> customfield_10001 (epic/feature link)
            region -> customfield_12900 (region selector)

        Note:
            Custom fields customfield_10001 (feature) and customfield_12900 (region) require post-creation update due to JIRA API limitations.
        """
        new_issue = self._jira.create_issue(
            fields={
                "assignee": {"key": issue.assignee, "name": issue.assignee},
                "customfield_10001": issue.feature,
                "customfield_10501": {"value": issue.team},
                "customfield_12900": {"value": issue.region},
                "customfield_11502": issue.ticket,
                "description": issue.description,
                "issuetype": {"name": issue.issue_type},
                "labels": issue.labels,
                "priority": {"name": issue.priority},
                "project": {"key": issue.project},
                "reporter": {"key": issue.reporter, "name": issue.reporter},
                "summary": issue.title,
            },
        )
        # some custom fields aren't populated on issue creation
        # so I have to update them after issue creation
        new_issue = self._jira.issue(new_issue.key)
        new_issue.update(customfield_10001=issue.feature)
        new_issue.update(customfield_12900={"value": issue.region})

        return JiraIssueDTO(
            project=new_issue.fields.project.key,
            title=new_issue.fields.summary,
            description=new_issue.fields.description,
            issue_type=new_issue.fields.issuetype.name,
            labels=new_issue.fields.labels,
            priority=new_issue.fields.priority.name,
            ticket=new_issue.fields.customfield_11502,
            feature=new_issue.fields.customfield_10001,
            assignee=new_issue.fields.assignee.key,
            reporter=new_issue.fields.reporter.key,
            team=new_issue.fields.customfield_10501.value,
            region=new_issue.fields.customfield_12900.value,
            id=new_issue.key,
            link=new_issue.permalink(),
        )
