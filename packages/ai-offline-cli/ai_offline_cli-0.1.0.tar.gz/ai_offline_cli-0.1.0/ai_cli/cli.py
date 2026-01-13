"""Command-line interface for AI CLI."""

import argparse
import asyncio
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple, List

from .client import OllamaClient
from .agent import AgentOrchestrator
from .prompt_manager import PromptManager
from .models import create_standard_registry


def extract_filename_from_query(query: str) -> Optional[str]:
    """Extract filename from query like 'Напиши HELLO-WORLD.md' or 'create config.py'."""
    # Patterns to match filenames with extensions
    patterns = [
        r'["\']?([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)["\']?',  # filename.ext
        r'файл\s+([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)',       # файл filename.ext
        r'create\s+([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)',     # create filename.ext
        r'write\s+([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)',      # write filename.ext
    ]

    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            return match.group(1)

    return None


def extract_code_blocks(text: str) -> str:
    """Extract code blocks from markdown-formatted text."""
    # Remove markdown code fences and keep only content
    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', text, re.DOTALL)

    if code_blocks:
        # If there are code blocks, join them
        return '\n\n'.join(code_blocks)

    # If no code blocks, return original text
    return text


def extract_shell_commands(text: str) -> List[str]:
    """Extract shell commands from markdown code blocks."""
    commands = []

    # Find code blocks marked as bash, sh, shell, or console
    patterns = [
        r'```(?:bash|sh|shell|console)\n(.*?)```',
        r'```\n(\$.*?)```',  # Commands starting with $
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            # Split by newlines and process each line
            for line in match.strip().split('\n'):
                line = line.strip()
                # Remove $ or # prefix
                if line.startswith('$ '):
                    line = line[2:]
                elif line.startswith('# ') and not line.startswith('#!/'):
                    continue  # Skip comments

                if line and not line.startswith('#'):
                    commands.append(line)

    return commands


def is_safe_command(command: str) -> Tuple[bool, str]:
    """Check if command is safe to execute with user confirmation."""
    dangerous_patterns = [
        r'\brm\s+-rf\s+/',  # rm -rf /
        r'\brm\s+-rf\s+\*',  # rm -rf *
        r':\(\)\{.*\};',  # Fork bomb
        r'>\s*/dev/sd[a-z]',  # Write to disk
        r'dd\s+if=.*of=/dev',  # dd to device
        r'mkfs\.',  # Format filesystem
        r'sudo\s+rm',  # sudo rm
        r'curl.*\|\s*(?:bash|sh)',  # Pipe curl to shell
        r'wget.*\|\s*(?:bash|sh)',  # Pipe wget to shell
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Potentially dangerous command detected: {pattern}"

    return True, "OK"


def confirm_command(command: str, auto_yes: bool = False, copy_to_clip: bool = True) -> bool:
    """Ask user to confirm command execution."""
    # Copy to clipboard by default
    if copy_to_clip:
        if copy_to_clipboard(command):
            print(f"\n📋 Command copied to clipboard!")
            print(f"   Paste in another terminal: Cmd+V")

    if auto_yes:
        return True

    print(f"\n🔧 Command to execute:")
    print(f"   {command}")
    print()

    while True:
        response = input("Execute here? [y/n/q] (y=yes, n=no/paste elsewhere, q=quit): ").strip().lower()

        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            print("⊘ Skipped - use clipboard to paste in another terminal")
            return False
        elif response in ['q', 'quit']:
            print("Execution cancelled.")
            sys.exit(0)
        else:
            print("Please enter 'y', 'n', or 'q'")


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard (macOS)."""
    try:
        subprocess.run(
            ['pbcopy'],
            input=text.encode('utf-8'),
            check=True,
            timeout=1
        )
        return True
    except Exception:
        return False


def execute_command(command: str, verbose: bool = True) -> Tuple[bool, str, str]:
    """Execute shell command and return result."""
    try:
        if verbose:
            print(f"\n▶ Executing: {command}")
            print("-" * 60)

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        success = result.returncode == 0

        if verbose:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"stderr: {result.stderr}", file=sys.stderr)

            if success:
                print("✓ Command completed successfully")
            else:
                print(f"✗ Command failed with exit code {result.returncode}")
            print("-" * 60)

        return success, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        error_msg = "Command timed out after 30 seconds"
        if verbose:
            print(f"✗ {error_msg}")
        return False, "", error_msg
    except Exception as e:
        error_msg = str(e)
        if verbose:
            print(f"✗ Error executing command: {error_msg}")
        return False, "", error_msg


class CLI:
    """Simple CLI for interacting with the AI system."""

    def __init__(self):
        self.client: Optional[OllamaClient] = None
        self.orchestrator: Optional[AgentOrchestrator] = None
        self.prompt_manager = PromptManager()

    async def initialize(self, ollama_url: str = "http://localhost:11434"):
        """Initialize the CLI."""
        print("🔌 Connecting to Ollama...", end=" ", flush=True)
        self.client = OllamaClient(base_url=ollama_url)
        await self.client.__aenter__()
        self.orchestrator = AgentOrchestrator(self.client, self.prompt_manager)
        print("✓")
        print()

    async def shutdown(self):
        """Shutdown the CLI."""
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def interactive_mode(self, enable_execute: bool = False, enable_copy: bool = True):
        """Run interactive chat mode."""
        print("AI CLI - Interactive Mode")
        print("Type 'exit' to quit, 'help' for commands")
        if enable_execute:
            print("⚡ Command execution is ENABLED")
        if enable_copy:
            print("📋 Commands will be copied to clipboard")
        print("-" * 60)

        from .types import Message

        messages = [
            Message(role="system", content="You are a helpful AI assistant for software development.")
        ]

        execute_mode = enable_execute

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break

                if user_input.lower() == "help":
                    self.print_help()
                    continue

                # Toggle execute mode
                if user_input.lower() in ["/execute", "/x"]:
                    execute_mode = not execute_mode
                    status = "ENABLED" if execute_mode else "DISABLED"
                    print(f"⚡ Command execution is now {status}")
                    continue

                if not user_input:
                    continue

                # Add user message
                messages.append(Message(role="user", content=user_input))

                # Get response
                print("\n💭 Thinking...", flush=True)
                response = await self.client.chat(
                    model="deepseek-r1:8b",
                    messages=messages,
                    stream=False
                )

                assistant_message = response["message"]["content"]

                # Add assistant message
                messages.append(Message(role="assistant", content=assistant_message))

                print(f"\nAssistant: {assistant_message}")

                # Execute commands if enabled
                if execute_mode:
                    print("\n🔍 Checking for executable commands...", flush=True)
                    commands = extract_shell_commands(assistant_message)

                    if commands:
                        print(f"✓ Found {len(commands)} command(s)\n")

                        for i, cmd in enumerate(commands, 1):
                            # Check if command is safe
                            safe, reason = is_safe_command(cmd)

                            if not safe:
                                print(f"\n⚠️  Command {i}: BLOCKED (unsafe)")
                                print(f"   {cmd}")
                                print(f"   Reason: {reason}")
                                continue

                            # Ask for confirmation
                            if confirm_command(cmd, auto_yes=False, copy_to_clip=enable_copy):
                                execute_command(cmd)
                            else:
                                print("⊘ Skipped")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")

    def print_help(self):
        """Print help message."""
        help_text = """
Available commands:
  exit, quit     - Exit the program
  help           - Show this help message
  /execute, /x   - Toggle command execution mode

Usage examples:
  - Ask questions about coding
  - Request code generation
  - Get explanations of concepts
  - Type /execute to enable command execution
        """
        print(help_text)

    async def create_agent_team(self, specializations: list[str], model: str = "deepseek-r1:8b"):
        """Create a team of coding agents."""
        if not self.orchestrator:
            print("Error: CLI not initialized")
            return

        team = self.orchestrator.create_coding_team(
            model=model,
            specializations=specializations
        )

        print(f"Created team with {len(team)} agents:")
        for name, agent in team.items():
            print(f"  - {name}: {agent.config.role}")

        return team

    async def run_workflow(self, task: str, specializations: list[str]):
        """Run a collaborative workflow."""
        if not self.orchestrator:
            print("Error: CLI not initialized")
            return

        # Create team
        await self.create_agent_team(specializations)

        print(f"\nTask: {task}")
        print("=" * 60)

        # Distribute task
        results = await self.orchestrator.distribute_task(task)

        # Print results
        for result in results:
            print(f"\n{result['agent']} ({result['role']}):")
            print("-" * 60)
            print(result['response'][:500])
            if len(result['response']) > 500:
                print("...")

    async def quick_query(self, query: str, model: str = "deepseek-r1:8b",
                         output_file: Optional[str] = None,
                         auto_save: bool = False,
                         extract_code: bool = False,
                         execute_commands: bool = False,
                         auto_yes: bool = False,
                         enable_copy: bool = True):
        """Quick single query without conversation history."""
        from .types import Message

        messages = [
            Message(role="system", content="You are a helpful AI assistant."),
            Message(role="user", content=query)
        ]

        print(f"Query: {query}")
        print("-" * 60)

        print("\n💭 Generating response...", flush=True)
        response = await self.client.chat(
            model=model,
            messages=messages,
            stream=False
        )
        print("✓ Done\n")

        assistant_message = response["message"]["content"]

        # Determine output filename
        filename = output_file
        if auto_save and not filename:
            filename = extract_filename_from_query(query)

        # Save to file if filename is specified
        if filename:
            content_to_save = assistant_message

            # Extract code blocks if requested
            if extract_code:
                content_to_save = extract_code_blocks(assistant_message)

            output_path = Path(filename)
            output_path.write_text(content_to_save, encoding='utf-8')

            print(f"\n✓ Saved to: {output_path.absolute()}")
            print(f"  Size: {len(content_to_save)} bytes")
            print(f"\nContent preview:")
            print("-" * 60)
            print(f"\n{assistant_message[:500]}")
            if len(assistant_message) > 500:
                print("...")
        else:
            # Just print to console
            print(f"\n{assistant_message}")

        # Execute commands if requested
        if execute_commands:
            print("\n🔍 Checking for executable commands...", flush=True)
            commands = extract_shell_commands(assistant_message)

            if commands:
                print(f"✓ Found {len(commands)} command(s) to execute:")
                print("=" * 60)

                executed_count = 0
                success_count = 0

                for i, cmd in enumerate(commands, 1):
                    # Check if command is safe
                    safe, reason = is_safe_command(cmd)

                    if not safe:
                        print(f"\n⚠️  Command {i}: BLOCKED (unsafe)")
                        print(f"   {cmd}")
                        print(f"   Reason: {reason}")
                        continue

                    # Ask for confirmation
                    if confirm_command(cmd, auto_yes, copy_to_clip=enable_copy):
                        success, stdout, stderr = execute_command(cmd)
                        executed_count += 1
                        if success:
                            success_count += 1
                    else:
                        print("⊘ Skipped")

                print("\n" + "=" * 60)
                print(f"Summary: Executed {executed_count}/{len(commands)} commands")
                print(f"         Success: {success_count}/{executed_count}")
            else:
                print("\nℹ No executable commands found in response")

        return assistant_message

    async def list_models(self):
        """List available models."""
        models = await self.client.list_models()
        print("\nAvailable models:")
        print("-" * 60)
        for model in models.get("models", []):
            name = model.get('name', 'unknown')
            size = model.get('size', 0)
            size_gb = size / (1024**3) if size > 0 else 0
            print(f"  {name:<30} ({size_gb:.2f} GB)")
        print()


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog='ai-cli',
        description='AI CLI - Multi-agent development system for Ollama',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-cli "explain python decorators"                           # Quick query
  ai-cli --model deepseek-r1:8b "write a function"              # Query with specific model
  ai-cli --auto-save "Напиши HELLO-WORLD.md"                   # Auto-save to file
  ai-cli --output result.py "write fibonacci function"         # Save to specific file
  ai-cli -s -c "create config.py"                              # Auto-save, extract code only
  ai-cli --execute "how to list all python files"              # Execute commands with confirmation
  ai-cli -x "show disk space"                                  # Execute commands (short form)
  ai-cli -x -y "create backup directory"                       # Auto-confirm execution
  ai-cli chat                                                   # Interactive chat mode
  ai-cli --models                                              # List available models
  ai-cli team "build a REST API"                               # Multi-agent workflow

For more information, visit: https://github.com/your-repo/ai-cli
        """
    )

    # Positional argument for quick queries
    parser.add_argument(
        'query',
        nargs='*',
        help='Quick query text (e.g., "explain python decorators")'
    )

    # Optional arguments
    parser.add_argument(
        '--model', '-m',
        default='deepseek-r1:8b',
        help='Model to use (default: deepseek-r1:8b)'
    )

    parser.add_argument(
        '--models',
        action='store_true',
        help='List available models'
    )

    parser.add_argument(
        '--ollama-url',
        default='http://localhost:11434',
        help='Ollama server URL (default: http://localhost:11434)'
    )

    parser.add_argument(
        '--output', '-o',
        metavar='FILE',
        help='Save output to file (e.g., --output result.md)'
    )

    parser.add_argument(
        '--auto-save', '-s',
        action='store_true',
        help='Automatically save to file if filename detected in query'
    )

    parser.add_argument(
        '--extract-code', '-c',
        action='store_true',
        help='Extract only code blocks from response (use with --output or --auto-save)'
    )

    parser.add_argument(
        '--execute', '-x',
        action='store_true',
        default=True,
        help='Execute shell commands from response with user confirmation (default: enabled)'
    )

    parser.add_argument(
        '--no-execute',
        action='store_true',
        help='Disable command execution'
    )

    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Auto-confirm all command executions (use with caution!)'
    )

    parser.add_argument(
        '--no-copy',
        action='store_true',
        help='Disable copying commands to clipboard'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        default=True,
        help='Continue in interactive mode after initial query (default: enabled)'
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='Execute only one query and exit (disable interactive mode)'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 0.1.0'
    )

    return parser


async def async_main():
    """Async main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle conflicting flags
    if args.no_execute:
        args.execute = False

    if args.once:
        args.interactive = False

    # Handle copy flag
    enable_copy = not args.no_copy

    cli = CLI()

    try:
        await cli.initialize(ollama_url=args.ollama_url)

        # List models
        if args.models:
            await cli.list_models()
            return

        # Check if query is a command
        if args.query:
            query_text = ' '.join(args.query)

            # Special commands
            if query_text == 'chat':
                await cli.interactive_mode(enable_execute=args.execute, enable_copy=enable_copy)
                return

            elif query_text.startswith('team '):
                task = query_text[5:]  # Remove 'team ' prefix
                await cli.run_workflow(
                    task=task,
                    specializations=["backend", "frontend", "testing"]
                )
                return

            # Regular quick query
            else:
                await cli.quick_query(
                    query_text,
                    model=args.model,
                    output_file=args.output,
                    auto_save=args.auto_save,
                    extract_code=args.extract_code,
                    execute_commands=args.execute,
                    auto_yes=args.yes,
                    enable_copy=enable_copy
                )

                # Continue in interactive mode if requested
                if args.interactive:
                    print("\n" + "=" * 60)
                    print("💬 Continuing in interactive mode...")
                    print("=" * 60)
                    await cli.interactive_mode(enable_execute=args.execute, enable_copy=enable_copy)

                return

        # No query provided - show help or start interactive mode
        else:
            parser.print_help()
            print("\nStarting interactive mode...\n")
            await cli.interactive_mode(enable_execute=args.execute, enable_copy=enable_copy)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await cli.shutdown()


def main():
    """Synchronous entry point for console_scripts."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
