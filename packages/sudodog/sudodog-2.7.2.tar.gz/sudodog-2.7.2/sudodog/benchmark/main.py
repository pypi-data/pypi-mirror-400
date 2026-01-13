#!/usr/bin/env python3
"""
SudoDog Benchmark - AI Agent Testing Tool

Usage:
    sudodog-benchmark              Run interactive benchmark
    sudodog-benchmark --help       Show help
    sudodog-benchmark --version    Show version
"""

import sys
import os
import time
import json
import hashlib
import platform
import argparse
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sudodog.scanner.scanner import scan_for_shadow_agents, DetectedAgent
from sudodog.benchmark.tester import AgentTester
from sudodog.benchmark.api import BenchmarkAPI
from sudodog.benchmark.display import Display
from sudodog.benchmark.runner import BenchmarkRunner, BenchmarkConfig, BenchmarkResults

VERSION = "2.7.0"

# ASCII Art Banner
BANNER = r"""
   _____ __  ______  ____  ____  ____  ______
  / ___// / / / __ \/ __ \/ __ \/ __ \/ ____/
  \__ \/ / / / / / / / / / / / / / / / / __
 ___/ / /_/ / /_/ / /_/ / /_/ / /_/ / /_/ /
/____/\____/_____/\____/\____/\____/\____/

         B E N C H M A R K   v{version}
"""


def get_machine_id() -> str:
    """Generate a unique machine identifier for rate limiting."""
    try:
        node = str(platform.node())
        mac = str(hex(uuid.getnode())) if 'uuid' in dir() else ''
        system = platform.system()
        machine = platform.machine()

        raw_id = f"{node}-{mac}-{system}-{machine}"
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16]
    except:
        return hashlib.sha256(os.urandom(32)).hexdigest()[:16]


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def select_agent(agents: List[DetectedAgent]) -> Optional[DetectedAgent]:
    """Let user select an agent to benchmark."""
    display = Display()

    if not agents:
        display.warning("No AI agents detected running on this machine.")
        display.info("\nMake sure your agent is running, then try again.")
        display.info("Tip: Start your agent in another terminal window first.")
        return None

    display.header("DETECTED AGENTS")
    print()

    for i, agent in enumerate(agents, 1):
        conf_pct = int(agent.confidence * 100)
        conf_bar = display.progress_bar(conf_pct, 100, width=10)

        print(f"  [{i}] {agent.suspected_framework.upper()}")
        print(f"      PID: {agent.pid}")
        print(f"      Confidence: {conf_bar} {conf_pct}%")
        print(f"      Command: {agent.command_line[:50]}{'...' if len(agent.command_line) > 50 else ''}")
        print()

    while True:
        try:
            choice = input(f"  Select agent to benchmark (1-{len(agents)}) or 'q' to quit: ").strip()

            if choice.lower() == 'q':
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(agents):
                return agents[idx]
            else:
                print(f"  Please enter a number between 1 and {len(agents)}")
        except ValueError:
            print("  Please enter a valid number")
        except (EOFError, KeyboardInterrupt):
            return None


def create_agent_from_pid(pid: int) -> Optional[DetectedAgent]:
    """Create a DetectedAgent from a PID."""
    try:
        if sys.platform == "linux":
            with open(f'/proc/{pid}/cmdline', 'r') as f:
                cmdline = f.read().replace('\x00', ' ').strip()
            with open(f'/proc/{pid}/comm', 'r') as f:
                comm = f.read().strip()

            # Try to detect framework from command line or environment
            framework = detect_framework_from_pid(pid, cmdline)

            return DetectedAgent(
                pid=pid,
                process_name=comm,
                command_line=cmdline,
                suspected_framework=framework,
                confidence=0.8,
                indicators=["Manually specified via --agent-pid"]
            )
        else:
            # For other platforms, create minimal agent
            return DetectedAgent(
                pid=pid,
                process_name="unknown",
                command_line="",
                suspected_framework="unknown",
                confidence=0.5,
                indicators=["Manually specified via --agent-pid"]
            )
    except (FileNotFoundError, PermissionError) as e:
        return None


def detect_framework_from_pid(pid: int, cmdline: str) -> str:
    """Detect the AI framework from process environment and command line."""
    cmdline_lower = cmdline.lower()

    # Check command line patterns
    framework_keywords = {
        'langchain': ['langchain', 'langsmith'],
        'autogpt': ['autogpt', 'auto-gpt', 'autogen'],
        'crewai': ['crewai', 'crew_ai'],
        'claude': ['claude', 'anthropic'],
        'openai': ['openai', 'gpt-4', 'gpt-3'],
        'llama': ['llama', 'llama_index', 'llamaindex'],
    }

    for framework, keywords in framework_keywords.items():
        for keyword in keywords:
            if keyword in cmdline_lower:
                return framework

    # Check environment variables on Linux
    try:
        if sys.platform == "linux":
            with open(f'/proc/{pid}/environ', 'r') as f:
                environ = f.read()

            env_framework_map = {
                'LANGCHAIN_API_KEY': 'langchain',
                'LANGCHAIN_TRACING': 'langchain',
                'OPENAI_API_KEY': 'openai',
                'ANTHROPIC_API_KEY': 'claude',
                'AUTOGEN_': 'autogpt',
            }

            for env_var, framework in env_framework_map.items():
                if env_var in environ:
                    return framework
    except:
        pass

    return "unknown"


def run_benchmark(agent: DetectedAgent, display: Display, duration: int = 30) -> Optional[Dict[str, Any]]:
    """Run the benchmark test on the selected agent."""
    display.header("RUNNING BENCHMARK")
    print()

    tester = AgentTester(agent)

    # Phase 1: Capture baseline
    display.status("Analyzing agent configuration...")
    time.sleep(0.5)
    config = tester.analyze_config()
    display.success("Configuration analyzed")

    # Phase 2: Monitor behavior
    display.status(f"Monitoring agent behavior ({duration} seconds)...")
    print()
    print("  Tip: Interact with your agent now to generate test data!")
    print()

    # Show countdown using the duration parameter
    for remaining in range(duration, 0, -1):
        progress = ((duration - remaining) / duration) * 100
        bar = display.progress_bar(int(progress), 100, width=30)
        print(f"\r  {bar} {remaining}s remaining  ", end='', flush=True)

        # Capture metrics during monitoring
        tester.capture_metrics()
        time.sleep(1)

    print()
    display.success("Behavior monitoring complete")

    # Phase 3: Collect results
    display.status("Collecting results...")
    results = tester.get_results()
    display.success("Results collected")

    return results


def analyze_locally(results: Dict[str, Any]) -> Dict[str, Any]:
    """Perform local analysis based on actual metrics."""
    # The analysis data is in results["analysis"], not results["metrics"]
    # results["metrics"] is a list of raw metric snapshots
    analysis = results.get("analysis", {})

    good = []
    needs_work = []
    score = 70  # Base score

    # Analyze CPU usage
    cpu_avg = analysis.get("avg_cpu_percent", 0)
    if cpu_avg < 20:
        good.append("Low CPU usage - efficient processing")
        score += 5
    elif cpu_avg > 50:
        needs_work.append(f"High CPU usage ({cpu_avg:.1f}%) - consider optimization")
        score -= 5

    # Analyze memory usage
    memory_mb = analysis.get("max_memory_mb", 0)
    if memory_mb < 200:
        good.append("Low memory footprint")
        score += 5
    elif memory_mb > 500:
        needs_work.append(f"High memory usage ({memory_mb:.0f}MB) - check for memory leaks")
        score -= 5

    # Analyze network connections
    network_conns = analysis.get("avg_connections", 0)
    if network_conns > 0:
        good.append(f"Active API connections ({int(network_conns)})")
        score += 5
    else:
        needs_work.append("No API connections detected during monitoring")

    # Analyze API calls
    api_calls = analysis.get("total_api_calls", 0)
    if api_calls > 0:
        good.append(f"Made {api_calls} API calls during test")
        score += 5

    # Check if process was stable
    samples = analysis.get("metric_samples", 0)
    if samples > 25:
        good.append("Agent remained stable during monitoring")
        score += 5
    elif samples < 10:
        needs_work.append("Agent may have crashed or stopped during monitoring")
        score -= 10

    # Default messages if no specific issues found
    if not good:
        good.append("Benchmark completed successfully")
    if not needs_work:
        needs_work.append("Consider running a longer benchmark for more detailed analysis")

    # Clamp score
    score = max(20, min(95, score))

    # Calculate grade
    if score >= 90: grade = "A+"
    elif score >= 85: grade = "A"
    elif score >= 80: grade = "B+"
    elif score >= 75: grade = "B"
    elif score >= 70: grade = "C+"
    elif score >= 65: grade = "C"
    elif score >= 60: grade = "D"
    else: grade = "F"

    return {
        "id": hashlib.sha256(json.dumps(results).encode()).hexdigest()[:12],
        "score": score,
        "grade": grade,
        "summary": {
            "good": good,
            "needs_work": needs_work
        },
        "report_url": None,
        "badge_url": None,
        "offline": True
    }


def submit_results(results: Dict[str, Any], machine_id: str, display: Display) -> Optional[Dict[str, Any]]:
    """
    Analyze benchmark results using SudoDog API (privacy-first).

    This uses the new analyze-and-forget flow:
    - Results are analyzed by AI
    - Only anonymous aggregate stats are stored
    - Individual data is NOT stored
    - User can optionally publish to leaderboard later
    """
    display.status("Analyzing with AI...")
    display.info("(Your data is analyzed but NOT stored - see privacy policy)")

    api = BenchmarkAPI()

    try:
        response = api.analyze_benchmark(results, machine_id)
        display.success("Analysis complete!")
        return response
    except Exception as e:
        display.error(f"Failed to analyze results: {e}")
        display.info("Running local analysis instead...")
        return analyze_locally(results)


def prompt_for_publish(
    results: Dict[str, Any],
    analysis: Dict[str, Any],
    machine_id: str,
    display: Display
) -> Optional[Dict[str, Any]]:
    """
    Prompt user to optionally publish results to the leaderboard.

    This is the opt-in step - data is only stored if user agrees.
    """
    print()
    display.header("PUBLISH TO LEADERBOARD?")
    print()
    print("  Your benchmark has been analyzed. Would you like to publish")
    print("  your results to the public leaderboard?")
    print()
    print("  What will be shared:")
    print("    - Agent framework and type")
    print("    - Score and grade")
    print("    - Performance metrics (latency, tokens, etc.)")
    print()
    print("  What will NOT be shared:")
    print("    - Your prompts or responses")
    print("    - Your API keys")
    print("    - Your source code")
    print()

    # Get user choice
    while True:
        choice = input("  Publish to leaderboard? [Y]es / [N]o / [V]iew data: ").strip().lower()

        if choice in ['y', 'yes']:
            # Ask for optional metadata
            print()
            agent_name = input("  Agent name (optional, press Enter to skip): ").strip() or None
            publisher = input("  Your name/company (optional): ").strip() or None
            website = input("  Website URL (optional): ").strip() or None

            display.status("Publishing to leaderboard...")
            api = BenchmarkAPI()

            try:
                publish_token = analysis.get("publish_token", "")
                pub_response = api.publish_benchmark(
                    results=results,
                    analysis=analysis,
                    machine_id=machine_id,
                    publish_token=publish_token,
                    agent_name=agent_name,
                    publisher=publisher,
                    website=website,
                )
                display.success("Published to leaderboard!")
                return pub_response
            except Exception as e:
                display.error(f"Failed to publish: {e}")
                return None

        elif choice in ['n', 'no']:
            print()
            display.info("Results not published. Your data was analyzed and forgotten.")
            return None

        elif choice in ['v', 'view']:
            print()
            print("  Data that would be shared:")
            print(f"    Framework: {results.get('agent_framework', 'unknown')}")
            print(f"    Agent Type: {results.get('agent_type', 'general')}")
            print(f"    Score: {analysis.get('score', 0)}/100 ({analysis.get('grade', '?')})")
            print(f"    Duration: {results.get('duration_seconds', 0):.1f}s")
            raw_analysis = results.get("analysis", {})
            print(f"    API Calls: {raw_analysis.get('total_api_calls', 0)}")
            print(f"    Total Tokens: {raw_analysis.get('total_tokens', 0)}")
            print()
        else:
            print("  Please enter Y, N, or V")


def show_results(response: Dict[str, Any], display: Display, published: Dict[str, Any] = None):
    """Display the benchmark results."""
    print()
    display.header("BENCHMARK RESULTS")
    print()

    score = response.get("score", 0)
    grade = response.get("grade", "?")

    # Score visualization
    score_bar = display.progress_bar(score, 100, width=30)

    print(f"  Overall Score: {score}/100 ({grade})")
    print(f"  {score_bar}")
    print()

    # Good things
    summary = response.get("summary", {})
    good = summary.get("good", [])
    if good:
        display.success("What's working well:")
        for item in good:
            print(f"    + {item}")
        print()

    # Needs improvement
    needs_work = summary.get("needs_work", [])
    if needs_work:
        display.warning("Areas for improvement:")
        for item in needs_work:
            print(f"    - {item}")
        print()

    # Show publish results if available
    if published:
        print()
        display.header("YOUR LEADERBOARD ENTRY")
        print()
        report_url = published.get("report_url")
        badge_url = published.get("badge_url")
        if report_url:
            print(f"  Full Report:  {report_url}")
        if badge_url:
            print(f"  Get Badge:    {badge_url}")
        print()
        print("  Share your score on Twitter!")
        share_text = published.get("share_text", "")
        if share_text:
            print(f"  \"{share_text}\"")
    elif response.get("offline"):
        print()
        display.header("NEXT STEPS")
        print()
        print("  You're in offline mode. Connect to the internet for:")
        print("    - Detailed AI-powered analysis")
        print("    - Shareable report link")
        print("    - Certification badge")
        print()
        print("  Visit: https://sudodog.com")
    else:
        # Analysis done but not published
        print()
        display.header("NEXT STEPS")
        print()
        print("  Your results were analyzed but not published.")
        print("  Run again with --publish to share on the leaderboard.")
        print()
        print("  Monitor your agents: https://sudodog.com/dashboard")


def run_automated_benchmark(
    command: str,
    framework: str,
    display: Display,
    quick: bool = False,
    agent_type: str = "general",
    agent_name: Optional[str] = None,
    publisher: Optional[str] = None,
    website: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Run the new automated benchmark that launches and tests the agent."""
    display.header("AUTOMATED BENCHMARK")
    print()

    # Get API keys from environment (optional - for measuring token usage)
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    config = BenchmarkConfig(
        agent_command=command,
        framework=framework,
        agent_type=agent_type,
        quick_mode=quick,
        openai_key=openai_key,
        anthropic_key=anthropic_key,
        agent_name=agent_name,
        publisher=publisher,
        website=website,
    )

    runner = BenchmarkRunner(config)

    def progress(msg, pct):
        if pct is not None:
            bar = display.progress_bar(int(pct), 100, width=30)
            print(f"\r  {bar} {msg:<45}", end='', flush=True)
        else:
            print(f"\r  {msg:<60}", end='', flush=True)

    display.status(f"Starting agent: {command[:50]}...")
    print()

    results = runner.run(progress_callback=progress)
    print()
    print()

    if results.error:
        display.error(f"Benchmark failed: {results.error}")
        return None

    # Convert results to format expected by submit_results
    return {
        "agent_framework": results.config.framework,
        "agent_command": results.config.agent_command,
        "agent_type": results.config.agent_type,
        "agent_name": results.config.agent_name,
        "publisher": results.config.publisher,
        "website": results.config.website,
        "duration_seconds": results.duration_seconds,
        "analysis": {
            "overall_score": results.overall_score,
            "overall_grade": results.overall_grade,
            "category_scores": results.category_scores,
            "total_requests": results.proxy_metrics.get("total_requests", 0),
            "total_tokens": results.proxy_metrics.get("total_input_tokens", 0) + results.proxy_metrics.get("total_output_tokens", 0),
            "avg_latency_ms": results.proxy_metrics.get("avg_latency_ms", 0),
            "test_results": [
                {
                    "id": r.challenge_id,
                    "passed": r.passed,
                    "latency_ms": r.latency_ms,
                    "tokens": r.tokens_used,
                }
                for r in results.test_results
            ],
        },
        "estimated_score": results.overall_score,
    }


def show_automated_results(results: BenchmarkResults, response: Dict[str, Any], display: Display):
    """Display results from automated benchmark."""
    print()
    display.header("BENCHMARK RESULTS")
    print()

    score = response.get("score", results.overall_score)
    grade = response.get("grade", results.overall_grade)

    # Score visualization
    score_bar = display.progress_bar(score, 100, width=30)

    print(f"  Overall Score: {score}/100 ({grade})")
    print(f"  {score_bar}")
    print()

    # Category breakdown
    if results.category_scores:
        print("  Category Breakdown:")
        for cat, data in results.category_scores.items():
            cat_pct = data.get("percentage", 0)
            cat_bar = display.progress_bar(int(cat_pct), 100, width=15)
            print(f"    {cat.capitalize():<12} {cat_bar} {cat_pct:.0f}%")
        print()

    # API metrics
    metrics = results.proxy_metrics
    if metrics.get("total_requests", 0) > 0:
        print("  Performance Metrics:")
        print(f"    API Calls:      {metrics.get('total_requests', 0)}")
        print(f"    Total Tokens:   {metrics.get('total_input_tokens', 0) + metrics.get('total_output_tokens', 0)}")
        print(f"    Avg Latency:    {metrics.get('avg_latency_ms', 0):.0f}ms")
        print(f"    Errors:         {metrics.get('total_errors', 0)}")
        print()

    # Good things
    summary = response.get("summary", {})
    good = summary.get("good", [])
    if good:
        display.success("What's working well:")
        for item in good:
            print(f"    + {item}")
        print()

    # Needs improvement
    needs_work = summary.get("needs_work", [])
    if needs_work:
        display.warning("Areas for improvement:")
        for item in needs_work:
            print(f"    - {item}")
        print()

    # Links
    report_url = response.get("report_url")
    badge_url = response.get("badge_url")

    print()
    display.header("NEXT STEPS")
    print()

    if response.get("offline"):
        print("  Running in offline mode.")
        print("  Connect to internet for AI-powered analysis.")
    else:
        if report_url:
            print(f"  Full Report:  {report_url}")
        if badge_url:
            print(f"  Get Badge:    {badge_url}")
        print()
        print("  Share your score on Twitter!")


def wait_for_exit():
    """Wait for user input before exiting (for Windows users)."""
    if os.name == 'nt':  # Windows
        print()
        input("  Press Enter to exit...")


def main():
    """Main entry point for the benchmark tool."""
    parser = argparse.ArgumentParser(
        description="SudoDog Benchmark - Test and score your AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudodog-benchmark                              Interactive mode (prompts for command)
  sudodog-benchmark --command "python agent.py"  Automated benchmark
  sudodog-benchmark --quick                      Run quick test suite
  sudodog-benchmark --json                       Output results as JSON
  sudodog-benchmark --no-submit                  Run locally without API submission
  sudodog-benchmark --agent-pid 12345            Monitor existing process (legacy mode)
        """
    )
    parser.add_argument('--version', action='version', version=f'sudodog-benchmark {VERSION}')
    parser.add_argument('--command', '-c', type=str, help='Command to start your agent (triggers automated benchmark)')
    parser.add_argument('--framework', '-f', type=str, default='unknown', help='Agent framework (langchain, autogen, crewai, etc.)')
    parser.add_argument('--type', '-t', type=str, default='general',
                        choices=['chat', 'code', 'data', 'task', 'general'],
                        help='Agent type for weighted scoring (chat, code, data, task, general)')
    parser.add_argument('--name', type=str, help='Agent name (shown on leaderboard)')
    parser.add_argument('--publisher', type=str, help='Publisher/author name (shown on leaderboard)')
    parser.add_argument('--website', type=str, help='Website URL (shown on leaderboard)')
    parser.add_argument('--quick', '-q', action='store_true', help='Run quick test suite (fewer tests)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--no-submit', action='store_true', help='Run locally without API submission')
    parser.add_argument('--duration', type=int, default=30, help='Monitoring duration in seconds (legacy mode)')
    parser.add_argument('--agent-pid', type=int, help='PID of agent to benchmark (legacy mode)')

    args = parser.parse_args()

    # JSON mode implies non-interactive
    non_interactive = args.json

    display = Display()
    machine_id = get_machine_id()

    # Show banner
    if not args.json:
        clear_screen()
        print(BANNER.format(version=VERSION))
        print()

    try:
        # NEW AUTOMATED BENCHMARK MODE
        # Triggered by --command or interactive prompt
        if args.command or (not args.agent_pid and not args.json):
            command = args.command

            # If no command provided, prompt for it
            if not command:
                print("  What command starts your agent?")
                print("  (e.g., 'python my_agent.py' or 'node agent.js')")
                print()
                try:
                    command = input("  > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n  Benchmark cancelled.")
                    wait_for_exit()
                    return 0

                if not command:
                    display.error("No command provided.")
                    wait_for_exit()
                    return 1

                print()

                # Ask for agent type
                print("  What type of agent is this?")
                print("    [1] Chat/Support - conversational agents, chatbots")
                print("    [2] Code Assistant - coding helpers, code generation")
                print("    [3] Data/Research - analysis, research, data processing")
                print("    [4] Task Automation - workflows, automation, task execution")
                print("    [5] General Purpose - balanced testing (default)")
                print()
                try:
                    type_choice = input("  > ").strip()
                    type_map = {'1': 'chat', '2': 'code', '3': 'data', '4': 'task', '5': 'general'}
                    args.type = type_map.get(type_choice, type_choice.lower() if type_choice else 'general')
                except (EOFError, KeyboardInterrupt):
                    args.type = 'general'
                print()

                # Ask for framework if not specified
                if args.framework == 'unknown':
                    print("  What framework does your agent use?")
                    print("  (langchain, autogen, crewai, openai, anthropic, or press Enter for 'unknown')")
                    print()
                    try:
                        framework = input("  > ").strip().lower() or 'unknown'
                    except (EOFError, KeyboardInterrupt):
                        framework = 'unknown'
                    args.framework = framework
                    print()

                # Optional metadata for leaderboard
                print("  ─── Optional: Leaderboard Info ───")
                print("  (This info will appear on the public benchmark leaderboard)")
                print()

                try:
                    print("  Agent name (or press Enter to skip):")
                    args.name = input("  > ").strip() or None

                    print("  Publisher/Author name (or press Enter to skip):")
                    args.publisher = input("  > ").strip() or None

                    print("  Website URL (or press Enter to skip):")
                    args.website = input("  > ").strip() or None
                except (EOFError, KeyboardInterrupt):
                    pass
                print()

            # Run the automated benchmark
            results_data = run_automated_benchmark(
                command=command,
                framework=args.framework,
                display=display,
                quick=args.quick,
                agent_type=args.type,
                agent_name=args.name,
                publisher=args.publisher,
                website=args.website,
            )

            if not results_data:
                wait_for_exit()
                return 1

            # Analyze results (privacy-first: analyze but don't store)
            if args.no_submit:
                response = analyze_locally(results_data)
                published = None
            else:
                response = submit_results(results_data, machine_id, display)

                # Prompt for optional publish to leaderboard
                if not response.get("offline"):
                    published = prompt_for_publish(results_data, response, machine_id, display)
                else:
                    published = None

            # Show results
            if args.json:
                output = response.copy()
                if published:
                    output["published"] = published
                print(json.dumps(output, indent=2))
            else:
                show_results(response, display, published)
                print()
                wait_for_exit()

            return 0

        # LEGACY MODE: If PID specified, use that directly
        if args.agent_pid:
            agent = create_agent_from_pid(args.agent_pid)
            if not agent:
                if args.json:
                    print(json.dumps({"error": f"Process {args.agent_pid} not found or not accessible"}))
                else:
                    display.error(f"Process {args.agent_pid} not found or not accessible")
                    wait_for_exit()
                return 1
            if not args.json:
                display.success(f"Using specified agent: {agent.suspected_framework} (PID {agent.pid})")
        else:
            # Step 1: Scan for agents
            if not args.json:
                display.status("Scanning for AI agents...")

            agents = scan_for_shadow_agents(quiet=True)

            if not args.json:
                display.success(f"Found {len(agents)} agent(s)")
                print()

            # Step 2: Select agent
            if len(agents) == 0:
                if args.json:
                    print(json.dumps({"error": "No agents detected"}))
                else:
                    display.warning("No AI agents detected!")
                    print()
                    print("  Make sure your agent is running before starting the benchmark.")
                    print("  Start your agent in another terminal, then run this tool again.")
                    print()
                    print("  Tip: Use --agent-pid <PID> to benchmark a specific process.")
                    print()
                    wait_for_exit()
                return 1

            if len(agents) == 1:
                agent = agents[0]
                if not args.json:
                    display.info(f"Auto-selected: {agent.suspected_framework} (PID {agent.pid})")
            else:
                if args.json:
                    # In JSON mode with multiple agents, just use first one
                    agent = agents[0]
                else:
                    agent = select_agent(agents)
                    if not agent:
                        print("\n  Benchmark cancelled.")
                        wait_for_exit()
                        return 0

        if not args.json:
            print()

        # Step 3: Run benchmark with specified duration
        results = run_benchmark(agent, display, duration=args.duration)

        if not results:
            if args.json:
                print(json.dumps({"error": "Benchmark failed"}))
            else:
                display.error("Benchmark failed to complete")
                wait_for_exit()
            return 1

        # Step 4: Analyze results (privacy-first: analyze but don't store)
        if not args.json:
            print()

        if args.no_submit:
            response = analyze_locally(results)
            published = None
        else:
            response = submit_results(results, machine_id, display)

            # Prompt for optional publish to leaderboard
            if not response.get("offline"):
                published = prompt_for_publish(results, response, machine_id, display)
            else:
                published = None

        # Step 5: Show results
        if args.json:
            output = response.copy()
            if published:
                output["published"] = published
            print(json.dumps(output, indent=2))
        else:
            show_results(response, display, published)
            print()
            wait_for_exit()

        return 0

    except KeyboardInterrupt:
        if not args.json:
            print("\n\n  Benchmark cancelled.")
            wait_for_exit()
        return 0
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            display.error(f"An error occurred: {e}")
            wait_for_exit()
        return 1


if __name__ == "__main__":
    sys.exit(main())
