# Reference: Execution Patterns

This document provides detailed reference for all 9 execution patterns supported in Topaz Agent Kit.

---

## Pattern Overview

| Pattern | Use Case | Key Config |
|---------|----------|------------|
| Sequential | Steps depend on each other | `type: sequential` |
| Parallel | Steps are independent | `type: parallel` |
| Repeat | Same agent, multiple inputs | `type: repeat` |
| Loop | Iterate until condition | `type: loop` |
| Conditional | Branch on condition | `condition:` |
| Switch | Route by field value | `type: switch` |
| Handoff | LLM chooses specialist | `type: handoff` |
| Group Chat | Collaborative conversation | `type: group_chat` |
| Pipeline Composition | Reuse entire pipeline | `type: pipeline` |

---

## 1. Sequential Pattern

**Use When**: Steps must execute in order, each depending on previous outputs.

```yaml
pattern:
  type: sequential
  name: "Sequential Processing"
  description: "Process steps in order"
  steps:
    - agent_1
    - agent_2
    - agent_3
```

**Data Flow**: `agent_1` → `agent_2` → `agent_3`

**Variable Access**: Each agent can access all upstream agent outputs.

---

## 2. Parallel Pattern

**Use When**: Steps are independent and can run simultaneously.

```yaml
pattern:
  type: parallel
  name: "Parallel Processing"
  description: "Run agents simultaneously"
  steps:
    - agent_a
    - agent_b
    - agent_c
```

**Data Flow**: All agents run at the same time.

**Variable Access**: Parallel agents CANNOT access each other's outputs.

**Combining with Sequential**:
```yaml
pattern:
  type: sequential
  steps:
    - first_agent
    - pattern:
        type: parallel
        steps:
          - parallel_agent_1
          - parallel_agent_2
    - final_agent  # Can access outputs from both parallel agents
```

---

## 3. Repeat Pattern

**Use When**: Run the same agent multiple times with different inputs.

```yaml
pattern:
  type: repeat
  name: "Process Multiple Items"
  agent: processor_agent
  instances:
    - input_key: "item_1"
      data: "{{scanner.items[0]}}"
    - input_key: "item_2"
      data: "{{scanner.items[1]}}"
```

**Or with count**:
```yaml
pattern:
  type: repeat
  agent: processor_agent
  count: "{{scanner.item_count}}"
  input_template:
    item: "{{scanner.items[{index}]}}"
```

**Accessing Results**: Use `{agent_id}_instances`:
```jinja
{% for key, result in processor_agent_instances.items() %}
  {{ result.output }}
{% endfor %}
```

---

## 4. Loop Pattern

**Use When**: Iterate over a list of items, processing each through steps.

```yaml
pattern:
  type: loop
  name: "Process Each Claim"
  description: "Iterates through pending claims"
  iterate_over: "scanner.claims_list"
  loop_item_key: "current_claim"
  accumulate_results: true
  steps:
    - claim_processor
    - claim_validator
```

**Key Properties**:
- `iterate_over`: Path to array (e.g., `scanner.items`)
- `loop_item_key`: Variable name for current item (e.g., `current_item`)
- `accumulate_results`: If true, creates `{agent_id}_instances` for all iterations

**Variable Access in Loop**:
```jinja
**Current Claim ID**: {{ current_claim.claim_id }}
**Claim Amount**: {{ current_claim.amount }}
```

---

## 5. Conditional Pattern

**Use When**: Execute step(s) only if condition is true.

```yaml
pattern:
  type: sequential
  steps:
    - analyzer
    - pattern:
        type: sequential
        condition: "{{analyzer.is_complex}} == true"
        steps:
          - deep_processor
    - finalizer
```

**With `on_false` Action**:
```yaml
condition: "{{analyzer.is_valid}} == true"
on_false: stop  # Stop pipeline if condition is false
```

**Or alternative branch**:
```yaml
condition: "{{analyzer.is_valid}} == true"
on_false:
  - error_handler
  - cleanup_agent
```

**Condition Syntax**:
- `{{agent.field}} == true`
- `{{agent.score}} > 5`
- `contains({{agent.text}}, 'keyword')`
- `{{agent.count}} >= 10`

---

## 6. Switch Pattern

**Use When**: Route to different branches based on a field value.

```yaml
pattern:
  type: switch
  name: "Complexity Router"
  switch_field: "{{classifier.complexity}}"
  cases:
    - value: "simple"
      steps:
        - simple_processor
    - value: "complex"
      steps:
        - complex_analyzer
        - complex_processor
    - value: "expert"
      steps:
        - expert_reviewer
        - expert_processor
  default:
    steps:
      - fallback_processor
```

**Key Properties**:
- `switch_field`: Variable to evaluate
- `cases`: List of value → steps mappings
- `default`: Steps if no case matches

---

## 7. Handoff Pattern

**Use When**: LLM decides which specialist agent to route to.

```yaml
pattern:
  type: handoff
  name: "Specialist Routing"
  orchestrator:
    prompt_template: "config/prompts/orchestrator.jinja"
    model:
      provider: "azure"
      model_name: "gpt-4o"
  specialists:
    - id: billing_specialist
      description: "Handles billing inquiries"
    - id: technical_specialist
      description: "Handles technical issues"
    - id: general_specialist
      description: "Handles general questions"
```

**Orchestrator Prompt**: Must instruct LLM to select specialist:
```jinja
Based on the user's request, select the most appropriate specialist:

Available specialists:
{% for specialist in specialists %}
- {{ specialist.id }}: {{ specialist.description }}
{% endfor %}

Return JSON with "selected_specialist" field.
```

---

## 8. Group Chat Pattern

**Use When**: Multiple agents collaborate in a conversation.

```yaml
pattern:
  type: group_chat
  name: "Collaborative Review"
  description: "Agents discuss and refine output"
  participants:
    - id: expert_1
      role: "Domain Expert"
    - id: critic
      role: "Quality Reviewer"
    - id: synthesizer
      role: "Final Editor"
  max_rounds: 5
  termination:
    condition: "contains({{last_message}}, 'CONSENSUS REACHED')"
```

**Key Properties**:
- `participants`: List of agents in the chat
- `max_rounds`: Maximum conversation turns
- `termination`: Condition to end early

---

## 9. Pipeline Composition

**Use When**: Reuse an entire pipeline as a step.

```yaml
pattern:
  type: sequential
  steps:
    - intake_agent
    - pattern:
        type: pipeline
        pipeline_id: "reusable_validation"
        inputs:
          document: "{{intake_agent.document}}"
    - output_agent
```

**Key Properties**:
- `pipeline_id`: ID of pipeline to execute
- `inputs`: Map of inputs to pass to sub-pipeline

---

## Nested Patterns

Patterns can be nested to create complex workflows:

```yaml
pattern:
  type: sequential
  steps:
    - scanner
    - pattern:
        type: loop
        iterate_over: "scanner.items"
        loop_item_key: "current_item"
        steps:
          - pattern:
              type: parallel
              steps:
                - validator_a
                - validator_b
          - pattern:
              type: switch
              switch_field: "{{validator_a.status}}"
              cases:
                - value: "approved"
                  steps: [approver]
                - value: "rejected"
                  steps: [rejector]
    - aggregator
```

**Best Practices for Nesting**:
- Keep nesting depth ≤ 3 levels
- Use clear naming for nested patterns
- Document complex flows with descriptions

---

## Pattern Description Variables

Pattern descriptions support Jinja2 for dynamic content:

```yaml
pattern:
  type: loop
  name: "Claims Processing"
  description: |
    ## Processing Claims
    
    | Claim ID | Amount |
    |----------|--------|
    {% for claim in scanner.claims %}
    | {{ claim.id }} | {{ claim.amount }} |
    {% endfor %}
```

**Note**: Descriptions are rendered BEFORE agents execute, so only upstream data is available.

---

## Common Pattern Combinations

### Sequential + Parallel
```yaml
pattern:
  type: sequential
  steps:
    - extractor
    - pattern:
        type: parallel
        steps: [validator_1, validator_2, validator_3]
    - aggregator
```

### Loop + Conditional
```yaml
pattern:
  type: loop
  iterate_over: "scanner.items"
  steps:
    - processor
    - pattern:
        condition: "{{processor.needs_review}} == true"
        steps: [reviewer]
```

### Sequential + Switch + HITL
```yaml
pattern:
  type: sequential
  steps:
    - classifier
    - pattern:
        type: switch
        switch_field: "{{classifier.type}}"
        cases:
          - value: "critical"
            steps:
              - critical_handler
              # HITL gate after critical handling
          - value: "normal"
            steps: [normal_handler]
```

---

## Real-World Pattern Examples

### Insurance Claims Processing (Loop + Conditional + HITL)

**Scenario**: Process a batch of insurance claims, each requiring analysis, validation, and conditional human review.

```yaml
pattern:
  type: sequential
  steps:
    # Step 1: Scan and identify all pending claims
    - node: eci_claims_scanner
    
    # Step 2: Loop through each claim
    - type: loop
      iterate_over: "eci_claims_scanner.claims_list"
      loop_item_key: "current_claim"
      accumulate_results: true
      steps:
        # 2.1: Analyze the claim
        - node: eci_claim_analyzer
        
        # 2.2: Route based on risk level
        - type: switch
          switch_field: "{{eci_claim_analyzer.risk_level}}"
          cases:
            - value: "HIGH_RISK"
              steps:
                # HITL gate for high-risk claims
                - type: gate
                  gate_id: eci_high_risk_review
                - node: eci_high_risk_handler
            - value: "MEDIUM_RISK"
              steps:
                - type: gate
                  gate_id: eci_medium_risk_review
                - node: eci_medium_risk_handler
            - value: "LOW_RISK"
              steps:
                - node: eci_auto_processor
          default:
            steps:
              - node: eci_escalation_handler
        
        # 2.3: Generate decision
        - node: eci_decision_generator
    
    # Step 3: Aggregate all results
    - node: eci_batch_summarizer
```

---

### Document Analysis (Parallel + Sequential)

**Scenario**: Analyze a document from multiple perspectives simultaneously, then synthesize.

```yaml
pattern:
  type: sequential
  steps:
    # Step 1: Parse the document
    - node: doc_parser
    
    # Step 2: Run parallel analyses
    - type: parallel
      steps:
        - node: sentiment_analyzer
        - node: topic_classifier
        - node: entity_extractor
        - node: key_points_extractor
    
    # Step 3: Synthesize all analyses
    - node: doc_synthesizer
```

**Variable Access in Synthesizer**:
```jinja
Synthesize the following analyses:

**Sentiment**: {{ sentiment_analyzer.sentiment }}
**Topics**: {{ topic_classifier.topics | join(", ") }}
**Entities**: {{ entity_extractor.entities | join(", ") }}
**Key Points**: {{ key_points_extractor.key_points | join("; ") }}
```

---

### Customer Support Routing (Handoff)

**Scenario**: Route customer inquiries to appropriate specialists based on LLM analysis.

```yaml
pattern:
  type: sequential
  steps:
    # Step 1: Understand the inquiry
    - node: inquiry_analyzer
    
    # Step 2: LLM-driven routing
    - type: handoff
      name: "Support Routing"
      orchestrator:
        prompt_template: "config/prompts/support_orchestrator.jinja"
        model:
          provider: "azure"
          model_name: "gpt-4o"
      specialists:
        - id: billing_specialist
          description: "Handles billing inquiries, payment issues, refunds"
        - id: technical_specialist
          description: "Handles product issues, bugs, feature requests"
        - id: account_specialist
          description: "Handles account access, profile changes, security"
        - id: general_specialist
          description: "Handles general questions, feedback"
    
    # Step 3: Response generation
    - node: response_generator
```

---

### Data Validation (Repeat Pattern)

**Scenario**: Validate multiple data records using the same validation agent.

```yaml
pattern:
  type: sequential
  steps:
    # Step 1: Extract records to validate
    - node: data_extractor
    
    # Step 2: Validate each record
    - type: repeat
      agent: record_validator
      instances:
        - input_key: "record_1"
          data: "{{data_extractor.records[0]}}"
        - input_key: "record_2"
          data: "{{data_extractor.records[1]}}"
        - input_key: "record_3"
          data: "{{data_extractor.records[2]}}"
    
    # Step 3: Aggregate validation results
    - node: validation_aggregator
```

**Accessing Repeat Results**:
```jinja
{% for key, result in record_validator_instances.items() %}
**{{ key }}**: {{ result.is_valid }} - {{ result.errors | default([]) | join(", ") }}
{% endfor %}
```

---

### Collaborative Review (Group Chat)

**Scenario**: Multiple expert agents discuss and refine a proposal.

```yaml
pattern:
  type: sequential
  steps:
    # Step 1: Generate initial proposal
    - node: proposal_generator
    
    # Step 2: Collaborative refinement
    - type: group_chat
      name: "Expert Review Panel"
      description: "Experts discuss and refine the proposal"
      participants:
        - id: domain_expert
          role: "Domain Expert - validates technical accuracy"
        - id: risk_assessor
          role: "Risk Assessor - identifies potential issues"
        - id: quality_reviewer
          role: "Quality Reviewer - ensures completeness"
        - id: synthesizer
          role: "Synthesizer - incorporates feedback"
      max_rounds: 4
      termination:
        condition: "contains({{last_message}}, 'REVIEW COMPLETE')"
    
    # Step 3: Finalize
    - node: proposal_finalizer
```

---

### Multi-Stage Processing with HITL (Full Pipeline)

**Scenario**: Complete pipeline with multiple stages, each with potential human intervention.

```yaml
pattern:
  type: sequential
  steps:
    # Stage 1: Intake
    - node: intake_parser
    - type: gate
      gate_id: intake_review
    
    # Stage 2: Analysis
    - type: parallel
      steps:
        - node: risk_analyzer
        - node: compliance_checker
        - node: fraud_detector
    
    # Stage 3: Decision Gate (based on analysis)
    - type: conditional
      condition: "{{fraud_detector.fraud_score}} > 0.7"
      steps:
        - type: gate
          gate_id: fraud_review
        - node: fraud_handler
      on_false:
        - node: standard_processor
    
    # Stage 4: Human Review (always)
    - type: gate
      gate_id: final_review
    
    # Stage 5: Output
    - node: response_generator
```

---

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|---------------------|
| Steps depend on each other | Sequential |
| Independent analyses | Parallel |
| Process list of similar items | Loop |
| Same agent, multiple inputs | Repeat |
| Branch on field value | Switch |
| Branch on condition | Conditional |
| LLM-driven routing | Handoff |
| Collaborative discussion | Group Chat |
| Reuse existing pipeline | Pipeline Composition |
| Complex multi-stage workflow | Nested Sequential + others |

---

## Anti-Patterns to Avoid

### ❌ Parallel when order matters
```yaml
# WRONG - These agents depend on each other
pattern:
  type: parallel
  steps:
    - data_parser      # Produces data
    - data_analyzer    # Needs parser output (FAILS)
```

### ❌ Deep nesting (>3 levels)
```yaml
# WRONG - Too complex, hard to maintain
pattern:
  type: sequential
  steps:
    - type: loop
      steps:
        - type: switch
          cases:
            - steps:
                - type: conditional
                  steps:
                    - type: loop  # ❌ 4th level - too deep
```

### ❌ Switch when condition would work
```yaml
# WRONG - Overcomplicated for simple boolean
pattern:
  type: switch
  switch_field: "{{analyzer.is_valid}}"
  cases:
    - value: "true"
      steps: [valid_handler]
    - value: "false"
      steps: [invalid_handler]

# BETTER - Use conditional
pattern:
  type: sequential
  steps:
    - analyzer
    - type: conditional
      condition: "{{analyzer.is_valid}} == true"
      steps: [valid_handler]
      on_false: [invalid_handler]
```

