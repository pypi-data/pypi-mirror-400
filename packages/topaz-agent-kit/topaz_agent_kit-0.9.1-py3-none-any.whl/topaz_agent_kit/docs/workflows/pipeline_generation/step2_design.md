# Step 2: Workflow Design & Proposal

This step uses the collected requirements to design the complete workflow structure.

## Prerequisites

✅ Step 1 complete with:
- Pipeline ID and prefix confirmed
- All agents identified with roles
- Pattern preferences documented
- HITL gates identified (if any)
- MCP tools identified (if any)
- Output requirements documented

---

## 2.1 Agent Finalization

### 2.1.1 Protocol Selection

**Default Protocol**: A2A for all remote agents, IN-PROC for local.

For each agent, determine:

| Agent ID | Protocol | Remote Initially | Notes |
|----------|----------|------------------|-------|
| {agent_id} | A2A | Yes/No | {notes} |

**Note**: Remote configuration is added to ALL agents regardless of initial protocol, enabling easy switching later.

### 2.1.2 MCP Tool Requirements Analysis

**Action**: For each agent, analyze MCP tool needs:

**File Processing Rule**: Only ONE agent should extract each file type.

| Agent ID | MCP Tools | Justification |
|----------|-----------|---------------|
| {agent_id} | {tools} | {why needed} |

**Common Tool Mappings**:
- File extraction → `doc_extract_structured_data`
- Document RAG → `doc_rag_*` tools
- Web search → `search_internet`
- Database → `sqlite_query`, `sqlite_execute`
- Browser → `browser_get_content`

**🔍 Important**: Agents using file/database tools need `project_dir` in inputs for path resolution.

---

## 2.2 Workflow Pattern Design

### 2.2.0 Review Available Patterns

If needed, reference `reference_patterns.md` for pattern details.

**Quick Pattern Reference**:

| Pattern | Use When | YAML Key |
|---------|----------|----------|
| Sequential | Steps depend on each other | `type: sequential` |
| Parallel | Steps are independent | `type: parallel` |
| Repeat | Same agent, multiple inputs | `type: repeat` |
| Loop | Iterate until condition | `type: loop` |
| Conditional | Branch on condition | `condition:` |
| Switch | Route by field value | `type: switch` |
| Handoff | LLM chooses specialist | `type: handoff` |
| Group Chat | Collaborative conversation | `type: group_chat` |
| Nested | Combine patterns | Nest `pattern:` blocks |

### 2.2.1 Design Execution Pattern

**Action**: Create the YAML representation of the execution pattern.

**Pattern Structure Template**:

```yaml
pattern:
  type: {sequential|parallel|loop|switch|handoff|group_chat}
  name: "{Pattern Name}"
  description: |
    {Description of what this pattern does}
  steps:
    - {agent_id_1}
    - {agent_id_2}
    # or nested patterns
    - pattern:
        type: parallel
        steps:
          - {parallel_agent_1}
          - {parallel_agent_2}
```

**Examples**:

**Simple Sequential**:
```yaml
pattern:
  type: sequential
  steps:
    - contract_analyzer_extractor
    - contract_analyzer_classifier
    - contract_analyzer_risk_assessor
    - contract_analyzer_report_generator
```

**Sequential with Parallel Section**:
```yaml
pattern:
  type: sequential
  steps:
    - claim_processor_extractor
    - pattern:
        type: parallel
        name: "Parallel Validation"
        steps:
          - claim_processor_policy_validator
          - claim_processor_coverage_checker
    - claim_processor_decision_maker
```

**With Conditional Branch**:
```yaml
pattern:
  type: sequential
  steps:
    - analyzer_classifier
    - pattern:
        type: sequential
        condition: "{{analyzer_classifier.is_complex}} == true"
        on_false: stop  # or [alternative_agent]
        steps:
          - analyzer_deep_processor
```

**Loop Pattern**:
```yaml
pattern:
  type: loop
  name: "Process Each Item"
  iterate_over: "scanner.items_list"
  loop_item_key: "current_item"
  accumulate_results: true
  steps:
    - item_processor
    - item_validator
```

### 2.2.2 Dependency Validation

**Action**: Verify all dependencies are satisfied:

| Agent | Requires Data From | Pattern Position | Valid? |
|-------|-------------------|------------------|--------|
| {agent} | {upstream_agents} | {position} | ✅/❌ |

**Validation Rules**:
- Agents can only access outputs from upstream agents
- Parallel agents cannot depend on each other
- Conditional branches must have valid condition variables
- Loop items must be iterable

### 2.2.3 Complex Workflow Considerations

**For complex workflows**, consider:

1. **Pipeline Composition**: Can any section be its own pipeline?
   ```yaml
   steps:
     - pattern:
         type: pipeline
         pipeline_id: "reusable_validation"
   ```

2. **Accumulate Results**: For loops accessing all iterations:
   ```yaml
   accumulate_results: true
   # Access via: {{agent_id}}_instances
   ```

3. **Nested Depth**: Keep nesting ≤ 3 levels for maintainability

---

## 2.3 HITL Gates Design

Reference `reference_hitl.md` for detailed gate configurations.

### 2.3.1 Gate Type Selection

For each identified HITL need, determine gate type:

| Gate ID | Type | After Agent | Purpose |
|---------|------|-------------|---------|
| {gate_id} | approval/input/selection | {agent} | {purpose} |

### 2.3.2 Gate Configuration

**Approval Gate Template**:
```yaml
hitl:
  - id: "{pipeline_id}_approve_{purpose}"
    type: "approval"
    after: "{agent_id}"
    title: "{Human-readable title}"
    description_template: "config/hitl/{gate_id}.jinja"
    actions:
      on_approve: "continue"
      on_reject: "stop"  # or retry
```

**Input Gate Template**:
```yaml
hitl:
  - id: "{pipeline_id}_input_{purpose}"
    type: "input"
    after: "{agent_id}"  # or "start" for first step
    title: "{Human-readable title}"
    description_template: "config/hitl/{gate_id}.jinja"
    fields:
      - name: "field_name"
        type: "text|textarea|select|file|checkbox"
        label: "Field Label"
        required: true
        placeholder: "Placeholder text"
```

**Selection Gate Template**:
```yaml
hitl:
  - id: "{pipeline_id}_select_{purpose}"
    type: "selection"
    after: "{agent_id}"
    title: "{Human-readable title}"
    description_template: "config/hitl/{gate_id}.jinja"
    options:
      - value: "option_1"
        label: "Option 1 Label"
        description: "What this option does"
      - value: "option_2"
        label: "Option 2 Label"
```

### 2.3.3 Gate Placement Strategies

**Best Practices**:
- **Start of workflow**: Input gates for file uploads
- **After analysis agents**: Approval gates for review
- **Before critical actions**: Approval gates (emails, submissions)
- **Decision points**: Selection gates for routing

### 2.3.4 Retry Logic Configuration

If retry is needed:
```yaml
actions:
  on_reject:
    action: "retry"
    retry_agent: "{agent_to_retry}"
    max_retries: 3
    inject_context: true  # Include rejection reason
```

---

## 2.4 Output Structure Design

### 2.4.1 Final Output Configuration

```yaml
outputs:
  - source: "{final_agent_id}"
    fields: ["field1", "field2"]
    transform: null  # or transformation function
```

### 2.4.2 Intermediate Outputs

If intermediate outputs needed:
```yaml
outputs:
  - source: "{agent_id}"
    fields: ["*"]  # or specific fields
    label: "intermediate"
```

### 2.4.3 Output Transformations

Common transformations:
- `markdown_to_html`
- `json_to_table`
- `flatten_nested`

---

## 2.5 Present Workflow Proposal

### 2.5.1 Create Design Document

Compile the complete workflow design:

```
## Workflow Design Proposal: {Pipeline Name}

### Pipeline Overview
- **ID**: {pipeline_id}
- **Agents**: {count} agents
- **Pattern**: {pattern_type}
- **HITL Gates**: {count} gates

### Agent Flow

{Visual representation}

1. [{agent_1}] → 2. [{agent_2}] → ...
       ↓ HITL: {gate}
   3. [{agent_3}] → ...

### Execution Pattern

```yaml
{Complete pattern YAML}
```

### HITL Gates

| Gate | Type | Placement | Actions |
|------|------|-----------|---------|
| {gate_id} | {type} | After {agent} | {actions} |

### MCP Tools by Agent

| Agent | Tools |
|-------|-------|
| {agent_id} | {tools} |

### Output Configuration

- **Final**: {agent}.{fields}
- **Intermediate**: {list}

### Files to Generate

1. Pipeline config: `config/pipelines/{id}.yml`
2. Agent configs: {count} files
3. Prompt templates: {count} files
4. HITL templates: {count} files
5. UI manifest: `config/ui_manifests/{id}.yml`
6. Icons: {count + 1} SVG files
```

### 2.5.2 Present Workflow Proposal

**Action**: Present the design document to user.

**Questions to ask**:
- "Does this workflow design meet your requirements?"
- "Are there any agents missing or unnecessary?"
- "Is the execution pattern correct?"
- "Are the HITL gates placed correctly?"

---

## 2.6 User Review: Workflow Proposal

**🔍 CHECKPOINT**: Wait for user approval.

**Handling Responses**:
- **If user approves**: Proceed to Step 3
- **If user wants changes**: Make adjustments, present updated proposal
- **If user identifies issues**: Address issues, re-validate dependencies

**Do not proceed to Step 3 without explicit user approval.**

---

## Proceed to Step 3

After user approves workflow proposal, proceed to:
→ `step3_refinement.md`

