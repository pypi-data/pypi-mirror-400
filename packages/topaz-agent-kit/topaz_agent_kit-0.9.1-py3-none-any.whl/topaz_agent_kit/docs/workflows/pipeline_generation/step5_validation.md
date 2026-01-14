# Step 5: Validation & Summary

This step validates all generated files and provides a completion summary.

## Prerequisites

✅ Step 4 complete: All files generated and user has reviewed

---

## 5.1 Validate Generated Files

### 5.1.1 File Existence Validation

**Verify all files exist**:

```
□ config/pipelines/{pipeline_id}.yml
□ config/agents/{agent_id}.yml (for each agent)
□ config/prompts/{agent_id}.jinja (for each agent)
□ config/hitl/{gate_id}.jinja (for each HITL gate)
□ config/ui_manifests/{pipeline_id}.yml
□ ui/static/assets/{pipeline_id}.svg
□ ui/static/assets/{agent_id}.svg (for each agent)
```

### 5.1.2 Context Variable Validation

**Critical**: Verify all context variables are accessible.

For each agent prompt, validate:

| Agent | Variable | Source Agent | Valid? |
|-------|----------|--------------|--------|
| {agent_id} | `{{var}}` | {source} | ✅/❌ |

**Validation Rules**:
1. Variables must reference upstream agents only
2. Loop item keys must match `loop_item_key` in pattern
3. `project_dir` available for all agents
4. `user_input` available for first agent (or all if needed)

**Common Issues**:
| Issue | Solution |
|-------|----------|
| Variable from downstream agent | Reorder agents or use different variable |
| Variable from parallel agent | Move agent to sequential or use different source |
| Undefined loop item | Add `loop_item_key` to loop pattern |
| Missing `project_dir` | Add to agent inputs in pattern |

### 5.1.3 HITL Validation

For each HITL gate:

| Gate ID | Type | After Agent Exists | Template Exists | Valid? |
|---------|------|-------------------|-----------------|--------|
| {gate_id} | {type} | ✅/❌ | ✅/❌ | ✅/❌ |

### 5.1.4 Pattern Validation

**Verify pattern structure**:
- [ ] All referenced agents exist
- [ ] Dependencies are in correct order
- [ ] Conditions reference valid variables
- [ ] Loop `iterate_over` references valid array
- [ ] Switch cases are exhaustive

### 5.1.5 User Review: Validation Results

**🔍 CHECKPOINT**: Present validation results.

```
## Validation Results

### File Existence: {PASS/FAIL}
{List of files checked}

### Context Variables: {PASS/FAIL}
{List of variables validated}

### HITL Gates: {PASS/FAIL}
{List of gates validated}

### Pattern Structure: {PASS/FAIL}
{Pattern validation notes}

### Overall: {PASS/FAIL}
```

**If any validation fails**:
- Identify specific issue
- Propose fix
- Apply fix
- Re-validate

**Do not proceed to summary until all validations pass.**

---

## 5.2 Generate Summary

### 5.2.1 Summary Template

Generate completion summary:

```
# Pipeline Generation Complete ✅

## Pipeline: {Pipeline Name}

### Overview
- **ID**: `{pipeline_id}`
- **Agents**: {count}
- **Pattern**: {pattern_type}
- **HITL Gates**: {count}
- **Framework**: {framework}

### Files Generated

#### Configuration Files
| File | Path |
|------|------|
| Pipeline | `config/pipelines/{pipeline_id}.yml` |
| UI Manifest | `config/ui_manifests/{pipeline_id}.yml` |

#### Agent Files ({count} agents)
| Agent | Config | Prompt | Icon |
|-------|--------|--------|------|
| {agent_id} | ✅ | ✅ | ✅ |

#### HITL Templates ({count} gates)
| Gate | Template |
|------|----------|
| {gate_id} | `config/hitl/{gate_id}.jinja` |

#### Updated Files
- ✅ `config/pipeline.yml`
- ✅ `config/ui_manifest.yml`
- ✅ `config/prompts/assistant_intent_classifier.jinja`

### Workflow Pattern

```yaml
{Pattern YAML}
```

### Testing Instructions

1. **Regenerate Project** (if using templates):
   ```bash
   topaz-agent-kit init --starter ensemble projects/ensemble
   ```

2. **Run Mock Data Script** (if applicable):
   ```bash
   uv run -m scripts.setup_{pipeline_id}_database --reset
   ```

3. **Test via CLI**:
   ```bash
   topaz-agent-kit serve cli --project projects/ensemble
   ```
   Then enter a request that triggers this pipeline.

4. **Test via UI**:
   ```bash
   topaz-agent-kit serve fastapi --project projects/ensemble
   ```
   Open browser to `http://localhost:8000`

### Next Steps

1. Test the pipeline with sample inputs
2. Refine prompts based on output quality
3. Adjust HITL gates if needed
4. Consider adding more test cases
```

---

## 5.3 User Review: Final Summary

**🔍 CHECKPOINT**: Present final summary to user.

**Questions**:
- "Is there anything else you'd like to add or modify?"
- "Do you have any questions about testing the pipeline?"
- "Would you like documentation for this pipeline?"

---

## 5.4 Post-Generation Notes

### 5.4.1 Testing Pipeline

**Recommended Testing Flow**:

1. **Unit Test**: Test each agent individually
   ```bash
   # If you have agent test utilities
   uv run pytest tests/agents/test_{agent_id}.py
   ```

2. **Integration Test**: Test full pipeline
   ```bash
   topaz-agent-kit serve cli --project projects/ensemble
   ```

3. **UI Test**: Test with UI interactions
   ```bash
   topaz-agent-kit serve fastapi --project projects/ensemble
   ```

### 5.4.2 Common Issues After Generation

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Agent not found | Missing from pipeline.yml | Add agent to agents list |
| Variable undefined | Upstream agent not run | Check pattern order |
| HITL not showing | Gate not in pattern | Add HITL to pipeline config |
| Icon not displaying | Wrong path | Check UI manifest icon path |
| Pipeline not in assistant | Not in classifier | Add to assistant_intent_classifier.jinja |

### 5.4.3 Iterating on Prompts

**Prompt Refinement Tips**:
1. Run pipeline with test input
2. Review agent outputs
3. Identify quality issues
4. Adjust prompt instructions
5. Re-test

**Common Prompt Adjustments**:
- Add more specific instructions
- Include edge case handling
- Clarify output format
- Add more examples

---

## Workflow Complete

The pipeline generation workflow is complete.

**Summary of what was created**:
- Pipeline configuration
- Agent configurations (×N)
- Prompt templates (×N)
- HITL templates (if any)
- UI manifest
- SVG icons (×N+1)
- Updated main config files

**User can now**:
- Test the pipeline
- Refine prompts
- Add more agents
- Modify patterns

