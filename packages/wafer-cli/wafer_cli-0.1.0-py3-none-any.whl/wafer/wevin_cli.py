#!/usr/bin/env python3
"""Wevin CLI - Direct entry point without typer.

Supports both stdout streaming (default) and interactive TUI modes.
Now with session persistence for resume/branch capabilities.

Usage:
    # Run with YAML config
    wafer wevin --problem path/to/problem.yaml

    # Run with CLI args (quick mode)
    wafer wevin --reference ref.py --description "Optimize this" --test "m=128,k=256"

    # Resume/branch sessions
    wafer wevin --resume last
    wafer wevin --resume <session-id> --from-turn 5
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable, Coroutine
from dataclasses import replace
from pathlib import Path
from typing import Any

import trio
from wafer_core.rollouts import (
    EndpointConfig,
    EnvironmentConfig,
    FileSessionStore,
    SessionStatus,
)
from wafer_core.rollouts.agents import _message_to_session_message


def create_cli_on_chunk(
    verbose: bool = True,
    json_output: bool = False,
    failure_state: dict[str, Any] | None = None,
) -> Callable[[Any], Coroutine[Any, Any, None]]:
    """Create on_chunk handler for CLI that streams to stdout.

    Args:
        verbose: Show tool call details in human-readable format.
        json_output: Output events as newline-delimited JSON.
        failure_state: Mutable dict for tracking failures: {"consecutive": 0, "max": N, "should_stop": False}
    """
    import json

    from wafer_core.rollouts.dtypes import (
        StreamChunk,
        TextDelta,
        ToolCallEnd,
        ToolCallStart,
        ToolResultReceived,
    )

    def record_tool_result(is_error: bool) -> None:
        """Update failure tracking state."""
        if failure_state is None:
            return
        if is_error:
            failure_state["consecutive"] += 1
            max_fails = failure_state.get("max")
            if max_fails and failure_state["consecutive"] >= max_fails:
                failure_state["should_stop"] = True
        else:
            failure_state["consecutive"] = 0

    async def on_chunk(
        chunk: StreamChunk | ToolResultReceived | TextDelta | ToolCallStart | ToolCallEnd,
    ) -> None:
        """Handle streaming chunks."""
        # Track tool failures
        if isinstance(chunk, ToolResultReceived):
            record_tool_result(chunk.is_error)

        if json_output:
            # JSON output mode - emit structured events
            event: dict[str, Any] = {}

            if isinstance(chunk, TextDelta):
                event = {"type": "text_delta", "delta": chunk.delta}
            elif isinstance(chunk, ToolCallStart):
                event = {"type": "tool_call_start", "tool_name": chunk.tool_name}
            elif isinstance(chunk, ToolCallEnd):
                event = {
                    "type": "tool_call_end",
                    "tool_name": chunk.tool_call.name,
                    "args": chunk.tool_call.args,
                }
            elif isinstance(chunk, ToolResultReceived):
                event = {
                    "type": "tool_result",
                    "is_error": chunk.is_error,
                }
            elif isinstance(chunk, StreamChunk):
                event = {"type": chunk.type, "data": chunk.data}

            if event:
                print(json.dumps(event), flush=True)
            return

        # Human-readable output mode
        # Handle new granular event types (rollouts 2.x)
        if isinstance(chunk, TextDelta):
            sys.stdout.write(chunk.delta)
            sys.stdout.flush()
        elif verbose:
            if isinstance(chunk, ToolCallStart):
                print(f"\n🔧 Calling tool: {chunk.tool_name}")
            elif isinstance(chunk, ToolCallEnd):
                print(f"   {chunk.tool_call.name}({chunk.tool_call.args})")
            elif isinstance(chunk, ToolResultReceived):
                status = "✅" if not chunk.is_error else "❌"
                print(f"   {status} Tool result")

        # Handle legacy StreamChunk format (backwards compatibility)
        if isinstance(chunk, StreamChunk):
            if chunk.type == "token":
                sys.stdout.write(chunk.data["text"])
                sys.stdout.flush()
            elif verbose:
                if chunk.type == "tool_call_start":
                    name = chunk.data["name"]
                    print(f"\n🔧 Calling tool: {name}")
                elif chunk.type == "tool_call_complete":
                    name = chunk.data["name"]
                    args = chunk.data["args"]
                    print(f"   {name}({args})")
                elif chunk.type == "tool_result":
                    ok = chunk.data["ok"]
                    status = "✅" if ok else "❌"
                    print(f"   {status} Tool result")
                    # Track legacy format failures too
                    record_tool_result(not ok)

    return on_chunk


def create_stop_handler_for_tool_failures(failure_state: dict[str, Any]) -> Callable[[Any], Any]:
    """Create stop handler that checks if max consecutive tool failures reached."""
    from dataclasses import replace

    from wafer_core.rollouts.dtypes import StopReason

    def handler(state: Any) -> Any:
        if failure_state.get("should_stop"):
            return replace(state, stop=StopReason.ABORTED)
        return state

    return handler


def _get_default_targets() -> list[Any]:
    """Get default Modal target configuration."""
    from wafer_core.utils.kernel_utils.targets.config import ModalTarget

    # Load Modal credentials from ~/.modal.toml
    modal_token_id = os.environ.get("MODAL_TOKEN_ID", "")
    modal_token_secret = os.environ.get("MODAL_TOKEN_SECRET", "")

    if not modal_token_id or not modal_token_secret:
        # Try loading from ~/.modal.toml
        try:
            import sys
            if sys.version_info >= (3, 11):
                import tomllib
            else:
                import tomli as tomllib

            modal_config_path = Path.home() / ".modal.toml"
            if modal_config_path.exists():
                with open(modal_config_path, "rb") as f:
                    config = tomllib.load(f)
                # Use first available profile
                for profile_name, profile in config.items():
                    if isinstance(profile, dict) and "token_id" in profile:
                        modal_token_id = profile["token_id"]
                        modal_token_secret = profile["token_secret"]
                        break
        except Exception:
            pass

    if not modal_token_id or not modal_token_secret:
        print("Warning: Modal credentials not found. Set MODAL_TOKEN_ID/MODAL_TOKEN_SECRET or run 'modal token new'", file=sys.stderr)
        return []

    return [
        ModalTarget(
            name="modal-b200",
            modal_app_name="kernel-eval-b200",
            modal_token_id=modal_token_id,
            modal_token_secret=modal_token_secret,
            modal_workspace=None,
            gpu_type="B200",
            compute_capability="10.0",
            timeout_seconds=600,
            cpu_count=4,
            memory_gb=16,
        )
    ]


def _load_problem_config(
    problem_path: str | None = None,
    reference: str | None = None,
    description: str | None = None,
    tests: list[str] | None = None,
    benchmarks: list[str] | None = None,
    model: str | None = None,
    max_turns: int | None = None,
    speedup_target: float | None = None,
) -> tuple[Any, str | None]:
    """Load problem config from YAML or CLI args.

    Returns:
        (ProblemConfig, None) on success, (None, error) on failure
    """
    from wafer_core.problem_config import (
        create_problem_config_from_cli,
        load_problem_config,
        parse_test_case,
    )

    if problem_path:
        # Load from YAML
        config, err = load_problem_config(problem_path)
        if err:
            return None, err

        # Apply CLI overrides
        if model:
            config = replace(config, model=model)
        if max_turns:
            config = replace(config, max_turns=max_turns)
        if speedup_target:
            config = replace(config, speedup_target=speedup_target)

        return config, None

    elif reference:
        # Build from CLI args
        if not description:
            description = "Optimize this kernel implementation."

        # Parse test cases
        parsed_tests = []
        for test_str in tests or []:
            test_case, err = parse_test_case(test_str)
            if err:
                return None, f"Invalid test case '{test_str}': {err}"
            parsed_tests.append(test_case)

        if not parsed_tests:
            return None, "At least one --test is required"

        # Parse benchmark cases
        parsed_benchmarks = []
        for bench_str in benchmarks or []:
            bench_case, err = parse_test_case(bench_str)
            if err:
                return None, f"Invalid benchmark '{bench_str}': {err}"
            parsed_benchmarks.append(bench_case)

        kwargs = {}
        if model:
            kwargs["model"] = model
        if max_turns:
            kwargs["max_turns"] = max_turns
        if speedup_target:
            kwargs["speedup_target"] = speedup_target

        return create_problem_config_from_cli(
            reference=reference,
            description=description,
            tests=parsed_tests,
            benchmarks=parsed_benchmarks or None,
            **kwargs,
        )

    else:
        return None, "Either --problem or --reference is required"


def _create_environment_from_config(
    problem_config: Any,
    enabled_tools: list[str] | None = None,
    allow_spawn: bool = False,
) -> tuple[Any, Any, Any]:
    """Create environment, endpoint, and trajectory from ProblemConfig.

    Args:
        problem_config: Problem configuration.
        enabled_tools: List of tool names to enable (None = all tools).
        allow_spawn: Allow wafer tool to spawn sub-wevin agents.

    Returns:
        (environment, endpoint, initial_trajectory)
    """
    from wafer_core.rollouts.dtypes import Endpoint, Message, Trajectory
    from wafer_core import CodingEnvironment

    # Determine API routing: Wafer proxy (preferred) or direct Anthropic (fallback)
    wafer_token = os.environ.get("WAFER_AUTH_TOKEN", "")
    wafer_api_url = os.environ.get("WAFER_API_URL", "https://www.api.wafer.ai")

    if wafer_token:
        # Use Wafer proxy - token becomes the API key for auth
        # Backend will inject the real Anthropic key server-side
        api_base = f"{wafer_api_url}/v1/anthropic"
        api_key = wafer_token
    else:
        # Direct Anthropic (fallback for local dev without auth)
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("Error: WAFER_AUTH_TOKEN or ANTHROPIC_API_KEY required", file=sys.stderr)
            print("  - Set WAFER_AUTH_TOKEN for production use (via Wafer proxy)", file=sys.stderr)
            print("  - Set ANTHROPIC_API_KEY for local development", file=sys.stderr)
            sys.exit(1)
        api_base = "https://api.anthropic.com"

    # Create endpoint
    endpoint = Endpoint(
        provider="anthropic",
        model=problem_config.model,
        api_base=api_base,
        api_key=api_key,
        temperature=problem_config.temperature,
        max_tokens=problem_config.max_tokens,
        max_retries=3,
        timeout=120.0,
    )

    # Create coding environment with tool filtering
    environment = CodingEnvironment(
        working_dir=Path.cwd(),
        enabled_tools=enabled_tools,
        allow_spawn=allow_spawn,
    )

    # Create initial messages
    initial_messages = [
        Message(role="system", content=problem_config.get_system_prompt()),
        Message(role="user", content=problem_config.get_user_message()),
    ]
    initial_trajectory = Trajectory(messages=initial_messages)

    return environment, endpoint, initial_trajectory


async def run_wevin_stdout(
    session_store: FileSessionStore,
    problem_config: Any,
    resume_session_id: str | None = None,
    from_turn: int | None = None,
    enabled_tools: list[str] | None = None,
    allow_spawn: bool = False,
    max_tool_fails: int | None = None,
    json_output: bool = False,
) -> None:
    """Run Wevin agent with stdout streaming and session persistence.

    Args:
        session_store: Session store for persistence.
        problem_config: Problem configuration.
        resume_session_id: Session ID to resume from.
        from_turn: Turn number to branch from.
        enabled_tools: List of tool names to enable (None = all tools).
        allow_spawn: Allow bash tool to spawn sub-wevin agents.
        max_tool_fails: Exit after N consecutive tool failures.
        json_output: Output in JSON format.
    """
    from wafer_core.rollouts.agents import (
        compose_handlers,
        handle_stop_max_turns,
        handle_stop_on_empty_message,
        run_agent,
    )
    from wafer_core.rollouts.dtypes import Actor, AgentState, RunConfig, StopReason

    environment, endpoint, initial_trajectory = _create_environment_from_config(
        problem_config,
        enabled_tools=enabled_tools,
        allow_spawn=allow_spawn,
    )
    sample_data = problem_config.to_sample_data()

    # Handle resume vs new session
    if resume_session_id:
        # Load existing session
        parent_session, err = await session_store.get(resume_session_id)
        if err or parent_session is None:
            print(f"Error loading session: {err}", file=sys.stderr)
            sys.exit(1)

        # Determine branch point
        branch_point = from_turn if from_turn is not None else len(parent_session.messages)

        # Create child session
        session = await session_store.create(
            endpoint=parent_session.endpoint,
            environment=parent_session.environment,
            parent_id=resume_session_id,
            branch_point=branch_point,
            tags=parent_session.tags,
        )

        # Copy messages up to branch point
        for msg in parent_session.messages[:branch_point]:
            await session_store.append_message(session.session_id, msg)

        # Restore environment state if available
        if parent_session.environment_state:
            from wafer_core import CodingEnvironment

            environment = await CodingEnvironment.deserialize(
                parent_session.environment_state
            )
            print("   Restored environment state from session")
        else:
            print("   Warning: No saved environment state, using fresh environment")

        # Rebuild trajectory from session messages
        # Session messages need to be converted to rollouts Message objects
        from wafer_core.rollouts.dtypes import Message as RolloutsMessage
        from wafer_core.rollouts.dtypes import TextContent, ToolCallContent, Trajectory

        def convert_content(content: str | list | None) -> str | list:
            """Convert stored content to rollouts Message content format.
            
            Content can be:
            - A string (simple text)
            - A list of content blocks (text, toolCall, etc.)
            
            Returns content in the format expected by rollouts Message.
            """
            if content is None:
                return ""
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                # Convert content blocks to proper types
                result = []
                for block in content:
                    if isinstance(block, dict):
                        block_type = block.get("type")
                        if block_type == "text":
                            result.append(TextContent(
                                type="text",
                                text=block.get("text", ""),
                                text_signature=block.get("text_signature"),
                            ))
                        elif block_type == "toolCall":
                            result.append(ToolCallContent(
                                type="toolCall",
                                id=block.get("id", ""),
                                name=block.get("name", ""),
                                arguments=block.get("arguments", {}),
                                thought_signature=block.get("thought_signature"),
                            ))
                    elif isinstance(block, str):
                        result.append(TextContent(type="text", text=block, text_signature=None))
                return result if result else ""
            return str(content)

        # Convert SessionMessage objects to Message objects
        rollouts_messages = []
        for sm in parent_session.messages[:branch_point]:
            # Convert content to proper format
            converted_content = convert_content(sm.content)
            
            if hasattr(sm, 'tool_call_id') and sm.tool_call_id:
                # Tool result message - content should be string
                tool_content = sm.content
                if isinstance(tool_content, list):
                    # Extract text from list if needed
                    texts = [b.get("text", "") if isinstance(b, dict) else str(b) for b in tool_content]
                    tool_content = "".join(texts)
                rollouts_messages.append(RolloutsMessage(
                    role=sm.role,
                    content=tool_content or "",
                    tool_call_id=sm.tool_call_id,
                ))
            else:
                # User/system/assistant message
                rollouts_messages.append(RolloutsMessage(
                    role=sm.role,
                    content=converted_content,
                ))

        # Add new user message if provided
        new_user_msg = problem_config.get_user_message()
        if new_user_msg:
            rollouts_messages.append(RolloutsMessage(role="user", content=new_user_msg))

        initial_trajectory = Trajectory(messages=rollouts_messages)

        print(f"📂 Resuming from session {resume_session_id}")
        if from_turn is not None:
            print(f"   Branching from turn {from_turn}")
        print(f"   New session: {session.session_id}")

    else:
        # Create new session
        endpoint_config = EndpointConfig(
            model=endpoint.model,
            provider=endpoint.provider,
            temperature=endpoint.temperature,
        )
        environment_config = EnvironmentConfig(
            type="coding",
            config={
                "enabled_tools": enabled_tools,
                "allow_spawn": allow_spawn,
            },
        )

        session = await session_store.create(
            endpoint=endpoint_config,
            environment=environment_config,
            tags={"problem": sample_data.get("problem_id", "unknown")},
        )

        # Persist initial messages (convert Message to SessionMessage)
        for msg in initial_trajectory.messages:
            await session_store.append_message(session.session_id, _message_to_session_message(msg))

        print(f"📝 New session: {session.session_id}")

    # Create actor and initial state
    actor = Actor(
        endpoint=endpoint,
        trajectory=initial_trajectory,
        tools=[],  # Environment provides tools
    )

    state = AgentState(
        actor=actor,
        environment=environment,
    )

    # Track initial message count for persistence
    initial_message_count = len(initial_trajectory.messages)

    # Log enabled tools
    if enabled_tools:
        if not json_output:
            print(f"   Tools: {', '.join(enabled_tools)}")
    else:
        if not json_output:
            print("   Tools: all (read, write, edit, bash, wafer)")

    # Create failure state dict for max_tool_fails tracking
    failure_state = {"consecutive": 0, "max": max_tool_fails, "should_stop": False} if max_tool_fails else None

    # Build run config
    cli_on_chunk = create_cli_on_chunk(
        verbose=not json_output,
        json_output=json_output,
        failure_state=failure_state,
    )

    # Build stop handlers
    stop_handlers = [
        handle_stop_max_turns(problem_config.max_turns),
        handle_stop_on_empty_message(),
    ]
    if failure_state:
        stop_handlers.append(create_stop_handler_for_tool_failures(failure_state))

    stop_handler = compose_handlers(stop_handlers)

    # Track the latest state in case run_agent throws an exception
    latest_state_holder: dict[str, AgentState] = {"state": state}
    
    def on_step_start(s: AgentState) -> AgentState:
        latest_state_holder["state"] = s
        return s

    run_config = RunConfig(
        on_chunk=cli_on_chunk,
        handle_stop=stop_handler,
        on_step_start=on_step_start,
    )

    # Run agent
    if not json_output:
        print("─" * 80)
        print(f"🚀 Starting Wevin agent (problem: {problem_config.problem_id})")
        print(f"   Model: {problem_config.model}")
        print(f"   Max turns: {problem_config.max_turns}")
        if hasattr(problem_config, "speedup_target"):
            print(f"   Speedup target: {problem_config.speedup_target}x")
        print("─" * 80 + "\n")
    else:
        import json
        print(json.dumps({
            "type": "session_start",
            "session_id": session.session_id,
            "problem_id": problem_config.problem_id,
            "model": problem_config.model,
            "max_turns": problem_config.max_turns,
        }), flush=True)

    try:
        states = await run_agent(state, run_config)
        final_state = states[-1]
    except ValueError as e:
        # Handle "aggregate_anthropic_stream produced empty message" error
        # This happens when the model returns an empty final turn (end_turn with no content)
        # The streaming already completed successfully, so we can safely ignore this
        if "empty message" in str(e).lower():
            # Use the latest state captured by on_step_start
            final_state = latest_state_holder["state"]
        else:
            raise

    if not json_output:
        print("\n" + "─" * 80)

    # Persist new messages (now using rollouts Message directly)
    # Skip empty assistant messages (model signaling "done" with no content)
    final_messages = final_state.actor.trajectory.messages
    for msg in final_messages[initial_message_count:]:
        if msg.role == "assistant" and not msg.content:
            continue  # Don't persist empty "done" signals
        await session_store.append_message(session.session_id, _message_to_session_message(msg))

    # Determine final status
    if final_state.stop == StopReason.TASK_COMPLETED:
        status = SessionStatus.COMPLETED
    elif final_state.stop == StopReason.ABORTED:
        status = SessionStatus.ABORTED
    elif final_state.stop == StopReason.MAX_TURNS:
        status = SessionStatus.TRUNCATED
    else:
        status = SessionStatus.PENDING

    # Save environment state and update status
    env_state = None
    if final_state.environment is not None:
        env_state = await final_state.environment.serialize()

    await session_store.update(
        session.session_id,
        status=status,
        environment_state=env_state,
    )

    if not json_output:
        print("✅ Session complete")
        print(f"   Session ID: {session.session_id}")
        print(f"   Turns: {final_state.turn_idx}")
        if final_state.stop:
            stop_val = (
                final_state.stop.value if hasattr(final_state.stop, "value") else final_state.stop
            )
            print(f"   Stop reason: {stop_val}")
    else:
        import json
        stop_val = None
        if final_state.stop:
            stop_val = final_state.stop.value if hasattr(final_state.stop, "value") else str(final_state.stop)
        print(json.dumps({
            "type": "session_end",
            "session_id": session.session_id,
            "status": status.value if hasattr(status, "value") else str(status),
            "turns": final_state.turn_idx,
            "stop_reason": stop_val,
        }), flush=True)

    if not json_output:
        print(f"\n   Resume with: wafer wevin --resume {session.session_id}")


async def run_wevin_tui(problem_config: Any) -> None:
    """Run Wevin agent with interactive TUI."""
    from wafer_core.rollouts.frontends.tui.interactive_agent import run_interactive_agent

    environment, endpoint, initial_trajectory = _create_environment_from_config(problem_config)

    await run_interactive_agent(
        initial_trajectory,
        endpoint,
        environment,
        max_turns=problem_config.max_turns,
        session_store=None,
        session_id=None,
        theme_name="minimal",
        debug=False,
        debug_layout=False,
    )


async def list_sessions_async(session_store: FileSessionStore) -> None:
    """List recent sessions."""
    sessions = await session_store.list(limit=10)
    if not sessions:
        print("No sessions found")
        return

    print("Recent sessions:")
    for s in sessions:
        status_emoji = {
            SessionStatus.PENDING: "⏳",
            SessionStatus.COMPLETED: "✅",
            SessionStatus.TRUNCATED: "⚠️",
            SessionStatus.ABORTED: "❌",
        }.get(s.status, "❓")

        msg_count = len(s.messages) if s.messages else "?"
        print(f"  {status_emoji} {s.session_id}  {s.created_at[:19]}  ({msg_count} msgs)")

        # Show parent if this is a branch
        if s.parent_id:
            print(f"      └── branched from {s.parent_id}")


def _create_simple_config(
    prompt: str,
    model: str | None = None,
    max_turns: int | None = None,
) -> Any:
    """Create a simple config for chat mode (no kernel optimization)."""
    from dataclasses import dataclass

    @dataclass
    class SimpleChatConfig:
        """Minimal config for chat mode."""
        prompt: str
        model: str = "claude-sonnet-4-5-20250929"
        temperature: float = 0.2
        max_tokens: int = 8192
        max_turns: int = 10
        problem_id: str = "chat"

        def get_system_prompt(self) -> str:
            return """You are Wevin, a GPU programming assistant specializing in CUDA, Triton, and CuTeDSL.

You have these tools available:
- **read**: Read file contents
- **write**: Create or overwrite files
- **edit**: Make surgical text replacements in files
- **bash**: Run shell commands
- **wafer**: Run wafer subcommands (ask-docs, ncu-analyze, remote-run, push, evaluate)

Help the user with GPU programming questions, kernel optimization, and code development."""

        def get_user_message(self) -> str:
            return self.prompt

        def to_sample_data(self) -> dict:
            return {"problem_id": self.problem_id, "prompt": self.prompt}

    return SimpleChatConfig(
        prompt=prompt,
        model=model or "claude-sonnet-4-5-20250929",
        max_turns=max_turns or 10,
    )


def main(
    prompt: str | None = None,
    interactive: bool = False,
    problem: str | None = None,
    reference: str | None = None,
    description: str | None = None,
    tests: list[str] | None = None,
    benchmarks: list[str] | None = None,
    model: str | None = None,
    max_turns: int | None = None,
    speedup_target: float | None = None,
    resume: str | None = None,
    from_turn: int | None = None,
    list_sessions: bool = False,
    tools: list[str] | None = None,
    allow_spawn: bool = False,
    max_tool_fails: int | None = None,
    json_output: bool = False,
) -> None:
    """Launch Wevin.

    Args:
        prompt: User prompt for one-shot mode.
        interactive: If True, use interactive TUI. If False, use stdout streaming.
        problem: [Legacy] Path to problem YAML config file.
        reference: [Legacy] Path to reference kernel file.
        description: [Legacy] Problem description.
        tests: [Legacy] List of test case strings.
        benchmarks: [Legacy] List of benchmark case strings.
        model: Model override (default: claude-sonnet-4-5-20250929).
        max_turns: Max turns override (default: 10).
        speedup_target: [Legacy] Speedup target override.
        resume: Session ID to resume (or 'last' for most recent).
        from_turn: Turn number to branch from (default: resume from end).
        list_sessions: If True, list sessions and exit.
        tools: List of tool names to enable (e.g., ['read', 'write', 'bash']).
        allow_spawn: Allow wafer tool to spawn sub-wevin agents.
        max_tool_fails: Exit after N consecutive tool failures.
        json_output: Output in JSON format for programmatic integration.
    """
    session_store = FileSessionStore()

    async def async_main() -> None:
        nonlocal resume

        # Handle list sessions
        if list_sessions:
            await list_sessions_async(session_store)
            return

        # Handle 'last' as resume value
        if resume == "last":
            latest, err = await session_store.get_latest()
            if err or latest is None:
                print(f"No sessions found: {err}", file=sys.stderr)
                sys.exit(1)
            resume = latest.session_id
            if not json_output:
                print(f"Resuming session: {resume}")

        # Determine config based on mode
        config: Any = None

        # Legacy kernel optimization mode
        if problem or reference:
            config, err = _load_problem_config(
                problem_path=problem,
                reference=reference,
                description=description,
                tests=tests,
                benchmarks=benchmarks,
                model=model,
                max_turns=max_turns,
                speedup_target=speedup_target,
            )
            if err:
                print(f"Error: {err}", file=sys.stderr)
                sys.exit(1)
        # Chat mode
        elif prompt:
            config = _create_simple_config(
                prompt=prompt,
                model=model,
                max_turns=max_turns,
            )
        # Interactive mode without prompt
        elif interactive:
            # TUI will handle prompting
            config = _create_simple_config(
                prompt="",  # TUI will get prompt from user
                model=model,
                max_turns=max_turns,
            )
        # Resume mode
        elif resume:
            # When resuming, we don't need a prompt - just continue the session
            # Create a minimal config, the resume logic will load the session
            config = _create_simple_config(
                prompt="",
                model=model,
                max_turns=max_turns,
            )
        else:
            print("Error: No prompt provided", file=sys.stderr)
            print("\nUsage:")
            print('  wafer wevin "What is TMEM?"')
            print("  wafer wevin -i  # interactive mode")
            print("  wafer wevin --resume last")
            sys.exit(1)

        if interactive:
            if resume:
                print("Note: TUI mode doesn't support resume yet", file=sys.stderr)
            if tools or json_output:
                print("Note: TUI mode doesn't support --tools or --json flags yet", file=sys.stderr)
            await run_wevin_tui(config)
        else:
            await run_wevin_stdout(
                session_store=session_store,
                problem_config=config,
                resume_session_id=resume,
                from_turn=from_turn,
                enabled_tools=tools,
                allow_spawn=allow_spawn,
                max_tool_fails=max_tool_fails,
                json_output=json_output,
            )

    trio.run(async_main)


if __name__ == "__main__":
    main()
