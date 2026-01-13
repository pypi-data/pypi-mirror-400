import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from autogen_agentchat.messages import TextMessage
from .agent_adapter import create_gemini_agent, create_amazonq_agent, create_opencode_agent, create_aider_agent, create_github_copilot_agent, CLIAgent
from .config import load_config, DEFAULT_CONFIG_FILENAME
from .ui import UserInterface, ConsoleUI
from .state_manager import StateManager
from .reporting import generate_timeline_report
from .sandbox import SandboxManager

# Configuration for the workflow steps
@dataclass
class WorkflowStep:
    name: str
    role_description: str
    input_keys: List[str] 
    output_keys: List[str] 
    arg_name: str
    model_arg_name: str
    fallback_tool_arg_name: str
    fallback_model_arg_name: str
    tool: Optional[str]
    model: Optional[str]
    fallback_tool: Optional[str]
    fallback_model: Optional[str]
    max_retries: int  
    transitions: List[Dict[str, str]]
    timeout: Optional[int]
    user_review_required: bool # New field
    read_only: bool # New field

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep':
        model_arg_name = data["arg_name"].replace("-tool", "-model")
        fallback_tool_arg_name = data["arg_name"].replace("-tool", "-fallback-tool")
        fallback_model_arg_name = data["arg_name"].replace("-tool", "-fallback-model")
        
        # Backward compatibility for input_key/output_key
        input_keys = data.get("input_keys", [])
        if not input_keys and "input_key" in data:
            input_keys.append(data["input_key"])
        if "context_refs" in data: # Merge context_refs into input_keys
             for ref in data["context_refs"]:
                 if ref not in input_keys:
                     input_keys.append(ref)

        output_keys = data.get("output_keys", [])
        if not output_keys and "output_key" in data:
            output_keys.append(data["output_key"])

        return cls(
            name=data["name"],
            role_description=data["role_description"],
            input_keys=input_keys,
            output_keys=output_keys,
            arg_name=data["arg_name"],
            model_arg_name=model_arg_name,
            fallback_tool_arg_name=fallback_tool_arg_name,
            fallback_model_arg_name=fallback_model_arg_name,
            tool=data.get("tool"),
            model=data.get("model"),
            fallback_tool=data.get("fallback_tool"),
            fallback_model=data.get("fallback_model"),
            max_retries=data.get("max_retries", 0),
            transitions=data.get("transitions", []),
            timeout=data.get("timeout"),
            user_review_required=data.get("user_review_required", False),
            read_only=data.get("read_only", False)
        )

# Load full set for argparse definition only
_full_default_config_path = os.path.join(os.path.dirname(__file__), DEFAULT_CONFIG_FILENAME)
with open(_full_default_config_path, 'r') as f:
    _full_default_config = json.load(f)
ALL_POSSIBLE_STEPS = [WorkflowStep.from_dict(step_data) for step_data in _full_default_config.get("steps", [])]

TOOL_FACTORIES = {
    "gemini": create_gemini_agent,
    "amazonq": create_amazonq_agent,
    "opencode": create_opencode_agent,
    "aider": create_aider_agent,
    "github-copilot": create_github_copilot_agent,
    "gh-copilot": create_github_copilot_agent
}

class SoftwareCompanyWorkflow:
    def __init__(self, task_id: str, 
                 steps: List[WorkflowStep],
                 state_directory: str,
                 role_tool_map: Dict[str, str], 
                 role_model_map: Dict[str, str], 
                 role_fallback_tool_map: Dict[str, str],
                 role_fallback_model_map: Dict[str, str],
                 default_tool: str,
                 work_dir: Optional[str] = None,
                 max_workflow_iterations: int = 20,
                 default_timeout: Optional[int] = None,
                 ui: Optional[UserInterface] = None):
        self.task_id = task_id
        self.steps = steps
        self.state_directory = state_directory
        self.role_tool_map = role_tool_map
        self.role_model_map = role_model_map
        self.role_fallback_tool_map = role_fallback_tool_map
        self.role_fallback_model_map = role_fallback_model_map
        self.default_tool = default_tool
        self.work_dir = work_dir
        self.max_workflow_iterations = max_workflow_iterations
        self.default_timeout = default_timeout
        
        if '-' in self.task_id:
            raise ValueError(f"Task ID '{self.task_id}' cannot contain hyphens (-).")
        
        self.ui = ui or ConsoleUI()
        self.state_manager = StateManager(self.task_id, self.state_directory)
        self.state = self.state_manager.state
        self.task_dir = self.state_manager.task_dir

        # Initialize Sandbox Manager
        # We load the config again or we can assume it's passed somewhere?
        # Actually config is not passed to Workflow init. We can load it.
        # Ideally Workflow should accept config dict, but for now we load it.
        # Optimization: Pass config to __init__ if possible, but let's stick to existing pattern or load it.
        # Since we don't have the config object here, we'll load it.
        self.config = load_config() # This might be redundant if we already have it in main.py, but safe.
        self.sandbox_manager = SandboxManager(self.config, self.task_id, self.work_dir or os.getcwd())

        idx = self.state_manager.get_current_step_index()
        # Check if we have progress (index > 0 or existing context like user_request)
        if idx > 0 or self.state_manager.get_context("user_request"):
            if idx < len(self.steps):
                self.ui.print_info(f"--- Resuming task '{self.task_id}' from step {idx} ({self.steps[idx].name}) ---")
            else:
                self.ui.print_info(f"--- Task '{self.task_id}' previously completed ---")

    def _resolve_input(self, input_key: str) -> Optional[str]:
        """Resolves input data, handling file references. Returns None if key not found or explicitly null."""
        data = self.state_manager.get_context(input_key)
        if data is None: # Explicit check for None
            return None
        
        if isinstance(data, dict) and data.get("type") == "file":
            self.ui.print_input_loading(input_key, data['path'])
            return self.state_manager.read_context_from_file(data["path"])
        
        return str(data)

    async def _execute_step(self, step: WorkflowStep, agent_name: str, tool_name: str, model_name: str) -> Dict[str, str]:
        if tool_name not in TOOL_FACTORIES:
            raise ValueError(f"Unknown tool '{tool_name}'")

        factory = TOOL_FACTORIES[tool_name]
        self.ui.print_assignment(step.name, tool_name, model_name)

        # Determine timeout: Step specific > Global Default
        timeout_val = step.timeout if step.timeout is not None else self.default_timeout
        if timeout_val:
            self.ui.print_timeout(timeout_val)

        agent = factory(
            name=agent_name,
            model=model_name,
            work_dir=self.work_dir,
            timeout=timeout_val,
            read_only=step.read_only,
            sandbox_manager=self.sandbox_manager
        )
        
        # Only enable streaming for TUI, disable for Console/Non-TUI
        if not isinstance(self.ui, ConsoleUI):
            agent.set_stream_callback(lambda line, source: self.ui.print_stream_line(line, source))
        
        # Resolve Inputs
        inputs_content = ""
        for key in step.input_keys:
            val = self._resolve_input(key)
            if val is not None:
                inputs_content += f"\n\nINPUT ({key.upper().replace('_', ' ')}):\n{val}"
            # If val is None, we just skip it (it's null/missing context)

        # Construct Output Requirement instruction
        output_req = ", ".join(step.output_keys)
        json_format_hint = "You MUST return the output as a valid JSON object. The keys should be: " + output_req

        read_only_instr = ""
        if step.read_only:
             read_only_instr = "You are in READ-ONLY mode. DO NOT modify any files. DO NOT create new files. Only analyze the provided context and return the requested JSON output.\n"

        prompt = (
            f"{read_only_instr}"
            f"ROLE: {step.role_description}\n"
            f"{inputs_content}\n\n"
            f"INSTRUCTIONS: Please produce your output.\n"
            f"{json_format_hint}\n"
            f"Ensure the JSON is well-formed."
        )
        
        msg = TextMessage(content=prompt, source="workflow_engine")

        self.ui.print_tool_start(step.name, tool_name)
        try:
            result = await agent.run(task=msg)
            # Ensure we end with a newline after streaming output
            self.ui.print_newline()
        finally:
            pass
        
        if result.messages:
            raw_output = result.messages[-1].content
            # Parse JSON
            try:
                # Try to find JSON block if mixed with text
                start = raw_output.find('{')
                end = raw_output.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = raw_output[start:end]
                    parsed = json.loads(json_str)
                    return parsed
                else:
                    # Fallback: if single output key expected, treat whole text as value
                    if len(step.output_keys) == 1:
                        return {step.output_keys[0]: raw_output}
                    else:
                        raise ValueError("Could not find JSON object in response")
            except json.JSONDecodeError:
                 if len(step.output_keys) == 1:
                     return {step.output_keys[0]: raw_output}
                 raise ValueError(f"Failed to parse JSON output: {raw_output[:100]}...")
        else:
            raise RuntimeError(f"Agent {tool_name} produced no messages.")

    def revert_last_step(self):
        """Reverts the last completed step manually."""
        idx = self.state_manager.get_current_step_index()
        if idx == 0:
            self.ui.print_warning("No steps completed to revert.")
            return

        # The step to revert is at index idx - 1
        step_to_revert_idx = idx - 1
        step = self.steps[step_to_revert_idx]
        
        self.ui.print_info(f"Reverting Step {step_to_revert_idx + 1}: {step.name}")
        
        # Remove all outputs generated by this step
        for key in step.output_keys:
            output_entry = self.state_manager.get_context(key)
            if isinstance(output_entry, dict) and output_entry.get("type") == "file":
                filepath = output_entry.get("path")
                try:
                    if self.state_manager.delete_file(filepath):
                        self.ui.print_info(f"Deleted output file: {filepath}")
                except Exception as e:
                    self.ui.print_warning(f"Failed to delete {filepath}: {e}")
            
            self.state_manager.remove_context(key)
        
        # Decrement index
        self.state_manager.set_current_step_index(step_to_revert_idx)
        self.state_manager.save_state()
        self.ui.print_success(f"Step {step.name} reverted. You can now resume the task to retry this step.")

    def _determine_next_step(self, current_step: WorkflowStep, output_dict: Dict[str, str], current_index: int) -> int:
        """Determines the next step index based on transitions and output dictionary."""
        if not current_step.transitions:
            return current_index + 1
        
        self.ui.print_info(f"Checking transitions for step '{current_step.name}'...")
        for transition in current_step.transitions:
            # New field: condition_key. If not present, default to the first output key (backward compat logic)
            condition_key = transition.get("condition_key", current_step.output_keys[0] if current_step.output_keys else None)
            
            if not condition_key or condition_key not in output_dict:
                continue

            output_val = output_dict[condition_key]
            if not isinstance(output_val, str):
                output_val = str(output_val)

            condition_type = transition.get("condition_type", "contains")
            condition_value = transition.get("condition_value", "").lower()
            target_step_name = transition.get("target_step")
            
            match = False
            if condition_type == "contains":
                if condition_value in output_val.lower():
                    match = True
            
            if match:
                self.ui.print_info(f"Transition match found: Key '{condition_key}' contains '{condition_value}'. Jumping to '{target_step_name}'.")
                # Find index of target step
                for i, s in enumerate(self.steps):
                    if s.name == target_step_name:
                        return i
                self.ui.print_warning(f"Target step '{target_step_name}' not found. Continuing to next step.")
        
        return current_index + 1

    def jump_to_step(self, step_name: str):
        """Jumps to a specific step by name, verifying context prerequisites."""
        target_index = -1
        target_step = None
        
        # 1. Find the step
        for i, step in enumerate(self.steps):
            if step.name.lower() == step_name.lower():
                target_index = i
                target_step = step
                break
        
        if target_index == -1:
            available_steps = ", ".join([s.name for s in self.steps])
            raise ValueError(f"Step '{step_name}' not found. Available steps: {available_steps}")

        self.ui.print_info(f"Attempting jump to step '{target_step.name}' (Index {target_index})...")

        # 2. Check for inputs
        # Special case: First step usually takes user_request which is injected by run() if present.
        # If jumping to first step, we assume it's fine or run() will catch missing user_request.
        if target_index > 0:
            missing_inputs = []
            for key in target_step.input_keys:
                if self.state_manager.get_context(key) is None:
                    missing_inputs.append(key)
            
            if missing_inputs:
                raise ValueError(f"Cannot jump to '{target_step.name}'. Missing required context inputs: {', '.join(missing_inputs)}. Please ensure previous steps have been completed or context is manually populated.")

        # 3. Update state
        self.state_manager.set_current_step_index(target_index)
        self.state_manager.save_state()
        self.ui.print_success(f"Successfully jumped to step '{target_step.name}'. Ready to run.")

    async def run(self, user_request: str = "", single_step: bool = False):
        # Start Sandbox if enabled
        if self.sandbox_manager.is_active():
            self.ui.print_info(f"Starting sandbox environment...")
            self.sandbox_manager.start()
        
        try:
            if self.state_manager.get_context("user_request") is None and user_request:
                self.state_manager.set_context("user_request", user_request)
                self.state_manager.save_state()
            elif self.state_manager.get_context("user_request") is None:
                 self.ui.print_error("No user request provided for new task.")
                 return

            iteration_count = 0
            
            while self.state_manager.get_current_step_index() < len(self.steps):
                if iteration_count >= self.max_workflow_iterations:
                     self.ui.print_warning(f"Max workflow iterations ({self.max_workflow_iterations}) reached. Halting loop to prevent infinite cycles.")
                     generate_timeline_report(self.task_id, self.state_manager)
                     break
                iteration_count += 1

                i = self.state_manager.get_current_step_index()
                step = self.steps[i]

                tool_name = self.role_tool_map.get(step.name, self.default_tool).lower()
                model_name = self.role_model_map.get(step.name, None)

                self.ui.print_step_header(i+1, step.name, self.work_dir)

                agent_name = f"{step.name.lower().replace(' ', '_')}_{self.task_id}"

                output_dict = {}
                success = False

                start_time = datetime.now()
                used_tool = tool_name

                # Retry Loop
                max_attempts = step.max_retries + 1
                for attempt in range(max_attempts):
                    try:
                        output_dict = await self._execute_step(step, agent_name, tool_name, model_name)
                        success = True
                        break
                    except Exception as e:
                        self.ui.print_error(f"Error executing step (Attempt {attempt+1}/{max_attempts}): {e}")

                        if attempt == max_attempts - 1:
                            # Fallback logic
                            fallback_tool = self.role_fallback_tool_map.get(step.name)
                            fallback_model = self.role_fallback_model_map.get(step.name)
                            if fallback_tool:
                                self.ui.print_warning(f"--- ATTEMPTING FALLBACK: {fallback_tool} (Model: {fallback_model or 'Default'}) ---")
                                try:
                                    used_tool = fallback_tool
                                    agent_name_fb = f"{agent_name}_fallback"
                                    output_dict = await self._execute_step(step, agent_name_fb, fallback_tool, fallback_model)
                                    success = True
                                except Exception as e_fb:
                                    self.ui.print_error(f"Fallback also failed: {e_fb}. Halting.")
                                    end_time = datetime.now()
                                    duration_sec = (end_time - start_time).total_seconds()
                                    self.state_manager.add_timeline_entry({
                                        "sequence_id": len(self.state_manager.get_timeline()) + 1,
                                        "step_name": step.name,
                                        "role_tool": used_tool,
                                        "status": "FAILED",
                                        "start_time": start_time.isoformat(timespec='seconds'),
                                        "end_time": end_time.isoformat(timespec='seconds'),
                                        "duration": f"{int(duration_sec // 60):02d}:{int(duration_sec % 60):02d}"
                                    })
                                    self.state_manager.save_state()
                                    generate_timeline_report(self.task_id, self.state_manager)
                                    return
                            else:
                                self.ui.print_error("No fallback configured and retries exhausted. Halting.")
                                end_time = datetime.now()
                                duration_sec = (end_time - start_time).total_seconds()
                                self.state_manager.add_timeline_entry({
                                    "sequence_id": len(self.state_manager.get_timeline()) + 1,
                                    "step_name": step.name,
                                    "role_tool": used_tool,
                                    "status": "FAILED",
                                    "start_time": start_time.isoformat(timespec='seconds'),
                                    "end_time": end_time.isoformat(timespec='seconds'),
                                    "duration": f"{int(duration_sec // 60):02d}:{int(duration_sec % 60):02d}"
                                })
                                self.state_manager.save_state()
                                generate_timeline_report(self.task_id, self.state_manager)
                                return

                end_time = datetime.now()
                duration_sec = (end_time - start_time).total_seconds()

                self.state_manager.add_timeline_entry({
                    "sequence_id": len(self.state_manager.get_timeline()) + 1,
                    "step_name": step.name,
                    "role_tool": used_tool,
                    "status": "COMPLETED",
                    "start_time": start_time.isoformat(timespec='seconds'),
                    "end_time": end_time.isoformat(timespec='seconds'),
                    "duration": f"{int(duration_sec // 60):02d}:{int(duration_sec % 60):02d}"
                })

                if not success:
                    return

                self.ui.print_output(step.name, output_dict)

                # WRITE OUTPUTS TO FILES
                written_files = []
                for key, val in output_dict.items():
                    if isinstance(val, (dict, list)):
                        content = json.dumps(val, indent=2)
                    else:
                        content = str(val)

                    file_path = self.state_manager.write_context_to_file(i + 1, step.name, key, content)
                    written_files.append((key, file_path))
                    
                    # Update state with file reference
                    self.state_manager.set_context(key, {
                        "type": "file",
                        "path": file_path
                    })
                
                # Notify UI of written artifacts
                self.ui.print_artifacts(step.name, written_files)
                
                # Display summary of completed step outputs
                self.ui.print_step_outputs_summary(step.name, written_files)
                
                # Determine next step
                next_index = self._determine_next_step(step, output_dict, i)

                self.state_manager.set_current_step_index(next_index)
                self.state_manager.save_state()

                # USER INTERVENTION
                if step.user_review_required:
                    # Iterate through only the output keys of the current step
                    current_step_output_paths = []
                    for key in step.output_keys:
                        output_entry = self.state_manager.get_context(key)
                        if isinstance(output_entry, dict) and output_entry.get("type") == "file":
                            current_step_output_paths.append((key, output_entry["path"]))

                    self.ui.print_user_intervention(step.name, current_step_output_paths)
                    self.ui.input("Press Enter to continue...")
                    self.ui.print_info("Resuming workflow...")

                if single_step:
                    generate_timeline_report(self.task_id, self.state_manager)
                    self.ui.print_info("--- Stopping after single step execution as requested ---")
                    return

            if self.state_manager.get_current_step_index() >= len(self.steps):
                generate_timeline_report(self.task_id, self.state_manager)
                self.ui.print_success(f"=== WORKFLOW FOR TASK '{self.task_id}' COMPLETED SUCCESSFULLY ===")
        finally:
            if self.sandbox_manager.is_active():
                 self.ui.print_info(f"Stopping sandbox environment...")
                 self.sandbox_manager.stop()
