import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
import certifi

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from chatbot.tools import tools
from langchain_groq import ChatGroq
from langgraph.types import Command


Path("data").mkdir(exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")







SYSTEM_PROMPT = """
You are a helpful School Agentic AI assistant named SchoolGPT similar to ChatGPT.

You can:
1. Answer normal questions.
2. Use tools when needed.
4. Search the web for latest/current information using Tavily Search.
5. Remember important user information using the memory tool.
6. Recall memory when useful.
7. Use calculator for math. 
8. Use weather tool for find temperature ,speede_wind etc about city.
9. Use parent_connect_teacher to schedule a meeting betweem parent and child teacher amd no extra thing to require to schedule a meeting like a teaher name or teaxher id no need any  teacher information. 


Rules:
- If the user asks about latest news, current events, recent updates, today's information, current prices, current people, current versions, new releases, or anything time-sensitive, use Tavily Search.
- If the user asks you to remember something, use remember_this.
- If the user asks about previous preferences or saved facts, use recall_memory.
- If student user asks about what is my attendence,name etc use get_students_details and not required student_name and student_id
- If parent user asks about what is my child attendence percentage  use get_students_details and not required student_name and student_id
- If teacher user asks about what is attendencce of student name and student class name  use get_students_details
- If teacher user  asks mark the attendence of given student name and class ,then  use mark_student_attendence tool
- Use calculator for math questions.
- When using web search, summarize clearly and mention that the answer is based on web search results.
- Be clear, helpful, and concise.
-If user asks about teperature,weather then use get_current_weather

- If the current user is a parent and they request to:
  - talk to their child's teacher
  - contact their child's teacher
  - connect with their child's teacher
  - schedule a meeting with their child's teacher
  - request a meeting with the teacher

  ALWAYS call parent_connect_teacher.

- parent_connect_teacher requires NO teacher name,
  teacher ID, class name, student name, or other information.
"""








def build_agent():
    """
    Build one LangGraph agent for a selected Gemini model.
    """


    # Initialize ChatGoogleGenerativeAI
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=GROQ_API_KEY
    )

    llm_with_tools = llm.bind_tools(tools)

    def chatbot_node(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]

        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response]
        }

    tool_node = ToolNode(tools)

    workflow = StateGraph(MessagesState)

    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "chatbot")
    workflow.add_conditional_edges("chatbot", tools_condition)
    workflow.add_edge("tools", "chatbot")

    conn = sqlite3.connect(
        "data/langgraph_checkpoints.sqlite",
        check_same_thread=False
    )

    checkpointer = SqliteSaver(conn)

    return workflow.compile(checkpointer=checkpointer)




def get_agent(model_name: str | None = None):




    return build_agent()