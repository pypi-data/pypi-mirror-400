import asyncio

import aiofiles


class Human:

    def __init__(self):
        pass

    async def get_next_action(self, axtree: str):

        async with aiofiles.open("/tmp/axtree.txt", "w", encoding="utf-8") as f:
            await f.write(axtree)

        value = await asyncio.to_thread(
            input, "Input the index of the element to click: "
        )

        return int(value)
