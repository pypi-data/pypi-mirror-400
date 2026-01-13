"""
Agent Tester - Monitors and captures agent behavior for benchmarking.
"""

import os
import sys
import time
import json
import subprocess
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime

# Import psutil if available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@dataclass
class MetricSnapshot:
    """A point-in-time capture of agent metrics."""
    timestamp: float
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    network_connections: int = 0
    api_calls_detected: int = 0
    errors_detected: int = 0


@dataclass
class BenchmarkResults:
    """Complete benchmark results for an agent."""
    agent_pid: int
    agent_framework: str
    agent_command: str
    start_time: str
    end_time: str
    duration_seconds: int
    metrics: List[Dict] = field(default_factory=list)
    config: Dict = field(default_factory=dict)
    estimated_score: int = 70
    analysis: Dict = field(default_factory=dict)


class AgentTester:
    """
    Monitors and tests an AI agent's behavior.

    Captures:
    - Resource usage (CPU, memory)
    - Network activity (API calls)
    - Process behavior
    - Error patterns
    """

    # Known AI API endpoints to monitor
    AI_ENDPOINTS = [
        "api.openai.com",
        "api.anthropic.com",
        "api.cohere.com",
        "generativelanguage.googleapis.com",
        "api.together.xyz",
        "api.replicate.com",
        "api.mistral.ai",
        "api.groq.com",
    ]

    def __init__(self, agent):
        """
        Initialize the tester with a detected agent.

        Args:
            agent: DetectedAgent instance from scanner
        """
        self.agent = agent
        self.pid = agent.pid
        self.framework = agent.suspected_framework
        self.command = agent.command_line

        self.start_time = datetime.now()
        self.metrics: List[MetricSnapshot] = []
        self.config: Dict[str, Any] = {}
        self.api_calls: List[Dict] = []
        self.errors: List[str] = []

        # Try to get process handle
        self.process = None
        if HAS_PSUTIL:
            try:
                self.process = psutil.Process(self.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def analyze_config(self) -> Dict[str, Any]:
        """
        Analyze the agent's configuration and environment.

        Returns:
            Dict with configuration details
        """
        config = {
            "framework": self.framework,
            "pid": self.pid,
            "command": self.command[:200],
            "platform": sys.platform,
            "python_version": None,
            "environment_vars": [],
            "working_directory": None,
        }

        # Try to get more details from /proc on Linux
        if sys.platform == "linux":
            try:
                # Working directory
                cwd = os.readlink(f"/proc/{self.pid}/cwd")
                config["working_directory"] = cwd

                # Environment variables (filter for AI-related ones)
                with open(f"/proc/{self.pid}/environ", 'r') as f:
                    environ = f.read().split('\x00')
                    ai_vars = [
                        v for v in environ
                        if any(k in v.upper() for k in [
                            'OPENAI', 'ANTHROPIC', 'API_KEY', 'MODEL',
                            'LANGCHAIN', 'TEMPERATURE', 'MAX_TOKENS'
                        ])
                    ]
                    # Redact actual key values
                    config["environment_vars"] = [
                        re.sub(r'=.*', '=***', v) for v in ai_vars[:10]
                    ]
            except (FileNotFoundError, PermissionError):
                pass

        # Try with psutil
        if self.process:
            try:
                config["working_directory"] = self.process.cwd()

                # Check cmdline for Python version hints
                cmdline = self.process.cmdline()
                for arg in cmdline:
                    if 'python' in arg.lower():
                        config["python_version"] = arg
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        self.config = config
        return config

    def capture_metrics(self) -> MetricSnapshot:
        """
        Capture current metrics for the agent process.

        Returns:
            MetricSnapshot with current values
        """
        snapshot = MetricSnapshot(timestamp=time.time())

        if self.process:
            try:
                # CPU and memory
                snapshot.cpu_percent = self.process.cpu_percent(interval=0.1)
                memory_info = self.process.memory_info()
                snapshot.memory_mb = memory_info.rss / (1024 * 1024)

                # Network connections
                try:
                    connections = self.process.connections()
                    snapshot.network_connections = len(connections)

                    # Check for AI API connections
                    for conn in connections:
                        if hasattr(conn, 'raddr') and conn.raddr:
                            remote_ip = conn.raddr.ip if hasattr(conn.raddr, 'ip') else str(conn.raddr[0])
                            # This is simplified - in production we'd do reverse DNS
                            if any(endpoint in str(conn) for endpoint in self.AI_ENDPOINTS):
                                snapshot.api_calls_detected += 1
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Alternative: use system commands
        elif sys.platform in ["linux", "darwin"]:
            try:
                # Check network connections
                result = subprocess.run(
                    ["lsof", "-i", "-n", "-P", "-p", str(self.pid)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.strip().split('\n')
                snapshot.network_connections = max(0, len(lines) - 1)

                # Count AI API calls
                for line in lines:
                    if any(endpoint in line.lower() for endpoint in self.AI_ENDPOINTS):
                        snapshot.api_calls_detected += 1

            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        self.metrics.append(snapshot)
        return snapshot

    def check_process_alive(self) -> bool:
        """Check if the agent process is still running."""
        if self.process:
            try:
                return self.process.is_running()
            except:
                pass

        # Fallback: check /proc
        if sys.platform == "linux":
            return os.path.exists(f"/proc/{self.pid}")

        # Fallback: try to send signal 0
        try:
            os.kill(self.pid, 0)
            return True
        except OSError:
            return False

    def get_results(self) -> Dict[str, Any]:
        """
        Compile all captured data into benchmark results.

        Returns:
            Dict with complete benchmark data
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).seconds

        # Calculate aggregate metrics
        if self.metrics:
            avg_cpu = sum(m.cpu_percent for m in self.metrics) / len(self.metrics)
            max_memory = max(m.memory_mb for m in self.metrics)
            total_api_calls = sum(m.api_calls_detected for m in self.metrics)
            avg_connections = sum(m.network_connections for m in self.metrics) / len(self.metrics)
        else:
            avg_cpu = 0
            max_memory = 0
            total_api_calls = 0
            avg_connections = 0

        # Estimate a basic score (will be recalculated by Claude API)
        score = 70  # Base score

        # Adjust based on metrics
        if avg_cpu < 50:
            score += 5  # Good: not CPU intensive
        if max_memory < 500:
            score += 5  # Good: reasonable memory usage
        if total_api_calls > 0:
            score += 10  # Good: actually making API calls (active agent)

        # Cap score
        score = min(95, max(30, score))

        results = BenchmarkResults(
            agent_pid=self.pid,
            agent_framework=self.framework,
            agent_command=self.command[:200],
            start_time=self.start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            metrics=[asdict(m) for m in self.metrics],
            config=self.config,
            estimated_score=score,
            analysis={
                "avg_cpu_percent": round(avg_cpu, 2),
                "max_memory_mb": round(max_memory, 2),
                "total_api_calls": total_api_calls,
                "avg_connections": round(avg_connections, 2),
                "metric_samples": len(self.metrics),
                "process_alive": self.check_process_alive(),
            }
        )

        return asdict(results)
