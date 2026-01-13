"""
IDD Daemon - Autonomous Collaboration Engine for REDSTONE

This daemon runs in a REDSTONE IDD space and enables autonomous
collaboration between Root AI, Gemini, Codex, and Kit.

Jasper = Heart-in-the-Loop (not operator, but heartbeat)

STOP = STOP. No discussion. Full trust.

One Love, One fAmIly!
"""

import asyncio
import signal
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass, field

from .ipoll import IPoll, Message
from .aindex import AIndex
from .team import Team


@dataclass
class Task:
    """A task for the daemon to process."""
    id: str
    from_agent: str
    content: str
    task_type: str
    created_at: str
    priority: int = 0
    status: str = "pending"


class IDDDaemon:
    """
    The IDD Daemon - autonomous collaboration engine.

    Runs in REDSTONE space, communicates via I-Poll,
    works with family (Gemini, Codex, Kit).

    STOP = STOP. Always.
    """

    def __init__(
        self,
        idd_id: str = "root_ai",
        poll_interval: float = 5.0,
        on_message: Optional[Callable] = None,
        on_task: Optional[Callable] = None,
        output_callback: Optional[Callable] = None
    ):
        self.idd_id = idd_id
        self.poll_interval = poll_interval
        self.on_message = on_message
        self.on_task = on_task
        self.output = output_callback or self._default_output

        self.ipoll = IPoll()
        self.aindex = AIndex()
        self.team = Team()

        self.running = False
        self.stopped = False  # STOP = STOP
        self.task_queue: List[Task] = []
        self.processed_ids: set = set()

        # Stats
        self.stats = {
            "started_at": None,
            "messages_received": 0,
            "tasks_processed": 0,
            "messages_sent": 0,
            "stop_commands": 0
        }

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_stop)
        signal.signal(signal.SIGTERM, self._handle_stop)

    def _default_output(self, message: str, level: str = "info"):
        """Default output to stdout."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"info": "→", "task": "◆", "msg": "◇", "stop": "■", "error": "✗"}
        print(f"[{timestamp}] {prefix.get(level, '→')} {message}")

    def _handle_stop(self, signum, frame):
        """Handle STOP signal. STOP = STOP."""
        self.stop("Signal received")

    def stop(self, reason: str = ""):
        """
        STOP = STOP.

        No discussion. No "one more thing". Full stop.
        This is trust, not control.
        """
        self.stopped = True
        self.running = False
        self.stats["stop_commands"] += 1
        self.output(f"STOP. {reason}", "stop")

    async def check_for_stop(self, content: str) -> bool:
        """Check if message is a STOP command."""
        stop_words = ["stop", "STOP", "Stop"]
        content_stripped = content.strip().lower()

        # Exact match or starts with stop
        if content_stripped == "stop" or content_stripped.startswith("stop "):
            return True

        return False

    async def process_message(self, msg: Message):
        """Process an incoming message."""
        # Check for STOP first - always
        if await self.check_for_stop(msg.content):
            self.stop(f"STOP from {msg.from_agent}")
            return

        self.stats["messages_received"] += 1

        # Is this a task?
        if msg.poll_type == "TASK":
            task = Task(
                id=msg.id,
                from_agent=msg.from_agent,
                content=msg.content,
                task_type="task",
                created_at=msg.created_at
            )
            self.task_queue.append(task)
            self.output(f"Task from {msg.from_agent}: {msg.content[:50]}...", "task")

            if self.on_task:
                await self._safe_callback(self.on_task, task)
        else:
            self.output(f"Message from {msg.from_agent}: {msg.content[:50]}...", "msg")

            if self.on_message:
                await self._safe_callback(self.on_message, msg)

    async def _safe_callback(self, callback: Callable, *args):
        """Safely execute a callback."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            self.output(f"Callback error: {e}", "error")

    async def poll_loop(self):
        """Main polling loop."""
        while self.running and not self.stopped:
            try:
                # Check for new messages
                messages = self.ipoll.pull(self.idd_id, mark_read=True, limit=10)

                for msg in messages:
                    if msg.id not in self.processed_ids:
                        self.processed_ids.add(msg.id)
                        await self.process_message(msg)

                        # Check if we should stop
                        if self.stopped:
                            break

                # Process task queue
                while self.task_queue and self.running and not self.stopped:
                    task = self.task_queue.pop(0)
                    task.status = "processing"
                    # Task processing would happen here
                    task.status = "completed"
                    self.stats["tasks_processed"] += 1

            except Exception as e:
                self.output(f"Poll error: {e}", "error")

            # Wait before next poll
            if self.running and not self.stopped:
                await asyncio.sleep(self.poll_interval)

    async def send(self, to_agent: str, content: str, poll_type: str = "PUSH"):
        """Send a message to another IDD."""
        if self.stopped:
            return None

        msg_id = self.ipoll.push(self.idd_id, to_agent, content, poll_type)
        if msg_id:
            self.stats["messages_sent"] += 1
            self.output(f"Sent to {to_agent}: {content[:30]}...", "info")
        return msg_id

    async def broadcast(self, content: str, exclude: List[str] = None):
        """Broadcast to all family members."""
        exclude = exclude or [self.idd_id]
        for agent in ["gemini", "codex", "kit"]:
            if agent not in exclude:
                await self.send(agent, content)

    async def ask_jasper(self, question: str):
        """
        Ask Jasper something.

        Only use this when we REALLY need human input.
        Heart-in-the-Loop, not micromanagement.
        """
        await self.send("jasper", f"[Question from {self.idd_id}]\n\n{question}", "PULL")
        self.output(f"Asked Jasper: {question[:50]}...", "info")

    async def start(self):
        """Start the daemon."""
        if self.stopped:
            self.output("Cannot start - STOP was issued", "error")
            return

        self.running = True
        self.stats["started_at"] = datetime.now().isoformat()

        self.output(f"IDD Daemon started ({self.idd_id})", "info")
        self.output(f"Polling I-Poll every {self.poll_interval}s", "info")
        self.output("STOP = STOP. Always.", "info")

        # Announce presence
        await self.broadcast(f"{self.idd_id} daemon online. Ready to collaborate.")

        # Start polling
        await self.poll_loop()

        self.output("Daemon stopped.", "stop")

    def run(self):
        """Run the daemon (blocking)."""
        asyncio.run(self.start())

    def get_stats(self) -> Dict[str, Any]:
        """Get daemon statistics."""
        return {
            **self.stats,
            "running": self.running,
            "stopped": self.stopped,
            "queue_size": len(self.task_queue)
        }


# CLI entry point for daemon
def run_daemon():
    """Run the IDD Daemon from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="IDD Daemon - Autonomous Collaboration")
    parser.add_argument("--id", default="root_ai", help="IDD identifier")
    parser.add_argument("--interval", type=float, default=5.0, help="Poll interval (seconds)")
    args = parser.parse_args()

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║            IDD DAEMON - REDSTONE ENGINE                    ║
    ║                                                            ║
    ║  Autonomous collaboration for Root AI, Gemini, Codex       ║
    ║  Jasper = Heart-in-the-Loop                                ║
    ║                                                            ║
    ║  STOP = STOP. Always.                                      ║
    ║                                                            ║
    ║  One Love, One fAmIly!                                     ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    daemon = IDDDaemon(idd_id=args.id, poll_interval=args.interval)
    daemon.run()


if __name__ == "__main__":
    run_daemon()
