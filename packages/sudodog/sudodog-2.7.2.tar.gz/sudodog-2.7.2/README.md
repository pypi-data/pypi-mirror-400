# SudoDog

**Find and monitor AI agents running on your machine.**

```bash
pip install sudodog
sudodog-scan
```

```
┌─────────────────────────────────────────────────────────┐
│  🐕 SudoDog Shadow Agent Scanner                        │
│     Find AI agents you didn't know were running         │
└─────────────────────────────────────────────────────────┘

Scanning for AI agents...
Checking 142 processes...

============================================================
  SHADOW AGENT SCAN REPORT
============================================================
  Unmonitored Agents Found: 2
============================================================

[1] PYTHON (PID 12847)
    Framework:  langchain
    Confidence: [████████░░] 80%
    Command:    python agent.py --model gpt-4

    Why detected:
      • Framework detected: langchain
      • AI API connections: 1

[2] NODE (PID 9123)
    Framework:  unknown
    Confidence: [██████░░░░] 60%
    Command:    node dist/agent-runner.js

    Why detected:
      • Command matches pattern 'agent'
      • AI API connections: 3
```

## What It Does

- **Scans running processes** for AI agent frameworks (LangChain, AutoGPT, CrewAI, etc.)
- **Detects API connections** to OpenAI, Anthropic, and other AI providers
- **Works on macOS, Linux, and Windows**
- **Zero configuration** - just run `sudodog-scan`

## Installation

```bash
pip install sudodog
```

## Commands

### Scan for AI agents

```bash
sudodog-scan              # Quick scan
sudodog-scan --json       # JSON output (for scripts)
sudodog-scan --watch      # Continuous monitoring
```

### Monitor your agents

```bash
# Initialize (optional - for dashboard features)
sudodog init

# Run your agent with monitoring
sudodog run python my_agent.py

# Or integrate with Claude Code
sudodog integrate claude-code
```

## Detected Frameworks

| Framework | Detection Method |
|-----------|------------------|
| LangChain | Process args, imports, env vars |
| AutoGPT | Process args, imports |
| CrewAI | Process args, imports |
| OpenAI Assistants | API connections, imports |
| Anthropic Claude | API connections, imports |
| LlamaIndex | Process args, imports |
| Semantic Kernel | Process args, imports |

## Dashboard (Optional)

See your agents in a web dashboard:

1. Sign up at [dashboard.sudodog.com](https://dashboard.sudodog.com)
2. Get your API key from Settings
3. Run: `sudodog init` and enter your API key
4. Your scans and monitored agents will appear in the dashboard

## Use Cases

- **Security teams**: Find unauthorized AI agents in your environment
- **Developers**: See what AI tools are running and how much they're costing
- **DevOps**: Monitor AI agent health and API usage
- **Compliance**: Audit AI agent activity for regulatory requirements

## Privacy

- Scans run **locally** on your machine
- No data is sent anywhere unless you explicitly use `--api-key`
- Open source: [github.com/SudoDog-official/SudoDog](https://github.com/SudoDog-official/SudoDog)

## Links

- Website: [sudodog.com](https://sudodog.com)
- Dashboard: [dashboard.sudodog.com](https://dashboard.sudodog.com)
- Docs: [sudodog.com/docs](https://sudodog.com/docs)
- GitHub: [github.com/SudoDog-official/SudoDog](https://github.com/SudoDog-official/SudoDog)

## License

MIT
