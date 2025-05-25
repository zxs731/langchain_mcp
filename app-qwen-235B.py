import asyncio
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv("silion.env")

async def mcp_agent_init():
    llm = ChatOpenAI(
        model="Qwen/Qwen3-235B-A22B",
        temperature=0.6,
        max_tokens=1000,
        timeout=None,
        max_retries=2,
        api_key=os.environ["api_key"], 
        base_url="https://api.siliconflow.cn/v1"
    )
    with open("mcp_server_config.json", "r") as f:
        config = json.load(f)
    client = MultiServerMCPClient(
        config["mcpServers"]
    )
    tools = await client.get_tools()
    agent =  create_react_agent(
        llm,
        tools=tools,
    )
    return agent
messages = []
async def main():
    try:
        agent =await mcp_agent_init()
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        while True:
            #try:
                query = input("\nYou: ").strip()
                if query.lower() == 'quit':
                    break
                messages.append({"role": "user", "content": query})
                async for step in agent.astream(
                    {"messages": messages},
                    {"recursion_limit":100},
                    stream_mode="values",
                ):
                    step["messages"][-1].pretty_print()
                #print("\nAI: " + response)
            #except Exception as e:
            #    print(f"\nError: {str(e)}")
    finally:
        print("AI: Bye! See you next time!")
if __name__ == "__main__":
    asyncio.run(main())
