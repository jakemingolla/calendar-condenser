import asyncio
import json
from datetime import UTC, datetime

import httpx
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.table import Table

BASE_URL = "http://localhost:8000"

thoughts: dict[str, str] = {}
contents: dict[str, str] = {}
thoughts_updated_at_records: dict[str, datetime] = {}
contents_updated_at_records: dict[str, datetime] = {}
thoughts_started_at_records: dict[str, datetime] = {}
contents_started_at_records: dict[str, datetime] = {}


def pretty_time_delta(ms: float) -> str:
    sign_string = "-" if ms < 0 else ""
    ms = abs(int(ms))
    days, ms = divmod(ms, 86400000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    if days > 0:
        return f"{sign_string}{days}d{hours}h{minutes}m{seconds}s"
    if hours > 0:
        return f"{sign_string}{hours}h{minutes}m{seconds}s"
    if minutes > 0:
        return f"{sign_string}{minutes}m{seconds}s"
    if seconds > 0:
        return f"{sign_string}{seconds}s"
    if ms > 0:
        return f"{sign_string}{ms}ms"
    return "0ms"


def get_renderable() -> Table:
    table = Table()
    table.add_column("Started")
    table.add_column("Updated")
    table.add_column("Duration")
    table.add_column("Type")
    table.add_column("Text")
    now = datetime.now(UTC)

    for id, thought in thoughts.items():
        started_ago_ms = (now - thoughts_started_at_records[id]).total_seconds() * 1000
        updated_ago_ms = (now - thoughts_updated_at_records[id]).total_seconds() * 1000
        duration_ms = abs(updated_ago_ms - started_ago_ms)
        table.add_row(
            pretty_time_delta(started_ago_ms),
            pretty_time_delta(updated_ago_ms),
            pretty_time_delta(duration_ms),
            "[yellow]Thought[/yellow]",
            Markdown(thought, style="bright_black"),
        )
    for id, content in contents.items():
        started_ago_ms = (now - contents_started_at_records[id]).total_seconds() * 1000
        updated_ago_ms = (now - contents_updated_at_records[id]).total_seconds() * 1000
        duration_ms = abs(updated_ago_ms - started_ago_ms)
        table.add_row(
            pretty_time_delta(started_ago_ms),
            pretty_time_delta(updated_ago_ms),
            pretty_time_delta(duration_ms),
            "[green]Content[/green]",
            Markdown(content),
        )
    return table


async def main() -> None:
    console = Console()
    async with httpx.AsyncClient() as client:
        with Live(console=console) as live:
            response = await client.get(f"{BASE_URL}/stream", timeout=None)
            async for line in response.aiter_lines():
                await asyncio.sleep(0.1)
                parsed = json.loads(line)
                event = parsed.get("event", None)
                data = parsed.get("data", {})

                if event == "on_chat_model_stream":
                    kwargs = data.get("chunk", {}).get("kwargs", {})
                    id = kwargs.get("id", None)
                    thought = kwargs.get("additional_kwargs", {}).get("reasoning_content", None)
                    content = kwargs.get("content", None)

                    if thought:
                        if id not in thoughts_started_at_records:
                            thoughts_started_at_records[id] = datetime.now(UTC)
                        if id not in thoughts:
                            thoughts[id] = ""
                        thoughts[id] += thought
                        thoughts_updated_at_records[id] = datetime.now(UTC)
                    elif content:
                        if id not in contents_started_at_records:
                            contents_started_at_records[id] = datetime.now(UTC)
                        if id not in contents:
                            contents[id] = ""
                        contents[id] += content
                        contents_updated_at_records[id] = datetime.now(UTC)
                live.update(get_renderable())


asyncio.run(main())
