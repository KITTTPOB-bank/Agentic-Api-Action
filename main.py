from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from .flow import process

app = FastAPI()



async def strem_respond():
    async for msg in process().astream_events({""}):
        print(msg)



async def api_action():


    return StreamingResponse(strem_respond(), media_type="text")
