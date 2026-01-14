import asyncio
import os
from typing import Any

import httpx
from timbal import Agent
from timbal.tools import WebSearch
from timbal.types import File

# os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ["TIMBAL_API_HOST"] = "api.timbal.ai"
# os.environ["TIMBAL_APP_ID"] = "185"
# os.environ["TIMBAL_PROJECT_ID"] = "60"
os.environ["TIMBAL_LOG_EVENTS"] = "START,OUTPUT,DELTA"


def get_datetime():
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


agent = Agent(
    name="test-proxies",
    model="anthropic/claude-haiku-4-5",  # type: ignore
    tools=[get_datetime, WebSearch()],  # type: ignore
    model_params={"max_tokens": 2048},  # type: ignore
)


async def call_remote_agent(prompt: str, parent_id: str | None = None) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=180.0)) as client:
        res = await client.post(
            f"https://{os.environ['TIMBAL_API_HOST']}/orgs/11/apps/39/runs/collect",
            headers={
                "Authorization": f"Bearer {os.environ['TIMBAL_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "version_id": "1139",
                "parent_id": parent_id,
                "input": {"prompt": prompt},
            },
        )
        res.raise_for_status()
        return res.json()


async def main():
    # await agent(prompt="when does fcbarcelona play next?", max_tokens=1024).collect()
    # await agent(prompt="hola", max_tokens=1024).collect()
    # await agent(prompt=[File.validate("~/Downloads/Transfer_Confirmation_EUR-USD_02-ene-2026_12.08.55.pdf")]).collect()
    # await agent(prompt="how much were the fees?").collect()
    await agent(prompt=[File.validate("~/Downloads/Timbal AI - Plan de Incentivos + Anexos vfinal-1.pdf")]).collect()
    await agent(prompt="summarize shorter").collect()
    # parent_id = None
    # while True:
    #     prompt = input("User: ")
    #     if prompt.strip() == "q":
    #         break
    #     # await agent(prompt=prompt, max_tokens=1024).collect()
    #     res_json = await call_remote_agent(prompt=prompt, parent_id=parent_id)
    #     print(res_json)
    #     parent_id = res_json["run_id"]


if __name__ == "__main__":
    asyncio.run(main())
