from langchain_core.tools import StructuredTool
import requests
import os

async def create_tool():
    TAVILY_KEY = os.getenv("TAVILY_KEY")

    def search_image (keyword: str):
        url = "https://api.tavily.com/search"
        payload = {
     
        }
        headers = {
            "Authorization": f"Bearer {TAVILY_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.request("POST", url, json=payload, headers=headers).json()
        print(response)
        result = response["images"][0]
        print(result)
        return result
         
    tools = StructuredTool.from_function(
        func=search_image,
        name="search_image",
        description="ส่ง keyword เพื่อค้นหารูปภาพ"
    )

    return [tools]
                

 