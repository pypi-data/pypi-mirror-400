"""Markdown formatter for MCP API responses."""

from typing import TYPE_CHECKING

from daimyo.application.formatters.helpers import RuleProcessorMixin, TemplateAwareMixin
from daimyo.application.formatters.tree_builder import CategoryTreeBuilder
from daimyo.domain import MergedScope, RuleSet

if TYPE_CHECKING:
    from daimyo.application.templating import TemplateRenderer


class MarkdownFormatter(TemplateAwareMixin, RuleProcessorMixin):
    """Format merged scope as markdown with hierarchy and MUST/SHOULD markers.

    Features:
    - Nested headings for category hierarchy (## python, ### web, #### testing)
    - MUST markers for commandments, SHOULD markers for suggestions
    - Include 'when' descriptions for each category
    - Jinja2 template rendering support
    """

    def __init__(self, template_renderer: "TemplateRenderer | None" = None):
        """Initialize formatter.

        :param template_renderer: Optional template renderer for dynamic rule text
        :type template_renderer: TemplateRenderer | None
        """
        self.template_renderer = template_renderer

    def format(self, scope: MergedScope) -> str:
        """Format merged scope as markdown.

        :param scope: The merged scope to format
        :type scope: MergedScope
        :returns: Markdown-formatted string
        :rtype: str
        """
        lines = []

        lines.append(f"# Rules for {scope.metadata.name}\n")
        if scope.metadata.description:
            lines.append(f"{scope.metadata.description}\n")

        merged_tree = CategoryTreeBuilder.merge_trees(
            list(scope.commandments.categories.values()),
            list(scope.suggestions.categories.values()),
        )

        lines.extend(self._format_merged_tree(merged_tree, scope, depth=2))

        return "\n".join(lines)

    def _format_merged_tree(
        self, tree: dict[str, dict], scope: MergedScope, depth: int, path: str = ""
    ) -> list[str]:
        """Format merged category tree with both MUST and SHOULD rules.

        :param tree: Merged category tree
        :type tree: Dict[str, Dict]
        :param scope: Scope for template rendering
        :type scope: MergedScope
        :param depth: Current heading depth
        :type depth: int
        :param path: Current category path
        :type path: str
        :returns: List of markdown lines
        :rtype: List[str]
        """
        lines = []

        for key, node in sorted(tree.items()):
            current_path = f"{path}.{key}" if path else key

            commandments = node.get("_commandments", [])
            suggestions = node.get("_suggestions", [])

            when_description = None
            category_for_when = None

            for category in commandments:
                if category.when:
                    when_description = category.when
                    category_for_when = category
                    break
            if not when_description:
                for category in suggestions:
                    if category.when:
                        when_description = category.when
                        category_for_when = category
                        break

            must_rules = []
            for category in commandments:
                must_rules.extend(self._render_and_prune_rules(category, scope))

            should_rules = []
            for category in suggestions:
                should_rules.extend(self._render_and_prune_rules(category, scope))

            children = node.get("_children", {})
            children_lines = []
            if children:
                children_lines = self._format_merged_tree(children, scope, depth + 1, current_path)

            if must_rules or should_rules or children_lines:
                heading = "#" * depth
                lines.append(f"{heading} {key}\n")

                if must_rules or should_rules:
                    from daimyo.domain import CategoryKey

                    current_category_key = CategoryKey.from_string(current_path)
                    when_to_render = self._get_when_with_hierarchical_fallback(
                        current_category_key,
                        when_description,
                        scope.commandments,
                        scope.suggestions,
                    )
                    if category_for_when:
                        rendered_when = self._render_text(when_to_render, scope, category_for_when)
                    else:
                        rendered_when = when_to_render
                    lines.append(f"*{rendered_when}*\n")

                    for rendered_rule in must_rules:
                        lines.append(f"- **MUST**: {rendered_rule}")

                    for rendered_rule in should_rules:
                        lines.append(f"- **SHOULD**: {rendered_rule}")

                    lines.append("")

                lines.extend(children_lines)

        return lines

    def _format_ruleset_markdown(self, ruleset: RuleSet, marker: str) -> str:
        """Format a ruleset as markdown with hierarchical headings.

        :param ruleset: The ruleset to format
        :type ruleset: RuleSet
        :param marker: The marker to use (MUST or SHOULD)
        :type marker: str
        :returns: Markdown string
        :rtype: str
        """
        lines = []

        category_tree = CategoryTreeBuilder.build_tree(list(ruleset.categories.values()))

        lines.extend(self._format_tree(category_tree, marker, depth=3))

        return "\n".join(lines)

    def _format_tree(
        self, tree: dict[str, dict], marker: str, depth: int, path: str = ""
    ) -> list[str]:
        """Recursively format category tree as markdown.

        :param tree: Category tree
        :type tree: Dict[str, Dict]
        :param marker: MUST or SHOULD
        :type marker: str
        :param depth: Current heading depth
        :type depth: int
        :param path: Current category path
        :type path: str
        :returns: List of markdown lines
        :rtype: List[str]
        """
        lines = []

        for key, node in sorted(tree.items()):
            heading = "#" * depth
            current_path = f"{path}.{key}" if path else key
            lines.append(f"{heading} {key}\n")

            for category in node.get("_categories", []):
                lines.append(f"*{category.when}*\n")

                for rule in category.rules:
                    lines.append(f"- **{marker}**: {rule.text}")
                lines.append("")

            children = node.get("_children", {})
            if children:
                lines.extend(self._format_tree(children, marker, depth + 1, current_path))

        return lines


__all__ = ["MarkdownFormatter"]
