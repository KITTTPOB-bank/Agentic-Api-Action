 
from langgraph.graph import StateGraph , START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage ,AIMessage, ToolMessage
import os
from .structured import MessageStatus, MessagesFlow
from .prompt import PROMPT_ANALYZE , PROMPT_TOOL_AGENT
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import datetime
import base64
load_dotenv()

def call_process(tools : list , Meme: bool):
    GPT_KEY = os.getenv("GPT_KEY")
 
    GEMINI_KEY = os.getenv("GEMINI_KEY")
    tools_by_name = {tool.name: tool for tool in tools}
    llm = ChatOpenAI(model="gpt-4o-mini",  temperature=0.3 , api_key=GPT_KEY)

    def call_generate(state: MessagesFlow):
        messages = state["messages"]
 
        meme_msg = llm.invoke(f"""
ภารกิจของคุณคือ:  **คิดข้อความที่จะสร้างรูปภาพแมวที่แปลก ฮา หลุดโลก และขอภาพนั้น** โดยอิงจากข้อความด้านล่าง ส่งคืนแค่ 1 ข้อความ
📄 ข้อความ:
{messages[0].content}

🎯 แนวทางสร้างมีม:
- ต้องมีแมวอยู่ในภาพเสมอ
- ถ้าพูดถึงทอง → ให้แมวถือทอง / อาบทอง / กลิ้งบนทอง
- ถ้าพูดถึงหุ้นแอปเปิ้ล → ให้แมวกัดแอปเปิ้ล หรือปีนต้นแอปเปิ้ล
- ถ้าเศรษฐกิจแย่ → ให้แมวใส่สูทดูเศร้า หรือถือกราฟตก
                                             
ผลลัพธ์ ที่คาดหวังจะเป็นข้อความสั้นๆเช่น `ขอภาพแมวใส่สร้องทองยิ่ม` , `ขอภาพแมวเลียแอปเปิ้ล` แค่ 1 ข้อความเท่านั้น""")
                
        message = {
    "role": "user",
    "content":  meme_msg.content
    }

        llm_gemini = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash-exp-image-generation",
            temperature=0.7,
            max_tokens=None,
            api_key=GEMINI_KEY
        )

        try:
            response = llm_gemini.invoke(
                [message],
                generation_config=dict(response_modalities=["TEXT", "IMAGE"]),
            )
    
            image_base64 = response.content[0].get("image_url").get("url").split(",")[-1]

            image_data = base64.b64decode(image_base64)

            folder_path = "generated_images"
            os.makedirs(folder_path, exist_ok=True)

            filename = f"meme_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "wb") as f:
                    f.write(image_data)
        except:
            print("ไม่สามารถสร้างรูปภาพได้อาจเกิดจาก Key มีจำกัดการสร้าง")
            return None

        return None
    
    def call_analyze(state: MessagesFlow):
        messages = state["messages"]

        prompt_template = PromptTemplate.from_template(PROMPT_ANALYZE)
        prompt = prompt_template.format(date_now=datetime.datetime.now().strftime("%Y-%m-%d"))
     
        llm_with_ouput = llm.with_structured_output(MessageStatus)
        message = llm_with_ouput.invoke([SystemMessage(content=prompt)] + messages)
        return {"messages": AIMessage(content=message.message), "status": message.status}
    

    def should_end(state: MessagesFlow):
        status = state["status"]
        if status == "end":
            return END
        return "call_agent"
    
    def should_end_meme(state: MessagesFlow):
        status = state["status"]
        if status == "end":
            return "generate"
        return "call_agent"

    def should_continue(state: MessagesFlow):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"

        return "call_analyze"

    def tool_node(state: dict):
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"], tools_by_name=tool_call["name"]))
        return {"messages": result}


    def call_model(state: MessagesFlow):
        messages = state["messages"]
        prompt_template = PromptTemplate.from_template(PROMPT_TOOL_AGENT)
        prompt = prompt_template.format(date_now=datetime.datetime.now().strftime("%Y-%m-%d"))

        model_with_tools = llm.bind_tools(tools)
        response = model_with_tools.invoke([SystemMessage(content=prompt)] + messages)

        return {"messages": [response]}


    workflow = StateGraph(MessagesFlow)

    workflow.add_node("call_agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("call_analyze", call_analyze)

    if Meme:
        workflow.add_node("generate", call_generate)

    workflow.add_edge(START, "call_analyze")
    if Meme:
        workflow.add_conditional_edges("call_analyze", should_end_meme, ["call_agent", "generate" ])
        workflow.add_conditional_edges("call_agent", should_continue, ["tools", "call_analyze"])
        workflow.add_edge("tools", "call_agent")
        workflow.add_edge("generate", END)
    else:
        workflow.add_conditional_edges("call_analyze", should_end, ["call_agent", END ])
        workflow.add_conditional_edges("call_agent", should_continue, ["tools", "call_analyze"])
        workflow.add_edge("tools", "call_agent")

    return workflow.compile()