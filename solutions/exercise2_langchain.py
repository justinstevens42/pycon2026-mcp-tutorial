import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv(override=True)


async def run_agent():
    model = ChatOpenAI(
        model=os.environ["LLM_MODEL_NAME"],
        base_url=os.environ["LLM_BASE_URL"],
        api_key=SecretStr(os.environ["LLM_API_KEY"]),
    )

    client = MultiServerMCPClient(
        {
            "deepwiki": {
                "url": "https://mcp.deepwiki.com/mcp",
                "transport": "streamable_http",
            }
        }
    )

    tools = await client.get_tools()
    agent = create_agent(
        model,
        tools,
        system_prompt=(
            "Use DeepWiki tools for repository-grounded answers and cite the DeepWiki sources you used at the end."
        ),
    )

    response = await agent.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "Consult the PrefectHQ/FastMCP Changelog and list the last 5 FastMCP "
                        "releases with release names and one highlight each."
                    )
                ),
            ]
        }
    )

    print(response["messages"][-1].text)


if __name__ == "__main__":
    asyncio.run(run_agent())
