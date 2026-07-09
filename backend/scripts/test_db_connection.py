"""Test MongoDB connection using MONGODB_URL from .env."""

import asyncio
import sys

from app.database.mongodb import close_mongo_connection, connect_to_mongo, ping_mongo


async def test_connection() -> bool:
    try:
        await connect_to_mongo()
        ok = await ping_mongo()
        if ok:
            print("OK: MongoDB connection successful")
        else:
            print("FAIL: MongoDB ping failed")
        await close_mongo_connection()
        return ok
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(test_connection()) else 1)
