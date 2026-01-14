# Daimyo - Rules Server for Agents

Daimyo (大名) is an extensible Python server providing rules to AI agents through REST and MCP interfaces. Supports scope-based rules with inheritance, categories for filtering, and server federation for distributed rule management.

## Features

- **Multiple Interfaces**: REST API, MCP (Model Context Protocol), and CLI
- **Scope Inheritance**: Single and multiple parent inheritance with priority-based conflict resolution
- **Rule Types**: Commandments (MUST) and Suggestions (SHOULD)
- **Categories**: Organize rules into hierarchical categories for selective retrieval
- **Server Federation**: Distribute scopes across multiple servers with automatic merging
- **Multiple Formats**: Output as YAML, JSON, or Markdown
- **Clean Architecture**: Domain-driven design with clear separation of concerns
- **Templating System**: Rules can use Jinja2 templates to be defined as generic rules that change their form depending on the context
- **Extensibility via Plugins**: Plugins can extend the features of daimyo instances

## Installation

```bash
pip install daimyo
```

Or install from source:

```bash
git clone https://gitlab.com/Kencho1/daimyo.git
cd daimyo
pip install -e .
```

## Quick Start

### 1. Set Up Your Rules

```bash
cp -r example-daimyo-rules daimyo-rules
```

### 2. Start the Server

```bash
daimyo serve
```

### 3. Access the API

Visit http://localhost:8000/docs for interactive API documentation.

```bash
curl http://localhost:8000/api/v1/scopes/python-general/rules
```

## Core Concepts

### Scopes

Scopes represent organizational contexts (company, team, project). Each scope is a directory containing:

- `metadata.yml` - Scope configuration and parent references
- `commandments.yml` - Mandatory rules (MUST)
- `suggestions.yml` - Recommended rules (SHOULD)

```text
.daimyo/rules/
├── python-general/
│   ├── metadata.yml
│   ├── commandments.yml
│   └── suggestions.yml
└── team-backend/
    ├── metadata.yml
    ├── commandments.yml
    └── suggestions.yml
```

### Metadata Format

```yaml
name: scope-name
description: Human-readable description
parents:
  - parent-scope-1
  - parent-scope-2
tags:
  team: backend
  language: python
```

**Fields:**

- `name`: Scope identifier (must match directory name)
- `description`: Human-readable description
- `parents`: List of parent scopes (first = highest priority)
- `tags`: Key-value pairs for categorization

### Categories

Categories are hierarchical subdivisions within rules:

```yaml
python.web.testing:
  when: When testing web interfaces
  ruleset:
    - Use playwright for acceptance tests
    - Use pytest fixtures for test setup
```

#### Optional "when" Descriptions

The "when" field is optional. When omitted or empty, the system uses intelligent fallback:

```yaml
python.testing:
  when: When writing tests for this project
  ruleset:
    - Use our custom test fixtures

python.web:
  ruleset:
    - Follow team web standards
```

**Fallback priority**:

1. **Category's merged "when" description**: After scope merging (local extends remote, child extends parent scope), the category's "when" field is used if non-empty
2. **Parent categories in the hierarchy**: If empty, traverse up the category path (e.g., `python.web.testing` → `python.web` → `python`) looking for a non-empty "when"
3. **Default**: "These rules apply at all times"

The scope merging process (local → remote → parent) happens before the hierarchical fallback, ensuring child scopes can override descriptions from remote servers or parent scopes.

This allows:

- Parent/remote scopes to define general descriptions
- Child scopes to override only when needed
- Hierarchical inheritance from broader to specific categories
- Simplified child scopes that inherit descriptions

### Rule Types

**Commandments (MUST)**: Mandatory rules that accumulate through inheritance

**Suggestions (SHOULD)**: Recommended rules that can be overridden or appended with `+` prefix

### Why not nesting the categories?

While it seems more intuitive, it proved to be confusing and harder to maintain in certain cases, e.g.:

- Appending suggestions: it's confusing to know whether the `+` must be prepended to the innermost category, to the root category, or to a category in between.
- Sharding categories: should it combine the innermost category or every category and subcategory defined?

For that reason it was decided to keep the categories at the root level, using the explicit path notation and nesting them logically using the dot path splitting.

## Usage

### REST API

Start the server:

```bash
daimyo serve
daimyo serve --host 0.0.0.0 --port 8080
```

Get rules:

```bash
curl http://localhost:8000/api/v1/scopes/python-general/rules

curl -H "Accept: application/json" \
  http://localhost:8000/api/v1/scopes/python-general/rules

curl -H "Accept: text/markdown" \
  http://localhost:8000/api/v1/scopes/python-general/rules
```

List available scopes:

```bash
curl http://localhost:8000/api/v1/scopes
```

Filter by categories:

```bash
curl "http://localhost:8000/api/v1/scopes/team-backend/rules?categories=python.web,python.testing"
```

### MCP Server

Start the MCP server:

```bash
# Using stdio transport (default)
daimyo mcp

# Using HTTP transport
daimyo mcp --transport http

# Using HTTP with custom host and port
daimyo mcp --transport http --host 127.0.0.1 --port 8002
```

Available tools:

- `get_rules(scope_name, categories?)` - Get formatted rules for a scope
- `get_category_index(scope_name)` - Get a hierarchical list of all available categories with their descriptions
- `list_scopes()` - List available scopes
- `apply_scope_rules(scope_name, categories?)` - Get prompt template with rules

#### Connecting to the MCP server

Add the running _daimyo_ MCP server instance to your configuration (replace the server name and the URL with your own):

```json
{
  "mcpServers": {
    "daimyo-rules": {
      "type": "http",
      "url": "http://daimyo-mcp-instance/mcp"
    }
  }
}
```

Instruct your agents how to use the tools:

- State the project scope to use.
- Tell it to read the categories index and fetch the rules of the relevant categories before anything else.

For instance, in `CLAUDE.md`:

```markdown
- The current scope name of this project is `project-api`.
- First and foremost, use the `daimyo-rules` MCP server tools.
  - Use `list_scopes()` to see available scopes.
  - Use `get_category_index` passing the current scope name to list available categories and their descriptions in the given scope.
  - Depending on the categories that apply to the current task, use `get_rules` with the current scope name and a comma-separated list of all the categories that apply, to fetch the specific rules for the related categories.
```

Note some less capable models (like local models via Ollama) may need additional or more detailed instructions.

To make the instructions reusable, the scope name can be read from a file (for instance `.project-scope`).

### CLI Commands

```bash
# List all available scopes
daimyo list-scopes

# Show details of a specific scope
daimyo show python-general

# View template context for debugging
daimyo context python-general
daimyo context python-general --category python.testing
daimyo context python-general --format json
daimyo context python-general --sources

# Version information
daimyo --version
```

#### Template Context Command

The `context` command displays the Jinja2 template context available when rendering rules for a scope. This is useful for debugging template issues and understanding what variables are available in templates.

**Basic usage:**

```bash
daimyo context <scope_name>
```

**Options:**

- `--category, -c`: Show context for a specific category (includes category key and when description)
- `--format, -f`: Output format - `yaml` (default), `json`, or `table`
- `--sources, -s`: Annotate each variable with its source (config, scope, category, or plugins)

**Examples:**

```bash
# View context in YAML format (default)
daimyo context python-general

# View context for a specific category
daimyo context python-general --category python.testing

# JSON format for programmatic use
daimyo context python-general --format json

# Table format for quick scanning
daimyo context python-general --format table

# Show variable sources
daimyo context python-general --sources
```

**Output includes:**

- **Configuration variables**: All DAIMYO_* settings from environment or config files
- **Scope metadata**: name, description, tags, sources
- **Category info**: key and when description (if --category specified)
- **Plugin context**: Variables provided by enabled plugins
- **Plugin metadata**: Available Jinja2 filters and tests from plugins

## Best Practices for Defining Scopes, Categories, and Rules

### 1. Category Organization Principles

#### Universal vs Conditional Categories

**Universal categories** - Always apply when their domain is relevant:

```text
development.coding.quality → Always applies when writing code
development.coding.python → Always applies when writing Python
general → Always applies
```

**Conditional categories** - Only apply when explicitly chosen or context matches:

```text
development.architecture_patterns.clean_architecture → ONLY when pattern chosen
development.coding.testing → ONLY when writing tests
development.lifecycle.review → ONLY during review phase
```

**Rule:** Clearly separate universal from conditional in your hierarchy. Don't mix them at the same level.

**Anti-pattern:**

```text
development.coding
  ├── architecture (universal - SOLID, DRY)
  └── clean_architecture (conditional - specific pattern)
```

**Better:**

```text
development.coding
  └── architecture (universal - SOLID, DRY)

development.architecture_patterns
  └── clean_architecture (conditional - specific pattern)
```

---

### 2. Hierarchical Structure Design

#### Use Aggregator Categories with "Do Not Use Directly" Warnings

**Purpose:** Provide logical grouping without forcing over-fetching

```text
development.coding [DO NOT USE DIRECTLY; pick relevant subcategories]
  ├── core (universal code rules)
  ├── python (language-specific)
  ├── security (security rules)
  └── testing (conditional - when writing tests)
```

**Benefit:** Users can:

- Fetch `development.coding.python` (specific)
- Skip `development.coding.testing` (conditional)
- Avoid accidentally fetching everything under `development.coding`

#### Hierarchical Inclusion is Automatic

**Remember:** Fetching a parent includes ALL children

**Implication:**

- Place conditional categories as siblings, not children of universal categories
- If a parent has mixed universal/conditional children, users can't selectively exclude

**Example problem:**

```text
development.coding.python (universal for Python)
  ├── implementation (universal)
  ├── quality (universal)
  └── testing (conditional - ONLY when writing tests)
```

Fetching `development.coding.python` forces inclusion of testing rules even when not writing tests.

**Solutions:**

1. Document clearly that testing is conditionally included
2. Move testing to sibling: `development.coding.python_testing`
3. Support exclusion in API: `exclude=["development.coding.python.testing"]`

---

### 3. Naming Conventions

#### Use Descriptive, Unambiguous Names

**Avoid:**

- `global` - ambiguous (global to what scope?)
- `common` - vague
- `misc` - catch-all anti-pattern

**Prefer:**

- `core` - base rules for this category
- `universal` - applies to everything in this domain
- `implementation` - during active coding
- `design` - architectural level

#### Use "Aggregated" in Descriptions for Parent Categories

```text
development.coding.python
  Description: "Aggregated rules that apply when the task involves Python programming"
```

Signals that this is a logical grouping with subdivisions.

---

### 4. Description Writing Guidelines

#### Format: "[Applicability] [What it contains]"

**Universal category:**

```text
development.coding.quality
  Description: "Code quality standards applied during implementation"
```

**Conditional category:**

```text
development.coding.testing
  Description: "Rules for writing and structuring tests. Apply when creating test code"
```

**Conditional pattern (emphasize):**

```text
development.architecture_patterns.clean_architecture
  Description: "Clean architecture rules. **ONLY apply when implementing clean architecture pattern**"
```

#### Use Bold for Critical Conditions

Make conditions unmissable:

- "**ONLY apply when...**"
- "**DO NOT use directly; always pick the relevant subcategories**"
- "**Security must be enforced**"

#### Be Explicit About Timing/Context

**Good:**

- "Apply when writing Python tests"
- "During active code development"
- "When designing system architecture"
- "For all code handling user input"

**Bad:**

- "For testing" (writing tests or running tests?)
- "Python rules" (all Python contexts or specific ones?)
- "Architecture" (designing it or following a pattern?)

---

### 5. When to Split Categories

#### Split When

1. **Different applicability conditions**

   ```text
   development.coding.python.implementation (always for Python)
   development.coding.python.testing (only when writing tests)
   ```

2. **Different granularity needed**

   ```text
   development.coding.security.design (architectural patterns)
   development.coding.security.implementation (coding practices)
   ```

3. **Rules serve different phases/activities**

   ```text
   development.lifecycle.implementation
   development.lifecycle.review
   development.lifecycle.deployment
   ```

4. **Domain-specific rules exist**

   ```text
   development.domain_specific.web_applications
   development.domain_specific.apis
   development.domain_specific.cli_tools
   ```

#### Don't Split When

1. **Rules always apply together** - Keep them in one category
2. **Only 1-2 rules exist** - Too granular; merge into parent
3. **Split creates ambiguity** - Which category gets which rule?

---

### 6. When to Merge Categories

#### Merge When

1. **Always fetched together**

   ```text
   # Before: Always fetch both
   development.coding.core
   development.coding.standards

   # After: Merged
   development.coding.core
   ```

2. **Redundant scoping**

   ```text
   # Before: Confusing split
   security (top-level universal)
   development.coding.security.global (also universal?)

   # After: Clarify relationship or merge
   development.security.core (all universal security)
     ├── mindset (high-level principles)
     └── implementation (coding practices)
   ```

3. **Single rule in category**

   ```text
   # Before: Wasteful
   development.architecture_patterns.core
     → Rule: "Prefer well-known patterns"

   # After: Move to parent or merge
   development.architecture_patterns
     → Description includes this guidance
   ```

---

### 7. Security Categories: Special Handling

#### Security Deserves Multiple Locations

**Pattern:**

```text
security (top-level scope)
  → "Universal security mindset. ALWAYS applies"
  → High-level: Security is first-class citizen

development.coding.security
  ├── core: "Universal security requirements for code"
  ├── design: "Security architecture patterns"
  └── implementation: "Secure coding practices"
```

**Why both?**

- Top-level `security`: Ensures security is NEVER forgotten (always included)
- `development.coding.security`: Specific implementation requirements

#### Security Should Be

- Mandatory (MUST, not SHOULD)
- Explicit in descriptions ("Critical for web applications, APIs...")
- Subdivided by concern (design vs implementation)
- Referenced in domain-specific categories (web apps mention OWASP, CORS, etc.)

---

### 8. Language-Specific Organization

#### Pattern: `coding.{language}.{aspect}`

```text
development.coding.python
  ├── implementation (tooling, structure, conventions)
  ├── quality (linting, type checking)
  └── testing (test framework practices)

development.coding.javascript
  ├── implementation (npm, ESLint, project structure)
  ├── quality (TypeScript, strict mode)
  └── testing (Jest patterns)
```

**Benefits:**

- Consistent across languages
- Easy to add new languages
- Clear aspect separation

**Alternative (if many languages):**

```text
development.coding.languages
  ├── python.*
  ├── javascript.*
  └── rust.*
```

---

### 9. Avoiding Ambiguity

#### Common Ambiguity Sources

1. **"Rules related to X"** - Too vague
   - Better: "Rules for writing X" or "Rules applied when X"

2. **"When appropriate"** - Who decides?
   - Better: "When {specific condition}" or "Unless explicitly excluded"

3. **"General" or "Common"** - General within what scope?
   - Better: "Universal" or "Core" with explicit scope

4. **Passive voice** - "Rules that are applied..."
   - Better: "Apply these rules when..."

#### Test Your Descriptions

Ask: "Can someone reading this description know EXACTLY when to include this category?"

**Ambiguous:**

```text
development.coding.testing
  Description: "Testing rules"
```

**Clear:**

```text
development.coding.testing
  Description: "Rules for writing and structuring tests. Apply when creating test code (test_*.py, *_test.py files)"
```

---

### 10. Rule Formulation Best Practices

#### Use MUST/SHOULD Consistently (commandments/suggestions)

**MUST** - Non-negotiable requirements; use commandments for these:

```text
- MUST: No code comments in generated code
- MUST: Security by default
- MUST: Follow SOLID principles
```

**SHOULD** - Strong recommendations (can be overridden with good reason); use suggestions for these:

```text
- SHOULD: Prefer pytest for testing
- SHOULD: Use ruff for linting
- SHOULD: Use English in code
```

#### Rules Should Be Actionable

**Bad (not actionable):**

```text
- SHOULD: Write good tests
- MUST: Be secure
```

**Good (actionable):**

```text
- SHOULD: Use pytest.mark.parametrize for tests with multiple input cases
- MUST: Validate and sanitize all user inputs before processing
```

#### One Concern Per Rule

**Bad (multiple concerns):**

```text
- MUST: Use type hints and validate them with mypy, and also use ruff for linting
```

**Good (separated):**

```text
- SHOULD: Use statically-typed code
- SHOULD: Use mypy to validate typing
- SHOULD: Use ruff for linting
```

---

### 11. Scope Design

#### When to Create Separate Scopes

Create separate scopes when:

1. **Different teams/projects with distinct rule sets**

   ```text
   backend-team (scope)
   frontend-team (scope)
   ml-team (scope)
   ```

2. **Different enforcement levels**

   ```text
   company-wide (scope) → mandatory for everyone
   team-backend (scope) → specific to backend team
   project-xyz (scope) → overrides for specific project
   ```

3. **Different domains with non-overlapping rules**

   ```text
   development (scope) → coding rules
   operations (scope) → deployment, monitoring
   documentation (scope) → writing docs
   ```

#### Scope Inheritance/Layering

Design scopes to be composable:

```text
Query: get_rules(scopes=["company-wide", "development", "python-web"])

Result: Merged rules from all three scopes
```

This allows:

- Company-wide universal policies
- Development-specific coding standards
- Project-specific overrides

---

### 12. Anti-Patterns to Avoid

#### Catch-All Categories

```text
development.coding.misc
development.other
```

Sign of poor organization.

#### Deeply Nested (>4 levels)

```text
development.coding.languages.python.frameworks.django.testing.unit
```

Too granular; hard to navigate.

#### Duplicated Rules

Same rule in multiple categories without clear reason.

#### Circular Dependencies

Category A includes rules about when to use Category B.

#### Implementation Details in Descriptions

```text
Description: "Stored in database table rules_python"
```

Keep descriptions user-focused.

---

### 13. Maintenance Guidelines

#### Regular Audits

1. **Check for orphaned rules** - Rules that don't fit their category
2. **Verify applicability** - Do descriptions still match rule content?
3. **Remove dead rules** - Deprecated tools, outdated practices
4. **Consolidate sparse categories** - <3 rules might belong elsewhere

#### Versioning Strategy

Consider versioning for rule changes:

```text
development.coding.python.v2
development.coding.python.v1 (deprecated)
```

Or use scope versioning:

```text
development-2024 (scope)
development-2025 (scope)
```

---

### Summary Checklist

When creating scopes/categories/rules, verify:

- [ ] **Applicability is crystal clear** - No guessing when to include
- [ ] **Universal and conditional are separated** - Different hierarchy levels
- [ ] **Names are descriptive and unambiguous** - No "global", "misc", "common"
- [ ] **Descriptions state WHEN to apply** - "Apply when..." or "ONLY when..."
- [ ] **Security is mandatory and explicit** - MUST rules, multiple locations
- [ ] **Hierarchies are logical** - Max 3-4 levels deep
- [ ] **Parent categories have warnings** - "DO NOT USE DIRECTLY" where needed
- [ ] **Rules are actionable** - Specific, measurable, implementable
- [ ] **MUST vs SHOULD is consistent** - Clear distinction
- [ ] **One concern per rule** - No compound requirements
- [ ] **No catch-all categories** - Everything has a proper home
- [ ] **Language-specific rules follow consistent pattern** - Same structure for each language

## Configuration

Configuration is managed via `.daimyo/config/settings.toml` or environment variables.

### Configuration Parameters

All configuration parameters with their defaults and descriptions:

#### Rules Directory

- **`rules_path`** (default: `".daimyo/rules"`)
  - Path to the directory containing scope definitions
  - Environment variable: `DAIMYO_RULES_PATH`

#### Logging

- **`console_log_level`** (default: `"WARNING"`)
  - Log level for console output: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  - Environment variable: `DAIMYO_CONSOLE_LOG_LEVEL`

- **`file_log_level`** (default: `"INFO"`)
  - Log level for file output: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  - Environment variable: `DAIMYO_FILE_LOG_LEVEL`

- **`log_file`** (default: `"logs/daimyo.log"`)
  - Path to the main log file
  - Environment variable: `DAIMYO_LOG_FILE`

- **`log_json_file`** (default: `"logs/daimyo.jsonl"`)
  - Path to the JSON-formatted log file
  - Environment variable: `DAIMYO_LOG_JSON_FILE`

#### Scope Resolution

- **`max_inheritance_depth`** (default: `10`, range: `1-100`)
  - Maximum depth for scope inheritance chain to prevent infinite loops
  - Environment variable: `DAIMYO_MAX_INHERITANCE_DEPTH`

#### Remote Server (Federation)

- **`master_server_url`** (default: `""`)
  - URL of master server for scope federation (e.g., `"http://master.example.com:8000"`)
  - Leave empty to disable federation
  - Environment variable: `DAIMYO_MASTER_SERVER_URL`

- **`remote_timeout_seconds`** (default: `5`, range: `1-60`)
  - Timeout in seconds for remote server requests
  - Environment variable: `DAIMYO_REMOTE_TIMEOUT_SECONDS`

- **`remote_max_retries`** (default: `3`, range: `0-10`)
  - Maximum number of retry attempts for failed remote requests
  - Environment variable: `DAIMYO_REMOTE_MAX_RETRIES`

#### REST API Server

- **`rest_host`** (default: `"0.0.0.0"`)
  - Host address to bind the REST API server
  - Environment variable: `DAIMYO_REST_HOST`

- **`rest_port`** (default: `8000`, range: `1-65535`)
  - Port number for the REST API server
  - Environment variable: `DAIMYO_REST_PORT`

#### MCP Server

- **`mcp_transport`** (default: `"stdio"`, options: `"stdio"`, `"http"`)
  - Transport type for MCP server
  - `stdio`: Standard input/output (for CLI integrations)
  - `http`: HTTP server (for HTTP-based integrations)
  - Environment variable: `DAIMYO_MCP_TRANSPORT`

- **`mcp_host`** (default: `"0.0.0.0"`)
  - Host address to bind the MCP server when using HTTP transport
  - Only applies when `mcp_transport="http"`
  - Environment variable: `DAIMYO_MCP_HOST`

- **`mcp_port`** (default: `8001`, range: `1-65535`)
  - Port number for the MCP server when using HTTP transport
  - Only applies when `mcp_transport="http"`
  - Environment variable: `DAIMYO_MCP_PORT`

### Configuration File Example

```toml
[default]
# Rules directory configuration
rules_path = ".daimyo/rules"

# Logging configuration
console_log_level = "WARNING"
file_log_level = "INFO"
log_file = "logs/daimyo.log"
log_json_file = "logs/daimyo.jsonl"

# Scope resolution configuration
max_inheritance_depth = 10

# Remote server configuration
master_server_url = ""
remote_timeout_seconds = 5
remote_max_retries = 3

# REST API configuration
rest_host = "0.0.0.0"
rest_port = 8000

# MCP configuration
mcp_transport = "stdio"
mcp_host = "0.0.0.0"
mcp_port = 8001

[development]
console_log_level = "DEBUG"
rest_port = 8001

[production]
console_log_level = "WARNING"
file_log_level = "WARNING"
```

### Environment Variables

Override any configuration parameter using environment variables with the `DAIMYO_` prefix:

```bash
# Rules path
export DAIMYO_RULES_PATH="/custom/rules/path"

# Logging
export DAIMYO_CONSOLE_LOG_LEVEL="DEBUG"
export DAIMYO_FILE_LOG_LEVEL="INFO"

# Server federation
export DAIMYO_MASTER_SERVER_URL="http://master.example.com:8000"

# REST API
export DAIMYO_REST_HOST="127.0.0.1"
export DAIMYO_REST_PORT="9000"

# MCP Server
export DAIMYO_MCP_TRANSPORT="http"
export DAIMYO_MCP_HOST="0.0.0.0"
export DAIMYO_MCP_PORT="8001"
```

## Examples

The `example-daimyo-rules/` directory contains working examples demonstrating best practices:

### python-general

**Parent:** None (base scope)

Foundation scope demonstrating proper category organization:

- **Universal categories**: `general`, `security`, `development.coding.python.implementation`, `development.coding.python.quality`, `development.coding.python.security`
  - Always apply when writing Python code
  - Defined in **commandments.yml** (mandatory rules)
- **Conditional categories**: `development.coding.python.testing`, `development.coding.python.documentation`
  - Only apply when performing specific activities
  - Defined in **suggestions.yml** (recommendations)
- **Aggregator categories**: `development.coding`, `development.coding.python`
  - Marked with "DO NOT USE DIRECTLY" warnings
  - Provide hierarchical organization without forcing over-fetching

**Key patterns demonstrated:**

- Separation of universal vs conditional categories
- Top-level `security` category for critical security mindset
- Clear "when" descriptions stating applicability
- Actionable, specific rules (not vague guidelines)

### team-backend

**Parent:** `python-general`

Team-specific scope demonstrating domain-specific organization:

- **Domain-specific categories**: `development.domain_specific.web_api`, `development.domain_specific.web_api.security`, `development.domain_specific.database`
  - Universal rules for backend development contexts
  - Defined in **commandments.yml**
- **Lifecycle categories**: `development.lifecycle.deployment`, `development.lifecycle.monitoring`
  - Phase-specific recommendations
  - Defined in **suggestions.yml**
- **Appending to parent**: Uses `+development.coding.python.testing` to extend parent's testing rules

**Key patterns demonstrated:**

- Domain-specific vs language-specific separation
- Lifecycle phase organization
- Using `+` prefix to append suggestions from parent scope
- Security as both commandments (mandatory) and domain-specific rules

### python-fastapi

**Parent:** `python-general`

Framework-specific scope demonstrating architecture pattern organization:

- **Architecture pattern categories**: `development.architecture_patterns.fastapi.*`
  - Marked with "ONLY apply when implementing FastAPI applications"
  - Emphasizes conditional nature with bold warnings
  - Includes routing, async operations, dependencies, performance, testing
- **Clear conditional boundaries**: All categories explicitly state they ONLY apply when using FastAPI

**Key patterns demonstrated:**

- Architecture patterns as conditional categories
- Consistent naming: `development.architecture_patterns.{framework}.{aspect}`
- Bold "ONLY apply when..." warnings to prevent misapplication
- Separating mandatory patterns (commandments) from optimization suggestions

### project-api

**Parents:** `[team-backend, python-fastapi]` (multiple inheritance)

Project-specific scope demonstrating practical composition:

- **Multiple parent inheritance**: Inherits from both team and framework scopes
- **Project-specific overrides**: Refines parent rules for specific project requirements
  - Example: Mandates UUID v4, RFC 7807 errors, request ID tracing
- **Appending to multiple parent categories**:
  - `+development.coding.python.testing` (extends both parents' testing rules)
  - `+development.architecture_patterns.fastapi.performance` (adds project-specific performance targets)
- **New project categories**: `development.lifecycle.review` for code review checklist

**Key patterns demonstrated:**

- Composing team rules + framework rules + project specifics
- Priority-based merging (team-backend = first parent = higher priority)
- Using `+` prefix to append to inherited suggestions
- Project-specific enforcement levels (e.g., authentication requirements)
- Practical combination of universal, conditional, and domain-specific rules

**Hierarchy summary:**

```text
project-api (project-level specifics)
  ├─ team-backend (domain: web APIs, databases)
  │   └─ python-general (language: Python fundamentals)
  └─ python-fastapi (framework: FastAPI patterns)
      └─ python-general (language: Python fundamentals)
```

**To explore these examples:**

```bash
# View category index for any scope
daimyo show python-general

# See merged rules with inheritance
curl http://localhost:8000/api/v1/scopes/project-api/rules

# Filter by specific categories
curl "http://localhost:8000/api/v1/scopes/project-api/rules?categories=development.coding.python.testing,development.domain_specific.web_api"
```

## Advanced Topics

### Multiple Parent Inheritance

```yaml
parents:
  - high-priority
  - low-priority
```

**Commandments**: All rules from all parents are combined (additive)

**Suggestions**: First parent wins in conflicts; use `+` prefix to append instead of replace

### Server Federation

Configure a master server for distributed scope management:

```bash
export DAIMYO_MASTER_SERVER_URL="http://master.example.com:8000"
```

The system will:

1. Look for scopes locally
2. Look for scopes on the master server
3. Merge both if found in both locations (local extends remote)

### Scope Sharding

The same scope name can exist on both master server and locally. When both exist, they are merged with the remote version as the base and the local version extending it.

### Markdown formatting

Rules are typically rendered in Markdown format. LLMs may take advantage of certain formatting features such as emphasis or code fragments, so feel free to use these when writing rules.

### Jinja2 Templates

Rules and category descriptions support Jinja2 templates for dynamic content based on configuration and scope metadata.

#### Available Template Variables

Templates can access:

- **Configuration**: All `DAIMYO_*` environment variables and settings from `config/settings.toml`
- **Scope metadata**: `scope.name`, `scope.description`, `scope.tags`, `scope.sources`
- **Category info**: `category.key`, `category.when` (in rule text only)

#### Basic Example

**Configuration** (`config/settings.toml`):

```toml
[default]
TEAM_NAME = "Backend Team"
SLACK_CHANNEL = "#backend"
```

**Rules with templates** (`commandments.yml`):

```yaml
python.monitoring:
  when: "When monitoring {{ scope.name }} in {{ scope.tags.env | default('dev') }}"
  ruleset:
    - "Alert {{ TEAM_NAME }} via {{ SLACK_CHANNEL }}"
    - "Log level: {{ LOG_LEVEL }}"
```

**Rendered output** (assuming `scope.tags.env = "production"`):

```markdown
## python.monitoring
*When monitoring my-service in production*
- **MUST**: Alert Backend Team via #backend
- **MUST**: Log level: INFO
```

#### Best Practices

**Always use the `default` filter** for optional variables:

```yaml
- "Use {{ MY_VAR | default('fallback_value') }} for configuration"
```

**Conditionals**:

```yaml
- "{% if scope.tags.env == 'prod' %}Use strict security{% else %}Use standard security{% endif %}"
```

**Multiple variables**:

```yaml
- "Team {{ scope.tags.team }} deploys to {{ scope.tags.region }}"
```

#### Error Handling

If a template references an undefined variable without a default:

**REST API**: Returns 422 Unprocessable Entity

```json
{
  "detail": "Template variable 'UNDEFINED_VAR' is undefined in scope 'my-scope', category 'python.web'\n\nTemplate: Use {{ UNDEFINED_VAR }} here\n\nTip: Use Jinja2 'default' filter: {{ UNDEFINED_VAR | default('fallback') }}"
}
```

**MCP/CLI**: Returns error string with same guidance

#### Use Cases

**Environment-aware rules**:

```yaml
python.deployment:
  when: "When deploying to {{ scope.tags.region }}"
  ruleset:
    - "Deploy to {{ scope.tags.region }} region"
    - "{% if scope.tags.env == 'production' %}Require manual approval{% endif %}"
    - "Notification: {{ SLACK_DEPLOY_CHANNEL | default('#deployments') }}"
```

**Team-specific rules**:

```yaml
code-review:
  when: "When reviewing code for {{ TEAM_NAME }}"
  ruleset:
    - "Review in {{ CODE_REVIEW_TOOL | default('SonarQube') }}"
    - "Require approval from {{ scope.tags.team }} lead"
```

## Plugin System

Daimyo supports plugins (bugyo - 奉行) that extend functionality through callback hooks.

### Using Plugins

#### 1. Install a Plugin

Plugins are installed via pip:

```bash
pip install daimyo-example-plugin
```

#### 2. Enable Plugins

Edit `.daimyo/config/settings.toml`:

```toml
enabled_plugins = [
    "git.*",         # Enable all git plugins
    "fs.*",          # Enable all filesystem plugins
    "example.*",     # Enable all plugins with 'example' prefix
    "git.context",   # Enable specific plugin only
]
```

Wildcard patterns supported:

- `"example.*"` - Enable all plugins starting with "example."
- `"example.context"` - Enable specific plugin only

Note: The `"*"` wildcard to enable all plugins is not supported. You must explicitly specify plugin patterns.

#### 3. Running plugins

Once enabled, plugin callbacks are called on different events. For instance, when providing additional context to the templating system:

```yaml
python.web:
  when: When writing Python web code
  ruleset:
    - Use custom variable: {{ custom_var }}
```

### Official Plugins

Daimyo provides official plugins for common use cases. See the [Plugin Catalog](plugins/README.md) for details.

### Creating Plugins

Each plugin has its own entry point and inherits from a specialized base class depending on its purpose.

#### Context Provider Plugins

Provide template variables for Jinja2 templates:

`my_plugin.py`:

```python
from daimyo.domain import ContextProviderPlugin

class MyPlugin(ContextProviderPlugin):
    @property
    def name(self) -> str:
        return "myplugin.context"

    @property
    def description(self) -> str:
        return "Provides custom context variables"

    def is_available(self) -> bool:
        """Check if plugin can run in current environment."""
        return True

    def get_context(self, scope) -> dict:
        """Provide template variables."""
        return {
            "my_var": "my_value",
            "git_branch": "main",
        }
```

`pyproject.toml`:

```toml
[project.entry-points."daimyo.plugins"]
"myplugin.context" = "my_plugin:MyPlugin"
```

Install and enable:

```bash
pip install -e .
```

Then add to `config/settings.toml`:

```toml
enabled_plugins = ["myplugin.*"]
```

#### Filter Provider Plugins

Provide custom Jinja2 filters and tests:

`my_filters.py`:

```python
from daimyo.domain import FilterProviderPlugin
import os.path

class MyFiltersPlugin(FilterProviderPlugin):
    @property
    def name(self) -> str:
        return "myplugin.filters"

    @property
    def description(self) -> str:
        return "Provides custom Jinja2 filters and tests"

    def is_available(self) -> bool:
        return True

    def get_filters(self) -> dict:
        """Provide custom Jinja2 filters."""
        return {
            "uppercase": lambda s: s.upper(),
            "quote": lambda s: f'"{s}"',
        }

    def get_tests(self) -> dict:
        """Provide custom Jinja2 tests."""
        return {
            "file_exists": lambda path: os.path.exists(path),
            "git_repo": lambda path: os.path.exists(os.path.join(path, ".git")),
        }
```

Use in templates:

```yaml
python.web:
  when: When writing Python web code
  ruleset:
    - Name must be {{ package_name | uppercase }}
    - |
      {% if "." is file_exists %}
      Include tests
      {% endif %}
```

#### Plugin Entry Points

Register plugins in **pyproject.toml**:

```toml
[project.entry-points."daimyo.plugins"]
"myplugin.context" = "my_plugin:MyPlugin"
"myplugin.filters" = "my_filters:MyFiltersPlugin"
```

Each plugin has its own entry point for independent discovery and enablement.

### Deployment Pattern: Workspace-Local Instance

A common deployment pattern is running a daimyo instance that:

- Has no local rules directory (or minimal workspace-specific rules)
- References a master daimyo server via `DAIMYO_MASTER_SERVER_URL` for shared organizational rules
- May have workspace-specific plugins installed for context (e.g., git metadata, local filesystem info)

This pattern is useful for:

- **Consistent org-wide rules** with workspace-specific context
- **Reduced duplication** across projects
- **Easier centralized rule management** - update rules once on the master server

Example configuration for a workspace-local instance:

```toml
[default]
rules_path = ".daimyo/rules"  # Empty or minimal local rules
master_server_url = "http://rules.company.com:8000"
enabled_plugins = ["git.*", "fs.*"]
```

In Japanese tradition, this role is called "rusuiyaku" (留守居役, "caretaker") - representing the master in the local workspace.

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
pytest --cov=daimyo
```

### Code Quality

```bash
mypy daimyo
ruff check daimyo
ruff format daimyo
```

## License

MIT
