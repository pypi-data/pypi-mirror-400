"""
Local Proxy Server for Benchmark

Intercepts API calls from the user's agent, forwards them to real APIs,
and captures metrics for analysis.
"""

import json
import time
import threading
import queue
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class APICall:
    """Record of a single API call."""
    timestamp: str
    provider: str  # openai, anthropic
    endpoint: str
    method: str
    request_body: Dict[str, Any]
    response_body: Dict[str, Any]
    status_code: int
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None


@dataclass
class BenchmarkMetrics:
    """Collected metrics from benchmark run."""
    api_calls: List[APICall] = field(default_factory=list)
    total_requests: int = 0
    total_errors: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_latency_ms: float = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_latency_ms": self.total_latency_ms,
            "avg_latency_ms": self.total_latency_ms / max(self.total_requests, 1),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "api_calls": [
                {
                    "timestamp": c.timestamp,
                    "provider": c.provider,
                    "endpoint": c.endpoint,
                    "latency_ms": c.latency_ms,
                    "input_tokens": c.input_tokens,
                    "output_tokens": c.output_tokens,
                    "status_code": c.status_code,
                    "error": c.error,
                }
                for c in self.api_calls
            ]
        }


class ProxyHandler(BaseHTTPRequestHandler):
    """HTTP handler that proxies requests to OpenAI/Anthropic APIs."""

    metrics: BenchmarkMetrics = None
    openai_key: str = None
    anthropic_key: str = None
    test_queue: queue.Queue = None

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_POST(self):
        """Handle POST requests (API calls)."""
        start_time = time.time()

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length).decode('utf-8')

        try:
            request_json = json.loads(request_body) if request_body else {}
        except json.JSONDecodeError:
            request_json = {"raw": request_body}

        # Determine provider and forward
        provider = self._detect_provider()

        try:
            response_body, status_code = self._forward_request(
                provider, request_body, request_json
            )
            error = None
        except Exception as e:
            response_body = {"error": str(e)}
            status_code = 500
            error = str(e)

        latency_ms = (time.time() - start_time) * 1000

        # Extract token counts
        input_tokens, output_tokens = self._extract_tokens(provider, request_json, response_body)

        # Record the call
        api_call = APICall(
            timestamp=datetime.utcnow().isoformat(),
            provider=provider,
            endpoint=self.path,
            method="POST",
            request_body=request_json,
            response_body=response_body,
            status_code=status_code,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error=error,
        )

        if self.metrics:
            self.metrics.api_calls.append(api_call)
            self.metrics.total_requests += 1
            self.metrics.total_latency_ms += latency_ms
            self.metrics.total_input_tokens += input_tokens
            self.metrics.total_output_tokens += output_tokens
            if error:
                self.metrics.total_errors += 1

        # Send response
        response_bytes = json.dumps(response_body).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response_bytes))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_GET(self):
        """Handle GET requests (health checks, models list)."""
        if self.path == "/health":
            self._send_json({"status": "ok"}, 200)
        elif self.path in ["/v1/models", "/models"]:
            # Return mock models list
            self._send_json({
                "data": [
                    {"id": "gpt-4", "object": "model"},
                    {"id": "gpt-3.5-turbo", "object": "model"},
                ]
            }, 200)
        else:
            self._send_json({"error": "Not found"}, 404)

    def _send_json(self, data: dict, status: int):
        response_bytes = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response_bytes))
        self.end_headers()
        self.wfile.write(response_bytes)

    def _detect_provider(self) -> str:
        """Detect which API provider based on path/headers."""
        if "/v1/messages" in self.path:
            return "anthropic"
        return "openai"

    def _forward_request(
        self, provider: str, raw_body: str, request_json: dict
    ) -> tuple:
        """Forward request to the real API."""

        if provider == "anthropic":
            url = f"https://api.anthropic.com{self.path}"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.anthropic_key or "",
                "anthropic-version": self.headers.get("anthropic-version", "2023-06-01"),
            }
        else:  # openai
            url = f"https://api.openai.com{self.path}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_key or ''}",
            }

        req = Request(url, data=raw_body.encode('utf-8'), headers=headers, method="POST")

        try:
            with urlopen(req, timeout=120) as response:
                response_body = json.loads(response.read().decode('utf-8'))
                return response_body, response.status
        except HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                return json.loads(error_body), e.code
            except:
                return {"error": error_body}, e.code
        except URLError as e:
            return {"error": str(e)}, 500

    def _extract_tokens(
        self, provider: str, request: dict, response: dict
    ) -> tuple:
        """Extract token counts from request/response."""
        input_tokens = 0
        output_tokens = 0

        if provider == "anthropic":
            usage = response.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
        else:  # openai
            usage = response.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

        return input_tokens, output_tokens


class BenchmarkProxy:
    """Manages the local proxy server."""

    def __init__(
        self,
        port: int = 8765,
        openai_key: str = None,
        anthropic_key: str = None,
    ):
        self.port = port
        self.openai_key = openai_key
        self.anthropic_key = anthropic_key
        self.metrics = BenchmarkMetrics()
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start the proxy server in a background thread."""
        # Configure handler class
        ProxyHandler.metrics = self.metrics
        ProxyHandler.openai_key = self.openai_key
        ProxyHandler.anthropic_key = self.anthropic_key

        self.metrics.start_time = datetime.utcnow().isoformat()

        self.server = HTTPServer(('127.0.0.1', self.port), ProxyHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the proxy server."""
        self.metrics.end_time = datetime.utcnow().isoformat()
        if self.server:
            self.server.shutdown()

    def get_metrics(self) -> BenchmarkMetrics:
        """Get collected metrics."""
        return self.metrics

    def get_base_url(self) -> str:
        """Get the proxy base URL."""
        return f"http://127.0.0.1:{self.port}"
