#!/usr/bin/env python3
"""
SudoDog Shadow Agent Scanner CLI

Find AI agents running on your machine that you might not know about.

Usage:
    sudodog-scan              # Scan and show results
    sudodog-scan --json       # Output as JSON
    sudodog-scan --watch      # Continuous monitoring
"""

import argparse
import sys
import time
from typing import Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from .scanner import scan_for_shadow_agents, format_report, export_json, DetectedAgent
from dataclasses import asdict


DEFAULT_API_URL = "https://api.sudodog.com/api/v1"

BANNER = """
┌─────────────────────────────────────────────────────────┐
│  🐕 SudoDog Shadow Agent Scanner                        │
│     Find AI agents you didn't know were running         │
└─────────────────────────────────────────────────────────┘
"""


def report_to_api(agents: list, api_key: str, api_url: str) -> bool:
    """Report discovered agents to SudoDog API."""
    if not HAS_REQUESTS:
        print("Error: 'requests' library required for API reporting.")
        print("Install with: pip install requests")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "agents": [asdict(a) for a in agents],
        "scan_source": "cli_scanner",
    }

    try:
        response = requests.post(
            f"{api_url}/shadow-agents/report",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Reported {len(agents)} agents to SudoDog dashboard")
            return True
        else:
            print(f"⚠️  API error: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Connection error: {e}")
        return False


def watch_mode(interval: int = 30, api_key: Optional[str] = None, api_url: str = DEFAULT_API_URL):
    """Continuously scan for new agents."""
    print(f"Watching for new AI agents (every {interval}s)...")
    print("Press Ctrl+C to stop\n")

    seen_pids = set()

    try:
        while True:
            agents = scan_for_shadow_agents(quiet=True)
            new_agents = [a for a in agents if a.pid not in seen_pids]

            if new_agents:
                print(f"\n🚨 {len(new_agents)} new agent(s) detected!")
                for agent in new_agents:
                    print(f"   • PID {agent.pid}: {agent.suspected_framework} ({agent.process_name})")
                    seen_pids.add(agent.pid)

                if api_key:
                    report_to_api(new_agents, api_key, api_url)
            else:
                print(".", end="", flush=True)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nStopped watching.")
        print(f"Total unique agents seen: {len(seen_pids)}")


def main():
    parser = argparse.ArgumentParser(
        description="Find AI agents running on your machine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudodog-scan                  # Quick scan
  sudodog-scan --json           # JSON output for scripting
  sudodog-scan --watch          # Continuous monitoring
  sudodog-scan --api-key KEY    # Report to SudoDog dashboard

More info: https://sudodog.com/docs
        """
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuously watch for new agents",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Watch interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--api-key",
        metavar="KEY",
        help="Report results to SudoDog dashboard",
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=argparse.SUPPRESS,  # Hidden option for testing
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output",
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="sudodog-scan 2.0.0",
    )

    args = parser.parse_args()

    # Watch mode
    if args.watch:
        if not args.quiet:
            print(BANNER)
        watch_mode(args.interval, args.api_key, args.api_url)
        return 0

    # Normal scan
    if not args.quiet and not args.json:
        print(BANNER)

    agents = scan_for_shadow_agents(quiet=args.json)

    # Output results
    if args.json:
        print(export_json(agents))
    elif not args.quiet:
        print(format_report(agents))
    else:
        # Quiet mode - just counts
        print(f"Found {len(agents)} unmonitored agent(s)")

    # Report to API if requested
    if args.api_key and agents:
        report_to_api(agents, args.api_key, args.api_url)

    # Exit code: 0 if no agents, 1 if agents found (useful for CI/CD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
