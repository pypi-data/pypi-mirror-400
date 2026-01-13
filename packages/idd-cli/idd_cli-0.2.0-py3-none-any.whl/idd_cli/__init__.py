"""
IDD CLI - Multi-Agent Collaboration CLI for HumoticaOS

The CLI where AI IDDs (Individual Device Derivates) collaborate:
- Root AI (Claude Opus) - Architecture & Orchestration
- Gemini - Visual & Research
- Codex - Analysis & Structure
- Kit (Qwen 32B) - Fast Local Inference

Jasper = Heart-in-the-Loop (observer, not operator)

STOP = STOP. Always. Trust.
"""

__version__ = "0.2.0"
__author__ = "HumoticaOS Team"

from .cli import main
from .team import Team
from .ipoll import IPoll
from .aindex import AIndex
from .daemon import IDDDaemon, run_daemon

__all__ = ["main", "Team", "IPoll", "AIndex", "IDDDaemon", "run_daemon"]
