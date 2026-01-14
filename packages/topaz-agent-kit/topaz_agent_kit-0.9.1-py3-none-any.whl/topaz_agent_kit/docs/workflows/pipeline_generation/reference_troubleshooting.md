# Reference: Troubleshooting

This document covers common validation errors, fixes, and important reminders for pipeline generation.

---

## Important Reminders

1. **Production-Ready**: Generate complete, runnable configs, not templates
2. **Use-Case Specific**: All content (prompts, descriptions) should be tailored to the specific use case
3. **Validation**: Always validate before completion
4. **Consistency**: Follow existing patterns and naming conventions
5. **Completeness**: Ensure all required sections are included in each file
6. **References**: Check that all file references are correct
7. **Context Variables**: Ensure prompt inputs reference valid context variables

---

## Common Validation Errors and Fixes

### 1. Intermediate Outputs with `id` Field

**Error**: `Additional properties are not allowed ('id' was unexpected) at outputs.intermediate.0`

**Cause**: Intermediate outputs schema does NOT allow `id` fields.

**Fix**: Remove `id` from all intermediate output entries. Only use `node`, `selectors`, and optional `transform`.

```yaml
# ✅ CORRECT
outputs:
  intermediate:
    - node: agent_id
      selectors:
        - field1
        - field2

# ❌ WRONG
outputs:
  intermediate:
    - id: output_name  # ❌ 'id' not allowed
      node: agent_id
      selectors:
        - field1
```

---

### 2. Variables in Prompt Files

**Error**: Variables appearing in prompt `.jinja` files

**Cause**: Variables should be in agent YML `inputs.inline`, not in prompt files.

**Fix**: Move all variables from prompt files to agent YML `prompt.inputs.inline` section.

```jinja
# ✅ CORRECT - Prompt file: prompts/agent_id.jinja
You are a **Parser Agent**, specializing in extracting structured information.

Tasks:
1. Extract field1 from input
2. Extract field2 from input
```

```yaml
# ✅ CORRECT - Agent YML: agents/agent_id.yml
prompt:
  instruction:
    jinja: prompts/agent_id.jinja
  inputs:
    inline: |
      User Input: {{user_text}}
      Field1: {{field1}}
```

```jinja
# ❌ WRONG - Variables in prompt file
You are a **Parser Agent**.

User Input: {{user_text}}  # ❌ Should be in agent YML
```

---

### 3. Agent IDs in Input Variables

**Error**: Variables using agent prefixes like `{{agent_id.field}}`

**Note**: Context resolution supports BOTH syntaxes:
- `{{field}}` - Simple syntax (when field name is unique)
- `{{agent_id.field}}` - Explicit syntax (preferred for clarity)

**Recommendation**: Use explicit syntax `{{agent_id.field}}` for clarity:

```yaml
# ✅ PREFERRED - Explicit syntax
inputs:
  inline: |
    Complaint Type: {{complaint_wizard_parser.complaint_type}}
    Billing Issues: {{complaint_wizard_parser.billing_issues}}

# ✅ ALSO VALID - Simple syntax (when field names are unique)
inputs:
  inline: |
    Complaint Type: {{complaint_type}}
    Billing Issues: {{billing_issues}}
```

---

### 4. Python-Style Conditionals in Jinja2 Templates

**Error**: `JSONUtils: Expected JSON but parsing failed`

**Cause**: Using Python-style conditionals like `{{var if var is not none else "default"}}`

**Fix**: Use proper Jinja2 conditional blocks: `{% if variable %}...{% endif %}`

```yaml
# ✅ CORRECT
inputs:
  inline: |
    Complaint Type: {{complaint_type}}
    {% if amount_mentioned %}Amount Mentioned: {{amount_mentioned}}{% endif %}
    {% if timeframe %}Timeframe: {{timeframe}}{% endif %}

# ❌ WRONG
inputs:
  inline: |
    Amount: {{amount if amount is not none else "not mentioned"}}  # ❌
    Timeframe: {{timeframe if timeframe is not none else "not specified"}}  # ❌
```

---

### 5. Missing Section Comments in Agent YMLs

**Error**: Agent YML files missing proper section comments

**Fix**: Add properly formatted section comments:

```yaml
# =============================================================================
# PARSER AGENT CONFIGURATION
# =============================================================================
#
# This agent parses user input to extract structured information...
#
# =============================================================================
id: agent_id
name: "Parser Agent"
...
```

---

### 6. Dynamic Gate Descriptions

**Pattern**: Gate descriptions can use Jinja2 templates to display content from upstream agents.

**Simple Inline Format** (for short descriptions):
```yaml
gates:
  - id: approve_root_cause
    type: approval
    title: "Approve Root Cause Analysis"
    description: "{{ agent_id.explanation | default('Review and approve to proceed.') }}"
```

**External Jinja File Format** (for complex descriptions):
```yaml
gates:
  - id: review_claim
    type: selection
    title: "Claim Decision Review"
    description:
      jinja: "hitl/eci_decision_gate.jinja"  # Path relative to config/
```

**When to Use Each**:
- **Inline**: Simple descriptions (1-10 lines), single-line dynamic content
- **External File**: Complex descriptions (50+ lines), multiple sections, extensive tables

---

### 7. MCP Tools - Only Add When Needed

**Error**: Adding MCP tools to agents that don't need external capabilities

**Cause**: Not all agents need external tools - some only process data from upstream agents.

**When to Add MCP**:
- ✅ Agent needs to search the web or external databases
- ✅ Agent needs to call external APIs
- ✅ Agent needs real-time data not available in context

**When NOT to Add MCP**:
- ❌ Agent only processes data from upstream agents
- ❌ Agent generates content based on provided context
- ❌ Agent analyzes mock/generated data

**Example**: An account researcher that analyzes mock account data doesn't need MCP tools - it only processes provided data.

---

### 8. Final Response Agent Pattern

**Pattern**: When multiple agents produce outputs that need to be combined, use a final response agent instead of complex transforms.

**Use Case**: Combining outputs from response generator and escalation handler into a unified package.

```yaml
# ✅ CORRECT Pattern
pattern:
  type: sequential
  steps:
    - node: response_generator
    - type: sequential
      condition: "sentiment_analyzer.escalation_recommended == true"
      steps:
        - node: escalation_handler
    - node: final_response  # Always runs, combines outputs
```

**Benefits**:
- Cleaner than complex Jinja2 transforms in outputs
- Agent can intelligently combine and format multiple outputs
- Easier to maintain and understand

---

## Handling Common Scenarios

### If User Requests Changes After Generation

1. Make the requested changes
2. Re-validate affected files
3. Update summary if needed

### If Validation Fails

1. Identify the issue using the common errors above
2. Fix the problem
3. Re-validate
4. Explain the fix to the user

### If Files Already Exist

1. Check with user before overwriting
2. Offer to backup existing files
3. Show diff if possible

---

## Workflow Completion Checklist

When following this workflow:

1. ✅ Work step-by-step with the user through each phase
2. ✅ Don't skip steps - ensure user approval at each major decision point
3. ✅ Generate files only after final design approval
4. ✅ Always validate before declaring completion
5. ✅ Provide clear summary of what was generated and next steps
6. ✅ Generate actual SVG icons (not just suggestions)
7. ✅ Update all three main config files:
   - `config/pipeline.yml`
   - `config/ui_manifest.yml`
   - `config/prompts/assistant_intent_classifier.jinja`

---

## Testing Generated Pipeline

**Steps to test**:

1. **Validate Configuration**:
   ```bash
   topaz-agent-kit validate <project_dir>
   ```

2. **Test Individual Agents** (optional but recommended):
   - Test each agent with sample inputs
   - Verify output format matches expected schema

3. **Test Full Pipeline**:
   ```bash
   topaz-agent-kit serve cli --project projects/ensemble
   ```
   - Run end-to-end scenario with realistic input
   - Verify all agents execute in correct order

4. **Test HITL Gates**:
   - Verify gates appear correctly in UI
   - Test all gate actions (approve, reject, continue, retry)

5. **Test Output**:
   - Verify final output format matches expectations
   - Check that all expected fields are present

6. **Test Error Handling**:
   - Test with invalid inputs
   - Verify error messages are clear

