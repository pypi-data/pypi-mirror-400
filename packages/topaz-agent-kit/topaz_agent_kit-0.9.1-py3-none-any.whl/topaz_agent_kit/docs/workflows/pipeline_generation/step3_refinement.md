# Step 3: Interactive Refinement

This step incorporates user feedback and finalizes the design before file generation.

## Prerequisites

✅ Step 1 complete: Requirements gathered and approved
✅ Step 2 complete: Workflow proposal presented and approved

---

## 3.1 Review & Feedback Loop

### 3.1.1 Collect Feedback

**Action**: Ask user if any refinements are needed:

**Questions**:
1. "Are there any adjustments to agent roles or responsibilities?"
2. "Any changes to the execution pattern?"
3. "Any modifications to HITL gates?"
4. "Any concerns about the MCP tool selections?"
5. "Any other changes before we generate the files?"

### 3.1.2 Process Changes

**For each change requested**:

1. **Document the change**:
   - What is being changed
   - Why the change is needed
   - Impact on other components

2. **Update affected components**:
   - Agent configurations
   - Pattern structure
   - HITL gates
   - Dependencies

3. **Re-validate**:
   - Dependency order still valid
   - Variable references still work
   - Pattern structure still correct

### 3.1.3 Common Refinement Scenarios

| Scenario | Action |
|----------|--------|
| Add new agent | Update pattern, check dependencies |
| Remove agent | Update pattern, remove from HITL if referenced |
| Change agent order | Update pattern, verify variable access |
| Add HITL gate | Update pattern with `after` placement |
| Change pattern type | Restructure entire pattern section |
| Add conditional | Add condition to step, define `on_false` |

### 3.1.4 Change Tracking

Track all changes made during refinement:

```
## Refinement Changes

| # | Change | Reason | Components Affected |
|---|--------|--------|---------------------|
| 1 | {change} | {reason} | {components} |
| 2 | {change} | {reason} | {components} |
```

---

## 3.2 Final Confirmation

**🔍 CHECKPOINT**: Get explicit confirmation before proceeding to file generation.

### 3.2.1 Pre-Generation Summary

Present final summary:

```
## Final Design Summary

### Pipeline: {pipeline_name}
- **ID**: {pipeline_id}
- **Prefix**: {prefix}

### Agents ({count} total)
| # | Agent ID | Role |
|---|----------|------|
| 1 | {agent_id} | {role} |
| 2 | {agent_id} | {role} |
...

### Pattern Type: {pattern_type}
{Brief pattern description}

### HITL Gates ({count} total)
| Gate ID | Type | After |
|---------|------|-------|
| {gate_id} | {type} | {agent} |

### Files to Generate
- [ ] Pipeline config (1)
- [ ] Agent configs ({count})
- [ ] Prompt templates ({count})
- [ ] HITL templates ({hitl_count})
- [ ] UI manifest (1)
- [ ] SVG icons ({icon_count})
- [ ] Update pipeline.yml
- [ ] Update ui_manifest.yml
- [ ] Update assistant_intent_classifier.jinja

### Mock Data
- Database: {yes/no}
- Script: {script_name or N/A}
```

### 3.2.2 Explicit Confirmation

**Action**: Ask for explicit confirmation:

```
"I'm ready to generate all files for the {pipeline_name} pipeline.

This will create:
- {count} agent configuration files
- {count} prompt template files
- {count} HITL template files (if any)
- 1 pipeline configuration file
- 1 UI manifest file
- {count + 1} SVG icon files

Should I proceed with file generation?"
```

**Wait for explicit "yes" or "proceed" before continuing.**

### 3.2.3 Handle Hesitation

**If user hesitates**:
- "Is there something specific you'd like to review or change?"
- "Would you like to see the proposed file contents before I generate them?"
- "Are there any concerns about the design?"

**If user wants to see files first**:
- Show template of key files (pipeline config, one agent config, one prompt)
- Get approval on templates before generating all files

---

## Proceed to Step 4

After receiving explicit confirmation, proceed to:
→ `step4_generation.md`

**Do NOT proceed without explicit user confirmation.**

