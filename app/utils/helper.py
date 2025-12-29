import asyncio

async def await_if_needed(maybe):
    return await maybe if asyncio.iscoroutine(maybe) else maybe