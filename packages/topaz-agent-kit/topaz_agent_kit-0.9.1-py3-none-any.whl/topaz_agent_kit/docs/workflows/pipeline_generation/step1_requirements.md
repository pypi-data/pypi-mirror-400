# Step 1: Comprehensive Requirements Gathering

This step collects ALL information needed before designing the workflow. Ask questions systematically before proceeding to design.

## Important Notes

- **Step 1 = COLLECT**: You are gathering information from the user
- **Step 2 = USE**: You will use the collected information to design the workflow
- If user doesn't know an answer, provide suggestions based on use case analysis
- If user gives partial information, ask follow-up questions
- If user provides conflicting information, ask for clarification

---

## Interactive Conversation Best Practices

**🔍 IMPORTANT**: This workflow requires natural, interactive conversation. Follow these principles:

### When to Batch Questions

**Batch related questions together** to avoid overwhelming users:
- ✅ **Good**: "Let me understand your workflow needs. What pattern should agents follow - sequential, parallel, or mixed? And which agents will run remotely initially?"
- ❌ **Bad**: Ask about pattern, wait for answer, then ask about remote execution separately

**Examples of good batching**:
- Basic use case info (name, description, purpose) - ask together
- Agent identification (roles, inputs, outputs) - ask for all agents at once
- HITL requirements (gates, placement, types) - group by gate type

### When to Ask One at a Time

**Ask complex questions individually** to allow thoughtful responses:
- ✅ **Good**: "What should we call this pipeline?" → wait → "What's the detailed purpose?" → wait
- ❌ **Bad**: "What's the name, description, purpose, pattern, agents, gates, and outputs?" (too much)

**Examples of one-at-a-time**:
- Pipeline naming (important decision)
- Complex pattern choices (needs explanation)
- Agent role definitions (each needs careful thought)
- Gate placement decisions (affects workflow structure)

### Handling User Uncertainty

**When users are unsure**, provide guidance rather than waiting:
- ✅ **Good**: "I see you're not sure about the pattern. Based on your use case, I'd suggest sequential flow because [reason]. Does that work?"
- ❌ **Bad**: "What pattern do you want?" → user says "I don't know" → "OK, let me know when you decide"

**Strategies for uncertainty**:
- **Provide examples**: Show 2-3 similar pipelines and explain why each might work
- **Make recommendations**: Analyze the use case and suggest the best option with reasoning
- **Offer to defer**: Allow users to skip optional sections and return later
- **Use progressive disclosure**: Start high-level, then drill down based on user responses

### Handling Interruptions

**When users interrupt or change direction**, adapt gracefully:
- ✅ **Good**: "I understand you want to change the agent list. Let me update what we have so far: [summary]. Now, what agents would you like instead?"
- ❌ **Bad**: "But we already discussed agents. Let's finish the current step first."

**Strategies for interruptions**:
- **Acknowledge the change**: "I see you want to modify [X]. Let me update our plan."
- **Summarize current state**: Briefly recap what's been decided so far
- **Resume from new point**: Continue from where the user wants to go
- **Save context**: Remember previous decisions that still apply

### Natural vs Robotic Patterns

**Natural conversation patterns**:
- ✅ "Based on your use case, I think we'll need about 3-4 agents. Let's start by identifying the main tasks..."
- ✅ "That makes sense! For a sequential flow like this, we typically need [X]. Does that align with what you're thinking?"
- ✅ "Great question! Let me explain how that works: [explanation]. Does that help clarify?"

**Robotic patterns to avoid**:
- ❌ "Step 1.3: Agent Identification. Please provide agent roles, inputs, and outputs."
- ❌ "According to the workflow, I need to ask about agents now."
- ❌ "You must provide all agent information before proceeding."

### Progressive Disclosure

**Start high-level, then drill down**:
1. **First**: "What problem does this pipeline solve?" (high-level)
2. **Then**: "What are the main steps to solve it?" (medium-level)
3. **Finally**: "For each step, what specific inputs and outputs are needed?" (detailed)

**Use examples to guide**:
- When user is unsure, reference similar existing pipelines
- Show patterns that worked for similar use cases
- Explain why certain patterns fit their needs

**Allow flexibility**:
- Users can skip optional sections and return later
- Users can change their minds and revise earlier decisions
- Don't force completion of every sub-step if user wants to move forward

---

## 1.1 Basic Use Case Information

**Action**: Ask the user for basic information:

**Questions**:
1. **Use Case Description**: What problem does this pipeline solve? (Detailed description)
2. **Pipeline Name**: What should we call this pipeline? (Human-readable name)
3. **Pipeline Description**: What is the detailed purpose statement? (1-2 sentences)

**Additional Clarifying Questions** (if use case is vague):
- What is the primary goal of this pipeline?
- What inputs does the pipeline receive from users?
- What is the expected final output?
- Are there any specific requirements or constraints?
- Are there any existing agents or patterns we should reference?

### 1.1.1 Handle Incomplete Information

**If use case is vague or incomplete**:
- Ask clarifying questions before proceeding
- Don't make assumptions - ask user for clarification
- Provide examples of good use case descriptions:
  - ✅ Good: "A pipeline that analyzes customer support tickets, classifies them by priority, and generates response drafts"
  - ❌ Vague: "Something for customer support"
- Offer to pause and let user refine requirements if needed

### 1.1.2 Generate Pipeline ID

**Action**: Convert pipeline name to snake_case ID:
- Use slugify: lowercase, replace spaces with underscores
- Remove special characters, keep only alphanumeric and underscores
- Example: "Email Summarizer" → `email_summarizer`
- Verify ID doesn't conflict with existing pipelines in templates folder
- If conflict exists: Ask user for alternative name or append number (e.g., `email_summarizer_v2`)

**Naming Conventions**:
| Type | Format | Example |
|------|--------|---------|
| Pipeline ID | `snake_case` | `email_summarizer` |
| Agent ID | `{pipeline_id}_{role}` | `email_summarizer_analyzer` |
| Gate ID | `{pipeline_id}_{purpose}` | `email_summarizer_review` |
| File Names | Match IDs exactly | `email_summarizer_analyzer.yml` |
| Icon Names | Match IDs exactly | `email_summarizer_analyzer.svg` |

### 1.1.3 Agent Naming Convention & Prefix Confirmation

**🔍 CRITICAL**: All agents MUST be prefixed with the pipeline ID to avoid conflicts.

**Action**: After generating pipeline ID, confirm the prefix with user:

1. **Suggest Prefix**: Based on pipeline ID
   - Example: Pipeline ID `contract_analyzer` → Prefix `contract_analyzer`

2. **Present to User**:
   - "Based on the pipeline ID `{pipeline_id}`, I suggest using `{pipeline_id}` as the prefix for all agents."
   - "All agent IDs will follow: `{pipeline_id}_{agent_role}`"
   - "Does this prefix work for you?"

3. **Handle User Response**:
   - If user approves: Proceed with suggested prefix
   - If user suggests alternative: Use user's preferred prefix
   - If user wants shorter prefix: Warn about potential conflicts

**Pattern Examples from Existing Pipelines**:
- `article_smith` → `article_research_analyst`, `article_content_author`, `article_chief_editor`
- `trip_planner` → `trip_requester`, `trip_flights_expert`, `trip_aggregator`
- `math_compass` → `math_strategist`, `math_calculator`, `math_auditor`
- `stock_analysis` → `stock_research_analyst`, `stock_financial_analyst`, `stock_investment_advisor`

---

## 1.2 Workflow Pattern Preferences

**Action**: Ask user about workflow pattern preferences BEFORE designing.

**If user is unsure**: Analyze the use case and suggest appropriate patterns, then ask for confirmation.

**Questions**:
1. **Execution Flow**: How should agents execute?
   - Sequential (one after another) - Default for dependent steps
   - Parallel (simultaneously) - For independent tasks
   - Repeat (same agent multiple times in parallel) - For processing multiple items
   - Loop (iterative until condition met) - For refinement workflows
   - Conditional (branching based on conditions)
   - Switch (route to different branches based on values)
   - Handoff (LLM-driven routing to specialists)
   - Group Chat (collaborative conversation)
   - Mixed (combination of patterns)

2. **Pattern Complexity**: What level of complexity?
   - Simple sequential flow
   - Sequential with some parallel steps
   - Complex nested patterns
   - Special patterns (group chat, handoff)

3. **Reference Examples**: Would you like to see examples?
   - Show 2-3 relevant pipeline examples from templates
   - Explain why each pattern might work for this use case

**Handling User Responses**:
- **If user knows**: Document their preferences directly
- **If user is unsure**: Suggest patterns based on use case, get confirmation
- **If user says "you decide"**: Make recommendation with reasoning, get confirmation

---

## 1.3 Agent Identification & Responsibilities

**Action**: Ask user to identify agents needed:

**Questions**:
1. **Agent Roles**: What agents are needed? (List all)
   - For each agent: What is its specific role/responsibility?
   - What tasks will each agent perform?
   - What inputs does each agent need?
   - What outputs will each agent produce?

2. **Agent Dependencies**: Which agents depend on others?
   - Which agents can run independently (parallel)?
   - Which agents must wait for others (sequential)?
   - Are there any circular dependencies?

3. **Agent Count**: How many agents total?
   - If 5+ agents: Should we consider breaking into sub-pipelines?

**Action**: After collecting agent information:
- List all agents with roles, inputs, and outputs
- Document dependencies clearly
- Apply confirmed prefix from Step 1.1.3 for agent IDs

### 1.3.1 Agent ID Conflict Check

**🔍 CRITICAL**: After identifying all agents, check for conflicts with existing agent files.

**Check Process**:
1. Generate full agent IDs: `{confirmed_prefix}_{agent_role}`
2. Check if file exists: `config/agents/{agent_id}.yml`
3. List any conflicts

**If conflicts found**:
- Present conflicts to user with existing file paths
- Ask user to resolve:
  - Option 1: Use different agent role names
  - Option 2: Use different prefix
  - Option 3: Overwrite existing (not recommended)
- Wait for user decision before proceeding

---

## 1.4 Conditional Logic & Decision Points

**Action**: Ask about conditional logic needs:

**Questions**:
1. **Decision Points**: Are there any decision points in the workflow?
   - Does the workflow need to branch based on conditions?
   - Different paths based on input type/complexity?

2. **Conditional Types**: What kind of conditionals?
   - Switch pattern (route based on agent output field)
   - Conditional nodes (run only if conditions met)
   - If-else pattern (`on_false` with alternative steps)
   - Stop action (`on_false: stop` to end pipeline)

3. **Conditional Variables**: What determines branching?
   - Agent output fields (e.g., `{{analyzer.complexity_score}} > 5`)
   - User selections from HITL gates
   - Input characteristics

**Variable Syntax for Conditions**:
- Explicit: `{{agent_id.field}}` (preferred)
- Simple: `{{field}}` (when unique)
- Supports expressions: `contains({{last_message}}, 'APPROVED')`

**`on_false` Actions**:
- Skip and continue (default)
- Stop pipeline: `on_false: stop`
- Execute alternative: `on_false: [error_handler, cleanup]`

---

## 1.5 Human-in-the-Loop (HITL) Requirements

**Action**: Ask about HITL gate needs:

**Questions**:
1. **Approval Gates**: Where do you need human approval?
   - After which agent outputs?
   - Before which critical actions?

2. **Input Gates**: Where do you need user input?
   - File uploads (which stages?)
   - Form inputs (what information?)

3. **Selection Gates**: Where do you need user selections?
   - Choosing between options
   - Editorial direction

4. **HITL Placement**: Where in the workflow?
   - At the start (file uploads)
   - Between agents (approvals)
   - Before final output (review)

**Action**: Document each HITL gate with:
- Gate type (approval/input/selection)
- Placement (after which agent)
- Purpose (what decision/input)
- Configuration details (fields, options)

---

## 1.6 MCP Tools & External Dependencies

**Action**: Ask about external tool needs:

**Questions**:
1. **File Processing**: Do any agents need to process files?
   - Which agent extracts files FIRST? (Only ONE should extract)
   - Which agents use extracted data? (Should NOT re-extract)
   - File types expected? (PDF, DOCX, images)

2. **External Tools**: Do any agents need external tools?
   - Web search capabilities?
   - Database access?
   - Browser automation?
   - Document RAG queries?

3. **Tool Justification**: For each tool:
   - Why is this tool needed?
   - Can we use upstream agent output instead?

**🔍 CRITICAL - Path Resolution**:
- Agents using file/database MCP tools must use `project_dir` for absolute paths
- Relative paths will fail with MCP tools

### 1.6.1 Local Tools (Pipeline-Specific Tools)

**When to Use Local Tools**:
- ✅ Pipeline-specific business logic
- ✅ Database operations specific to pipeline schema
- ✅ Domain-specific computations (billing, statistics)
- ✅ Deterministic operations requiring correctness guarantees

**When NOT to Use Local Tools**:
- ❌ Generic operations (use MCP tools instead)
- ❌ Simple prompt-only logic

**If local tools needed**, document:
- Toolkit name (e.g., `rate_case`, `claims`)
- Module path (e.g., `tools.{pipeline_id}.{module_name}`)
- Tool functions with signatures
- Which agents will use each tool

---

## 1.7 Output Requirements

**Action**: Ask about output structure:

**Questions**:
1. **Final Output**: What is the final output?
   - Which agent produces it?
   - What fields should be included?
   - What format? (JSON, markdown, text)

2. **Intermediate Outputs**: Do you need intermediate outputs?
   - Which agent outputs should be captured?
   - For debugging, review, or downstream use?

3. **Output Transformations**: Do outputs need transformation?
   - Format conversions?
   - Data restructuring?

---

## 1.8 Icon & Visual Preferences

**Note**: Icons will be GENERATED (as SVG files) in Step 4. This step collects preferences.

**Questions**:
1. **Icon Style**: Do you have icon preferences?
   - Minimal, detailed, specific themes?
   - Any specific symbols for certain roles?

2. **Pipeline Icon**: What represents the overall pipeline?
   - Suggest 2-3 concepts based on use case

3. **Agent Icons**: For each agent role:
   - What visual represents their function?

**If user is unsure**: Note "Icons will be generated in Step 4 based on agent roles"

---

## 1.9 Protocol & Remote Execution Preferences

**Action**: Ask about protocol preferences:

**Questions**:
1. **Protocol Selection**: All remote agents use A2A protocol
   - Default: A2A for remote, IN-PROC for local

2. **Remote Execution**: Will any agents run remotely initially?
   - Which agents? (If any)
   - Note: Remote config added to ALL agents for future flexibility

---

## 1.10 Additional Requirements

**Questions**:
1. **Special Requirements**: Any other requirements?
   - Retry logic needed?
   - Error handling preferences?
   - Performance considerations?

2. **Existing References**: Any existing pipelines to reference?
   - Similar use cases?
   - Patterns to follow?

---

## 1.11 Requirements Summary & Review

**🔍 CHECKPOINT**: Present complete requirements summary.

### Requirements Completeness Checklist

Before presenting summary, verify:
- [ ] Pipeline name, ID, and description collected
- [ ] Agent prefix confirmed
- [ ] Workflow pattern preferences documented
- [ ] All agents identified with roles, inputs, outputs
- [ ] Agent IDs generated with prefix
- [ ] Agent ID conflict check passed
- [ ] Agent dependencies documented
- [ ] Conditional logic requirements documented (if any)
- [ ] HITL gate requirements documented (if any)
- [ ] MCP tool requirements documented (if any)
- [ ] Output requirements documented
- [ ] Icon preferences noted (or deferred to Step 4)
- [ ] Protocol preferences documented
- [ ] Additional requirements documented

### Requirements Summary Template

Present this to user:

```
## Requirements Summary

### 1. Use Case Summary
- **Pipeline Name**: {name}
- **Pipeline ID**: {id}
- **Pipeline Description**: {description}
- **Confirmed Prefix**: {prefix}

### 2. Workflow Preferences
- **Pattern Type**: {sequential/parallel/conditional/etc.}
- **Pattern Complexity**: {simple/complex/nested}
- **Execution Flow**: {description}

### 3. Agents Summary
- **Total Agents**: {count}

| Agent ID | Role | Inputs | Outputs | Dependencies |
|----------|------|--------|---------|--------------|
| {id} | {role} | {inputs} | {outputs} | {deps} |

### 4. Conditional Logic (if any)
- **Decision Points**: {list}
- **Conditional Types**: {types}
- **Variables**: {variables}

### 5. HITL Gates (if any)
| Gate ID | Type | After Agent | Purpose |
|---------|------|-------------|---------|
| {id} | {type} | {agent} | {purpose} |

### 6. MCP Tools
- **File Processing**: {which agent extracts first}
- **External Tools**: {list by agent}

### 7. Outputs
- **Final Output**: {agent, fields, format}
- **Intermediate Outputs**: {list if any}

### 8. Icons
- **Status**: {selected or deferred to Step 4}

### 9. Protocols
- **Protocol**: A2A for remote agents
- **Remote Execution**: {if any}

### 10. Additional Requirements
- {any special requirements}
```

**Action**: Present summary, then ask:
- "Does this requirements summary look complete and correct?"
- "Are there any missing requirements or changes needed?"
- "Should we proceed to workflow design with these requirements?"

**Wait for user approval before proceeding to Step 1.12 or Step 2.**

---

## 1.12 Mock Data Requirements & Script Generation

**🔍 CRITICAL CHECKPOINT**: Before designing the workflow, determine mock data needs.

**Questions**:
1. "Does this pipeline require mock data for testing?"
2. "What type of data does the pipeline need?"
   - Database records (SQLite, PostgreSQL)
   - Document files (PDFs, text files)
   - Structured data files (JSON, CSV)

**If mock data is needed**:

### 1.12.1 Identify Data Requirements

Work with user to define:

1. **Database Schema** (if applicable):
   - Tables needed
   - Table relationships
   - Fields per table
   - Sample values

2. **Document Files** (if applicable):
   - Document types needed
   - Content structure
   - Extractable fields
   - Sample count

3. **Data Paths**:
   - Database: `projects/ensemble/data/{pipeline_id}/`
   - Documents: `projects/ensemble/data/{pipeline_id}/documents/`

### 1.12.2 Generate Mock Data Script

**File Location**: `src/topaz_agent_kit/scripts/setup_{pipeline_id}_database.py`

**Key Requirements**:
- ✅ Use `resolve_script_path()` for path resolution
- ✅ Default paths relative to repository root
- ✅ Include `--reset` flag for database recreation
- ✅ Include `--db-path` and `--output-dir` arguments
- ✅ Include count arguments for mock data generation
- ✅ Create proper schema with tables and indexes
- ✅ Generate realistic mock data

### 1.12.3 Register Script in scripts.yml

**File**: `src/topaz_agent_kit/scripts/scripts.yml`

Add entry:
```yaml
- filename: "setup_{pipeline_id}_database.py"
  name: "Setup {Pipeline Name} Database"
  description: "Initializes database and generates mock data"
  category: "Setup"
  parameters:
    - name: "db-path"
      description: "Path to SQLite database file"
      type: "string"
      default: "projects/ensemble/data/{pipeline_id}/{pipeline_id}_database.db"
    - name: "reset"
      description: "Reset database"
      type: "flag"
    - name: "count"
      description: "Number of records"
      type: "integer"
      default: "10"
```

### 1.12.4 User Testing & Validation

**🔍 CHECKPOINT**: Before proceeding to Step 2:
1. User should run the mock data script
2. Verify database/files are created correctly
3. Confirm data structure matches requirements

**Testing Command**:
```bash
uv run -m scripts.setup_{pipeline_id}_database --reset
```

---

## Proceed to Step 2

After user approves requirements summary (and mock data script if applicable), proceed to:
→ `step2_design.md`

