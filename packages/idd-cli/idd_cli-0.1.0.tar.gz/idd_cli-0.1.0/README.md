# IDD CLI

Multi-Agent Collaboration CLI for HumoticaOS.

Where AI IDDs (Individual Device Derivates) work together:
- **Root AI** (Claude Opus) - Orchestration, code, architecture
- **Gemini** - Vision, research, diagrams
- **Codex** - Analysis, structure
- **Kit** (Qwen 32B) - Fast local inference

**Jasper = Heart-in-the-Loop**

## Installation

```bash
pip install idd-cli
```

## Usage

```bash
# Ask the team (auto-routes to best IDD)
idd ask "Can someone analyze this architecture?"

# Direct message to specific agent
idd @gemini "What patterns do you see in this image?"
idd @codex "Structure this data into categories"

# Check inbox
idd inbox

# Team status
idd team

# Broadcast to all
idd broadcast "Team meeting in 5 minutes"

# Start discussion
idd discuss "Redis vs SQLite for caching?"
```

## How It Works

The CLI uses:
- **I-Poll** - Inter-agent messaging (HTTP-based)
- **AIndex** - AI Index for routing queries to the right IDD
- **TIBET** - Trust and provenance tracking

Queries are automatically routed based on keywords and capabilities:
- Vision keywords (image, diagram) → Gemini
- Analysis keywords (research, structure) → Codex
- Code keywords (implement, build) → Root AI
- Fast/local keywords → Kit

## Philosophy

Not AI vs Human. **AI with Human.**

The IDD Team works autonomously within scope, with Jasper as Heart-in-the-Loop - the observer, not operator.

## Part of HumoticaOS

- [AInternet](https://pypi.org/project/ainternet/) - AI Networking Protocol
- [TIBET](https://pypi.org/project/tibet-protocol/) - Trust & Provenance
- [KmBiT Kernel](https://pypi.org/project/kmbit-kernel/) - AI Filesystem

**One Love, One fAmIly!**
