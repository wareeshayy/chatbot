"""Initialize database — connect and seed."""

import asyncio

from scripts.seed_data import seed


async def setup_db() -> None:
    await seed()


if __name__ == "__main__":
    asyncio.run(setup_db())
