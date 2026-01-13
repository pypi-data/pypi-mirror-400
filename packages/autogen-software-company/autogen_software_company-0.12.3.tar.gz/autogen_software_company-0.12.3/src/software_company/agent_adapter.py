import asyncio
from typing import Sequence, Type, Optional, Callable
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import BaseChatMessage, TextMessage
from autogen_core import CancellationToken

from .cli.base import BaseCLIWrapper
from .cli.gemini import GeminiCLIWrapper
from .cli.amazonq import AmazonQCLIWrapper
from .cli.opencode import OpenCodeCLIWrapper
from .cli.aider import AiderCLIWrapper
from .cli.github_copilot import GitHubCopilotCLIWrapper

class CLIAgent(BaseChatAgent):
    """
    An AutoGen agent that delegates tasks to a CLI tool wrapper.
    """
    
    def __init__(self, name: str, wrapper: BaseCLIWrapper, description: str = "A CLI-based agent.", timeout: Optional[int] = None):
        super().__init__(name, description)
        self.wrapper = wrapper
        self.timeout = timeout
        self.stream_callback: Optional[Callable[[str, str], None]] = None

    def set_stream_callback(self, callback: Callable[[str, str], None]):
        self.stream_callback = callback

    @property
    def produced_message_types(self) -> Sequence[Type[BaseChatMessage]]:
        return (TextMessage,)

    async def on_messages(
        self,
        messages: Sequence[BaseChatMessage],
        cancellation_token: CancellationToken,
    ) -> Response:
        """
        Handles incoming messages by passing the last message content to the CLI wrapper.
        """
        if not messages:
            return Response(chat_message=TextMessage(content="", source=self.name))

        # Extract last message content
        last_msg = messages[-1]
        user_input = last_msg.content if isinstance(last_msg, TextMessage) else str(last_msg)
        
        # Run CLI wrapper in a thread to avoid blocking the event loop
        # since subprocess is blocking.
        if self.timeout:
            response_text = await asyncio.to_thread(
                self.wrapper.ask,
                user_input,
                timeout=self.timeout,
                stream_callback=self.stream_callback
            )
        else:
            response_text = await asyncio.to_thread(
                self.wrapper.ask,
                user_input,
                stream_callback=self.stream_callback
            )
        
        return Response(chat_message=TextMessage(content=response_text, source=self.name))

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        """
        Resets the agent state (clears CLI session).
        """
        self.wrapper.close()

def create_gemini_agent(name: str = "gemini_agent", model: str = None, work_dir: str = None, timeout: int = None, read_only: bool = False, sandbox_manager=None) -> CLIAgent:
    wrapper = GeminiCLIWrapper(model=model, work_dir=work_dir, read_only=read_only, sandbox_manager=sandbox_manager)
    return CLIAgent(name, wrapper, description="Agent powered by Gemini CLI", timeout=timeout)

def create_amazonq_agent(name: str = "q_agent", model: str = None, work_dir: str = None, timeout: int = None, read_only: bool = False, sandbox_manager=None) -> CLIAgent:
    wrapper = AmazonQCLIWrapper(model=model, work_dir=work_dir, read_only=read_only, sandbox_manager=sandbox_manager)
    return CLIAgent(name, wrapper, description="Agent powered by Amazon Q CLI", timeout=timeout)

def create_opencode_agent(name: str = "opencode_agent", model: str = None, work_dir: str = None, timeout: int = None, read_only: bool = False, sandbox_manager=None) -> CLIAgent:
    wrapper = OpenCodeCLIWrapper(model=model, work_dir=work_dir, read_only=read_only, sandbox_manager=sandbox_manager)
    return CLIAgent(name, wrapper, description="Agent powered by OpenCode CLI", timeout=timeout)

def create_aider_agent(name: str = "aider_agent", model: str = None, work_dir: str = None, timeout: int = None, read_only: bool = False, sandbox_manager=None) -> CLIAgent:
    wrapper = AiderCLIWrapper(model=model, work_dir=work_dir, read_only=read_only, sandbox_manager=sandbox_manager)
    return CLIAgent(name, wrapper, description="Agent powered by Aider CLI", timeout=timeout)

def create_github_copilot_agent(name: str = "copilot_agent", model: str = None, work_dir: str = None, timeout: int = None, read_only: bool = False, sandbox_manager=None) -> CLIAgent:
    wrapper = GitHubCopilotCLIWrapper(model=model, work_dir=work_dir, read_only=read_only, sandbox_manager=sandbox_manager)
    return CLIAgent(name, wrapper, description="Agent powered by GitHub Copilot CLI", timeout=timeout)
