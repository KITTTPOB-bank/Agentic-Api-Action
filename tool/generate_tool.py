from langchain_core.tools import StructuredTool
import requests
import os
from typing import Literal, List
from pydantic import BaseModel, Field
import yfinance


class SeachAPi(BaseModel):
    query : str = Field(description="หัวข้อที่จะค้นหาข้อมูล ให้ใช้เป็นคำภาษาอังกฤษ สำหรับค้นหาข้อมูล")
    sortby: Literal["relevancy", "popularity", "publishedAt"] = Field(description="""
relevancy = articles more closely related to q come first.
popularity = articles from popular sources and publishers come first.
publishedAt = newest articles come first
""")
    
class Yfinance(BaseModel):
    ticker: str = Field(..., description="หัวข้อที่จะค้นหาข้อมูล เช่น 'GC=F' สำหรับ Gold Futures")
    fastInfo: List[Literal[
        'currency', 'dayHigh', 'dayLow', 'exchange', 'fiftyDayAverage', 'lastPrice', 'lastVolume',
        'marketCap', 'open', 'previousClose', 'quoteType', 'regularMarketPreviousClose',
        'shares', 'tenDayAverageVolume', 'threeMonthAverageVolume', 'timezone',
        'twoHundredDayAverage', 'yearChange', 'yearHigh', 'yearLow'
    ]] = Field(..., description="รายการ fast_info ที่ต้องการ เช่น ['currency', 'lastPrice']")

async def structool(func, name, desc, args):
    tool = StructuredTool.from_function(
        func=func,
        name=name,
        description=desc,
        args_schema=args
    )
    return tool

async def create_tool():

    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    tools = []
    def search_news_ByApi(query: str , sortby: str):
        url = f"https://newsapi.org/v2/everything"
        payload = {
            "q": query,
            "apiKey": NEWS_API_KEY,
            "sortBy": sortby,
            "pageSize": 5
        }

        response = requests.request("GET", url, params=payload).text      
        return response
    

    def yfinance_fast_info(ticker: str , fastInfo: List[str]):

        dat = yfinance.Ticker(ticker)
        info = {field: dat.fast_info[field] for field in fastInfo}
        
        return info
                  


    tools.append(await structool(search_news_ByApi, "search_news_ByApi", "ส่ง `หัวข้อ` เพื่อค้นหาข้อมูลที่สนใจ", SeachAPi))
    tools.append(await structool(yfinance_fast_info, "yfinance_fast_info", "ใช้ yfinance ดึงรายละเอียด `หุ้น , กองทุน, btc เป็นต้น โดยจะเป็นชื่อย่อ` เพื่อค้นหาข้อมูล", Yfinance))

    return tools


                

 