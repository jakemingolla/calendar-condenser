import asyncio
import json

import rich
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"


async def main() -> None:
    async with AsyncClient() as client:
        print("Checking server status...")
        await client.get(f"{BASE_URL}/")
        print("Server is running.")

        print("Invoking agent...")
        async with client.stream("POST", f"{BASE_URL}/", timeout=None) as response:
            async for line in response.aiter_lines():
                parsed = json.loads(line)
                if "type" in parsed:
                    if parsed["type"] == "AIMessageChunk":
                        rich.print(parsed["content"], end="")
                    else:
                        rich.print(parsed)


if __name__ == "__main__":
    asyncio.run(main())
