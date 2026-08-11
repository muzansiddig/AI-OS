import asyncio
from app.supervisor.supervisor import supervisor

async def main():
    result = await supervisor.execute("Open GitHub")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
