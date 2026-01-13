import asyncio
import argparse
import os
import hashlib
import sys
from datetime import datetime
from .workflow import SoftwareCompanyWorkflow, WorkflowStep, ALL_POSSIBLE_STEPS, TOOL_FACTORIES
from .config import load_config
from .utils import list_tools, list_tasks
from .rich_help import RichArgumentParser

async def run_workflow():
    parser = RichArgumentParser(description="Software Company Team Workflow")
    parser.add_argument("prompt", nargs="?", help="The feature request or task description")
    parser.add_argument("--id", help="Unique ID for the task (resumes if exists)", default=None)
    parser.add_argument("--config-file", help="Path to a custom configuration file", default=None)
    parser.add_argument("--template", help="Name of a workflow template to use (e.g., planning, development)", default=None)
    parser.add_argument("--revert", action="store_true", help="Revert the last completed step of the specified task")
    parser.add_argument("--step", action="store_true", help="Execute only the next single step and then stop")
    parser.add_argument("--run-step", help="Jump to and run a specific step by name")
    parser.add_argument("--list-tools", action="store_true", help="List available AI tools")
    parser.add_argument("--list-tasks", action="store_true", help="List previous tasks and their status")
    parser.add_argument("--tui", action="store_true", help="Run in Terminal User Interface mode (experimental)")

    # We use default config values just for parser help/defaults logic,
    # but actual values will come from loaded config.
    default_tool_name = "gemini"

    parser.add_argument("--default-tool", help="Default tool for all roles", default=None, choices=TOOL_FACTORIES.keys())
    parser.add_argument("--default-model", help="Default model for all roles", default=None)
    parser.add_argument("--work-dir", help="Working directory for the agents", default=None)

    # Add arguments for each step dynamically from the FULL set of possible steps (from package default)
    for step in ALL_POSSIBLE_STEPS:
        parser.add_argument(f"--{step.arg_name}", help=f"Tool for {step.name}", choices=TOOL_FACTORIES.keys())
        parser.add_argument(f"--{step.model_arg_name}", help=f"Model for {step.name}")
        parser.add_argument(f"--{step.fallback_tool_arg_name}", help=f"Fallback tool for {step.name}", choices=TOOL_FACTORIES.keys())
        parser.add_argument(f"--{step.fallback_model_arg_name}", help=f"Fallback model for {step.name}")

    args = parser.parse_args()

    config_path = args.config_file

    if args.template:
        template_name = args.template
        if not template_name.endswith(".json"):
            template_name += ".json"

        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(base_dir, "templates")
        potential_path = os.path.join(template_dir, template_name)

        if os.path.exists(potential_path):
            if config_path:
                print(f"Warning: --template '{args.template}' is overriding --config-file '{args.config_file}'.")
            config_path = potential_path
            print(f"Using template: {template_name}")
        else:
            print(f"Error: Template '{args.template}' not found.")
            print("Available templates:")
            if os.path.exists(template_dir):
                for f in sorted(os.listdir(template_dir)):
                    if f.endswith(".json"):
                         print(f"  - {f[:-5]}")
            else:
                print("  (Templates directory not found)")
            sys.exit(1)

    # Load Config (Priority: CLI --config-file > CWD config.json > Default)
    config_data = load_config(config_path)

    # Runtime Steps
    runtime_steps = [WorkflowStep.from_dict(step_data) for step_data in config_data.get("steps", [])]
    state_directory = config_data.get("state_directory", ".tasks") # Default to .tasks if not in config

    if args.list_tools:
        list_tools(list(TOOL_FACTORIES.keys()))
        return

    if args.list_tasks:
        list_tasks(state_directory)
        return

    max_workflow_iterations = config_data.get("max_workflow_iterations", 20)
    default_timeout = config_data.get("default_timeout", 120)

    # Resolve Defaults (CLI Arg > Config > Hardcoded 'gemini')
    default_tool = args.default_tool or config_data.get("default_tool", "gemini")
    default_model = args.default_model or config_data.get("default_model", None)
    work_dir = args.work_dir or config_data.get("default_work_dir", None)

    task_id = args.id
    prompt = args.prompt

    if work_dir:
        work_dir = os.path.abspath(work_dir)
        if not os.path.exists(work_dir):
            try:
                os.makedirs(work_dir)
                print(f"Created working directory: {work_dir}")
            except Exception as e:
                print(f"Error creating working directory {work_dir}: {e}")
                return

    if not task_id:
        if prompt:
            short_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            task_id = f"{timestamp}_{short_hash}"
            print(f"Generated Task ID: {task_id}")
        else:
            print("Error: Provide a prompt or a task ID to resume/revert.")
            return

    role_tool_map = {}
    role_model_map = {}
    role_fallback_tool_map = {}
    role_fallback_model_map = {}

    for step in runtime_steps:
        # Tool
        attr_name_tool = step.arg_name.replace("-", "_")
        specific_tool_arg = getattr(args, attr_name_tool, None)
        if specific_tool_arg: role_tool_map[step.name] = specific_tool_arg
        elif step.tool: role_tool_map[step.name] = step.tool
        else: role_tool_map[step.name] = default_tool

        # Model
        attr_name_model = step.model_arg_name.replace("-", "_")
        specific_model_arg = getattr(args, attr_name_model, None)
        if specific_model_arg: role_model_map[step.name] = specific_model_arg
        elif step.model: role_model_map[step.name] = step.model
        else: role_model_map[step.name] = default_model

        # Fallback Tool
        attr_name_fb_tool = step.fallback_tool_arg_name.replace("-", "_")
        specific_fb_tool = getattr(args, attr_name_fb_tool, None)
        if specific_fb_tool: role_fallback_tool_map[step.name] = specific_fb_tool
        elif step.fallback_tool: role_fallback_tool_map[step.name] = step.fallback_tool

        # Fallback Model
        attr_name_fb_model = step.fallback_model_arg_name.replace("-", "_")
        specific_fb_model = getattr(args, attr_name_fb_model, None)
        if specific_fb_model: role_fallback_model_map[step.name] = specific_fb_model
        elif step.fallback_model: role_fallback_model_map[step.name] = step.fallback_model

    if args.tui:
        from .tui.app import SoftwareCompanyApp

        # Factory to create workflow instance injected with TUI adapter
        def workflow_factory(ui, task_id_override=None):
            return SoftwareCompanyWorkflow(
                task_id=task_id_override or task_id,
                steps=runtime_steps,
                state_directory=state_directory,
                role_tool_map=role_tool_map,
                role_model_map=role_model_map,
                role_fallback_tool_map=role_fallback_tool_map,
                role_fallback_model_map=role_fallback_model_map,
                default_tool=default_tool,
                work_dir=work_dir,
                max_workflow_iterations=max_workflow_iterations,
                default_timeout=default_timeout,
                ui=ui
            )

        app = SoftwareCompanyApp(workflow_factory=workflow_factory, state_directory=state_directory)
        
        # We need to manually inject user_request into state if present,
        # because the app runs workflow.run() without args or with hardcoded ones.
        
        # Alternate plan: We can manually prep the state file before launching TUI if it's a new task.
        if prompt:
             from .state_manager import StateManager
             # We need to init state manager to save the prompt.
             # This is a bit duplicative but safe.
             temp_sm = StateManager(task_id, state_directory)
             if temp_sm.get_context("user_request") is None:
                 temp_sm.set_context("user_request", prompt)
                 temp_sm.save_state()

        await app.run_async()

    else:
        workflow = SoftwareCompanyWorkflow(
            task_id=task_id,
            steps=runtime_steps,
            state_directory=state_directory,
            role_tool_map=role_tool_map,
            role_model_map=role_model_map,
            role_fallback_tool_map=role_fallback_tool_map,
            role_fallback_model_map=role_fallback_model_map,
            default_tool=default_tool,
            work_dir=work_dir,
            max_workflow_iterations=max_workflow_iterations,
            default_timeout=default_timeout
        )

        try:
            if args.revert:
                workflow.revert_last_step()
            elif args.run_step:
                try:
                    workflow.jump_to_step(args.run_step)
                    await workflow.run(prompt if prompt else "", single_step=args.step)
                except ValueError as e:
                    print(f"Error: {e}")
            else:
                await workflow.run(prompt if prompt else "", single_step=args.step)
        except asyncio.CancelledError:
            workflow.ui.stop_spinner()
            workflow.ui.print_warning("Operation cancelled by user.")

def main():
    try:
        asyncio.run(run_workflow())
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
