# Reference: Jinja2 & Variable Syntax

This document provides detailed reference for Jinja2 templating, variable syntax, and whitespace control in prompts and configurations.

---

## Variable Syntax

### Explicit Syntax (Preferred)

```jinja
{{ agent_id.field }}
```

**Examples**:
- `{{ extractor.document_text }}`
- `{{ analyzer.risk_score }}`
- `{{ classifier.category }}`

### Simple Syntax

```jinja
{{ field }}
```

**Use when**: Field name is unique across all upstream agents.

**Examples**:
- `{{ user_input }}`
- `{{ project_dir }}`

### Never Use

```jinja
{{ context.get('field') }}
{{ context.upstream.agent_id.field }}
```

---

## Variable Sources

| Source | Syntax | Description |
|--------|--------|-------------|
| User input | `{{ user_input }}` | Original user message |
| Upstream agent | `{{ agent_id.field }}` | Output from previous agent |
| Loop item | `{{ loop_item_key }}` | Current item in loop |
| Loop item field | `{{ loop_item_key.field }}` | Field from current item |
| Project directory | `{{ project_dir }}` | Absolute path to project |
| Repeat instances | `{{ agent_id_instances }}` | All repeat pattern results |

---

## Expressions & Filters

### Basic Expressions

```jinja
{{ value + 1 }}
{{ value * 2 }}
{{ "prefix_" + name }}
{{ list | length }}
```

### Common Filters

| Filter | Purpose | Example |
|--------|---------|---------|
| `default` | Default if undefined | `{{ value \| default('N/A') }}` |
| `upper` | Uppercase | `{{ text \| upper }}` |
| `lower` | Lowercase | `{{ text \| lower }}` |
| `length` | Count items | `{{ items \| length }}` |
| `round` | Round number | `{{ score \| round(2) }}` |
| `join` | Join list | `{{ items \| join(', ') }}` |
| `first` | First item | `{{ items \| first }}` |
| `last` | Last item | `{{ items \| last }}` |

### Custom Topaz Filters

| Filter | Purpose | Example |
|--------|---------|---------|
| `format_currency` | Format as currency | `{{ amount \| format_currency }}` |
| `default_if_none` | Handle None values | `{{ value \| default_if_none }}` |
| `risk_score_color` | Color for risk score | `{{ score \| risk_score_color }}` |
| `credit_score_color` | Color for credit score | `{{ score \| credit_score_color }}` |

---

## Conditionals

### Basic If

```jinja
{% if condition %}
  Content when true
{% endif %}
```

### If-Else

```jinja
{% if condition %}
  Content when true
{% else %}
  Content when false
{% endif %}
```

### If-Elif-Else

```jinja
{% if score > 80 %}
  High
{% elif score > 50 %}
  Medium
{% else %}
  Low
{% endif %}
```

### Inline Conditional

```jinja
{{ 'Yes' if value else 'No' }}
```

---

## Loops

### Basic For Loop

```jinja
{% for item in items %}
  {{ item.name }}: {{ item.value }}
{% endfor %}
```

### Loop with Index

```jinja
{% for item in items %}
  {{ loop.index }}. {{ item.name }}
{% endfor %}
```

### Loop Variables

| Variable | Description |
|----------|-------------|
| `loop.index` | Current iteration (1-indexed) |
| `loop.index0` | Current iteration (0-indexed) |
| `loop.first` | True if first iteration |
| `loop.last` | True if last iteration |
| `loop.length` | Total number of items |

---

## Whitespace Control

### The Problem

Jinja2 tags add whitespace/newlines that can break markdown formatting.

### Solution: Whitespace Control Characters

| Syntax | Effect |
|--------|--------|
| `{%-` | Strip whitespace before tag |
| `-%}` | Strip whitespace after tag |
| `{{-` | Strip whitespace before variable |
| `-}}` | Strip whitespace after variable |

### When to Use Whitespace Control

**Use `{%-` and `-%}`** for:
- Conditionals inside table cells
- Loops inside table rows
- Any Jinja inside inline content

**Do NOT use whitespace control** for:
- `{% set %}` statements before tables
- Content that needs newlines preserved

---

## Markdown Tables in Templates

### Critical Rules

1. **No blank lines within tables**:
   ```jinja
   ❌ BAD:
   | Header |
   |--------|
   
   | Row |
   
   ✅ GOOD:
   | Header |
   |--------|
   | Row |
   ```

2. **Use whitespace control for conditionals in tables**:
   ```jinja
   ❌ BAD:
   | Field | {% if value %}{{ value }}{% else %}N/A{% endif %} |
   
   ✅ GOOD:
   | Field | {%- if value %}{{ value }}{%- else %}N/A{%- endif %} |
   ```

3. **Set statements before tables - NO whitespace control**:
   ```jinja
   ❌ BAD:
   {%- set score = agent.score %}
   | Score |
   |-------|
   | {{ score }} |
   
   ✅ GOOD:
   {% set score = agent.score %}
   | Score |
   |-------|
   | {{ score }} |
   ```

4. **Set statements on separate lines**:
   ```jinja
   ❌ BAD:
   | Amount | {% set sym = currency %}{{ sym }}{{ amount }} |
   
   ✅ GOOD:
   {% set sym = currency %}
   | Amount | {{ sym }}{{ amount }} |
   ```

5. **Blank line after HTML tags before tables**:
   ```jinja
   ❌ BAD:
   <details>
   <summary>Summary</summary>
   | Header |
   |--------|
   
   ✅ GOOD:
   <details>
   <summary>Summary</summary>
   
   | Header |
   |--------|
   ```

### Loop Inside Table

```jinja
| Name | Value |
|------|-------|
{%- for item in items %}
| {{ item.name }} | {{ item.value }} |
{%- endfor %}
```

### Conditional Rows

```jinja
| Field | Value |
|-------|-------|
{%- if agent.field1 %}
| Field 1 | {{ agent.field1 }} |
{%- endif %}
{%- if agent.field2 %}
| Field 2 | {{ agent.field2 }} |
{%- endif %}
```

---

## Prompt Template Best Practices

### Variable Sections

```jinja
**Input:**
{%- if user_input %}
**User Request:** {{ user_input }}
{%- endif %}

{%- if upstream_agent.output %}
**Previous Analysis:** {{ upstream_agent.output }}
{%- endif %}
```

### Optional Sections

```jinja
{%- if context.additional_info %}
**Additional Context:**
{{ context.additional_info }}
{%- endif %}
```

### Safe Variable Access

```jinja
{{ agent.field | default('Not available') }}
{{ agent.nested.field | default_if_none }}
```

---

## Common Patterns

### Display Items with Index

```jinja
{% for item in items %}
{{ loop.index }}. **{{ item.title }}**
   {{ item.description }}
{% endfor %}
```

### Conditional Formatting

```jinja
Status: {%- if score > 80 %} ✅ Approved{%- elif score > 50 %} ⚠️ Review{%- else %} ❌ Rejected{%- endif %}
```

### Summary Table

```jinja
| Metric | Value |
|--------|-------|
| Total Items | {{ items | length }} |
| Average Score | {{ total_score / (items | length) | round(2) }} |
| Status | {{ 'Complete' if all_done else 'Pending' }} |
```

### Nested Data Access

```jinja
{% for claim in claims %}
**Claim {{ claim.id }}:**
- Amount: {{ claim.details.amount | format_currency }}
- Status: {{ claim.details.status }}
{% endfor %}
```

---

## Debugging Tips

### Check Variable Availability

```jinja
{# Debug: Show available variables #}
<!-- DEBUG: upstream_agent = {{ upstream_agent | default('UNDEFINED') }} -->
```

### Validate Before Use

```jinja
{% if upstream_agent is defined and upstream_agent.field %}
  {{ upstream_agent.field }}
{% else %}
  [Field not available]
{% endif %}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `UndefinedError` | Variable doesn't exist | Check upstream agent, use `default` |
| Broken table | Whitespace in table | Use `{%-` and `-%}` |
| Missing newlines | Over-aggressive whitespace control | Remove `-` from `{% set %}` |
| Empty output | Condition never true | Check condition logic |

---

## Jinja2 Filters Reference

The Topaz Agent Kit provides these filters automatically in all templates.

### Number Formatting Filters

**`format_currency(value, decimals=2)`**
- Formats numbers as currency with commas and decimal places
- Example: `{{ 125000 | format_currency }}` → `"125,000.00"`
- Example: `{{ 125000 | format_currency(decimals=0) }}` → `"125,000"`

**`format_number(value, decimals=0, thousands_sep=",")`**
- Generic number formatting with optional decimals and separator
- Example: `{{ 1250.5 | format_number(decimals=2) }}` → `"1,250.50"`

**`format_percentage(value, decimals=1, multiply=True)`**
- Formats numbers as percentages
- Example: `{{ 0.85 | format_percentage }}` → `"85.0%"`
- Example: `{{ 0.8523 | format_percentage(decimals=2) }}` → `"85.23%"`

### Score/Risk Color Coding Filters

**`risk_score_color(value)`**
- Returns color code for risk scores where **lower is better** (0-100 scale)
- Color mapping:
  - 0-25: `#22c55e` (green - low risk)
  - 26-50: `#f59e0b` (amber - medium risk)
  - 51-75: `#ef4444` (red - high risk)
  - 76-100: `#dc2626` (dark red - very high risk)
- Example: `<span style="color: {{ risk_score | risk_score_color }};">{{ risk_score }}</span>`

**`credit_score_color(value)`**
- Returns color code for credit/quality scores where **higher is better** (0-100 scale)
- Color mapping:
  - 85-100: `#22c55e` (green - excellent)
  - 70-84: `#f59e0b` (amber - good)
  - 50-69: `#ef4444` (red - fair)
  - <50: `#dc2626` (dark red - poor)
- Example: `<span style="color: {{ credit_score | credit_score_color }};">{{ credit_score }}</span>`

**`score_color(value, thresholds=None, low_is_better=False)`**
- Generic score color coding with configurable thresholds
- `thresholds`: List of `(threshold, color)` tuples in ascending order
- `low_is_better`: If `True`, lower scores are better (inverts logic)

### Text Formatting Filters

**`truncate_text(value, max_length=100, suffix="...")`**
- Truncates text to maximum length with suffix
- Example: `{{ "Very long text here" | truncate_text(10) }}` → `"Very long..."`

**`pluralize(value, singular, plural=None)`**
- Returns singular or plural form based on count
- Example: `{{ 5 | pluralize("item") }}` → `"items"`
- Example: `{{ 1 | pluralize("child", "children") }}` → `"child"`

**`highlight_text(value, search_terms, highlight_class="highlight")`**
- Highlights search terms in text (wraps in `<mark>` tags)
- Example: `{{ text | highlight_text("search term") }}`

### Date/Time Formatting Filters

**`format_date(value, format_str="%Y-%m-%d")`**
- Formats date/datetime values
- Example: `{{ "2025-01-28" | format_date }}` → `"2025-01-28"`
- Example: `{{ "2025-01-28" | format_date("%B %d, %Y") }}` → `"January 28, 2025"`

**`format_duration(seconds, compact=False)`**
- Formats duration in seconds as human-readable string
- Example: `{{ 3665 | format_duration }}` → `"1 hour 1 minute 5 seconds"`
- Example: `{{ 3665 | format_duration(compact=True) }}` → `"1h 1m 5s"`

### Data Formatting Filters

**`format_file_size(value, binary=False)`**
- Formats bytes as human-readable file size
- Example: `{{ 1572864 | format_file_size }}` → `"1.5 MB"`
- Example: `{{ 1572864 | format_file_size(binary=True) }}` → `"1.5 MiB"`

**`mask_sensitive(value, visible_chars=4, mask_char="*")`**
- Masks sensitive data, showing only first N characters
- Example: `{{ "1234567890" | mask_sensitive(4) }}` → `"1234******"`

**`format_phone(value, format_str="us")`**
- Formats phone numbers
- Example: `{{ "1234567890" | format_phone }}` → `"(123) 456-7890"`
- Options: `"us"`, `"international"`, `"compact"`

### Utility Filters

**`safe_divide(numerator, denominator, default=0)`**
- Safely divides two numbers, returning default if denominator is zero
- Example: `{{ 10 | safe_divide(2) }}` → `5.0`
- Example: `{{ 10 | safe_divide(0, "N/A") }}` → `"N/A"`

**`default_if_none(value, default="N/A")`**
- Returns default value if input is None
- Example: `{{ None | default_if_none("—") }}` → `"—"`

### Usage Examples

**Pattern Descriptions:**
```yaml
description: |
  ## Current Claim Details
  
  | Field | Value |
  |-------|-------|
  | Claim Amount | {{ current_claim.currency_symbol }}{{ current_claim.invoice_amount | format_currency }} |
  | Risk Score | <span style="color: {{ risk_score | risk_score_color }};">{{ risk_score }}</span>/100 |
```

**HITL Gate Descriptions:**
```yaml
description: |
  **Application ID:** {{ current_application.application_id }}
  **Requested Amount:** {{ current_application.requested_amount | format_currency }}
  **Credit Score:** <span style="color: {{ credit_score | credit_score_color }};">{{ credit_score }}</span>
```

**Agent Input Templates:**
```yaml
inputs:
  inline: |
    Amount: {{ amount | format_currency }}
    Percentage: {{ ratio | format_percentage }}
    Date: {{ date | format_date("%B %d, %Y") }}
```

### Best Practices

1. **Use filters consistently**: Always use `format_currency` instead of `round(2)` for monetary values
2. **Color coding**: Use `risk_score_color` or `credit_score_color` instead of inline color logic
3. **Handle None values**: Use `default_if_none` or conditional rendering for optional fields
4. **Readability**: Use filters to improve template readability and maintainability

