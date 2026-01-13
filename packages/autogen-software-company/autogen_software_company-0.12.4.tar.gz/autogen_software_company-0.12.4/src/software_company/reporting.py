import os
from .state_manager import StateManager

def generate_timeline_report(task_id: str, state_manager: StateManager):
    """
    Generates a Markdown report of the task execution timeline.
    """
    timeline = state_manager.get_timeline()
    if not timeline:
        # We might want to generate an empty report or just skip.
        # But if the task completed, there should be a timeline.
        # If it crashed immediately, maybe not.
        return

    # Table Header
    content = f"# Workflow Execution Timeline - Task {task_id}\n\n"
    content += "| Sequence ID | Step Name | Role/Tool | Status | Start Time | End Time | Duration |\n"
    content += "|---|---|---|---|---|---|---|\n"

    for entry in timeline:
        seq_id = entry.get("sequence_id", "")
        step_name = entry.get("step_name", "")
        role_tool = entry.get("role_tool", "")
        status = entry.get("status", "")
        start_time = entry.get("start_time", "")
        end_time = entry.get("end_time", "")
        duration = entry.get("duration", "")

        content += f"| {seq_id} | {step_name} | {role_tool} | {status} | {start_time} | {end_time} | {duration} |\n"

    # Save to file
    report_filename = "timeline.md"
    report_path = os.path.join(state_manager.task_dir, report_filename)

    try:
        with open(report_path, "w", encoding='utf-8') as f:
            f.write(content)
        # We can assume UI is available or print to stdout.
        # Since this is a library function, maybe it shouldn't print,
        # but the requirements say "Modify... to ensure... report generation is triggered".
        # WorkflowEngine has UI, so maybe we can let WorkflowEngine log the success message.
    except Exception as e:
        print(f"Error generating timeline report: {e}")
