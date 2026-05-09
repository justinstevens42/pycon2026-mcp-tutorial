import asyncio
import logging
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv(override=True)


async def main():
    openai_client = AsyncOpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
    )
    model = OpenAIChatModel(
        os.environ["LLM_MODEL_NAME"],
        provider=OpenAIProvider(openai_client=openai_client),
    )

    server = MCPServerStreamableHTTP(url="https://mcp.deepwiki.com/mcp")

    agent: Agent[None, str] = Agent(
        model,
        system_prompt=(
            "You help answer questions using documentation. "
            "Cite the DeepWiki sources you used at the end of your answer."
        ),
        output_type=str,
        toolsets=[server],
    )

    result = await agent.run(
        "Consult the PrefectHQ FastMCP Changelog and list the last 5 FastMCP releases with release names and one highlight each."
    )
    print(result.output)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    asyncio.run(main())
