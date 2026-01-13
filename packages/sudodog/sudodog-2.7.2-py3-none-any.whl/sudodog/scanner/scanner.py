"""
SudoDog Shadow Agent Scanner

Scans running processes on the local machine to detect AI agents
that are not being monitored by SudoDog.
"""

import os
import sys
import json
import subprocess
import re
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class DetectedAgent:
    """Represents a detected shadow agent."""
    pid: int
    process_name: str
    command_line: str
    suspected_framework: str
    confidence: float
    indicators: List[str]
    working_directory: Optional[str] = None
    user: Optional[str] = None
    cpu_percent: Optional[float] = None
    memory_mb: Optional[float] = None
    start_time: Optional[str] = None


# Detection patterns for various AI agent frameworks
FRAMEWORK_PATTERNS = {
    "langchain": {
        "imports": [
            r"from\s+langchain",
            r"import\s+langchain",
            r"langchain\.agents",
            r"langchain\.chains",
        ],
        "env_vars": ["LANGCHAIN_API_KEY", "LANGCHAIN_TRACING"],
        "packages": ["langchain", "langchain-core", "langchain-community"],
    },
    "autogen": {
        "imports": [
            r"from\s+autogen",
            r"import\s+autogen",
            r"autogen_studio",
            r"AssistantAgent",
            r"UserProxyAgent",
        ],
        "env_vars": ["AUTOGEN_"],
        "packages": ["pyautogen", "autogen"],
    },
    "crewai": {
        "imports": [
            r"from\s+crewai",
            r"import\s+crewai",
            r"CrewAI",
        ],
        "env_vars": [],
        "packages": ["crewai"],
    },
    "openai-assistants": {
        "imports": [
            r"openai\.beta\.assistants",
            r"client\.beta\.assistants",
            r"AssistantEventHandler",
        ],
        "env_vars": ["OPENAI_API_KEY"],
        "packages": ["openai"],
    },
    "anthropic-claude": {
        "imports": [
            r"from\s+anthropic",
            r"import\s+anthropic",
            r"claude-3",
        ],
        "env_vars": ["ANTHROPIC_API_KEY"],
        "packages": ["anthropic"],
    },
    "semantic-kernel": {
        "imports": [
            r"from\s+semantic_kernel",
            r"import\s+semantic_kernel",
        ],
        "env_vars": [],
        "packages": ["semantic-kernel"],
    },
    "llama-index": {
        "imports": [
            r"from\s+llama_index",
            r"import\s+llama_index",
        ],
        "env_vars": [],
        "packages": ["llama-index"],
    },
    "haystack": {
        "imports": [
            r"from\s+haystack",
            r"import\s+haystack",
        ],
        "env_vars": [],
        "packages": ["farm-haystack", "haystack-ai"],
    },
}

# Command line patterns that suggest AI agent activity
# More specific patterns to reduce false positives
AGENT_CMD_PATTERNS = [
    (r"langchain", 0.6),
    (r"autogen", 0.6),
    (r"crewai", 0.6),
    (r"llama.index", 0.5),
    (r"openai\.beta", 0.5),
    (r"agent\.py", 0.4),
    (r"agent_runner", 0.5),
    (r"run_agent", 0.5),
    (r"assistants\.create", 0.5),
]

# Patterns to EXCLUDE (not AI agents, just mentions keywords)
EXCLUDE_PATTERNS = [
    r"sudodog",           # Our own process
    r"sudodog-scan",      # Our scan command
    r"pip\s+install",     # Package installation
    r"pip3\s+install",
    r"npm\s+install",
    r"git\s+",            # Git commands
    r"grep\s+",           # Searching for agent keywords
    r"find\s+",           # Finding files
    r"vim\s+",            # Editing files
    r"nano\s+",
    r"code\s+",           # VS Code
    r"pytest",            # Running tests
    r"unittest",
]


def get_running_processes() -> List[Dict[str, Any]]:
    """Get list of running processes with their details."""
    processes = []
    current_pid = os.getpid()

    if sys.platform == "darwin":  # macOS
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            lines = result.stdout.strip().split('\n')[1:]

            for line in lines:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    pid = int(parts[1])
                    if pid == current_pid:
                        continue
                    processes.append({
                        "user": parts[0],
                        "pid": pid,
                        "cpu": float(parts[2]),
                        "mem": float(parts[3]),
                        "command": parts[10],
                    })
        except Exception as e:
            pass

    elif sys.platform == "linux":
        try:
            for pid_dir in os.listdir('/proc'):
                if pid_dir.isdigit():
                    try:
                        pid = int(pid_dir)
                        if pid == current_pid:
                            continue

                        with open(f'/proc/{pid}/cmdline', 'r') as f:
                            cmdline = f.read().replace('\x00', ' ').strip()

                        if not cmdline:
                            continue

                        with open(f'/proc/{pid}/comm', 'r') as f:
                            comm = f.read().strip()

                        user = "unknown"
                        try:
                            import pwd
                            stat = os.stat(f'/proc/{pid}')
                            user = pwd.getpwuid(stat.st_uid).pw_name
                        except:
                            pass

                        processes.append({
                            "user": user,
                            "pid": pid,
                            "cpu": 0.0,
                            "mem": 0.0,
                            "command": cmdline,
                            "name": comm,
                        })
                    except (FileNotFoundError, PermissionError):
                        continue
        except Exception as e:
            pass

    elif sys.platform == "win32":
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-Process | Select-Object Id,ProcessName,Path,CommandLine | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    proc_list = json.loads(result.stdout)
                    if isinstance(proc_list, dict):
                        proc_list = [proc_list]

                    for p in proc_list:
                        pid = p.get("Id", 0)
                        if pid == current_pid:
                            continue
                        name = p.get("ProcessName", "")
                        cmdline = p.get("CommandLine") or p.get("Path") or name

                        if pid and name:
                            processes.append({
                                "user": "unknown",
                                "pid": pid,
                                "cpu": 0.0,
                                "mem": 0.0,
                                "command": cmdline,
                                "name": name.lower(),
                            })
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            pass

    return processes


def check_network_connections(pid: int) -> List[str]:
    """Check network connections for a process to detect API calls."""
    connections = []

    ai_endpoints = [
        "api.openai.com",
        "api.anthropic.com",
        "api.cohere.com",
        "generativelanguage.googleapis.com",
        "api.together.xyz",
        "api.replicate.com",
        "api.mistral.ai",
    ]

    try:
        if sys.platform in ["darwin", "linux"]:
            result = subprocess.run(
                ["lsof", "-i", "-n", "-P", "-p", str(pid)],
                capture_output=True,
                text=True
            )

            for line in result.stdout.split('\n'):
                if any(api in line.lower() for api in ai_endpoints):
                    connections.append(line.strip())

        elif sys.platform == "win32":
            try:
                ps_result = subprocess.run(
                    ["powershell", "-Command",
                     f"Get-NetTCPConnection -OwningProcess {pid} -ErrorAction SilentlyContinue | "
                     "Select-Object RemoteAddress,RemotePort | ConvertTo-Json"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if ps_result.stdout:
                    try:
                        conn_data = json.loads(ps_result.stdout)
                        if isinstance(conn_data, dict):
                            conn_data = [conn_data]
                        for conn in conn_data:
                            addr = conn.get("RemoteAddress", "")
                            if any(api in addr for api in ai_endpoints):
                                connections.append(f"{addr}:{conn.get('RemotePort', '')}")
                    except json.JSONDecodeError:
                        pass
            except Exception:
                pass

    except Exception:
        pass

    return connections


def analyze_process(proc: Dict[str, Any]) -> Optional[DetectedAgent]:
    """Analyze a process to determine if it's an AI agent."""
    command = proc.get("command", "")
    command_lower = command.lower()
    name = proc.get("name", command.split()[0] if command else "").lower()

    # Skip system processes
    skip_names = [
        "kernel", "systemd", "init", "kworker", "ksoftirq",
        "chrome", "firefox", "safari", "code", "vscode",
        "terminal", "bash", "zsh", "fish", "sh",
        "finder", "dock", "windowserver",
        "launchd", "cfprefsd", "distnoted",
        "sshd", "nginx", "apache", "postgres", "mysql", "redis",
    ]

    if any(skip in name for skip in skip_names):
        return None

    # Only look at runtime processes
    is_runtime = any(runtime in name for runtime in [
        "python", "node", "java", "dotnet", "ruby"
    ])

    if not is_runtime:
        return None

    # Check exclusion patterns (skip these even if they match agent patterns)
    for exclude_pattern in EXCLUDE_PATTERNS:
        if re.search(exclude_pattern, command_lower, re.IGNORECASE):
            return None

    indicators = []
    confidence = 0.0
    detected_framework = "unknown"

    # Check command line patterns
    for pattern, weight in AGENT_CMD_PATTERNS:
        if re.search(pattern, command_lower, re.IGNORECASE):
            indicators.append(f"Command matches pattern '{pattern}'")
            confidence += weight

    # Check for framework-specific patterns
    for framework, patterns in FRAMEWORK_PATTERNS.items():
        for import_pattern in patterns["imports"]:
            if re.search(import_pattern, command, re.IGNORECASE):
                indicators.append(f"Framework detected: {framework}")
                confidence += 0.5
                detected_framework = framework
                break

    # Check environment variables (Linux only)
    try:
        if sys.platform == "linux":
            with open(f'/proc/{proc["pid"]}/environ', 'r') as f:
                environ = f.read()
                for framework, patterns in FRAMEWORK_PATTERNS.items():
                    for env_var in patterns["env_vars"]:
                        if env_var in environ:
                            indicators.append(f"Environment: {env_var}")
                            confidence += 0.3
                            if detected_framework == "unknown":
                                detected_framework = framework
    except:
        pass

    # Check network connections for AI API calls
    connections = check_network_connections(proc["pid"])
    if connections:
        indicators.append(f"AI API connections: {len(connections)}")
        confidence += 0.4

    # Only report if confidence is high enough
    if confidence < 0.4 or not indicators:
        return None

    confidence = min(0.95, confidence)

    process_name = name
    for runtime in ["python", "node", "java", "dotnet"]:
        if runtime in name:
            process_name = runtime
            break

    return DetectedAgent(
        pid=proc["pid"],
        process_name=process_name,
        command_line=command[:500],
        suspected_framework=detected_framework,
        confidence=round(confidence, 2),
        indicators=indicators,
        user=proc.get("user"),
        cpu_percent=proc.get("cpu"),
        memory_mb=proc.get("mem"),
    )


def scan_for_shadow_agents(quiet: bool = False) -> List[DetectedAgent]:
    """Scan the system for shadow (unmonitored) AI agents."""
    if not quiet:
        print("Scanning for AI agents...")

    processes = get_running_processes()

    if not quiet:
        print(f"Checking {len(processes)} processes...")

    detected_agents = []

    for proc in processes:
        agent = analyze_process(proc)
        if agent:
            detected_agents.append(agent)

    return detected_agents


def format_report(agents: List[DetectedAgent]) -> str:
    """Format the scan results as a human-readable report."""
    if not agents:
        return """
No unmonitored AI agents detected.

This could mean:
  - No AI agents are currently running
  - All running agents are already monitored by SudoDog
  - Agents are running in containers (use --docker to scan)

Tip: Run 'sudodog-scan --help' for more options.
"""

    report = f"""
{'='*60}
  SHADOW AGENT SCAN REPORT
{'='*60}
  Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Unmonitored Agents Found: {len(agents)}
{'='*60}
"""

    for i, agent in enumerate(agents, 1):
        conf_bar = '█' * int(agent.confidence * 10) + '░' * (10 - int(agent.confidence * 10))
        report += f"""
[{i}] {agent.process_name.upper()} (PID {agent.pid})
    Framework:  {agent.suspected_framework}
    Confidence: [{conf_bar}] {agent.confidence * 100:.0f}%
    Command:    {agent.command_line[:60]}{'...' if len(agent.command_line) > 60 else ''}

    Why detected:
"""
        for indicator in agent.indicators:
            report += f"      • {indicator}\n"

    report += f"""
{'='*60}
  NEXT STEPS
{'='*60}
  To monitor these agents, run:
    sudodog run <your-agent-command>

  Or integrate with your existing agents:
    sudodog integrate claude-code  # For Claude Code
    sudodog integrate --help       # See all options

  Dashboard: https://dashboard.sudodog.com
{'='*60}
"""
    return report


def export_json(agents: List[DetectedAgent]) -> str:
    """Export scan results as JSON."""
    return json.dumps({
        "scan_time": datetime.now().isoformat(),
        "agent_count": len(agents),
        "agents": [asdict(a) for a in agents],
    }, indent=2)


if __name__ == "__main__":
    agents = scan_for_shadow_agents()
    print(format_report(agents))
