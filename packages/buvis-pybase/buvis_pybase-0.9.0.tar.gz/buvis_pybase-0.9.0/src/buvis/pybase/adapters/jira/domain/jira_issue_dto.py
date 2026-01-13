from dataclasses import dataclass


@dataclass
class JiraIssueDTO:
    """DTO for JIRA issue creation.

    Maps Python fields to JIRA API field names; custom fields use JIRA internal
    IDs (customfield_*).

    Attributes:
        project: JIRA project key (e.g., 'BUV').
        title: Issue summary text, maps to JIRA 'summary'.
        description: Issue body text.
        issue_type: Type name (e.g., 'Task', 'Bug').
        labels: List of label strings.
        priority: Priority name (e.g., 'Medium', 'High').
        ticket: Parent ticket reference, maps to customfield_11502.
        feature: Feature/epic link, maps to customfield_10001.
        assignee: Assignee username key.
        reporter: Reporter username key.
        team: Team name, maps to customfield_10501.
        region: Region value, maps to customfield_12900.
        id: Server-assigned issue key (e.g., 'BUV-123'), populated after creation.
        link: Permalink URL, populated after creation.
    """

    project: str
    title: str
    description: str
    issue_type: str
    labels: list[str]
    priority: str
    ticket: str
    feature: str
    assignee: str
    reporter: str
    team: str
    region: str
    id: str | None = None
    link: str | None = None
