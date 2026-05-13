import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv(override=True)


async def run_agent():
    # TODO: Configure ChatOpenAI using LLM_* env vars.
    model = ChatOpenAI(
        model=os.environ["LLM_MODEL_NAME"],
        base_url=os.environ["LLM_BASE_URL"],
        api_key=SecretStr(os.environ["LLM_API_KEY"]),
    )

    client = MultiServerMCPClient(
        {
            "justinserver": {  # TODO: Set a server name
                "url": "https://huggingface.co/mcp",  # TODO: Set the MCP server URL
                "transport": "streamable_http",
            }
        }
    )

    tools = await client.get_tools()
    agent = create_agent(
        model,
        tools,
        system_prompt=(
            "Use the Hugging Face MCP API to answer questions about popular text models"
        ),
    )

    response = await agent.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "What is the most popular text model on Hugging Face and what is it used for?"
                    )
                ),
            ]
        }
    )

    print(response["messages"][-1].text)


if __name__ == "__main__":
    asyncio.run(run_agent())