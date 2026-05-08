import asyncio
import os

from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv(override=True)


async def main():
    client = OpenAIChatCompletionClient(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        model=os.environ["LLM_MODEL_NAME"],
    )

    async with (
        MCPStreamableHTTPTool(
            name="DeepWiki MCP",
            url="https://mcp.deepwiki.com/mcp",
        ) as mcp_server,
        Agent(
            client=client,
            name="DocsAgent",
            instructions=(
                "You help answer questions using documentation. "
                "Cite the DeepWiki sources you used at the end of your answer."
            ),
            tools=[mcp_server],
        ) as agent,
    ):
        result = await agent.run(
            "Consult the FastMCP Changelog and list the last 5 FastMCP releases "
            "with release names and one highlight each."
        )
        print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
