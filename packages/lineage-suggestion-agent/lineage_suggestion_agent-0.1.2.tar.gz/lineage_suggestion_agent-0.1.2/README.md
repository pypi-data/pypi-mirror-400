# Lineage Suggestion Agent

An AI-powered assistant that provides friendly, context-aware guidance to users navigating a data lineage workflow.

## Description

This agent acts as a virtual assistant within a data lineage application. It takes the current status of the user's workflow as input and uses a large language model (LLM) to generate a concise, encouraging, and actionable suggestion for the next logical step.

The primary goal is to enhance the user experience by providing clear, timely guidance, reducing confusion, and helping users move smoothly through complex data lineage tasks.

## Key Features

-   **Context-Aware Guidance**: Analyzes the current workflow status to provide relevant suggestions.
-   **Friendly & Actionable**: Generates suggestions that are easy to understand and act upon.
-   **Encouraging Tone**: Uses positive language to motivate users as they make progress.
-   **Simple Integration**: Designed to be easily integrated into any application requiring guided user interaction.

## Installation

### Prerequisites

-   [**uv**](https://docs.astral.sh/uv/getting-started/installation/) – A fast Python package and environment manager.
-   [**Git**](https://git-scm.com/)

### Steps

1.  **Clone the `lineage_suggestion_agent` repository:**
    ```bash
    git clone https://github.com/stepfnAI/lineage_suggestion_agent.git
    cd lineage_suggestion_agent
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    git switch dev
    uv sync --extra dev
    source .venv/bin/activate
    ```

3.  **Clone and install the `sfn_blueprint` dependency:**
    The agent requires the `sfn_blueprint` library.
    ```bash
    cd ../
    git clone https://github.com/stepfnAI/sfn_blueprint.git
    cd sfn_blueprint
    git switch dev
    uv pip install -e .
    cd ../lineage_suggestion_agent
    ```

## Configuration

Configure the agent by creating a `.env` file in the project root or by exporting environment variables.

### Available Settings

| Environment Variable      | Description                                  | Default  |
| ------------------------- | -------------------------------------------- | -------- |
| `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` | **(Required)** Your AI provider API key.     | *None*   |
| `LINEAGE_AI_PROVIDER`     | AI provider for suggestions.                 | `openai` |
| `LINEAGE_MODEL`           | AI model for suggestions.                    | `gpt-4o` |
| `LINEAGE_TEMPERATURE`     | AI model temperature (`0.0` to `2.0`).       | `0.3`    |
| `LINEAGE_MAX_TOKENS`      | Maximum tokens for the AI response.          | `4000`   |

### Example `.env` file:

```dotenv
# .env
OPENAI_API_KEY="sk-your-openai-api-key-here"

# Optional: Use a different model
# LINEAGE_MODEL="gpt-4o-mini"
```

## Testing

To run the test suite, use the following command from the project root:

```bash
pytest
```

## Usage

### Running the Example Script

A basic usage example is provided in the `examples/` directory.

```bash
python examples/basic_usage.py
```

### Using as a Library

Integrate the `LineageSuggestionAgent` directly into your application.

```python
from lineage_suggestion_agent import LineageSuggestionAgent

# 1. Initialize the agent
agent = LineageSuggestionAgent()

# 2. Define the current workflow status as a context string
context = "Join and transformations on 'Entity_X' are complete, creating 'Table_A'. Next action: MarkAsFinal."

# 3. Call the agent to get a suggestion
suggestion, cost = agent({"context": context})

# 4. Print the results
print(f"Suggestion: {suggestion.answer}")
print(f"Cost Details: {cost}")
```

### Example Output

The agent returns a `LineageSuggestion` object and a cost dictionary.

```
Suggestion: Great job on completing the join and transformations for 'Entity_X'! Now, let's finalize this table. Please use the 'MarkAsFinal' action to complete the process.
Cost Details: {'prompt_tokens': 457, 'completion_tokens': 41, 'total_tokens': 498, 'total_cost_usd': 0.0016}
```
