"""Project comment tools for Linear toolkit."""

from typing import Annotated, Any, cast

from arcade_mcp_server import Context, tool
from arcade_mcp_server.auth import Linear

from arcade_linear.client import LinearClient
from arcade_linear.constants import FUZZY_AUTO_ACCEPT_CONFIDENCE
from arcade_linear.models.enums import ProjectCommentFilter
from arcade_linear.models.mappers import map_pagination
from arcade_linear.models.tool_outputs.comments import (
    AddProjectCommentOutput,
    ListProjectCommentsOutput,
)
from arcade_linear.utils.comment_utils import map_comment
from arcade_linear.utils.project_comment_utils import (
    filter_resolved_comments,
    nest_replies_under_parents,
    resolve_project_for_comments,
)
from arcade_linear.utils.response_utils import remove_none_values_recursive


# =============================================================================
# list_project_comments
# API Calls: 2-3 (1 for project lookup, 1 for document content, 1 for comments)
# APIs Used: project_document_content query, project_comments query (GraphQL)
# Response Complexity: MEDIUM - list of comments with pagination
# -----------------------------------------------------------------------------
# ToolAnnotations:
#   title: "List Project Comments"
#   readOnlyHint: true      - Only reads comment data, no modifications
#   openWorldHint: true     - Interacts with Linear's external API
# =============================================================================
@tool(requires_auth=Linear(scopes=["read"]))
async def list_project_comments(
    context: Context,
    project: Annotated[
        str,
        "Project ID, slug_id, or name. Prefer project ID for better performance.",
    ],
    comment_filter: Annotated[
        ProjectCommentFilter,
        "Filter which comments to return. Default is only_quoted.",
    ] = ProjectCommentFilter.ONLY_QUOTED,
    include_resolved: Annotated[
        bool,
        "Include resolved comments in the response. Default is True.",
    ] = True,
    limit: Annotated[
        int,
        "Maximum number of comments to return. Min 1, max 50. Default is 20.",
    ] = 20,
    end_cursor: Annotated[
        str | None,
        "Cursor for pagination. Use 'end_cursor' from previous response. Default is None.",
    ] = None,
    auto_accept_matches: Annotated[
        bool,
        f"Auto-accept fuzzy matches above {FUZZY_AUTO_ACCEPT_CONFIDENCE:.0%} confidence. "
        "Default is False.",
    ] = False,
) -> Annotated[ListProjectCommentsOutput, "Comments on the project document"]:
    """List comments on a project's document content.

    Returns comments with user info, timestamps, quoted text for inline comments,
    and reply threading info. Replies are nested under their parent comments.

    Use comment_filter to control which comments are returned:
    - only_quoted (default): Only comments attached to a quote in the text
    - only_unquoted: Only comments not attached to a particular quote
    - all: All comments regardless of being attached to a quote or not
    """
    limit = max(1, min(limit, 50))

    async with LinearClient(context.get_auth_token_or_empty()) as client:
        project_info = await resolve_project_for_comments(client, project, auto_accept_matches)

        comments_response = await client.get_project_comments(
            document_content_id=project_info["document_content_id"],
            first=limit,
            after=end_cursor,
        )

    comments_nodes = comments_response.get("nodes", [])
    page_info = comments_response.get("pageInfo", {})

    filtered_comments = filter_resolved_comments(comments_nodes, include_resolved)

    if comment_filter == ProjectCommentFilter.ALL:
        parent_comments = [c for c in filtered_comments if not c.get("parent")]
    elif comment_filter == ProjectCommentFilter.ONLY_UNQUOTED:
        parent_comments = [
            c for c in filtered_comments if not c.get("quotedText") and not c.get("parent")
        ]
    else:
        parent_comments = [
            c for c in filtered_comments if c.get("quotedText") and not c.get("parent")
        ]

    mapped_parents: list[dict[str, Any]] = [
        cast(dict[str, Any], map_comment(c)) for c in parent_comments
    ]
    nested_comments = nest_replies_under_parents(mapped_parents, filtered_comments)

    result: ListProjectCommentsOutput = {
        "project_id": project_info["project_id"],
        "project_name": project_info["project_name"],
        "document_content_id": project_info["document_content_id"],
        "comments": cast(list[Any], nested_comments),
        "items_returned": len(nested_comments),
        "pagination": map_pagination(page_info),
    }

    return cast(ListProjectCommentsOutput, remove_none_values_recursive(result))


# =============================================================================
# add_project_comment
# API Calls: 2-3 (1 for project lookup, 1 for document content, 1 for create)
# APIs Used: project_document_content query, commentCreate mutation (GraphQL)
# Response Complexity: LOW
# -----------------------------------------------------------------------------
# ToolAnnotations:
#   title: "Add Project Comment"
#   readOnlyHint: false     - Creates new comment on project
#   destructiveHint: false  - Additive operation, creates new comment
#   idempotentHint: false   - Each call creates a new comment
#   openWorldHint: true     - Interacts with Linear's external API
# =============================================================================
@tool(requires_auth=Linear(scopes=["comments:create"]))
async def add_project_comment(
    context: Context,
    project: Annotated[
        str,
        "Project ID, slug_id, or name. Prefer project ID for better performance.",
    ],
    body: Annotated[str, "Comment body in Markdown format."],
    quoted_text: Annotated[
        str | None,
        "Text from the project document to reference. Default is None.",
    ] = None,
    auto_accept_matches: Annotated[
        bool,
        f"Auto-accept fuzzy matches above {FUZZY_AUTO_ACCEPT_CONFIDENCE:.0%} confidence. "
        "Default is False.",
    ] = False,
) -> Annotated[AddProjectCommentOutput, "Created comment details"]:
    """Add a comment to a project's document content.

    IMPORTANT: Due to Linear API limitations, comments created via the API will NOT
    appear visually anchored inline in the document (no yellow highlight on text).
    The comment will be stored and can be retrieved via list_project_comments, but
    it will appear in the comments panel rather than inline in the document.

    For true inline comments that are visually anchored to text, users should create
    them directly in the Linear UI by selecting text and adding a comment.

    The quoted_text parameter stores metadata about what text the comment references,
    which is useful for context even though the comment won't be visually anchored.
    """
    async with LinearClient(context.get_auth_token_or_empty()) as client:
        project_info = await resolve_project_for_comments(client, project, auto_accept_matches)

        comment_data = await client.create_project_comment(
            document_content_id=project_info["document_content_id"],
            body=body,
            quoted_text=quoted_text,
        )

    raw_quoted = comment_data.get("quotedText")
    quoted_text_result: str | None = str(raw_quoted) if raw_quoted else None
    result: AddProjectCommentOutput = {
        "id": comment_data.get("id", ""),
        "project_id": project_info["project_id"],
        "project_name": project_info["project_name"],
        "body": comment_data.get("body", ""),
        "quoted_text": quoted_text_result,
        "created_at": str(comment_data.get("createdAt", "")),
    }

    return cast(AddProjectCommentOutput, remove_none_values_recursive(result))


# =============================================================================
# reply_to_project_comment
# API Calls: 2-3 (1 for project lookup, 1 for document content, 1 for create)
# APIs Used: project_document_content query, commentCreate mutation (GraphQL)
# Response Complexity: LOW
# -----------------------------------------------------------------------------
# ToolAnnotations:
#   title: "Reply to Project Comment"
#   readOnlyHint: false     - Creates reply to existing comment
#   destructiveHint: false  - Additive operation, creates new reply
#   idempotentHint: false   - Each call creates a new reply
#   openWorldHint: true     - Interacts with Linear's external API
# =============================================================================
@tool(requires_auth=Linear(scopes=["comments:create"]))
async def reply_to_project_comment(
    context: Context,
    project: Annotated[
        str,
        "Project ID, slug_id, or name.",
    ],
    parent_comment_id: Annotated[str, "ID of the comment to reply to."],
    body: Annotated[str, "Reply body in Markdown format."],
    auto_accept_matches: Annotated[
        bool,
        f"Auto-accept fuzzy matches above {FUZZY_AUTO_ACCEPT_CONFIDENCE:.0%} confidence. "
        "Default is False.",
    ] = False,
) -> Annotated[AddProjectCommentOutput, "Created reply details"]:
    """Reply to an existing comment on a project document.

    Creates a threaded reply to the specified parent comment.
    """
    async with LinearClient(context.get_auth_token_or_empty()) as client:
        project_info = await resolve_project_for_comments(client, project, auto_accept_matches)

        comment_data = await client.create_project_comment(
            document_content_id=project_info["document_content_id"],
            body=body,
            parent_id=parent_comment_id,
        )

    result: AddProjectCommentOutput = {
        "id": comment_data.get("id", ""),
        "project_id": project_info["project_id"],
        "project_name": project_info["project_name"],
        "body": comment_data.get("body", ""),
        "created_at": str(comment_data.get("createdAt", "")),
    }

    return cast(AddProjectCommentOutput, remove_none_values_recursive(result))
