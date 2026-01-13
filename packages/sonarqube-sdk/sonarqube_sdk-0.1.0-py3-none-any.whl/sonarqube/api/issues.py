"""Issues API for SonarQube SDK.

This module provides methods to search, update, and manage issues
found by SonarQube analysis.

Example:
    Using the Issues API::

        from sonarqube import SonarQubeClient

        client = SonarQubeClient(base_url="...", token="...")

        # Search for issues
        issues = client.issues.search(
            project_keys=["my-project"], severities=["CRITICAL", "BLOCKER"]
        )
        for issue in issues.issues:
            print(f"{issue.severity}: {issue.message}")
"""

from __future__ import annotations

from typing import Any, Optional

from sonarqube.api.base import BaseAPI
from sonarqube.models.issues import (
    Issue,
    IssueAuthorsResponse,
    IssueChangelogResponse,
    IssueSearchResponse,
    IssueTagsResponse,
)


class IssuesAPI(BaseAPI):
    """API for managing SonarQube issues.

    Issues are problems found by SonarQube during code analysis. This API
    provides methods to search, assign, comment, and transition issues.

    Attributes:
        API_PATH: Base path for issues API ("/api/issues").

    Example:
        Using the issues API::

            # Search for critical issues
            issues = client.issues.search(
                project_keys=["my-project"], severities=["CRITICAL"]
            )

            # Assign an issue
            client.issues.assign(issue="AXoN-12345", assignee="john")

            # Transition an issue
            client.issues.do_transition(issue="AXoN-12345", transition="resolve")
    """

    API_PATH = "/api/issues"

    def add_comment(self, issue: str, text: str) -> Issue:
        """Add a comment to an issue.

        Requires authentication and 'Browse' permission on the project.

        Args:
            issue: Issue key.
            text: Comment text (max 40000 characters).

        Returns:
            The updated issue.

        Raises:
            SonarQubeNotFoundError: If issue not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> issue = client.issues.add_comment(
            ...     issue="AXoN-12345", text="This should be fixed in the next sprint."
            ... )
        """
        response = self._post(
            "/add_comment",
            data={
                "issue": issue,
                "text": text,
            },
        )
        return Issue.model_validate(response.get("issue", response))

    def assign(
        self,
        issue: str,
        assignee: Optional[str] = None,
    ) -> Issue:
        """Assign or unassign an issue.

        Requires authentication and 'Browse' permission on the project.

        Args:
            issue: Issue key.
            assignee: User login to assign, or None to unassign.

        Returns:
            The updated issue.

        Raises:
            SonarQubeNotFoundError: If issue not found.
            SonarQubePermissionError: If lacking required permissions.

        Example:
            >>> # Assign to a user
            >>> issue = client.issues.assign(issue="AXoN-12345", assignee="john")
            >>> # Unassign
            >>> issue = client.issues.assign(issue="AXoN-12345")
        """
        data: dict[str, Any] = {"issue": issue}
        if assignee:
            data["assignee"] = assignee

        response = self._post("/assign", data=data)
        return Issue.model_validate(response.get("issue", response))

    def authors(
        self,
        project: str,
        ps: Optional[int] = None,
        q: Optional[str] = None,
    ) -> IssueAuthorsResponse:
        """Get list of issue authors.

        Requires 'Browse' permission on the project.

        Args:
            project: Project key.
            ps: Page size (max 100).
            q: Search query for author names.

        Returns:
            Response containing list of authors.

        Example:
            >>> response = client.issues.authors(project="my-project")
            >>> for author in response.authors:
            ...     print(author)
        """
        return self._get_model(
            "/authors",
            IssueAuthorsResponse,
            params={
                "project": project,
                "ps": ps,
                "q": q,
            },
        )

    def bulk_change(
        self,
        issues: list[str],
        add_tags: Optional[list[str]] = None,
        assign: Optional[str] = None,
        comment: Optional[str] = None,
        do_transition: Optional[str] = None,
        remove_tags: Optional[list[str]] = None,
        set_severity: Optional[str] = None,
        set_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """Bulk change issues.

        Requires authentication and 'Browse' permission on the project.

        Args:
            issues: List of issue keys.
            add_tags: Tags to add.
            assign: User to assign (use empty string to unassign).
            comment: Comment to add.
            do_transition: Transition to perform.
            remove_tags: Tags to remove.
            set_severity: New severity.
            set_type: New type.

        Returns:
            Response containing bulk change results.

        Example:
            >>> result = client.issues.bulk_change(
            ...     issues=["AXoN-12345", "AXoN-12346"], add_tags=["team-a"], assign="john"
            ... )
        """
        data: dict[str, Any] = {"issues": ",".join(issues)}

        if add_tags:
            data["add_tags"] = ",".join(add_tags)
        if assign is not None:
            data["assign"] = assign
        if comment:
            data["comment"] = comment
        if do_transition:
            data["do_transition"] = do_transition
        if remove_tags:
            data["remove_tags"] = ",".join(remove_tags)
        if set_severity:
            data["set_severity"] = set_severity
        if set_type:
            data["set_type"] = set_type

        return self._post("/bulk_change", data=data)

    def changelog(
        self,
        issue: str,
    ) -> IssueChangelogResponse:
        """Get changelog for an issue.

        Requires 'Browse' permission on the project.

        Args:
            issue: Issue key.

        Returns:
            Response containing changelog entries.

        Example:
            >>> changelog = client.issues.changelog(issue="AXoN-12345")
            >>> for entry in changelog.changelog:
            ...     print(entry)
        """
        return self._get_model(
            "/changelog",
            IssueChangelogResponse,
            params={"issue": issue},
        )

    def delete_comment(self, comment: str) -> Issue:
        """Delete a comment from an issue.

        Requires authentication and ownership of the comment.

        Args:
            comment: Comment key.

        Returns:
            The updated issue.

        Example:
            >>> issue = client.issues.delete_comment(comment="AU-Tpxb")
        """
        response = self._post("/delete_comment", data={"comment": comment})
        return Issue.model_validate(response.get("issue", response))

    def do_transition(self, issue: str, transition: str) -> Issue:
        """Perform a transition on an issue.

        Requires authentication and 'Browse' permission on the project.

        Args:
            issue: Issue key.
            transition: Transition to perform (confirm, unconfirm, reopen,
                resolve, falsepositive, wontfix, close).

        Returns:
            The updated issue.

        Raises:
            SonarQubeNotFoundError: If issue not found.
            SonarQubeValidationError: If transition is not valid.

        Example:
            >>> issue = client.issues.do_transition(issue="AXoN-12345", transition="resolve")
        """
        response = self._post(
            "/do_transition",
            data={
                "issue": issue,
                "transition": transition,
            },
        )
        return Issue.model_validate(response.get("issue", response))

    def edit_comment(self, comment: str, text: str) -> Issue:
        """Edit a comment on an issue.

        Requires authentication and ownership of the comment.

        Args:
            comment: Comment key.
            text: New comment text.

        Returns:
            The updated issue.

        Example:
            >>> issue = client.issues.edit_comment(comment="AU-Tpxb", text="Updated comment")
        """
        response = self._post(
            "/edit_comment",
            data={
                "comment": comment,
                "text": text,
            },
        )
        return Issue.model_validate(response.get("issue", response))

    def search(
        self,
        additional_fields: Optional[list[str]] = None,
        asc: Optional[bool] = None,
        assigned: Optional[bool] = None,
        assignees: Optional[list[str]] = None,
        author: Optional[str] = None,
        branch: Optional[str] = None,
        clean_code_attribute_categories: Optional[list[str]] = None,
        code_variants: Optional[list[str]] = None,
        component_keys: Optional[list[str]] = None,
        created_after: Optional[str] = None,
        created_at: Optional[str] = None,
        created_before: Optional[str] = None,
        created_in_last: Optional[str] = None,
        directories: Optional[list[str]] = None,
        facets: Optional[list[str]] = None,
        files: Optional[list[str]] = None,
        impact_severities: Optional[list[str]] = None,
        impact_software_qualities: Optional[list[str]] = None,
        in_new_code_period: Optional[bool] = None,
        issue_statuses: Optional[list[str]] = None,
        issues: Optional[list[str]] = None,
        languages: Optional[list[str]] = None,
        on_component_only: Optional[bool] = None,
        p: Optional[int] = None,
        project_keys: Optional[list[str]] = None,
        ps: Optional[int] = None,
        pull_request: Optional[str] = None,
        resolutions: Optional[list[str]] = None,
        resolved: Optional[bool] = None,
        rules: Optional[list[str]] = None,
        s: Optional[str] = None,
        scopes: Optional[list[str]] = None,
        severities: Optional[list[str]] = None,
        statuses: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        types: Optional[list[str]] = None,
    ) -> IssueSearchResponse:
        """Search for issues.

        Requires 'Browse' permission on the project.

        Args:
            additional_fields: Additional fields to return.
            asc: Ascending sort order.
            assigned: Filter by assigned status.
            assignees: Filter by assignees.
            author: Filter by author.
            branch: Branch name.
            clean_code_attribute_categories: Clean code attribute categories.
            code_variants: Code variants.
            component_keys: Component keys.
            created_after: Issues created after this date.
            created_at: Issues created at this date.
            created_before: Issues created before this date.
            created_in_last: Issues created in last period (e.g., "1m").
            directories: Filter by directories.
            facets: Facets to return.
            files: Filter by files.
            impact_severities: Impact severities.
            impact_software_qualities: Impact software qualities.
            in_new_code_period: Issues in new code period.
            issue_statuses: Issue statuses.
            issues: Issue keys.
            languages: Filter by languages.
            on_component_only: Only issues on the component.
            p: Page number.
            project_keys: Project keys.
            ps: Page size.
            pull_request: Pull request ID.
            resolutions: Filter by resolutions.
            resolved: Filter by resolved status.
            rules: Filter by rules.
            s: Sort field.
            scopes: Filter by scopes.
            severities: Filter by severities.
            statuses: Filter by statuses.
            tags: Filter by tags.
            types: Filter by types.

        Returns:
            Response containing list of issues and paging info.

        Example:
            >>> response = client.issues.search(
            ...     project_keys=["my-project"], severities=["CRITICAL", "BLOCKER"]
            ... )
            >>> for issue in response.issues:
            ...     print(f"{issue.severity}: {issue.message}")
        """
        params: dict[str, Any] = {}

        if additional_fields:
            params["additionalFields"] = ",".join(additional_fields)
        if asc is not None:
            params["asc"] = str(asc).lower()
        if assigned is not None:
            params["assigned"] = str(assigned).lower()
        if assignees:
            params["assignees"] = ",".join(assignees)
        if author:
            params["author"] = author
        if branch:
            params["branch"] = branch
        if clean_code_attribute_categories:
            params["cleanCodeAttributeCategories"] = ",".join(
                clean_code_attribute_categories
            )
        if code_variants:
            params["codeVariants"] = ",".join(code_variants)
        if component_keys:
            params["componentKeys"] = ",".join(component_keys)
        if created_after:
            params["createdAfter"] = created_after
        if created_at:
            params["createdAt"] = created_at
        if created_before:
            params["createdBefore"] = created_before
        if created_in_last:
            params["createdInLast"] = created_in_last
        if directories:
            params["directories"] = ",".join(directories)
        if facets:
            params["facets"] = ",".join(facets)
        if files:
            params["files"] = ",".join(files)
        if impact_severities:
            params["impactSeverities"] = ",".join(impact_severities)
        if impact_software_qualities:
            params["impactSoftwareQualities"] = ",".join(impact_software_qualities)
        if in_new_code_period is not None:
            params["inNewCodePeriod"] = str(in_new_code_period).lower()
        if issue_statuses:
            params["issueStatuses"] = ",".join(issue_statuses)
        if issues:
            params["issues"] = ",".join(issues)
        if languages:
            params["languages"] = ",".join(languages)
        if on_component_only is not None:
            params["onComponentOnly"] = str(on_component_only).lower()
        if p:
            params["p"] = p
        if project_keys:
            params["projects"] = ",".join(project_keys)
        if ps:
            params["ps"] = ps
        if pull_request:
            params["pullRequest"] = pull_request
        if resolutions:
            params["resolutions"] = ",".join(resolutions)
        if resolved is not None:
            params["resolved"] = str(resolved).lower()
        if rules:
            params["rules"] = ",".join(rules)
        if s:
            params["s"] = s
        if scopes:
            params["scopes"] = ",".join(scopes)
        if severities:
            params["severities"] = ",".join(severities)
        if statuses:
            params["statuses"] = ",".join(statuses)
        if tags:
            params["tags"] = ",".join(tags)
        if types:
            params["types"] = ",".join(types)

        return self._get_model("/search", IssueSearchResponse, params=params)

    def set_severity(self, issue: str, severity: str) -> Issue:
        """Set severity for an issue.

        Requires authentication and 'Browse' permission on the project.

        Args:
            issue: Issue key.
            severity: New severity (BLOCKER, CRITICAL, MAJOR, MINOR, INFO).

        Returns:
            The updated issue.

        Example:
            >>> issue = client.issues.set_severity(issue="AXoN-12345", severity="CRITICAL")
        """
        response = self._post(
            "/set_severity",
            data={
                "issue": issue,
                "severity": severity,
            },
        )
        return Issue.model_validate(response.get("issue", response))

    def set_tags(self, issue: str, tags: list[str]) -> Issue:
        """Set tags for an issue.

        Requires authentication and 'Browse' permission on the project.

        Args:
            issue: Issue key.
            tags: List of tags to set.

        Returns:
            The updated issue.

        Example:
            >>> issue = client.issues.set_tags(issue="AXoN-12345", tags=["team-a", "priority"])
        """
        response = self._post(
            "/set_tags",
            data={
                "issue": issue,
                "tags": ",".join(tags),
            },
        )
        return Issue.model_validate(response.get("issue", response))

    def set_type(self, issue: str, type_: str) -> Issue:
        """Set type for an issue.

        Requires authentication and 'Browse' permission on the project.

        Args:
            issue: Issue key.
            type_: New type (BUG, VULNERABILITY, CODE_SMELL).

        Returns:
            The updated issue.

        Example:
            >>> issue = client.issues.set_type(issue="AXoN-12345", type_="BUG")
        """
        response = self._post(
            "/set_type",
            data={
                "issue": issue,
                "type": type_,
            },
        )
        return Issue.model_validate(response.get("issue", response))

    def tags(
        self,
        project: Optional[str] = None,
        ps: Optional[int] = None,
        q: Optional[str] = None,
    ) -> IssueTagsResponse:
        """Get list of issue tags.

        Requires 'Browse' permission on the project.

        Args:
            project: Project key.
            ps: Page size (max 100).
            q: Search query for tags.

        Returns:
            Response containing list of tags.

        Example:
            >>> response = client.issues.tags(project="my-project")
            >>> for tag in response.tags:
            ...     print(tag)
        """
        return self._get_model(
            "/tags",
            IssueTagsResponse,
            params={
                "project": project,
                "ps": ps,
                "q": q,
            },
        )
