"""Utility functions for project comment tools."""

from collections.abc import Mapping
from typing import Any, cast

from arcade_mcp_server.exceptions import RetryableToolError, ToolExecutionError
from gql.transport.exceptions import TransportQueryError

from arcade_linear.client import LinearClient
from arcade_linear.constants import (
    DEFAULT_PAGE_SIZE,
    MAX_DISPLAY_SUGGESTIONS,
)
from arcade_linear.utils.comment_utils import map_comment
from arcade_linear.utils.fuzzy_utils import try_fuzzy_match_by_name


async def resolve_project_for_comments(
    client: LinearClient,
    project: str,
    auto_accept_matches: bool,
) -> dict[str, Any]:
    """Resolve project by ID, slug_id, or name and return project data with documentContentId.

    Args:
        client: Linear API client
        project: Project ID, slug_id, or name
        auto_accept_matches: Whether to auto-accept fuzzy matches above threshold

    Returns:
        Dict with project_id, project_name, and document_content_id

    Raises:
        ToolExecutionError: If project not found
        RetryableToolError: If fuzzy match suggestions available
    """
    project_data: Mapping[str, Any] = {}

    try:
        project_data = await client.get_project_document_content(project)
    except TransportQueryError as e:
        if "not found" not in str(e).lower() and "invalid" not in str(e).lower():
            raise

    if project_data.get("id"):
        doc_content = project_data.get("documentContent", {})
        if not doc_content or not doc_content.get("id"):
            raise ToolExecutionError(
                message=f"Project '{project}' has no document content for comments."
            )
        return {
            "project_id": project_data["id"],
            "project_name": project_data.get("name", ""),
            "document_content_id": doc_content["id"],
        }

    projects_response = await client.search_projects(first=DEFAULT_PAGE_SIZE)
    projects = projects_response.get("nodes", [])

    matched, fuzzy_info = try_fuzzy_match_by_name(projects, project, auto_accept_matches)

    if not matched:
        if fuzzy_info:
            suggestions = fuzzy_info.get("suggestions", [])
            suggestions_text = ", ".join(
                f"{s['name']} ({round(s['confidence'] * 100)}%)"
                for s in suggestions[:MAX_DISPLAY_SUGGESTIONS]
            )
            raise RetryableToolError(
                message=f"Project not found: {project}",
                additional_prompt_content=f"Suggestions: {suggestions_text}",
            )
        raise ToolExecutionError(message=f"Project not found: {project}")

    matched_project = matched[0]
    full_project = await client.get_project_document_content(str(matched_project["id"]))

    doc_content = full_project.get("documentContent", {})
    if not doc_content or not doc_content.get("id"):
        raise ToolExecutionError(
            message=f"Project '{matched_project.get('name', project)}' has no document content."
        )

    return {
        "project_id": full_project["id"],
        "project_name": full_project.get("name", ""),
        "document_content_id": doc_content["id"],
    }


def filter_resolved_comments(
    comments: list[Mapping[str, Any]],
    include_resolved: bool,
) -> list[Mapping[str, Any]]:
    """Filter comments based on resolved status."""
    if include_resolved:
        return list(comments)
    return [c for c in comments if not c.get("resolvedAt")]


def nest_replies_under_parents(
    parent_comments: list[dict[str, Any]],
    all_comments: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Nest direct replies under their parent comments.

    Linear only supports flat threads (one level of replies). All replies to a
    comment are direct children - there are no nested reply chains.

    Args:
        parent_comments: List of mapped parent comments (top-level or inline)
        all_comments: All raw comments from API (to find direct replies)

    Returns:
        List of parent comments with 'replies' field containing direct replies
    """
    # Build a map of parent_id -> replies
    parent_ids = {c["id"] for c in parent_comments}
    replies_by_parent: dict[str, list[dict[str, Any]]] = {pid: [] for pid in parent_ids}

    for raw_comment in all_comments:
        parent_data = raw_comment.get("parent")
        if parent_data:
            parent_id = parent_data.get("id")
            if parent_id and parent_id in replies_by_parent:
                replies_by_parent[parent_id].append(cast(dict[str, Any], map_comment(raw_comment)))

    # Attach replies to parents
    for comment in parent_comments:
        comment_id = comment.get("id", "")
        replies = replies_by_parent.get(comment_id, [])
        if replies:
            # Sort replies by created_at
            replies.sort(key=lambda r: r.get("created_at", ""))
            comment["replies"] = replies

    return parent_comments
