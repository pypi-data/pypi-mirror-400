"""
Benchmark Runner

Orchestrates the full benchmark:
1. Starts proxy server
2. Launches user's agent with proxy env vars
3. Waits for agent to be ready
4. Runs test suite
5. Collects and analyzes results
"""

import os
import sys
import time
import subprocess
import signal
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from .proxy import BenchmarkProxy, BenchmarkMetrics
from .test_suite import (
    TestChallenge, TestResult, ALL_TESTS, get_quick_suite,
    evaluate_response, calculate_category_scores, calculate_weighted_score,
    TestCategory, AgentType, get_agent_type_from_string
)


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark run."""
    agent_command: str
    framework: str = "unknown"
    agent_type: str = "general"  # chat, code, data, task, general
    quick_mode: bool = False
    timeout_seconds: int = 300  # 5 minute max
    proxy_port: int = 8765
    openai_key: Optional[str] = None
    anthropic_key: Optional[str] = None
    # Optional metadata for leaderboard
    agent_name: Optional[str] = None
    publisher: Optional[str] = None
    website: Optional[str] = None


@dataclass
class BenchmarkResults:
    """Complete benchmark results."""
    config: BenchmarkConfig
    test_results: List[TestResult]
    proxy_metrics: Dict[str, Any]
    category_scores: Dict[str, Any]
    overall_score: float
    overall_grade: str
    duration_seconds: float
    agent_detected: bool = False
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "framework": self.config.framework,
            "agent_type": self.config.agent_type,
            "agent_command": self.config.agent_command,
            "agent_name": self.config.agent_name,
            "publisher": self.config.publisher,
            "website": self.config.website,
            "test_results": [
                {
                    "challenge_id": r.challenge_id,
                    "passed": r.passed,
                    "latency_ms": r.latency_ms,
                    "tokens_used": r.tokens_used,
                    "score": r.score,
                    "error": r.error,
                }
                for r in self.test_results
            ],
            "proxy_metrics": self.proxy_metrics,
            "category_scores": self.category_scores,
            "overall_score": self.overall_score,
            "overall_grade": self.overall_grade,
            "duration_seconds": self.duration_seconds,
            "agent_detected": self.agent_detected,
            "error": self.error,
        }


class BenchmarkRunner:
    """Runs the full benchmark suite."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.proxy: Optional[BenchmarkProxy] = None
        self.agent_process: Optional[subprocess.Popen] = None
        self.test_results: List[TestResult] = []

    def run(self, progress_callback=None) -> BenchmarkResults:
        """
        Run the complete benchmark.

        Args:
            progress_callback: Optional function(message, progress_pct) for updates
        """
        start_time = time.time()

        def log(msg, pct=None):
            if progress_callback:
                progress_callback(msg, pct)

        try:
            # Step 1: Start proxy
            log("Starting benchmark proxy server...", 5)
            self._start_proxy()

            # Step 2: Launch agent
            log("Launching your agent...", 10)
            self._launch_agent()

            # Give agent time to start
            log("Waiting for agent to initialize...", 15)
            time.sleep(3)

            # Step 3: Run tests
            tests = get_quick_suite() if self.config.quick_mode else ALL_TESTS
            total_tests = len(tests)

            for i, test in enumerate(tests):
                pct = 20 + int((i / total_tests) * 70)
                log(f"Running test: {test.name}", pct)

                result = self._run_single_test(test)
                self.test_results.append(result)

            # Step 4: Stop and collect
            log("Collecting results...", 95)
            self._stop_agent()
            self.proxy.stop()

            # Step 5: Calculate scores with agent type weighting
            duration = time.time() - start_time
            proxy_metrics = self.proxy.get_metrics().to_dict()

            # Use weighted scoring based on agent type
            agent_type = get_agent_type_from_string(self.config.agent_type)
            overall_score, overall_grade, category_scores = calculate_weighted_score(
                self.test_results, agent_type
            )

            log("Benchmark complete!", 100)

            return BenchmarkResults(
                config=self.config,
                test_results=self.test_results,
                proxy_metrics=proxy_metrics,
                category_scores=category_scores,
                overall_score=overall_score,
                overall_grade=overall_grade,
                duration_seconds=duration,
                agent_detected=proxy_metrics.get("total_requests", 0) > 0,
            )

        except Exception as e:
            duration = time.time() - start_time
            self._cleanup()
            return BenchmarkResults(
                config=self.config,
                test_results=self.test_results,
                proxy_metrics={},
                category_scores={},
                overall_score=0,
                overall_grade="F",
                duration_seconds=duration,
                error=str(e),
            )

    def _start_proxy(self):
        """Start the proxy server."""
        self.proxy = BenchmarkProxy(
            port=self.config.proxy_port,
            openai_key=self.config.openai_key,
            anthropic_key=self.config.anthropic_key,
        )
        self.proxy.start()

    def _launch_agent(self):
        """Launch the user's agent with proxy env vars."""
        env = os.environ.copy()

        # Set proxy URLs for common providers
        proxy_url = self.proxy.get_base_url()
        env["OPENAI_BASE_URL"] = proxy_url + "/v1"
        env["OPENAI_API_BASE"] = proxy_url + "/v1"  # Legacy
        env["ANTHROPIC_BASE_URL"] = proxy_url

        # Also set for LangChain and other frameworks
        env["LANGCHAIN_OPENAI_API_BASE"] = proxy_url + "/v1"

        # Parse command
        import shlex
        cmd_parts = shlex.split(self.config.agent_command)

        self.agent_process = subprocess.Popen(
            cmd_parts,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if os.name != 'nt' else None,
        )

    def _run_single_test(self, challenge: TestChallenge) -> TestResult:
        """
        Run a single test challenge.

        Note: For MVP, we're measuring based on what the agent does
        through the proxy. In a full implementation, we'd inject
        test prompts directly.
        """
        start_time = time.time()

        # For MVP: We wait and observe what the agent does
        # In full version: We'd have a way to inject prompts
        time.sleep(0.5)  # Small delay between tests

        # Check if any API calls were made
        metrics = self.proxy.get_metrics()
        calls_before = len(metrics.api_calls)

        # Wait for potential response
        time.sleep(2)

        calls_after = len(metrics.api_calls)
        new_calls = calls_after - calls_before

        latency_ms = (time.time() - start_time) * 1000

        # For now, mark as passed if agent is making API calls
        # Full implementation would validate actual responses
        if new_calls > 0:
            latest_call = metrics.api_calls[-1]
            response_text = json.dumps(latest_call.response_body)
            passed, score, reason = evaluate_response(challenge, response_text)
            tokens_used = latest_call.input_tokens + latest_call.output_tokens
        else:
            passed = False
            score = 0.0
            tokens_used = 0
            response_text = ""

        return TestResult(
            challenge_id=challenge.id,
            passed=passed,
            response=response_text[:500],  # Truncate for storage
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            score=score,
        )

    def _stop_agent(self):
        """Stop the agent process."""
        if self.agent_process:
            try:
                if os.name != 'nt':
                    os.killpg(os.getpgid(self.agent_process.pid), signal.SIGTERM)
                else:
                    self.agent_process.terminate()
                self.agent_process.wait(timeout=5)
            except:
                if os.name != 'nt':
                    os.killpg(os.getpgid(self.agent_process.pid), signal.SIGKILL)
                else:
                    self.agent_process.kill()

    def _cleanup(self):
        """Clean up resources."""
        self._stop_agent()
        if self.proxy:
            self.proxy.stop()

    def _calculate_grade(self, score: int) -> str:
        """Calculate letter grade from score."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D"
        else:
            return "F"


def run_interactive_benchmark(
    agent_command: str,
    framework: str = "unknown",
    quick: bool = False,
    openai_key: str = None,
    anthropic_key: str = None,
) -> BenchmarkResults:
    """
    Convenience function to run a benchmark interactively.
    """
    config = BenchmarkConfig(
        agent_command=agent_command,
        framework=framework,
        quick_mode=quick,
        openai_key=openai_key or os.environ.get("OPENAI_API_KEY"),
        anthropic_key=anthropic_key or os.environ.get("ANTHROPIC_API_KEY"),
    )

    runner = BenchmarkRunner(config)

    def progress(msg, pct):
        bar_width = 30
        filled = int(bar_width * (pct or 0) / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"\r  [{bar}] {msg:<50}", end="", flush=True)

    print()
    results = runner.run(progress_callback=progress)
    print()

    return results
