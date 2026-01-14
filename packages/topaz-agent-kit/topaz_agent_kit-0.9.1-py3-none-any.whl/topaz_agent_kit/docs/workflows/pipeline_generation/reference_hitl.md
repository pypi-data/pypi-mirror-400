# Reference: Human-in-the-Loop (HITL) Gates

This document provides detailed reference for HITL gate types, configuration, and placement strategies.

---

## Gate Types Overview

| Type | Purpose | User Action |
|------|---------|-------------|
| Approval | Review and approve/reject | Click approve or reject |
| Input | Collect information | Fill form fields |
| Selection | Choose between options | Select from list |

---

## 1. Approval Gates

**Use When**: Human needs to review and approve/reject before continuing.

### Basic Approval Gate

```yaml
hitl:
  - id: "{pipeline_id}_approve_{purpose}"
    type: "approval"
    after: "{agent_id}"
    title: "Review {Agent} Output"
    description_template: "config/hitl/{gate_id}.jinja"
    actions:
      on_approve: "continue"
      on_reject: "stop"
```

### Approval with Retry

```yaml
hitl:
  - id: "{pipeline_id}_approve_{purpose}"
    type: "approval"
    after: "{agent_id}"
    title: "Review Analysis"
    description_template: "config/hitl/{gate_id}.jinja"
    actions:
      on_approve: "continue"
      on_reject:
        action: "retry"
        retry_agent: "{agent_to_retry}"
        max_retries: 3
        inject_context: true
```

### Description Template Example

```jinja
## Review Required

The {{ agent_name }} has completed analysis.

**Summary:**
{{ agent_output.summary }}

**Key Findings:**
{% for finding in agent_output.findings %}
- {{ finding }}
{% endfor %}

**Confidence Score:** {{ agent_output.confidence }}%

Please review and approve to continue, or reject to stop the pipeline.
```

---

## 2. Input Gates

**Use When**: Need to collect information from user.

### Basic Input Gate

```yaml
hitl:
  - id: "{pipeline_id}_input_{purpose}"
    type: "input"
    after: "{agent_id}"  # or "start"
    title: "Provide Information"
    description_template: "config/hitl/{gate_id}.jinja"
    fields:
      - name: "field_name"
        type: "text"
        label: "Field Label"
        required: true
        placeholder: "Enter value..."
```

### Input Gate at Start (File Upload)

```yaml
hitl:
  - id: "{pipeline_id}_upload_document"
    type: "input"
    after: "start"
    title: "Upload Document"
    description_template: "config/hitl/{gate_id}.jinja"
    fields:
      - name: "document_file"
        type: "file"
        label: "Document"
        required: true
        accept: ".pdf,.docx,.txt"
      - name: "document_type"
        type: "select"
        label: "Document Type"
        required: true
        options:
          - value: "contract"
            label: "Contract"
          - value: "invoice"
            label: "Invoice"
          - value: "report"
            label: "Report"
```

### Field Types

| Type | Description | Additional Properties |
|------|-------------|----------------------|
| `text` | Single line text | `placeholder`, `pattern` |
| `textarea` | Multi-line text | `rows`, `placeholder` |
| `select` | Dropdown selection | `options` |
| `checkbox` | Boolean toggle | `default` |
| `file` | File upload | `accept`, `multiple` |
| `number` | Numeric input | `min`, `max`, `step` |
| `date` | Date picker | `min`, `max` |
| `email` | Email input | `placeholder` |

### Pre-populated Fields

```yaml
fields:
  - name: "suggested_response"
    type: "textarea"
    label: "Response Draft"
    required: true
    default: "{{ drafter.response }}"  # Pre-fill from agent output
    rows: 10
```

### Conditional Fields

```yaml
fields:
  - name: "needs_escalation"
    type: "checkbox"
    label: "Escalate to Manager"
    default: false
  - name: "escalation_reason"
    type: "textarea"
    label: "Escalation Reason"
    required: true
    condition: "{{ needs_escalation }} == true"
```

---

## 3. Selection Gates

**Use When**: User needs to choose between options.

### Basic Selection Gate

```yaml
hitl:
  - id: "{pipeline_id}_select_{purpose}"
    type: "selection"
    after: "{agent_id}"
    title: "Select Option"
    description_template: "config/hitl/{gate_id}.jinja"
    options:
      - value: "option_1"
        label: "Option 1"
        description: "Description of option 1"
      - value: "option_2"
        label: "Option 2"
        description: "Description of option 2"
```

### Selection with Branch Routing

```yaml
hitl:
  - id: "{pipeline_id}_select_path"
    type: "selection"
    after: "{agent_id}"
    title: "Choose Processing Path"
    options:
      - value: "fast_track"
        label: "Fast Track"
        description: "Quick processing, less thorough"
        next_agent: "fast_processor"
      - value: "detailed"
        label: "Detailed Analysis"
        description: "Thorough analysis, takes longer"
        next_agent: "detailed_processor"
      - value: "expert_review"
        label: "Expert Review"
        description: "Send to human expert"
        next_agent: "expert_notifier"
```

### Dynamic Options from Agent Output

```yaml
hitl:
  - id: "{pipeline_id}_select_candidate"
    type: "selection"
    after: "ranker"
    title: "Select Best Candidate"
    options_source: "ranker.candidates"
    option_template:
      value: "{{ item.id }}"
      label: "{{ item.name }}"
      description: "Score: {{ item.score }}"
```

---

## Gate Placement Strategies

### At Pipeline Start

```yaml
pattern:
  type: sequential
  steps:
    # HITL gate is first step
    - pattern:
        type: hitl
        gate_id: "{pipeline_id}_upload_document"
    - extractor
    - analyzer
```

Or using `after: "start"`:
```yaml
hitl:
  - id: "{pipeline_id}_upload"
    type: "input"
    after: "start"
```

### Between Agents

```yaml
pattern:
  type: sequential
  steps:
    - analyzer
    # Implicit HITL gate placement via "after"
    - processor
```

With explicit gate:
```yaml
hitl:
  - id: "{pipeline_id}_review_analysis"
    type: "approval"
    after: "analyzer"
```

### Before Critical Actions

```yaml
pattern:
  type: sequential
  steps:
    - drafter
    - pattern:
        type: hitl
        gate_id: "{pipeline_id}_approve_email"
    - email_sender
```

### In Loops

```yaml
pattern:
  type: loop
  iterate_over: "scanner.items"
  steps:
    - processor
    - pattern:
        type: hitl
        gate_id: "{pipeline_id}_approve_item"
        condition: "{{processor.needs_review}} == true"
```

---

## Conditional Gates

Gates can be conditional:

```yaml
hitl:
  - id: "{pipeline_id}_escalate"
    type: "selection"
    after: "analyzer"
    condition: "{{analyzer.risk_score}} > 80"
    title: "High Risk - Manual Review Required"
```

---

## Context Injection

When retry is used, previous context can be injected:

```yaml
actions:
  on_reject:
    action: "retry"
    retry_agent: "drafter"
    inject_context: true
    context_fields:
      - "rejection_reason"
      - "user_feedback"
```

The retry agent's prompt can then use:
```jinja
{% if rejection_reason %}
**Previous Attempt Rejected:**
{{ rejection_reason }}

**User Feedback:**
{{ user_feedback }}

Please address this feedback in your revised output.
{% endif %}
```

---

## Timeout Configuration

```yaml
hitl:
  - id: "{pipeline_id}_approve"
    type: "approval"
    after: "analyzer"
    timeout:
      duration: 3600  # seconds
      action: "auto_approve"  # or "auto_reject" or "stop"
```

---

## HITL Description Templates

### Best Practices

1. **Clear context**: Explain what was done and why review is needed
2. **Key information**: Highlight important data points
3. **Actionable**: Clear instructions on what user should do

### Template Structure

```jinja
## {Gate Title}

### Summary
{Brief description of what happened}

### Key Information

| Field | Value |
|-------|-------|
| {Field 1} | {{ agent.field1 }} |
| {Field 2} | {{ agent.field2 }} |

### Details

{{ agent.detailed_output }}

### Action Required

{Instructions for the user}
```

### Using Markdown Tables

Follow whitespace rules (see `reference_jinja.md`):
```jinja
| Field | Value |
|-------|-------|
{%- for item in items %}
| {{ item.name }} | {{ item.value }} |
{%- endfor %}
```

---

## Common HITL Patterns

### Review Before Send

```yaml
# After drafter, before sender
hitl:
  - id: "{pipeline_id}_review_draft"
    type: "approval"
    after: "drafter"
    title: "Review Before Sending"
```

### Upload at Start, Review at End

```yaml
hitl:
  - id: "{pipeline_id}_upload"
    type: "input"
    after: "start"
  - id: "{pipeline_id}_final_review"
    type: "approval"
    after: "finalizer"
```

### Conditional Escalation

```yaml
hitl:
  - id: "{pipeline_id}_escalate"
    type: "selection"
    after: "analyzer"
    condition: "{{analyzer.confidence}} < 0.7"
    title: "Low Confidence - Please Review"
    options:
      - value: "proceed"
        label: "Proceed Anyway"
      - value: "escalate"
        label: "Escalate to Expert"
      - value: "reject"
        label: "Reject and Stop"
```

