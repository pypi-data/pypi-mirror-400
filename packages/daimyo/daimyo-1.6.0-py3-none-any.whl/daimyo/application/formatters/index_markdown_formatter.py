"""Markdown formatter for category index."""

from typing import TYPE_CHECKING

from daimyo.application.formatters.helpers import TemplateAwareMixin
from daimyo.application.formatters.tree_builder import CategoryTreeBuilder
from daimyo.domain import Category, MergedScope

if TYPE_CHECKING:
    from daimyo.application.templating import TemplateRenderer


class IndexMarkdownFormatter(TemplateAwareMixin):
    """Format merged scope as markdown category index with hierarchy.

    Features:
    - Hierarchical category listing with indentation
    - Category descriptions (when available)
    - Backtick formatting for category keys
    - Optional footer text about subcategories
    - Jinja2 template rendering for 'when' descriptions
    """

    def __init__(
        self,
        include_footer: bool = True,
        template_renderer: "TemplateRenderer | None" = None,
    ):
        """Initialize formatter.

        :param include_footer: Whether to include footer about subcategories
        :type include_footer: bool
        :param template_renderer: Optional template renderer
        :type template_renderer: TemplateRenderer | None
        """
        self.include_footer = include_footer
        self.template_renderer = template_renderer

    def format(self, scope: MergedScope) -> str:
        """Format merged scope as markdown category index.

        :param scope: The merged scope to format
        :type scope: MergedScope
        :returns: Markdown-formatted category index
        :rtype: str
        """
        lines = [f"# Index of rule categories for scope {scope.metadata.name}\n"]

        if scope.metadata.description:
            lines.append(f"{scope.metadata.description}\n")

        all_categories = {}
        category_objects: dict[str, Category] = {}

        for cat in scope.commandments.categories.values():
            key = str(cat.key)
            if key not in all_categories:
                all_categories[key] = self._get_when_with_hierarchical_fallback(
                    cat.key, cat.when, scope.commandments, scope.suggestions
                )
                category_objects[key] = cat

        for cat in scope.suggestions.categories.values():
            key = str(cat.key)
            if key not in all_categories:
                all_categories[key] = self._get_when_with_hierarchical_fallback(
                    cat.key, cat.when, scope.commandments, scope.suggestions
                )
                category_objects[key] = cat

        category_list = [(key, when) for key, when in sorted(all_categories.items())]
        category_tree = CategoryTreeBuilder.build_index_tree(category_list)

        lines.extend(self._format_tree(category_tree, scope, category_objects))

        if self.include_footer:
            lines.append(
                "\nWhen requesting rules, the rules of a given category include also the rules of "
                "all its subcategories."
            )

        return "\n".join(lines)

    def _format_tree(
        self,
        tree: dict,
        scope: MergedScope,
        category_objects: dict[str, Category],
        depth: int = 0,
    ) -> list[str]:
        """Recursively format category tree as markdown with indentation.

        :param tree: Category tree structure
        :type tree: dict
        :param scope: Scope for template rendering
        :type scope: MergedScope
        :param category_objects: Map of category key -> Category object
        :type category_objects: dict[str, Category]
        :param depth: Current indentation depth
        :type depth: int
        :returns: List of formatted markdown lines
        :rtype: list[str]
        """
        result = []
        indent = "  " * depth

        for key, node in sorted(tree.items()):
            full_key = node["_key"]
            when_desc = node.get("_when", "")

            if when_desc:
                category_obj = category_objects.get(full_key)
                rendered_when = self._render_text(when_desc, scope, category_obj)
                result.append(f"{indent}- `{full_key}`: {rendered_when}")
            else:
                result.append(f"{indent}- `{full_key}`")

            children = node.get("_children", {})
            if children:
                result.extend(self._format_tree(children, scope, category_objects, depth + 1))

        return result


__all__ = ["IndexMarkdownFormatter"]
