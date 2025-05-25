from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

from ollama import chat
from ollama import ChatResponse

from fastapi import FastAPI, Request

import requests
import pprint
import uvicorn

import json

app = FastAPI()

mcp_session = None  # 全域變數，儲存 MCP session

server_params = StdioServerParameters(
    command="/home/yale/.local/bin/uv",  # Executable
    args=["run","--with","mcp[cli]","mcp","run","/home/yale/coding/cbot918/mcpbox/functions.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
)

# tools
get_stock_price_tool = {
    'type': 'function',
    'function': {
        'name': 'get_stock_price',
        'description': 'Get the current stock price for any symbol',
        'parameters': {
            'type': 'object',
            'required': ['symbol'],
            'properties': {
                'symbol': {'type': 'string', 'description': 'The stock symbol (e.g., AAPL, GOOGL)'},
            },
        },
    },
}

add_tool = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "Calculate the sum of two numbers",
        "parameters": {
            "type": "object",
            "required": ["a", "b"],
            "properties": {
                "a": {
                    "type": "integer",
                    "description": "The first number"
                },
                "b": {
                    "type": "integer",
                    "description": "The second number"
                }
            }
        }
    }
}

# response = chat(
#     'qwen3:30b-a3b',
#     messages=[{'role': 'user', 'content': 'hi how are you'}],
#     tools=[get_stock_price_tool],
# )


tools = [
  get_stock_price_tool,
  add_tool
]

async def ask_ollama(prompt: str) -> str:
    res = requests.post(
        "http://localhost:11434/api/chat",
        json = {
            "model": "qwen3:30b-a3b",
            "stream": False,
            "messages": [
                {
                "role": "user",
                "content": prompt
                }
            ],
        }
    )
    data = res.json()
    print(f'data: {data}')
    return data

async def ask_ollama_with_tool(prompt: str, tools: []) -> str:
    res = requests.post(
        "http://localhost:11434/api/chat",
        json = {
            "model": "qwen3:30b-a3b",
            "stream": False,
            "messages": [
                {
                "role": "user",
                "content": prompt
                }
            ],
            "tools": tools
        }
    )
    data = res.json()
    print(f'data: {data}')
    return data


@app.post("/ask")
async def ask(request: Request):
    req = await request.json()
    prompt = req.get("prompt")

    result_raw = await ask_ollama_with_tool(prompt, tools)

    if isinstance(result_raw, str):
        result = json.loads(result_raw)
    else:
        result = result_raw

    func_name = result['message']['tool_calls'][0]['function']['name']
    val_a = result['message']['tool_calls'][0]['function']['arguments']['a']
    val_b = result['message']['tool_calls'][0]['function']['arguments']['b']

    print('**************')
    print(f'result:{result}')

    function_result = await mcp_session.call_tool(func_name, arguments={"a": val_a,"b":val_b})

    result = await ask_ollama(f'{function_result} is the result of prompt {prompt}, please give me the complete sentence back to user with result')

    # result = await mcp_session.call_tool("add", arguments={"a": 1, "b": 2})  # 你可以改成根據 prompt 決定使用什麼工具
    return {"response": result['message']['content']}

async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )

# 啟動 HTTP server + MCP session
async def main():
    global mcp_session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=handle_sampling_message
        ) as session:
            mcp_session = session

            await session.initialize()
            config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
            server = uvicorn.Server(config)
            await server.serve()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
