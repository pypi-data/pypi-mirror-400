# Autogen Software Company

This project implements an AI agent team using the [Microsoft AutoGen](https://microsoft.github.io/autogen/) framework. It simulates a **Software Company Workflow** that orchestrates multiple CLI-based agents (Product Owner, PM, Tech Lead, Dev, Reviewer, Tester) to deliver software features and bug fixes.

## Features

- **Software Company Workflow:** A full lifecycle workflow simulating a software team, from product ideation to testing.
- **CLI Agents:** Wrappers for Gemini, Amazon Q, and OpenCode CLI tools, enabling them to act as autonomous agents within the workflow.
- **Robust Persistence:** Workflows are saved to `.tasks/` directory. Each step's output is stored in a readable Markdown file, while task metadata is tracked in JSON.
- **Resumability & Reversion:** Tasks can be resumed from the last successful step. If a step produces incorrect results, it can be manually reverted and retried.
- **Step-by-Step Execution:** Execute only a single step at a time for fine-grained control and debugging.
- **User Intervention:** Configure steps to pause for user review, allowing manual editing of outputs before continuing.
- **Conditional Logic & Loops:** Workflows support conditional transitions (e.g., if the Reviewer rejects code, the workflow loops back to the Developer) based on specific output keys.
- **Configurable Timeouts:** Prevent long-running agents from hanging indefinitely by setting timeouts globally or per step.
- **Flexible Tooling:** Assign specific CLI tools to individual roles, set defaults, and configure fallback strategies for reliability.
- **Structured Data Passing:** Agents exchange data via JSON objects, allowing for multiple outputs and inputs per step.

## Prerequisites

- **Python:** >= 3.11
- **Poetry:** For dependency management.
- **CLI Tools:** Ensure the desired CLI tools (`gemini`, `q` (Amazon Q), or `opencode`) are installed, configured, and authenticated on your system.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd autogen
    ```

2.  **Install dependencies:**
    ```bash
    poetry install
    ```

## Usage

Use the installed CLI command `software-company` to manage tasks.

### Starting a New Task

To initiate a new software development task, provide a descriptive prompt. A unique task ID will be automatically generated.

```bash
# Example: Creating a new feature
poetry run software-company "Develop a user authentication module with OAuth2 support."
```

### Resuming a Task

If a task is interrupted or you wish to continue it later, use the `--id` flag with the Task ID (found in the output or `.tasks/` folder).

```bash
poetry run software-company --id <TASK_ID>
```

### Executing a Single Step

For fine-grained control or debugging, you can execute only the next pending step of a task.
```bash
# Execute only the next step for the given task ID
poetry run software-company --id <TASK_ID> --step
```
If no `--id` is provided, it runs the first step of a new task.

### Running a Specific Step

You can also jump directly to and run a specific step by name using the `--run-step` flag. This is useful for restarting a failed step, re-running a step after manually editing its inputs, or focusing on a particular part of the workflow.

```bash
# Example: Jump to and run the 'Code Reviewer' step
poetry run software-company --id <TASK_ID> --run-step "Code Reviewer"

# Combine with --step to run only the specified step and then pause
poetry run software-company --id <TASK_ID> --run-step "Developer Team" --step
```

**Important:** When jumping to a step, the workflow will validate that all `input_keys` required by that step are present in the current context. If inputs are missing, an error will be raised.

### Reverting a Step

If a specific step produces unsatisfactory results (e.g., the code is buggy or the spec is incomplete), you can manually revert the last completed step. This deletes the output file and resets the workflow pointer, allowing you to retry that step (possibly with different parameters).

```bash
poetry run software-company --id <TASK_ID> --revert
```

## Configuration

The application is highly configurable via `config.json`.

### Configuration File Loading

The system loads configuration in the following order:
1.  **Explicit Path:** `--config-file <path>`
2.  **Current Working Directory:** `config.json`
3.  **Internal Default:** `software_company/default_config.json`

### Example `config.json`

This example demonstrates how to configure tools, retries, multi-variable inputs/outputs, conditional logic, and timeouts.

```json
{
  "state_directory": ".tasks",
  "default_tool": "gemini",
  "max_workflow_iterations": 30,
  "default_timeout": 600, // Global default timeout for all steps (in seconds)
  "steps": [
    {
      "name": "Product Owner",
      "user_review_required": true, // Example: Pause here for manual review of the PRD
      "role_description": "You are an expert Product Owner. Analyze the requested feature/bug from 'user_request'. Create a comprehensive Product Requirement Document (PRD) that defines the goals, user stories, acceptance criteria, and constraints. Your output MUST be a JSON object with a single key 'prd'.",
      "input_keys": ["user_request"],
      "output_keys": ["prd"],
      "arg_name": "po-tool",
      "tool": null,
      "model": null,
      "fallback_tool": null,
      "fallback_model": null,
      "max_retries": 1,
      "timeout": 3600,
      "transitions": []
    },
    {
      "name": "Developer Team",
      "role_description": "Implement the feature...",
      "input_keys": ["tech_spec"],
      "output_keys": ["implementation"],
      "arg_name": "dev-tool",
      "tool": "amazonq",
      "max_retries": 1,
      "timeout": 3600 // Step-specific timeout, overrides default_timeout
    },
    {
      "name": "Code Reviewer",
      "role_description": "Review the code. Return JSON with 'status' (APPROVED/REJECTED) and 'review_comments'.",
      "input_keys": ["implementation"],
      "output_keys": ["status", "review_comments"],
      "arg_name": "reviewer-tool",
      "tool": "gemini",
      "max_retries": 2,
      "transitions": [
        {
          "condition_type": "contains",
          "condition_value": "REJECTED",
          "condition_key": "status",
          "target_step": "Developer Team"
        }
      ]
    }
  ]
}
```

### Key Configuration Fields

*   **`input_keys`**: (List[String]) The keys from the workflow context to pass as input to this step.
*   **`output_keys`**: (List[String]) The keys the agent is expected to return in a JSON object.
*   **`max_retries`**: (Integer) Number of times to automatically retry a step if the agent/tool fails.
*   **`timeout`**: (Integer, Optional) Timeout in seconds for this specific step. Overrides `default_timeout`.
*   **`transitions`**: (List) Defines conditional jumps.
    *   `condition_type`: Currently supports `"contains"`.
    *   `condition_value`: The string to look for (case-insensitive).
    *   `condition_key`: The specific output key to check (e.g., `"status"`).
    *   `target_step`: The exact name of the step to jump to if the condition is met.
*   **`max_workflow_iterations`**: (Integer) A safety limit to prevent infinite loops (e.g., endless Dev <-> Review cycles).
*   **`default_timeout`**: (Integer, Global) Default timeout in seconds for all steps that don't specify their own `timeout`.
*   **`user_review_required`**: (Boolean) If `true`, the workflow will pause after this step for user inspection and manual editing of the output files.

### Fallbacks

You can specify a fallback tool/model to use if the primary tool fails.

**Via CLI:**
```bash
poetry run software-company "Task..." \
  --dev-tool amazonq --dev-fallback-tool opencode
```

## Output Structure

All task data is stored in the configured `state_directory` (default: `.tasks/`).

*   **`task_{ID}.json`**: Contains task metadata, current step index, and references to output files.
*   **`task_{ID}_step_{N}_{NAME}_{KEY}.md`**: The actual content output generated by each step. This allows for easy reading and manual inspection.

## Project Structure

-   `src/software_company/`: Main package directory.
    -   `main.py`: CLI entry point (`software-company`).
    -   `workflow.py`: Workflow engine (orchestration, state, logic).
    -   `config.py`: Configuration loader.
    -   `agent_adapter.py`: AutoGen adapter for CLI wrappers.
    -   `cli/`: Tool wrappers.
-   `cli_agent/`: Standalone ReAct agent implementation.
-   `pyproject.toml`: Poetry configuration and dependency definitions.