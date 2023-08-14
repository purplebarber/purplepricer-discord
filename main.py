from src.sse_listener import SSEListener
from asyncio import run


async def main() -> None:
    sse = SSEListener()
    await sse.update_pricelist()
    try:
        await sse.listen_and_update()
    finally:
        await sse.close()


if __name__ == "__main__":
    run(main())
