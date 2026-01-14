"""Template rendering mixin for formatters."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from daimyo.application.templating import TemplateRenderer
    from daimyo.domain import Category, CategoryKey, MergedScope, RuleSet


class TemplateAwareMixin:
    """Mixin providing template rendering capability.

    Classes using this mixin must have a 'template_renderer' attribute
    of type TemplateRenderer | None.
    """

    template_renderer: "TemplateRenderer | None"

    @staticmethod
    def _get_when_with_fallback(when: str | None) -> str:
        """Get 'when' description with fallback to default.

        :param when: Optional when description
        :type when: str | None
        :returns: When description or default fallback
        :rtype: str
        """
        if when and when.strip():
            return when
        return "These rules apply at all times"

    @staticmethod
    def _get_when_with_hierarchical_fallback(
        category_key: "CategoryKey",
        when: str | None,
        commandments: "RuleSet",
        suggestions: "RuleSet",
    ) -> str:
        """Get 'when' description with hierarchical fallback.

        Fallback order:
        1. Provided 'when' parameter (from scope merging)
        2. Parent categories in hierarchy (e.g., python.web -> python)
        3. Default: "These rules apply at all times"

        :param category_key: The category key
        :type category_key: CategoryKey
        :param when: Optional when description from category
        :type when: str | None
        :param commandments: Commandments ruleset to search parent categories
        :type commandments: RuleSet
        :param suggestions: Suggestions ruleset to search parent categories
        :type suggestions: RuleSet
        :returns: When description with hierarchical fallback
        :rtype: str
        """
        if when and when.strip():
            return when

        parts = category_key.parts
        for i in range(len(parts) - 1, 0, -1):
            parent_parts = parts[:i]
            from daimyo.domain import CategoryKey

            parent_key = CategoryKey(parts=parent_parts)

            if parent_key in commandments.categories:
                parent_when = commandments.categories[parent_key].when
                if parent_when and parent_when.strip():
                    return parent_when

            if parent_key in suggestions.categories:
                parent_when = suggestions.categories[parent_key].when
                if parent_when and parent_when.strip():
                    return parent_when

        return "These rules apply at all times"

    def _render_text(
        self, text: str, scope: "MergedScope", category: "Category | None" = None
    ) -> str:
        """Render text template if renderer available.

        :param text: Text to render
        :type text: str
        :param scope: Scope for context
        :type scope: MergedScope
        :param category: Optional category for context
        :type category: Category | None
        :returns: Rendered text (or original if no renderer)
        :rtype: str
        """
        if self.template_renderer:
            return self.template_renderer.render_rule_text(text, scope, category)
        return text


__all__ = ["TemplateAwareMixin"]
