from langgraph.graph import StateGraph, MessagesState , START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from typing import List, TypedDict, Annotated
from langchain_core.messages import HumanMessage, SystemMessage ,AIMessage, ToolMessage
import os
from .structured import LogoChoice
from .prompt import PROMPT_ANYSIC
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
load_dotenv()
class State(TypedDict):
    messages: Annotated[List, add_messages]
    brandname: str 
 
def call_process(tools : list):
    GPT_KEY = os.getenv("GPT_KEY")
    print(GPT_KEY)
    GEMINI_KEY = os.getenv("GEMINI_KEY")
    print(tools)
    tools_by_name = {tool.name: tool for tool in tools}
    llm = ChatOpenAI(model="gpt-4o-mini",  temperature=0 , top_p=0, api_key=GPT_KEY)

    # def call_generate(state: MessagesState):
    #     llm = ChatGoogleGenerativeAI(
    #         model="gemini-2.0-flash-001",
    #         temperature=0,
    #         max_tokens=None,
    #         timeout=None,
    #         max_retries=2,
    #         api_key=key
            
    #     )
    #     return None
    
    def call_plan(state: MessagesState):
        messages = state["messages"]

        prompt_template = PromptTemplate.from_template(PROMPT_ANYSIC)
        prompt = prompt_template.format(user_request=messages[-1].content)

        llm_with_ouput = llm.with_structured_output(LogoChoice)
        message = llm_with_ouput.invoke(prompt)

        print(message)

        newmssage = f"รายการ keyword ที่จะค้นหารูปภาพ {str(message.keywords)}"
        return {"messages": AIMessage(content=newmssage), "brandname": message.brand_name}
    

    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def tool_node(state: dict):
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"], tools_by_name=tool_call["name"]))
        return {"messages": result}


    def call_model(state: MessagesState):
        messages = state["messages"]
        print("-------------------------------------------")
        print(messages)
        print("-------------------------------------------")
        model_with_tools = llm.bind_tools(tools)
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}


    workflow = StateGraph(MessagesState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("plan", call_plan)
    # workflow.add_node("generate", call_generate)

    workflow.add_edge(START, "plan")
    workflow.add_edge("plan", "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    # workflow.add_edge("generate", END)

    return workflow.compile()