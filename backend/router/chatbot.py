from dotenv import load_dotenv
import os
import certifi

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import json
from pathlib import Path

from fastapi import Depends,APIRouter,  Request,HTTPException,status
from pydantic import Field
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from langgraph.types import interrupt, Command



from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    AIMessageChunk,
    ToolMessage
)

from chatbot.agent import get_agent
from Service.ChatMessageService import ChatMessageService  

from chatbot.tools import set_current_thread_id
from chatbot.tools import set_current_user_id,set_current_role
from security.dependencies import get_current_user



router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"]
)


Path("uploads").mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)



def build_thread_id(user_id: int,role:str) -> str:
    # Prefix with the role so a parent with id 1 and a student with id 1
    # never share the same conversation memory.
    return f"{role}_{user_id}"

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)

def role_checker(role: str, current_user=Depends(get_current_user)):
    if current_user["role"] != role:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission"
        )

    return current_user

@router.get("/chat/history/{role}")
async def history(current_user=Depends(role_checker)):
    
    user_id = current_user["user_id"]
    thread_id = build_thread_id(user_id,current_user["role"])
    messages = ChatMessageService.get_chat_history(user_id,thread_id)

    return {
        "messages": [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    }






def sse_data(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def should_stream_chunk(chunk, metadata) -> bool:
    """
    This prevents raw tool/search/RAG JSON from appearing in the frontend.

    We only stream normal AI text chunks.
    We do NOT stream:
    - ToolMessage
    - messages from tool nodes
    - tool call chunks
    - raw tool outputs
    """

    metadata = metadata or {}

    node_name = str(metadata.get("langgraph_node", "")).lower()

    if "tool" in node_name:
        return False

    if isinstance(chunk, ToolMessage):
        return False

    if not isinstance(chunk, (AIMessage, AIMessageChunk)):
        return False

    if getattr(chunk, "tool_calls", None):
        return False

    if getattr(chunk, "invalid_tool_calls", None):
        return False

    additional_kwargs = getattr(chunk, "additional_kwargs", {}) or {}

    if additional_kwargs.get("tool_calls"):
        return False

    return True


def extract_text_from_chunk(chunk) -> str:
    content = getattr(chunk, "content", "")

    if not content:
        return ""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):
                if item.get("type") == "text" and isinstance(item.get("text"), str):
                    text_parts.append(item["text"])
                elif isinstance(item.get("text"), str):
                    text_parts.append(item["text"])
                elif isinstance(item.get("content"), str):
                    text_parts.append(item["content"])

        return "".join(text_parts)

    return ""



@router.post("/chat/stream/{role}")
async def chat_stream(request: Request,current_user=Depends(role_checker)):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            {"error": "Invalid JSON body."},
            status_code=400
        )

    user_message = data.get("message", "").strip()
    user_id = current_user["user_id"]
    thread_id = build_thread_id(user_id,current_user["role"])
    
    set_current_thread_id(thread_id)
    set_current_user_id(user_id)
    set_current_role(current_user["role"])
    
    if not user_message.strip():
        return JSONResponse(
            {"error": "Message is required."},
            status_code=400
        )

    agent = get_agent()

    ChatMessageService.save_chat_message(user_id,thread_id, "user", user_message)


    

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    
    # Check if this thread is currently paused waiting on a human response
    state = agent.get_state(config)

    if state.next:
        # The incoming user_message IS the human's answer to the pending interrupt
        stream_input = Command(resume=user_message)
    else:
        stream_input = {"messages": [HumanMessage(content=user_message)]}

    def event_generator():
        final_answer = ""

        try:

            for chunk, metadata in agent.stream(
                stream_input,
                config=config,
                stream_mode="messages",
            ):
                if not should_stream_chunk(chunk, metadata):
                    continue

                token = extract_text_from_chunk(chunk)

                if token:
                    final_answer += token
                    yield sse_data({"token": token})
                    
            # After streaming ends, check if graph paused on a NEW interrupt
            new_state = agent.get_state(config)

            if new_state.next:
                interrupt_msg = None
                for task in new_state.tasks:
                    if task.interrupts:
                        interrupt_msg = task.interrupts[0].value
                        break

                if interrupt_msg:
                    yield sse_data({"token": f"\n\n{interrupt_msg}"})
                    final_answer += f"\n\n{interrupt_msg}"        

            if final_answer.strip():
                ChatMessageService.save_chat_message(user_id,thread_id, "assistant", final_answer)

            yield sse_data({"done": True})

        except Exception as e:
            yield sse_data({"error": str(e)})
            yield sse_data({"done": True})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )





