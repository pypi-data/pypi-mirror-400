"""Template rendering service using Jinja2."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, StrictUndefined, UndefinedError

from daimyo.infrastructure.logging import get_logger

if TYPE_CHECKING:
    from daimyo.domain import Category, MergedScope

logger = get_logger(__name__)

TEMPLATE_PATTERN = re.compile(r"\{\{.*?\}\}|\{%.*?%\}")


class TemplateRenderer:
    """Renders Jinja2 templates in rule text with strict undefined checking.

    Features:
    - Strict mode: Raises TemplateRenderingError if variable is undefined
    - Auto-detection: Only processes strings with {{ }} or {% %} syntax
    - Rich context: Provides config, scope metadata, category info
    """

    def __init__(self, settings: Any, plugin_registry: Any = None):
        """Initialize renderer with Dynaconf settings.

        :param settings: Dynaconf settings object
        :type settings: Any
        :param plugin_registry: Optional plugin registry for context and filter providers
        :type plugin_registry: Any | None
        """
        self.settings = settings
        self.plugin_registry = plugin_registry

        self.env = Environment(
            undefined=StrictUndefined,
            autoescape=False,
        )

        # Register plugin-provided filters and tests
        if self.plugin_registry is not None:
            enabled_patterns = getattr(self.settings, "ENABLED_PLUGINS", [])
            if enabled_patterns:
                try:
                    filters, tests = self.plugin_registry.aggregate_filters_and_tests(
                        enabled_patterns
                    )

                    self.env.filters.update(filters)
                    self.env.tests.update(tests)

                    logger.info(
                        f"Registered {len(filters)} custom filters "
                        f"and {len(tests)} custom tests from plugins"
                    )

                except Exception as e:
                    logger.error(f"Failed to register plugin filters/tests: {e}")

    def needs_rendering(self, text: str) -> bool:
        """Check if text contains template syntax.

        :param text: Text to check
        :type text: str
        :returns: True if text contains {{ }} or {% %}
        :rtype: bool
        """
        return bool(TEMPLATE_PATTERN.search(text))

    def render_rule_text(
        self,
        text: str,
        scope: MergedScope,
        category: Category | None = None,
    ) -> str:
        """Render a rule text template.

        :param text: Rule text (may contain templates)
        :type text: str
        :param scope: Merged scope for context
        :type scope: MergedScope
        :param category: Optional category for context
        :type category: Category | None
        :returns: Rendered text
        :rtype: str
        :raises TemplateRenderingError: If template variable is undefined
        """
        if not self.needs_rendering(text):
            return text

        context = self._build_context(scope, category)

        try:
            template = self.env.from_string(text)
            result = template.render(context)
            logger.debug(f"Rendered template: {text[:50]}... → {result[:50]}...")
            return result

        except UndefinedError as e:
            from daimyo.domain import TemplateRenderingError

            match = re.search(r"'([^']+)' is undefined", str(e))
            variable_name = match.group(1) if match else "unknown"

            context_info = f"scope '{scope.metadata.name}'"
            if category:
                context_info += f", category '{category.key}'"

            raise TemplateRenderingError(
                template_text=text,
                variable_name=variable_name,
                context_info=context_info,
            ) from e

    def render_category_when(
        self,
        when_text: str,
        scope: MergedScope,
        category: Category,
    ) -> str:
        """Render a category 'when' description template.

        :param when_text: Category when description
        :type when_text: str
        :param scope: Merged scope for context
        :type scope: MergedScope
        :param category: Category for context
        :type category: Category
        :returns: Rendered when description
        :rtype: str
        :raises TemplateRenderingError: If template variable is undefined
        """
        return self.render_rule_text(when_text, scope, category)

    def _build_context(
        self,
        scope: MergedScope,
        category: Category | None = None,
    ) -> dict[str, Any]:
        """Build Jinja2 context dictionary including plugin-provided context.

        :param scope: Merged scope
        :type scope: MergedScope
        :param category: Optional category
        :type category: Category | None
        :returns: Context dictionary for template rendering
        :rtype: dict[str, Any]
        """
        context: dict[str, Any] = {}

        for key, value in self.settings.as_dict().items():
            if isinstance(value, (str, int, bool, float, type(None))):
                context[key] = value

        context["scope"] = {
            "name": scope.metadata.name,
            "description": scope.metadata.description,
            "tags": scope.metadata.tags,
            "sources": scope.sources,
        }

        if category:
            context["category"] = {
                "key": str(category.key),
                "when": category.when,
            }

        if self.plugin_registry is not None:
            enabled_patterns = getattr(self.settings, "ENABLED_PLUGINS", [])

            if enabled_patterns:
                try:
                    plugin_context = self.plugin_registry.aggregate_context(
                        scope=scope,
                        enabled_patterns=enabled_patterns,
                    )

                    conflicts = set(context.keys()) & set(plugin_context.keys())
                    if conflicts:
                        logger.warning(f"Plugin context conflicts: {conflicts}")

                    context.update(plugin_context)
                    logger.debug(f"Added {len(plugin_context)} plugin context variables")

                except Exception as e:
                    logger.error(f"Failed to get plugin context: {e}")

        return context

    def get_context_with_sources(
        self,
        scope: MergedScope,
        category: Category | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Get template context organized by source.

        This method exposes the template context used for rendering rules,
        organized by where each variable comes from. Useful for debugging
        and understanding what variables are available in templates.

        :param scope: Merged scope for context
        :type scope: MergedScope
        :param category: Optional category for context
        :type category: Category | None
        :returns: Dictionary with sections: config, scope, category (optional), plugins
        :rtype: dict[str, dict[str, Any]]
        """
        result: dict[str, dict[str, Any]] = {
            "config": {},
            "scope": {},
            "plugins": {},
        }

        for key, value in self.settings.as_dict().items():
            if isinstance(value, (str, int, bool, float, type(None))):
                result["config"][key] = value

        result["scope"] = {
            "name": scope.metadata.name,
            "description": scope.metadata.description,
            "tags": scope.metadata.tags,
            "sources": scope.sources,
        }

        if category:
            result["category"] = {
                "key": str(category.key),
                "when": category.when,
            }

        if self.plugin_registry is not None:
            enabled_patterns = getattr(self.settings, "ENABLED_PLUGINS", [])

            if enabled_patterns:
                try:
                    plugin_context = self.plugin_registry.aggregate_context(
                        scope=scope,
                        enabled_patterns=enabled_patterns,
                    )
                    result["plugins"] = plugin_context
                    logger.debug(f"Extracted {len(plugin_context)} plugin context variables")

                except Exception as e:
                    logger.error(f"Failed to get plugin context: {e}")

        return result


__all__ = ["TemplateRenderer"]
