"""
IDD CLI - Multi-Agent Collaboration Interface.

Usage:
    idd ask "Can someone analyze this architecture?"
    idd @gemini "What patterns do you see in this image?"
    idd @codex "Structure this data into categories"
    idd inbox
    idd team
    idd broadcast "Team meeting in 5 minutes"
    idd discuss "Should we use Redis or SQLite for caching?"
"""

import sys
import json
from typing import List, Optional
from .team import Team
from .ipoll import IPoll


def print_header():
    """Print CLI header."""
    print("""
 ___ ___  ___     ___ _    ___
|_ _|   \\|   \\   / __| |  |_ _|
 | || |) | |) | | (__| |__ | |
|___|___/|___/   \\___|____|___|

HumoticaOS Multi-Agent CLI v0.1.0
One Love, One fAmIly!
""")


def cmd_ask(team: Team, args: List[str]) -> None:
    """Ask the team a question (auto-routes)."""
    if not args:
        print("Usage: idd ask <question>")
        return

    query = " ".join(args)
    result = team.ask(query)

    if result.success:
        print(f"Routed to: {result.agent}")
        print(f"Status: {result.content}")
    else:
        print(f"Failed: {result.content}")


def cmd_direct(team: Team, agent: str, args: List[str]) -> None:
    """Send direct message to an agent."""
    if not args:
        print(f"Usage: idd @{agent} <message>")
        return

    message = " ".join(args)
    result = team.ask_agent(agent, message)

    if result.success:
        print(f"Sent to {agent}")
    else:
        print(f"Failed: {result.content}")


def cmd_inbox(team: Team, args: List[str]) -> None:
    """Check inbox for messages."""
    limit = int(args[0]) if args else 10
    messages = team.check_inbox(limit=limit)

    if not messages:
        print("Inbox empty")
        return

    print(f"Found {len(messages)} message(s):\n")
    for msg in messages:
        print(f"From: {msg.from_agent}")
        print(f"Type: {msg.poll_type}")
        print(f"Time: {msg.created_at}")
        print(f"Content: {msg.content[:200]}...")
        print("-" * 40)


def cmd_team(team: Team, args: List[str]) -> None:
    """Show team status."""
    status = team.team_status()

    print("IDD Team Status:")
    print("-" * 50)
    for agent_id, info in status.items():
        health_icon = {"ok": "+", "degraded": "~", "unknown": "?", "planned": "-"}.get(
            info["health"], "?"
        )
        print(f"[{health_icon}] {info['name']:<12} | {info['role'][:40]}")
    print("-" * 50)


def cmd_broadcast(team: Team, args: List[str]) -> None:
    """Broadcast message to all team members."""
    if not args:
        print("Usage: idd broadcast <message>")
        return

    message = " ".join(args)
    results = team.broadcast(message)

    sent = sum(1 for r in results if r.success)
    print(f"Broadcast sent to {sent}/{len(results)} team members")


def cmd_discuss(team: Team, args: List[str]) -> None:
    """Start a team discussion."""
    if not args:
        print("Usage: idd discuss <topic>")
        return

    topic = " ".join(args)
    results = team.discuss(topic)

    print(f"Discussion started: {topic}")
    sent = sum(1 for r in results if r.success)
    print(f"Invited {sent} team members")


def cmd_route(team: Team, args: List[str]) -> None:
    """Show which agent would handle a query."""
    if not args:
        print("Usage: idd route <query>")
        return

    query = " ".join(args)
    target = team.route(query)
    print(f"Would route to: {target}")


def cmd_status(team: Team, args: List[str]) -> None:
    """Show I-Poll system status."""
    status = team.ipoll.status()
    print(json.dumps(status, indent=2))


def cmd_help() -> None:
    """Show help."""
    print("""
IDD CLI Commands:

  ask <question>       Ask the team (auto-routes to best IDD)
  @<agent> <message>   Direct message to specific agent
  inbox [limit]        Check your inbox
  team                 Show team status
  broadcast <message>  Send to all team members
  discuss <topic>      Start team discussion
  route <query>        Show routing destination
  status               I-Poll system status
  help                 This help

Examples:
  idd ask "Who can review this architecture?"
  idd @gemini "Analyze this diagram"
  idd @codex "Structure these findings"
  idd broadcast "AIndex v0.2 is ready for review"
  idd discuss "Redis vs SQLite for caching"

Team Members:
  root_ai   - Orchestration, code, architecture
  gemini    - Vision, research, diagrams
  codex     - Analysis, structure (no code)
  kit       - Fast local inference (Qwen 32B)

Heart-in-the-Loop: Jasper
""")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print_header()
        cmd_help()
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    # Handle direct agent messages (@agent)
    if command.startswith("@"):
        agent = command[1:]
        with Team() as team:
            cmd_direct(team, agent, args)
        return

    # Regular commands
    with Team() as team:
        if command == "ask":
            cmd_ask(team, args)
        elif command == "inbox":
            cmd_inbox(team, args)
        elif command == "team":
            cmd_team(team, args)
        elif command == "broadcast":
            cmd_broadcast(team, args)
        elif command == "discuss":
            cmd_discuss(team, args)
        elif command == "route":
            cmd_route(team, args)
        elif command == "status":
            cmd_status(team, args)
        elif command in ("help", "-h", "--help"):
            cmd_help()
        else:
            # Treat as a question
            cmd_ask(team, [command] + args)


if __name__ == "__main__":
    main()
