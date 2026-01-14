<div align="center">
  <img src="ui/static/assets/brand-logo.svg" alt="Project Logo" width="200"/>
</div>

# My Agent Project

Welcome to your agent project! This is a minimal, functional setup built with **Topaz Agent Kit** that includes an example pipeline and several independent agents ready to use.

## 🎯 What is Topaz Agent Kit?

**Topaz Agent Kit** is a powerful, config-driven multi-agent orchestration framework that enables you to build sophisticated AI agent workflows quickly and easily. Instead of writing complex code from scratch, you define your agents and pipelines using simple YAML configuration files.

### Key Features

- **🔄 Multi-Framework Support**: Build agents using LangGraph, CrewAI, Agno, ADK, OAK, Semantic Kernel, or MAF — all in one unified system
- **🤖 Multiple LLM Providers**: Azure OpenAI, OpenAI, Google AI, Anthropic, and Ollama (local models)
- **🧰 Rich Tool Ecosystem**: Access 50+ pre-built tools via MCP (Model Context Protocol) for document processing, web search, email, travel, and more
- **🔀 10 Execution Patterns**: Sequential, parallel, conditional, switch, loop, repeat, handoff, group chat, pipeline composition, and nested patterns
- **🌐 Remote Agents (A2A)**: Deploy agents as microservices with the Agent-to-Agent protocol
- **🎛️ Modern Web UI**: Interactive web interface with real-time agent visualization, file uploads, and session management
- **📄 Document Intelligence**: Built-in RAG (Retrieval-Augmented Generation) with document upload, analysis, and semantic search
- **🚪 Human-in-the-Loop**: Approval gates, input prompts, and selection gates for interactive workflows
- **⚡ Rapid Development**: Go from idea to working demo in hours, not weeks

### What This Basic Project Includes

This basic template provides:

- ✅ **Example Pipeline**: A simple `hello_agent` pipeline to get you started
- ✅ **Independent Agents**: Five ready-to-use agents (content_analyzer, rag_query, content_extractor, image_extractor, web_search)
- ✅ **MCP Integration**: Pre-configured MCP server for tool access
- ✅ **Web UI**: Full-featured web interface for interacting with your agents
- ✅ **Project Structure**: Organized configuration files and auto-generated code

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Branding & Customization](#branding--customization)
- [AI-Assisted Pipeline Generation](#ai-assisted-pipeline-generation)
- [Adding a New Pipeline](#adding-a-new-pipeline)
- [Agent Configuration](#agent-configuration)
  - [Model Providers](#model-providers)
  - [Remote Agents (A2A)](#remote-agents-a2a)
  - [Local Tools](#local-tools)
- [Pipeline Patterns](#pipeline-patterns)
- [Human-in-the-Loop Gates](#human-in-the-loop-gates)
- [Scripts & Data Setup](#scripts--data-setup)
- [Running Your Project](#running-your-project)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

1. **Set up your environment variables** (see [Environment Setup](#environment-setup))
2. **Start the services**:
   ```bash
   topaz-agent-kit serve fastapi --project .
   ```
3. **Open your browser** to `http://127.0.0.1:8090`

## 🔧 Environment Setup

### Step 1: Create Your `.env` File

Copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Configure Required Variables

Open `.env` and fill in the required values. The basic template uses **Azure OpenAI** by default, so you need:

```bash
# Azure OpenAI Configuration (Required)
AZURE_OPENAI_API_BASE=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_MODEL=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Note**: If you want to use a different model provider (Google AI, Ollama), you'll need to:
1. Update the `model` field in your agent YAML files
2. Add the corresponding environment variables (see `.env.example` for all options)

### Optional: Other Model Providers

If you want to use other providers, uncomment and configure the relevant sections in `.env`:

- **Google AI**: `GOOGLE_API_KEY` (for Gemini models)
- **Ollama**: `OLLAMA_BASE_URL` (defaults to `http://localhost:11434` for local models)

### Optional: MCP Toolkits

If you plan to use MCP toolkits, you'll need to configure the corresponding API keys:

- **Web Search**: `SERPER_API_KEY` (for Serper API) or `TAVILY_API_KEY` (for Tavily)
- **SEC API**: `SEC_API_KEY` (for SEC filings search)
- **Amadeus Travel**: `AMADEUS_CLIENT_ID` and `AMADEUS_CLIENT_SECRET` (for flights, hotels, activities)
- **Gmail**: `GMAIL_CREDENTIALS_PATH` (path to `client_secret.json` for email operations)
- **Browser Automation**: `BROWSERLESS_API_KEY` (for browser automation tools)

See `.env.example` for all available options.

## 📁 Project Structure

```
.
├── config/
│   ├── pipeline.yml              # Main pipeline configuration
│   ├── ui_manifest.yml           # Global UI configuration
│   ├── agents/                   # Agent configurations
│   │   ├── hello_agent.yml       # Example agent
│   │   ├── content_analyzer.yml  # Independent agents
│   │   ├── rag_query.yml
│   │   └── ...
│   ├── pipelines/                # Individual pipeline definitions
│   │   └── example.yml           # Example pipeline
│   ├── prompts/                  # Jinja2 prompt templates
│   │   ├── hello_agent.jinja
│   │   └── ...
│   └── ui_manifests/             # Pipeline-specific UI configs
│       ├── example.yml
│       └── independent_agents.yml
├── docs/                        # Documentation
│   └── workflows/
│       └── pipeline_generation/ # AI workflow reference docs
├── rules/                       # AI assistant rules
│   └── pipeline_generation.mdc  # Cursor rule for pipeline creation
├── agents/                      # Generated agent code (auto-generated)
├── services/                    # Generated service code (auto-generated)
├── ui/                          # UI assets
│   └── static/
│       └── assets/              # Logos, icons, workflow diagrams
│           ├── brand-logo.svg   # Your brand logo (replace this)
│           └── brand-icon.svg   # Your brand icon (replace this)
├── data/                        # Runtime data (created automatically)
│   ├── chat.db                  # Chat history
│   ├── chroma_db/               # Vector database
│   ├── rag_files/               # RAG document storage
│   └── user_files/              # User-uploaded files
├── .env                         # Your environment variables (create from .env.example)
└── README.md                    # This file
```

## 🎨 Branding & Customization

### Replacing the Logo

The project includes a **placeholder logo** (`ui/static/assets/brand-logo.svg`) that displays "YOUR BRAND LOGO". You should replace this with your own company/project logo.

**Option 1: Replace the placeholder file directly**

```bash
# Replace with your own logo (SVG or PNG)
cp /path/to/your-logo.svg ui/static/assets/brand-logo.svg

# Or if using PNG
cp /path/to/your-logo.png ui/static/assets/brand-logo.png
```

If using a different filename or format, update `config/ui_manifest.yml`:

```yaml
brand:
  logo: "assets/your-logo.png"      # Your main logo
  logo2: "assets/tak-logo.png"      # Secondary logo (Topaz Agent Kit)
```

**Option 2: Keep your logo with a custom name**

1. Copy your logo to `ui/static/assets/`:
   ```bash
   cp /path/to/acme-logo.png ui/static/assets/acme-logo.png
   ```

2. Update `config/ui_manifest.yml`:
   ```yaml
   brand:
     logo: "assets/acme-logo.png"
     logo2: "assets/tak-logo.png"
   ```

**Logo specifications:**
- **Dimensions**: 1050 x 750 pixels (or similar aspect ratio ~1.4:1)
- **Format**: SVG (preferred) or PNG with transparency
- **Location**: `ui/static/assets/`

### Customizing the UI

Edit `config/ui_manifest.yml` to customize:

| Setting | Location | Description |
|---------|----------|-------------|
| **Project Title** | `title` | Main heading in the UI |
| **Subtitle** | `subtitle` | Description shown below title |
| **Theme** | `appearance.default_theme` | `system`, `light`, or `dark` |
| **Accent Color** | `appearance.default_accent` | HSL color value (e.g., `"210 92% 56%"`) |
| **Chat Placeholder** | `chat.placeholder` | Input field placeholder text |
| **Footer** | `footer.text` | Footer text (`{{year}}` = current year) |

**Example customization:**

```yaml
title: "Acme AI Assistant"
subtitle: "Intelligent automation for your business"

brand:
  logo: "assets/acme-logo.png"    # Your company logo
  logo2: "assets/tak-logo.png"    # Topaz Agent Kit branding

appearance:
  default_theme: "dark"
  default_accent: "142 76% 36%"   # Green accent

footer:
  text: "© {{year}} Acme Corp — Powered by Topaz Agent Kit"
```

---

## 🤖 AI-Assisted Pipeline Generation

This project includes a structured workflow for creating new pipelines with AI assistance. If you're using **Cursor IDE** or another AI-powered editor, you can leverage the included rules and documentation for guided pipeline creation.

### What's Included

| Folder | Purpose |
|--------|---------|
| `rules/pipeline_generation.mdc` | Cursor rule that guides the AI through a 5-step workflow |
| `docs/workflows/pipeline_generation/` | Detailed reference documentation for each step |

### How to Use (Cursor IDE)

1. **Enable the Rule**: Copy `rules/pipeline_generation.mdc` to your `.cursor/rules/` folder:
   ```bash
   mkdir -p .cursor/rules
   cp rules/pipeline_generation.mdc .cursor/rules/
   ```

2. **Start the Workflow**: In Cursor chat, say:
   > "Follow the pipeline generation workflow to create a new pipeline for [your use case]"

3. **Follow the Steps**: The AI will guide you through:
   - **Step 1**: Requirements gathering (use case, agents, patterns)
   - **Step 2**: Workflow design (execution pattern, HITL gates)
   - **Step 3**: Interactive refinement (feedback and adjustments)
   - **Step 4**: File generation (configs, prompts, icons)
   - **Step 5**: Validation and testing

### Reference Documentation

The `docs/workflows/pipeline_generation/` folder contains detailed references:

| File | Contents |
|------|----------|
| `README.md` | Overview and quick start |
| `step1_requirements.md` | Requirements gathering guide |
| `step2_design.md` | Workflow design patterns |
| `step3_refinement.md` | Refinement process |
| `step4_generation.md` | File generation details |
| `step5_validation.md` | Validation checklist |
| `reference_patterns.md` | All 9 execution patterns with examples |
| `reference_hitl.md` | Human-in-the-loop gate configurations |
| `reference_jinja.md` | Jinja2 variable syntax and filters |
| `reference_icons.md` | SVG icon templates |
| `reference_troubleshooting.md` | Common issues and solutions |

### Without AI Assistance

If you prefer to create pipelines manually, see the [Adding a New Pipeline](#adding-a-new-pipeline) section below. The reference documentation in `docs/workflows/pipeline_generation/` is still useful for understanding patterns and best practices.

---

## ➕ Adding a New Pipeline

### Step 1: Create the Pipeline Configuration

Create a new file in `config/pipelines/` (e.g., `config/pipelines/my_pipeline.yml`):

```yaml
name: "My Pipeline"
description: "Description of what this pipeline does"

nodes:
  - id: my_agent
    config_file: agents/my_agent.yml

pattern:
  type: sequential
  steps:
    - node: my_agent
```

### Step 2: Create Agent Configuration

Create `config/agents/my_agent.yml`:

```yaml
id: my_agent
type: agno
model: "azure_openai"
run_mode: "local"

prompt:
  instruction:
    jinja: prompts/my_agent.jinja
  inputs:
    inline: |
      - User Query: {{user_text}}

outputs:
  final:
    selectors:
      - response
    selector_mode: "first"
    transform: |
      {{ value.response }}
```

### Step 3: Create Prompt Template

Create `config/prompts/my_agent.jinja`:

```jinja
You are a helpful assistant. Respond to user queries.

## Guidelines:
- Be clear and concise
- Provide accurate information

## Response:
Provide a helpful response to the user's query.
```

### Step 4: Register the Pipeline

Add your pipeline to `config/pipeline.yml`:

```yaml
pipelines:
  - id: example
    config_file: pipelines/example.yml
  - id: my_pipeline
    config_file: pipelines/my_pipeline.yml  # Add this line
```

### Step 5: Create UI Manifest (Optional)

Create `config/ui_manifests/my_pipeline.yml`:

```yaml
title: "My Pipeline"
subtitle: "Description of what this pipeline does"

agents:
  - id: my_agent
    title: "My Agent"
    subtitle: "Agent description"
    icon: "assets/my_agent.svg"

interaction_diagram: "assets/my_pipeline_workflow.svg"
```

And add it to `config/ui_manifest.yml`:

```yaml
pipelines:
  - id: "example"
    title: "Example Pipeline"
    ui_manifest: "ui_manifests/example.yml"
  - id: "my_pipeline"
    title: "My Pipeline"
    ui_manifest: "ui_manifests/my_pipeline.yml"  # Add this
```

### Step 6: Generate Code

After creating your configuration files, regenerate the agent and service code:

```bash
topaz-agent-kit generate agents --project .
topaz-agent-kit generate services --project .
topaz-agent-kit generate diagrams --project .
```

---

## ⚙️ Agent Configuration

### Model Providers

Topaz Agent Kit supports multiple LLM providers. Configure the `model` field in your agent YAML:

| Provider | Model Value | Required Environment Variables |
|----------|-------------|-------------------------------|
| **Azure OpenAI** | `azure_openai` | `AZURE_OPENAI_API_BASE`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT` |

**Example Agent with OpenAI:**

```yaml
id: my_agent
type: agno
model: "openai"  # Uses OPENAI_API_KEY from .env
run_mode: "local"
```

**Example with Ollama (local models):**

```yaml
id: local_agent
type: agno
model: "ollama_llama3.2:latest"  # Format: ollama_<model_name>
run_mode: "local"
```

### Remote Agents (A2A)

Agents can run locally (in-process) or remotely via the A2A (Agent-to-Agent) protocol. Remote agents run as separate services and communicate over HTTP.

**Local Agent (default):**

```yaml
id: my_agent
type: agno
model: "azure_openai"
run_mode: "local"  # Runs in the same process
```

**Remote Agent:**

```yaml
id: my_remote_agent
type: agno
model: "azure_openai"
run_mode: "remote"  # Runs as separate A2A service
```

**When to Use Remote Agents:**
- **Scaling**: Run multiple instances of compute-heavy agents
- **Isolation**: Keep agents isolated for security or resource management
- **Mixed deployments**: Some agents local, others on different machines
- **Microservices**: Deploy agents as independent services

**Starting Remote Services:**

```bash
# Generate remote services
topaz-agent-kit generate services --project .

# Start all remote agent services
topaz-agent-kit serve services --project .
```

Remote agents are automatically discovered and connected via the A2A protocol.

### Local Tools

You can add custom Python tools that agents can use. Create a `tools/` folder with your custom tool implementations.

**Step 1: Create Tool File**

Create `tools/my_tools.py`:

```python
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate the discounted price.
    
    Args:
        price: Original price
        discount_percent: Discount percentage (0-100)
    
    Returns:
        Discounted price
    """
    return price * (1 - discount_percent / 100)

def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))
```

**Step 2: Configure Agent to Use Tools**

```yaml
id: my_agent
type: agno
model: "azure_openai"
run_mode: "local"

local_tools:
  - module: tools.my_tools
    functions:
      - calculate_discount
      - validate_email

prompt:
  instruction:
    jinja: prompts/my_agent.jinja
```

The agent will automatically have access to these tools and can call them during execution.

---

## 🔀 Pipeline Patterns

Topaz Agent Kit supports multiple execution patterns. Here are the most common ones:

### 1. Sequential Pattern

Execute agents one after another in order:

```yaml
pattern:
  type: sequential
  steps:
    - node: agent1
    - node: agent2
    - node: agent3
```

**Use when**: Each agent depends on the output of the previous agent.

### 2. Parallel Pattern

Execute multiple agents simultaneously:

```yaml
pattern:
  type: sequential
  steps:
    - node: coordinator
    - type: parallel
      steps:
        - node: agent1
        - node: agent2
        - node: agent3
    - node: aggregator
```

**Use when**: Agents are independent and can run concurrently to save time.

### 3. Conditional Pattern

Execute steps based on conditions:

```yaml
pattern:
  type: sequential
  steps:
    - node: analyzer
    - type: sequential
      condition: "analyzer.needs_review == true"
      steps:
        - node: reviewer
        - gate: approve_review
    - node: finalizer
```

**Use when**: You need to conditionally execute parts of the pipeline based on previous results.

### 4. Switch Pattern

Route to different branches based on a condition:

```yaml
pattern:
  type: sequential
  steps:
    - node: classifier
    - type: switch(classifier.complexity > 5)
      cases:
        true:
          - node: complex_processor
          - node: validator
        false:
          - node: simple_processor
    - node: finalizer
```

**Use when**: You need to choose between different execution paths.

### 5. Loop Pattern

Repeat a step or pattern multiple times. There are two ways to control loops:

#### 5a. Numeric Loop (with max_iterations)

Iterate a fixed number of times or until a termination condition is met:

```yaml
pattern:
  type: sequential
  steps:
    - node: initializer
    - type: loop
      body:
        type: sequential
        steps:
          - node: processor
          - gate: continue_loop
            condition: "processor.has_more == true"
      termination:
        max_iterations: 10
        condition: "processor.has_more == false"  # Optional: early exit condition
    - node: finalizer
```

**Use when**: You need to iterate until a condition is met or a maximum number of iterations is reached.

#### 5b. List Iteration (with iterate_over)

Iterate over a list/array from a previous agent's output:

```yaml
pattern:
  type: sequential
  steps:
    - node: scanner
    - type: loop
      condition: "scanner.total_count > 0"  # Optional: skip loop if list is empty
      iterate_over: "scanner.items_list"   # Path to the list/array
      loop_item_key: "current_item"         # Context key for current item (default: "loop_item")
      termination:
        max_iterations: 100  # Optional: safety limit to prevent infinite loops
      body:
        type: sequential
        steps:
          - node: processor  # current_item is automatically available in context
          - node: validator
          - node: recorder
    - node: finalizer
```

**Key Features**:
- **`iterate_over`**: Path to the list/array to iterate over (e.g., `"scanner.pending_items"`)
- **`loop_item_key`**: Context key where the current item is injected (default: `"loop_item"`)
- **`max_iterations`**: Optional safety limit (recommended for large lists)
- **`condition`**: Optional pattern-level condition to skip the loop entirely if the list is empty

**Accessing the Current Item**:
- In agent prompts: Use `{{current_item.field_name}}` or `{{loop_item.field_name}}` (depending on `loop_item_key`)
- In agent inputs: Use `{{current_item.field_name}}` in the YAML input mapping
- The loop automatically terminates when all items in the list are processed

**Accessing Accumulated Results** (when `accumulate_results=true`, default):
- After the loop completes, downstream agents can access all loop iteration results using `{agent_id}_instances`
- Example: If `validator` runs inside a loop, use `{{validator_instances}}` in downstream agents
- The `*_instances` dictionary contains keys like `validator_0`, `validator_1`, etc., with each iteration's result
- This allows summary/aggregation agents to process all loop results, not just the last one

**Example from ECI Claims Vetter**:
```yaml
- type: loop
  condition: "eci_pending_claims_scanner.total_pending_count > 0"
  iterate_over: "eci_pending_claims_scanner.pending_claims_list"
  loop_item_key: "current_claim"
  termination:
    max_iterations: 100  # Safety limit
  body:
    type: sequential
    steps:
      - node: eci_claims_extractor  # Accesses current_claim.claim_id, current_claim.claim_form_path, etc.
      - node: eci_claim_validator    # Accesses current_claim.claim_id
```

**Use when**: You have a list of items to process (e.g., pending claims, files, emails, orders) and want to process each item through the same sequence of steps.

### 6. Repeat Pattern

Run the same agent multiple times in parallel with different inputs:

```yaml
pattern:
  type: sequential
  steps:
    - node: file_scanner
    - type: parallel
      repeat:
        node: processor
        instances: "file_scanner.file_count"
        instance_id_template: "processor_{{index}}"
        input_mapping:
          user_text: "{{file_scanner.file_paths[index]}}"
    - node: aggregator
```

**Use when**: You need to process multiple items in parallel (e.g., multiple files, multiple problems).

### 7. Handoff Pattern

Let the LLM dynamically choose which specialist agent to route to:

```yaml
pattern:
  type: sequential
  steps:
    - node: intake_agent
    - type: handoff
      name: "Specialist Routing"
      description: "Route to appropriate specialist based on query type"
      router: intake_agent  # Agent that decides the routing
      specialists:
        - id: billing_expert
          description: "Handles billing, payments, and invoice questions"
        - id: technical_support
          description: "Handles technical issues and troubleshooting"
        - id: sales_agent
          description: "Handles pricing, upgrades, and new services"
      fallback: general_support  # If no specialist matches
    - node: response_formatter
```

**Use when**: You need intelligent, LLM-driven routing based on query content rather than fixed conditions.

### 8. Group Chat Pattern

Enable multiple agents to have a collaborative discussion:

```yaml
pattern:
  type: sequential
  steps:
    - node: proposal_generator
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
      max_rounds: 4
      termination:
        condition: "contains({{last_message}}, 'REVIEW COMPLETE')"
    - node: proposal_finalizer
```

**Use when**: You need collaborative refinement where multiple expert perspectives improve the output.

### 9. Pipeline Composition

Reuse an entire existing pipeline as a step in another pipeline:

```yaml
pattern:
  type: sequential
  steps:
    - node: intake_parser
    - type: pipeline
      pipeline_id: validation_pipeline  # Reference to another pipeline
      input_mapping:
        user_text: "{{intake_parser.extracted_text}}"
    - node: response_generator
```

**Use when**: You have reusable sub-workflows that can be composed into larger pipelines.

### 10. Nested Patterns

Combine patterns for complex workflows:

```yaml
pattern:
  type: sequential
  steps:
    - node: coordinator
    - type: parallel
      steps:
        - type: sequential
          condition: "coordinator.needs_flights == true"
          steps:
            - node: flights_expert
            - gate: select_flights
        - type: sequential
          condition: "coordinator.needs_hotels == true"
          steps:
            - node: hotels_expert
            - gate: select_hotels
    - node: aggregator
```

**Use when**: You need complex workflows with conditional parallel execution.

---

## 🎯 Accessing Agent Outputs

In your patterns, you can access outputs from previous agents using Jinja2 expressions:

```yaml
pattern:
  type: sequential
  steps:
    - node: agent1
    - node: agent2
      # agent2 can access agent1's output
      # In agent2's prompt, use: {{agent1.field_name}}
```

**Example**: If `agent1` returns `{"summary": "..."}`, you can access it in `agent2`'s prompt as `{{agent1.summary}}`.

---

## 🚪 Human-in-the-Loop Gates

HITL gates pause pipeline execution for human review, input, or selection. There are three gate types:

### 1. Approval Gate

Pause for human approval before continuing:

```yaml
# In pipeline pattern
pattern:
  type: sequential
  steps:
    - node: analyzer
    - type: gate
      gate_id: analysis_review
      gate_type: approval
      title: "Review Analysis"
      description: "Review the analysis before proceeding"
    - node: processor
```

**Gate Configuration** (`config/hitl/analysis_review.jinja`):

```jinja
## Analysis Review Required

The analyzer has completed. Please review the results:

**Summary**: {{analyzer.summary}}

**Confidence**: {{analyzer.confidence}}%

Do you approve this analysis to proceed?
```

### 2. Input Gate

Pause to collect additional information from the user:

```yaml
- type: gate
  gate_id: additional_info
  gate_type: input
  title: "Additional Information Needed"
  fields:
    - name: priority
      type: select
      options: ["low", "medium", "high"]
      required: true
    - name: notes
      type: text
      required: false
```

### 3. Selection Gate

Pause to let user choose from options:

```yaml
- type: gate
  gate_id: option_selection
  gate_type: selection
  title: "Select Recommendation"
  options_source: "recommender.options"  # List from previous agent
  selection_mode: single  # or "multiple"
```

### Gate Placement

Gates can be placed:
- **After agents**: `after: agent_id`
- **Inline in pattern**: As a step in the pattern
- **Conditionally**: With `condition` field

```yaml
# Conditional gate - only shows if condition is true
- type: gate
  gate_id: fraud_review
  condition: "{{fraud_detector.score}} > 0.7"
```

---

## 📜 Scripts & Data Setup

Some pipelines require database setup or mock data. Scripts are located in the `scripts/` folder.

### Running Scripts

```bash
# List available scripts
topaz-agent-kit scripts --project .

# Run a specific script
topaz-agent-kit scripts --project . --run setup_database
```

### Common Scripts

| Script | Purpose |
|--------|---------|
| `setup_database.py` | Initialize SQLite database with schema |
| `generate_mock_data.py` | Populate database with sample data |
| `fetch_documents.py` | Download required documents |

### Creating Custom Scripts

Create a Python script in `scripts/` and register it in `scripts/scripts.yml`:

```yaml
scripts:
  - id: setup_my_data
    name: "Setup My Data"
    description: "Initialize data for my pipeline"
    script: setup_my_data.py
    requires_confirmation: true
```

---

## 🚀 Running Your Project

### Start All Services

```bash
topaz-agent-kit serve all --project .
```

This starts:
- FastAPI server (UI) on `http://127.0.0.1:8090`
- MCP server on `http://127.0.0.1:8050`

### Start Individual Services

```bash
# UI only
topaz-agent-kit serve fastapi --project .

# CLI only
topaz-agent-kit serve cli --project .

# MCP server only
topaz-agent-kit serve mcp --project .
```

### Validate Configuration

```bash
topaz-agent-kit validate .
```

## 📚 Next Steps

### Getting Started
1. **Customize the example pipeline**: Edit `config/pipelines/example.yml` and `config/agents/hello_agent.yml`
2. **Try different models**: Update the `model` field to use OpenAI, Google AI, or Ollama
3. **Use independent agents**: The project includes several independent agents (content_analyzer, rag_query, etc.) that can be used directly

### Building New Pipelines
4. **Use AI-assisted generation**: If using Cursor IDE, try the [AI-Assisted Pipeline Generation](#ai-assisted-pipeline-generation) workflow
5. **Add pipelines manually**: Follow the [Adding a New Pipeline](#adding-a-new-pipeline) guide
6. **Explore execution patterns**: Try [Pipeline Patterns](#pipeline-patterns) for complex workflows

### Advanced Features
7. **Add HITL gates**: Implement [Human-in-the-Loop Gates](#human-in-the-loop-gates) for user interaction
8. **Use remote agents**: Configure [Remote Agents (A2A)](#remote-agents-a2a) for microservices architecture
9. **Add custom tools**: Create [Local Tools](#local-tools) for agent-specific functionality
10. **Set up data**: Use [Scripts](#scripts--data-setup) to initialize databases and mock data

## 🆘 Troubleshooting

### Environment Variables Not Loading

- Make sure `.env` exists (copy from `.env.example`)
- Check that variable names match exactly (case-sensitive)
- Restart the services after changing `.env`

### Agents Not Generating

- Run `topaz-agent-kit generate agents --project .` after creating agent configs
- Check that agent YAML files are valid (use `topaz-agent-kit validate .`)
- Verify `config/pipeline.yml` references your agents correctly

### Pipeline Not Appearing in UI

- Make sure the pipeline is registered in `config/pipeline.yml`
- Create a UI manifest in `config/ui_manifests/`
- Add the pipeline to `config/ui_manifest.yml`
- Regenerate diagrams: `topaz-agent-kit generate diagrams --project .`

### Model Connection Errors

- Verify API keys are set correctly in `.env`
- Check model name matches provider format (e.g., `azure_openai`, `openai`, `ollama_llama3.2`)
- For Ollama, ensure the model is pulled locally: `ollama pull llama3.2`

### Remote Agents Not Connecting

- Ensure remote services are running: `topaz-agent-kit serve services --project .`
- Check that `run_mode: "remote"` is set in agent config
- Verify no port conflicts with other services

### HITL Gate Not Showing

- Verify `gate_id` matches the filename in `config/hitl/`
- Check `gate_type` is valid (`approval`, `input`, or `selection`)
- Ensure the gate's `condition` (if any) evaluates to true

### Variable Not Found in Template

- Check the variable name matches the agent's output field exactly
- Verify the upstream agent is in the pattern before the current agent
- Use `{{agent_id.field}}` syntax for explicit access

---

## 📋 Quick Reference: Adding a Pipeline Checklist

When adding a new pipeline, ensure you've completed these steps:

- [ ] Created pipeline config in `config/pipelines/{pipeline_id}.yml`
- [ ] Created agent configs in `config/agents/{agent_id}.yml` for each agent
- [ ] Created prompt templates in `config/prompts/{agent_id}.jinja` for each agent
- [ ] Added pipeline to `config/pipeline.yml`
- [ ] Created UI manifest in `config/ui_manifests/{pipeline_id}.yml`
- [ ] Added UI manifest reference to `config/ui_manifest.yml`
- [ ] Created HITL templates in `config/hitl/` (if using gates)
- [ ] Created icons in `ui/static/assets/` (optional)
- [ ] Ran `topaz-agent-kit generate agents --project .`
- [ ] Ran `topaz-agent-kit generate services --project .`
- [ ] Ran `topaz-agent-kit generate diagrams --project .`
- [ ] Tested with `topaz-agent-kit serve cli --project .`

---

**Happy Building! 🎉**

