"""FastMCP server for Daimyo rules."""

from fastmcp import FastMCP

from daimyo.application.error_handling import ErrorMapper
from daimyo.application.formatters import IndexMarkdownFormatter, MarkdownFormatter
from daimyo.infrastructure.di import get_container
from daimyo.infrastructure.logging import get_logger

logger = get_logger(__name__)

_container = get_container()
_scope_service = _container.scope_service()
_filter_service = _container.category_filter_service()
_scope_repository = _container.scope_repository()
_template_renderer = _container.template_renderer()

mcp = FastMCP("Daimyo Rules Server")


@mcp.tool()
def get_rules(scope_name: str, categories: str | None = None) -> str:
    """Get rules for a scope in markdown format.

    The rules of a given category include also the rules of all its subcategories.\f

    :param scope_name: Name of the scope to retrieve (e.g., 'python-general', 'team-backend')
    :type scope_name: str
    :param categories: Optional comma-separated category filters (e.g., 'python.web,python.testing')
    :type categories: str | None
    :returns: Markdown-formatted rules with hierarchy, MUST/SHOULD markers, and descriptions
    :rtype: str

    Examples::

        get_rules("python-general")
        get_rules("team-backend", "python.web")
    """
    try:
        logger.info(f"MCP get_rules: scope={scope_name}, categories={categories}")

        merged_scope = _scope_service.resolve_scope(scope_name)
        merged_scope = _filter_service.filter_from_string(merged_scope, categories)

        formatter = MarkdownFormatter(template_renderer=_template_renderer)
        result = formatter.format(merged_scope)

        logger.info(f"Successfully retrieved rules for scope '{scope_name}'")
        return result

    except Exception as e:
        return ErrorMapper.map_to_error_string(e, context=scope_name)


@mcp.tool()
def get_category_index(scope_name: str) -> str:
    """Get a hierarchical index of all available categories in a scope.

    Returns a list of all categories with their descriptions to help determine
    which categories are relevant before requesting specific rules.\f

    :param scope_name: Name of the scope to retrieve categories from
    :type scope_name: str
    :returns: Markdown-formatted hierarchical list of categories with descriptions
    :rtype: str

    Examples::

        get_category_index("python-general")
        get_category_index("team-backend")
    """
    try:
        logger.info(f"MCP get_category_index: scope={scope_name}")

        merged_scope = _scope_service.resolve_scope(scope_name)

        formatter = IndexMarkdownFormatter(template_renderer=_template_renderer)
        result = formatter.format(merged_scope)

        logger.info(f"Successfully retrieved category index for scope '{scope_name}'")
        return result

    except Exception as e:
        return ErrorMapper.map_to_error_string(e, context=scope_name)


@mcp.tool()
def list_scopes() -> str:
    """List all available scopes.\f

    :returns: Formatted list of available scope names
    :rtype: str

    Examples::

        list_scopes()
    """
    try:
        logger.info("MCP list_scopes")
        scopes = _scope_repository.list_scopes()

        if not scopes:
            return "No scopes found in the rules directory."

        result = "Available scopes:\n\n"
        for scope_name in scopes:
            result += f"- {scope_name}\n"

        return result

    except Exception as e:
        return ErrorMapper.map_to_error_string(e, context="list_scopes")


@mcp.prompt()
def apply_scope_rules(scope_name: str, categories: str | None = None) -> str:
    """Prompt template to apply scope rules to an agent.\f

    :param scope_name: Name of the scope to apply
    :type scope_name: str
    :param categories: Optional comma-separated category filters
    :type categories: str | None
    :returns: Formatted prompt with rules for the agent to follow
    :rtype: str
    """
    try:
        logger.info(f"MCP apply_scope_rules: scope={scope_name}, categories={categories}")
        rules = get_rules.fn(scope_name, categories)

        prompt = f"""You are an AI agent that must follow these rules from the '{scope_name}' scope.

{rules}

Instructions:
1. **MUST rules (Commandments)**: These are mandatory and cannot be violated
2. **SHOULD rules (Suggestions)**: These are strong recommendations you should
   follow unless you have a good reason not to

Apply these rules to all your actions, recommendations, and code generation.
When rules conflict, commandments take precedence over suggestions.
"""
        return prompt

    except Exception as e:
        error_msg = f"Error generating prompt: {str(e)}"
        logger.exception(error_msg)
        return error_msg


__all__ = ["mcp"]
