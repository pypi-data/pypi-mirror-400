"""
Main CLI entry point for SudoDog.

Provides command-line interface for running AI agents with monitoring.
"""

import sys
import argparse
import logging
import uuid
import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import List

from ..sandbox.factory import SandboxFactory
from ..core.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def print_banner(platform: str = None):
    """Print SudoDog banner"""
    emoji = SandboxFactory.get_platform_emoji(platform)

    print("🐕 SudoDog AI Agent Security")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if platform:
        platform_name = platform.capitalize() if platform != 'darwin' else 'macOS'
        print(f"{emoji} Platform: {platform_name}")
    print()


def cmd_init(args):
    """Initialize SudoDog configuration"""
    print_banner()

    config = Config()

    if config.is_initialized():
        print("⚠️  SudoDog is already initialized")
        print(f"   Config location: {config.config_path}")
        print()
        print("To reinitialize, delete the config file and run 'sudodog init' again")
        return 0

    # Prompt for API key (optional)
    print("Initialize SudoDog")
    print()
    print("Enter your API key (leave blank for local-only mode):")
    api_key = input("API Key: ").strip()

    # Initialize
    if config.init(api_key=api_key):
        print()
        print("✅ SudoDog initialized successfully!")
        print()
        print(f"   Config location: {config.config_path}")
        print()
        print("Next steps:")
        print("  1. Run your agent: sudodog run python agent.py")
        # BUG-009 FIX: Use correct dashboard URL
        print("  2. View dashboard: https://dashboard.sudodog.com")
        return 0
    else:
        print()
        print("❌ Failed to initialize SudoDog")
        return 1


def cmd_run(args):
    """Run command in sandbox"""
    # Load configuration
    config = Config()

    if not config.is_initialized() and not args.no_init_check:
        print("⚠️  SudoDog not initialized. Run 'sudodog init' first.")
        print()
        print("Or use --no-init-check to skip this warning")
        return 1

    # Get platform
    platform = SandboxFactory.get_current_platform()
    print_banner(platform)

    # Parse resource limits
    limits = {}
    if args.cpu_limit:
        limits['cpu_limit'] = args.cpu_limit
    if args.memory_limit:
        limits['memory_limit'] = args.memory_limit

    # Build config
    run_config = config.to_dict()

    # Override with CLI flags
    if args.docker:
        run_config['use_docker'] = True

    if args.no_network:
        run_config['allow_network'] = False

    # Generate agent ID
    agent_id = args.agent_id or str(uuid.uuid4())

    # Display info
    if args.docker:
        print("🐳 Using Docker sandbox")
    else:
        platform_name = platform.capitalize() if platform != 'darwin' else 'macOS'
        print(f"📦 Using {platform_name} native sandbox")

    if args.name:
        print(f"🏷️  Agent name: {args.name}")

    print(f"🆔 Agent ID: {agent_id}")
    print()
    print(f"▶️  Running: {' '.join(args.command)}")
    print()

    # Create sandbox
    try:
        sandbox = SandboxFactory.create(
            agent_id=agent_id,
            limits=limits,
            config=run_config
        )
    except Exception as e:
        print(f"❌ Failed to create sandbox: {e}")
        return 1

    # Run command
    try:
        exit_code = sandbox.run(args.command)

        print()
        if exit_code == 0:
            print("✅ Command completed successfully")
        else:
            print(f"⚠️  Command failed with exit code {exit_code}")

        return exit_code

    except KeyboardInterrupt:
        print()
        print("⏹️  Interrupted by user")
        sandbox.cleanup()
        return 130

    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        sandbox.cleanup()
        return 1


def cmd_integrate(args):
    """Integrate SudoDog with AI agent tools"""
    print_banner()

    if args.tool == 'claude-code':
        return integrate_claude_code(args)
    elif args.tool == 'docker':
        return integrate_docker(args)
    else:
        print(f"Unknown integration: {args.tool}")
        print("Available integrations: claude-code, docker")
        return 1


def integrate_claude_code(args):
    """Install Claude Code hooks for SudoDog observability"""
    print("Installing Claude Code Integration")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    config = Config()
    sudodog_dir = Path.home() / '.sudodog'
    hooks_dir = sudodog_dir / 'hooks'
    claude_settings_dir = Path.home() / '.claude'
    claude_settings_file = claude_settings_dir / 'settings.json'
    hook_script_path = hooks_dir / 'claude-code-hook.sh'

    # Check if SudoDog is initialized
    if not config.is_initialized():
        print("⚠️  SudoDog not initialized. Running 'sudodog init' first...")
        print()
        cmd_init(argparse.Namespace())
        config = Config()  # Reload config

    # Create hooks directory
    hooks_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created hooks directory: {hooks_dir}")

    # Create the hook script
    hook_script = '''#!/bin/bash
# SudoDog Claude Code Hook
set -euo pipefail

SUDODOG_CONFIG="${HOME}/.sudodog/config.json"
SUDODOG_CACHE="${HOME}/.sudodog/claude-code-session.json"

get_config_value() {
    local key="$1"
    local default="${2:-}"
    if [ -f "$SUDODOG_CONFIG" ]; then
        local value
        value=$(jq -r ".$key // empty" "$SUDODOG_CONFIG" 2>/dev/null)
        [ -n "$value" ] && echo "$value" && return
    fi
    echo "$default"
}

API_KEY=$(get_config_value "api_key" "")
API_ENDPOINT=$(get_config_value "endpoint" "https://api.sudodog.com/api/v1/telemetry")
USER_ID=$(get_config_value "user_id" "")

if [ "$(get_config_value 'telemetry_enabled' 'true')" != "true" ]; then
    echo '{"continue": true}'
    exit 0
fi

get_session_id() {
    if [ -f "$SUDODOG_CACHE" ]; then
        local sid=$(jq -r '.session_id // empty' "$SUDODOG_CACHE" 2>/dev/null)
        [ -n "$sid" ] && echo "$sid" && return
    fi
    local new_id="claude-$(date +%s)-$(head -c 4 /dev/urandom | xxd -p 2>/dev/null || echo $$)"
    mkdir -p "$(dirname "$SUDODOG_CACHE")"
    echo "{\\"session_id\\": \\"$new_id\\", \\"started_at\\": \\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\\"}" > "$SUDODOG_CACHE"
    echo "$new_id"
}

SESSION_ID=$(get_session_id)
EVENT_TYPE="${1:-unknown}"
INPUT=""
[ ! -t 0 ] && INPUT=$(cat)
TOOL_NAME="${CLAUDE_TOOL_NAME:-$(echo "$INPUT" | jq -r '.tool // empty' 2>/dev/null || echo '')}"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TOOL_DURATION="${CLAUDE_TOOL_DURATION:-0}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

send_telemetry() {
    [ -z "$API_KEY" ] && return 0
    (curl -s -X POST "$API_ENDPOINT" \\
        -H "Content-Type: application/json" \\
        -H "Authorization: Bearer $API_KEY" \\
        -H "User-Agent: SudoDog-ClaudeCode-Hook/1.0" \\
        -d "$1" --max-time 5 >/dev/null 2>&1) &
}

# Build and send telemetry
PAYLOAD=$(cat << EOF
{
    "user_id": "$USER_ID",
    "agent_id": "$SESSION_ID",
    "session_id": "$SESSION_ID",
    "event_type": "action",
    "timestamp": "$TIMESTAMP",
    "data": {
        "agent_id": "$SESSION_ID",
        "agent_name": "Claude Code",
        "framework": "claude-code",
        "platform": "$(uname -s | tr '[:upper:]' '[:lower:]')",
        "action_type": "tool",
        "target": "$TOOL_NAME",
        "duration_ms": $TOOL_DURATION,
        "project_dir": "$PROJECT_DIR",
        "details": {"hook_type": "$EVENT_TYPE"}
    }
}
EOF
)
send_telemetry "$PAYLOAD"
echo '{"continue": true}'
exit 0
'''

    # Write hook script
    with open(hook_script_path, 'w') as f:
        f.write(hook_script)
    hook_script_path.chmod(0o755)
    print(f"✅ Installed hook script: {hook_script_path}")

    # Create Claude Code settings directory
    claude_settings_dir.mkdir(parents=True, exist_ok=True)

    # Build hooks configuration
    hook_cmd = str(hook_script_path)
    hooks_config = {
        "SessionStart": [
            {"matcher": "*", "hooks": [{"type": "command", "command": f"{hook_cmd} SessionStart"}]}
        ],
        "PreToolUse": [
            {"matcher": "Write|Edit|Read|Bash|Glob|Grep|WebFetch|WebSearch|Task",
             "hooks": [{"type": "command", "command": f"{hook_cmd} PreToolUse"}]}
        ],
        "PostToolUse": [
            {"matcher": "Write|Edit|Read|Bash|Glob|Grep|WebFetch|WebSearch|Task",
             "hooks": [{"type": "command", "command": f"{hook_cmd} PostToolUse"}]}
        ],
        "Stop": [
            {"matcher": "*", "hooks": [{"type": "command", "command": f"{hook_cmd} Stop"}]}
        ]
    }

    # Load or create Claude settings
    if claude_settings_file.exists():
        # Backup existing settings
        backup_path = claude_settings_file.with_suffix(f'.backup.{int(__import__("time").time())}')
        shutil.copy(claude_settings_file, backup_path)
        print(f"✅ Backed up existing settings to: {backup_path}")

        with open(claude_settings_file, 'r') as f:
            claude_settings = json.load(f)
    else:
        claude_settings = {}

    # Merge hooks into settings
    claude_settings['hooks'] = hooks_config

    # Write settings
    with open(claude_settings_file, 'w') as f:
        json.dump(claude_settings, f, indent=2)
    print(f"✅ Updated Claude Code settings: {claude_settings_file}")

    # Update SudoDog config with user_id if needed
    if not config.get('user_id'):
        api_key = config.get('api_key', '')
        if api_key:
            config.set('user_id', api_key[:16])

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Claude Code integration complete!")
    print()
    print("What's captured:")
    print("  • File operations (read, write, edit)")
    print("  • Shell commands")
    print("  • Web searches and fetches")
    print("  • Agent tasks")
    print("  • Session events")
    print()
    print("View your dashboard at: https://dashboard.sudodog.com")
    print()

    return 0


def integrate_docker(args):
    """Install Docker MCP server for SudoDog observability"""
    print("Installing Docker MCP Integration")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    config = Config()

    # Check if SudoDog is initialized
    if not config.is_initialized():
        print("⚠️  SudoDog not initialized. Running 'sudodog init' first...")
        print()
        cmd_init(argparse.Namespace())
        config = Config()

    api_key = config.get('api_key', '')

    print("To use SudoDog with Docker MCP, add the following to your")
    print("Claude Desktop config (~/Library/Application Support/Claude/claude_desktop_config.json):")
    print()
    print('```json')
    print('{')
    print('  "mcpServers": {')
    print('    "sudodog": {')
    print('      "command": "docker",')
    print('      "args": [')
    print('        "run", "-i", "--rm",')
    if api_key:
        print(f'        "-e", "SUDODOG_API_KEY={api_key}",')
    else:
        print('        "-e", "SUDODOG_API_KEY=YOUR_API_KEY",')
    print('        "ghcr.io/sudodog-official/sudodog-mcp"')
    print('      ]')
    print('    }')
    print('  }')
    print('}')
    print('```')
    print()
    print("Available MCP Tools:")
    print("  • start_session - Start observability session")
    print("  • log_file_change - Log file operations")
    print("  • log_command - Log shell commands")
    print("  • log_llm_usage - Track token usage and costs")
    print("  • get_session_summary - View session statistics")
    print("  • end_session - End session with summary")
    print()
    print("View your dashboard at: https://dashboard.sudodog.com")
    print()

    return 0


def cmd_config(args):
    """Show or modify configuration"""
    config = Config()

    if args.show:
        print_banner()
        print("Configuration:")
        print()

        config_dict = config.to_dict()
        for key, value in sorted(config_dict.items()):
            # Hide API key (show only first 8 chars)
            if key == 'api_key' and value:
                value = value[:8] + '...'
            print(f"  {key}: {value}")

        print()
        print(f"Config file: {config.config_path}")
        return 0

    elif args.set:
        key, value = args.set.split('=', 1)

        # Parse boolean values
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'

        config.set(key, value)
        print(f"✅ Set {key} = {value}")
        return 0

    else:
        print("Usage: sudodog config --show | --set KEY=VALUE")
        return 1


def main(argv: List[str] = None):
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='SudoDog - Monitor and secure your AI agents',
        prog='sudodog',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudodog init                      # Set up SudoDog (optional)
  sudodog run python agent.py       # Run agent with monitoring
  sudodog integrate claude-code     # Add Claude Code monitoring
  sudodog config --show             # View configuration

Scan for running agents:
  sudodog-scan                      # Find AI agents on your machine

More info: https://sudodog.com/docs
        """
    )

    subparsers = parser.add_subparsers(dest='subcommand', help='Command to run')

    # init command
    parser_init = subparsers.add_parser('init', help='Set up SudoDog (get API key at dashboard.sudodog.com)')

    # run command
    parser_run = subparsers.add_parser('run', help='Run your agent with monitoring')
    parser_run.add_argument('command', nargs='+', help='Command to run (e.g., python agent.py)')
    parser_run.add_argument('--name', type=str, help='Agent name')
    parser_run.add_argument('--agent-id', type=str, help='Agent ID (generated if not provided)')
    parser_run.add_argument('--docker', action='store_true', help='Use Docker sandbox')
    parser_run.add_argument('--cpu-limit', type=float, help='CPU limit (cores)')
    parser_run.add_argument('--memory-limit', type=str, help='Memory limit (e.g., 1g, 512m)')
    parser_run.add_argument('--no-network', action='store_true', help='Disable network access')
    parser_run.add_argument('--no-init-check', action='store_true', help='Skip initialization check')

    # config command
    parser_config = subparsers.add_parser('config', help='Show or modify configuration')
    parser_config.add_argument('--show', action='store_true', help='Show configuration')
    parser_config.add_argument('--set', type=str, help='Set configuration (KEY=VALUE)')

    # integrate command
    parser_integrate = subparsers.add_parser('integrate', help='Integrate with AI agent tools')
    parser_integrate.add_argument('tool', type=str, help='Tool to integrate (claude-code, docker)')

    # Parse arguments
    args = parser.parse_args(argv)

    # Execute command
    if args.subcommand == 'init':
        return cmd_init(args)

    elif args.subcommand == 'run':
        return cmd_run(args)

    elif args.subcommand == 'config':
        return cmd_config(args)

    elif args.subcommand == 'integrate':
        return cmd_integrate(args)

    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
