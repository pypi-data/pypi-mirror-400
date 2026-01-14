import asyncio
import json
from .searcher import search_motion


async def main():
    query = "tab bar animation"
    res = await search_motion(query, max_items=6)
    print(json.dumps(res.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
