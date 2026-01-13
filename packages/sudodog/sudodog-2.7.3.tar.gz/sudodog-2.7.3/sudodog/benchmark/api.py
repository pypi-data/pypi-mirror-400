"""
Benchmark API - Communicates with SudoDog backend for analysis.

Privacy Model (Option 3 - Analyze and Forget):
- analyze_benchmark(): Get AI analysis without storing data
- publish_benchmark(): Opt-in to store and appear on leaderboard
- Individual data is NOT stored unless user explicitly publishes
"""

import os
import json
import hashlib
import platform
from typing import Dict, Any, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class BenchmarkAPI:
    """
    API client for the SudoDog benchmark service.

    Privacy model:
    - analyze_benchmark(): Get full Claude analysis, data is NOT stored
    - publish_benchmark(): Opt-in to store results and appear on leaderboard

    Handles:
    - Analyzing benchmark results (without storage)
    - Publishing to leaderboard (opt-in)
    - Rate limiting and error handling
    """

    DEFAULT_API_URL = "https://api.sudodog.com/api/v1"
    TIMEOUT = 30  # seconds

    def __init__(self, api_url: str = None):
        """
        Initialize the API client.

        Args:
            api_url: Override the default API URL (for testing)
        """
        self.api_url = api_url or os.environ.get("SUDODOG_API_URL", self.DEFAULT_API_URL)

    def _get_headers(self, machine_id: str = None) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"sudodog-benchmark/1.0 ({platform.system()})",
        }

        if machine_id:
            headers["X-Machine-ID"] = machine_id

        return headers

    def _make_request(self, endpoint: str, data: Dict = None, method: str = "GET",
                      machine_id: str = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.

        Args:
            endpoint: API endpoint (e.g., "/benchmark")
            data: Request body for POST requests
            method: HTTP method
            machine_id: Machine identifier for rate limiting

        Returns:
            Parsed JSON response

        Raises:
            Exception on network or API errors
        """
        url = f"{self.api_url}{endpoint}"
        headers = self._get_headers(machine_id)

        body = None
        if data:
            body = json.dumps(data).encode('utf-8')

        request = Request(url, data=body, headers=headers, method=method)

        try:
            with urlopen(request, timeout=self.TIMEOUT) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as e:
            # Parse error response if possible
            try:
                error_body = json.loads(e.read().decode('utf-8'))
                error_msg = error_body.get("detail", str(e))
            except:
                error_msg = str(e)

            if e.code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            elif e.code == 400:
                raise Exception(f"Invalid request: {error_msg}")
            else:
                raise Exception(f"API error ({e.code}): {error_msg}")
        except URLError as e:
            raise Exception(f"Network error: {e.reason}")
        except Exception as e:
            raise Exception(f"Request failed: {e}")

    def analyze_benchmark(self, results: Dict[str, Any], machine_id: str) -> Dict[str, Any]:
        """
        Analyze benchmark results WITHOUT storing individual data.

        This is the privacy-first endpoint:
        - Full Claude analysis is performed
        - Only anonymous aggregate stats are stored (for platform improvement)
        - Individual benchmark data is NOT stored
        - Returns full analysis + publish_token for optional leaderboard submission

        Args:
            results: Benchmark results from AgentTester
            machine_id: Unique machine identifier

        Returns:
            Analysis response with score, grade, summary, metrics, and publish_token
        """
        payload = {
            "results": results,
            "machine_id": machine_id,
            "version": "1.0",
        }

        return self._make_request("/benchmark/analyze", data=payload, method="POST", machine_id=machine_id)

    def publish_benchmark(
        self,
        results: Dict[str, Any],
        analysis: Dict[str, Any],
        machine_id: str,
        publish_token: str,
        agent_name: str = None,
        publisher: str = None,
        website: str = None
    ) -> Dict[str, Any]:
        """
        Publish benchmark results to the leaderboard (opt-in).

        Call this AFTER analyze_benchmark() when user explicitly chooses
        to share their results publicly.

        Args:
            results: Original benchmark results
            analysis: Analysis response from analyze_benchmark()
            machine_id: Unique machine identifier
            publish_token: Token from analyze_benchmark() response
            agent_name: Optional friendly name for the agent
            publisher: Optional publisher/author name
            website: Optional website URL

        Returns:
            Response with report_url, badge_url, share_text
        """
        payload = {
            "results": results,
            "analysis": {
                "score": analysis.get("score"),
                "grade": analysis.get("grade"),
                "good": analysis.get("summary", {}).get("good", []),
                "needs_work": analysis.get("summary", {}).get("needs_work", []),
                "recommendations": analysis.get("summary", {}).get("recommendations", []),
            },
            "machine_id": machine_id,
            "publish_token": publish_token,
            "agent_name": agent_name,
            "publisher": publisher,
            "website": website,
        }

        return self._make_request("/benchmark/publish", data=payload, method="POST", machine_id=machine_id)

    def submit_benchmark(self, results: Dict[str, Any], machine_id: str) -> Dict[str, Any]:
        """
        LEGACY: Submit benchmark results for analysis AND storage.

        DEPRECATED: Use analyze_benchmark() + publish_benchmark() instead.
        This method is kept for backwards compatibility only.

        Args:
            results: Benchmark results from AgentTester
            machine_id: Unique machine identifier

        Returns:
            Analysis response with score, report URL, etc.
        """
        payload = {
            "results": results,
            "machine_id": machine_id,
            "version": "1.0",
        }

        return self._make_request("/benchmark/", data=payload, method="POST", machine_id=machine_id)

    def get_report(self, report_id: str) -> Dict[str, Any]:
        """
        Fetch a benchmark report by ID.

        Args:
            report_id: The report identifier

        Returns:
            Report data
        """
        return self._make_request(f"/benchmark/{report_id}")

    def check_rate_limit(self, machine_id: str) -> Dict[str, Any]:
        """
        Check rate limit status for this machine.

        Args:
            machine_id: Machine identifier

        Returns:
            Rate limit info (remaining, reset time, etc.)
        """
        return self._make_request("/benchmark/rate-limit", machine_id=machine_id)


class MockBenchmarkAPI(BenchmarkAPI):
    """
    Mock API for testing and offline mode.
    Returns realistic-looking responses without network calls.
    """

    def analyze_benchmark(self, results: Dict[str, Any], machine_id: str) -> Dict[str, Any]:
        """Return mock analysis results (no storage, privacy-first)."""
        framework = results.get("agent_framework", "unknown")
        estimated_score = results.get("estimated_score", 70)

        # Generate grade
        if estimated_score >= 90:
            grade = "A+"
        elif estimated_score >= 80:
            grade = "A"
        elif estimated_score >= 70:
            grade = "B+"
        elif estimated_score >= 60:
            grade = "B"
        elif estimated_score >= 50:
            grade = "C"
        else:
            grade = "D"

        # Generate a mock publish token
        publish_token = hashlib.sha256(
            f"{framework}:{estimated_score}:{results.get('duration_seconds', 0)}".encode()
        ).hexdigest()[:24]

        return {
            "score": estimated_score,
            "grade": grade,
            "framework": framework,
            "summary": {
                "good": [
                    f"Agent ({framework}) is responding to requests",
                    "Resource usage within normal range",
                    "API connections detected and active",
                ],
                "needs_work": [
                    "Consider implementing retry logic for failed API calls",
                    "Monitor token usage to optimize costs",
                    "Add structured error handling",
                ],
                "recommendations": [
                    f"# Recommended configuration for {framework}",
                    "# Add error handling:",
                    "try:",
                    "    response = agent.run(query)",
                    "except Exception as e:",
                    "    logger.error(f'Agent error: {e}')",
                    "    # Implement retry or fallback",
                ]
            },
            "metrics": {
                "response_time_avg": "1.2s",
                "cpu_usage": f"{results.get('analysis', {}).get('avg_cpu_percent', 0):.1f}%",
                "memory_peak": f"{results.get('analysis', {}).get('max_memory_mb', 0):.1f}MB",
                "api_calls": results.get('analysis', {}).get('total_api_calls', 0),
            },
            "publish_token": publish_token,
            "offline": True,
        }

    def publish_benchmark(
        self,
        results: Dict[str, Any],
        analysis: Dict[str, Any],
        machine_id: str,
        publish_token: str,
        agent_name: str = None,
        publisher: str = None,
        website: str = None
    ) -> Dict[str, Any]:
        """Return mock publish response."""
        result_hash = hashlib.sha256(
            json.dumps(results, sort_keys=True).encode()
        ).hexdigest()[:12]

        framework = results.get("agent_framework", "unknown")
        score = analysis.get("score", 70)
        grade = analysis.get("grade", "B")

        return {
            "id": result_hash,
            "report_url": f"https://sudodog.com/report/{result_hash}",
            "badge_url": f"https://sudodog.com/badge/{result_hash}",
            "share_text": f"My {framework} agent scored {score}/100 ({grade}) on SudoDog Benchmark!",
        }

    def submit_benchmark(self, results: Dict[str, Any], machine_id: str) -> Dict[str, Any]:
        """LEGACY: Return mock analysis results with storage."""
        # Generate a deterministic ID from results
        result_hash = hashlib.sha256(
            json.dumps(results, sort_keys=True).encode()
        ).hexdigest()[:12]

        framework = results.get("agent_framework", "unknown")
        estimated_score = results.get("estimated_score", 70)

        # Generate grade
        if estimated_score >= 90:
            grade = "A+"
        elif estimated_score >= 80:
            grade = "A"
        elif estimated_score >= 70:
            grade = "B+"
        elif estimated_score >= 60:
            grade = "B"
        elif estimated_score >= 50:
            grade = "C"
        else:
            grade = "D"

        return {
            "id": result_hash,
            "score": estimated_score,
            "grade": grade,
            "framework": framework,
            "summary": {
                "good": [
                    f"Agent ({framework}) is responding to requests",
                    "Resource usage within normal range",
                    "API connections detected and active",
                ],
                "needs_work": [
                    "Consider implementing retry logic for failed API calls",
                    "Monitor token usage to optimize costs",
                    "Add structured error handling",
                ],
                "recommendations": [
                    f"# Recommended configuration for {framework}",
                    "# Add error handling:",
                    "try:",
                    "    response = agent.run(query)",
                    "except Exception as e:",
                    "    logger.error(f'Agent error: {e}')",
                    "    # Implement retry or fallback",
                ]
            },
            "metrics": {
                "response_time_avg": "1.2s",
                "cpu_usage": f"{results.get('analysis', {}).get('avg_cpu_percent', 0):.1f}%",
                "memory_peak": f"{results.get('analysis', {}).get('max_memory_mb', 0):.1f}MB",
                "api_calls": results.get('analysis', {}).get('total_api_calls', 0),
            },
            "report_url": f"https://sudodog.com/report/{result_hash}",
            "badge_url": f"https://sudodog.com/badge/{result_hash}",
            "share_text": f"My {framework} agent scored {estimated_score}/100 ({grade}) on SudoDog Benchmark!",
            "offline": False,
        }
