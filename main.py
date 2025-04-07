from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agent import system_flow
from tool.generate_tool import create_tool
from model.module import RequestMessage
from langchain_core.messages import AIMessage, HumanMessage
app = FastAPI()


async def call_system_flow(request : str):
    messages = [HumanMessage(content=request)]
    tool = await create_tool()
    responed = system_flow.call_process(tool).invoke({"messages" : messages})
    print(responed)

    return None


@app.post("/request_chat")
async def chat_action(chatmessages: RequestMessage):
    return await call_system_flow(chatmessages.requset)
