from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .chatbot import graph, conversation_history, create_new_conversation
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)

class ChatRequest(BaseModel):
    user_input: str

@router.get("/")
async def read_root():
    return {"message": "Welcome Here!!!!"}

@router.post("/chat")
async def chat(request: ChatRequest):
    global conversation_history
    logging.info(f"Received request: {request.user_input}")
    try:
        # Add the new user message to the conversation history
        conversation_history["messages"].append({"role": "user", "content": request.user_input})
        
        # Invoke the graph with the updated state and explicit configuration
        result = graph.invoke(
            conversation_history,
            config={
                "thread_id": "default",
                "checkpoint_ns": "default_namespace",
                "checkpoint_id": "default_checkpoint"
            }
        )
        
        # Update the conversation history with the result
        conversation_history.update(result)
        
        response_content = conversation_history["messages"][-1].content
        logging.info(f"Response: {response_content}")
        return {"response": response_content}
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        # Reset conversation history on error
        conversation_history = create_new_conversation()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_conversation():
    global conversation_history
    conversation_history = create_new_conversation()
    return {"message": "Conversation reset successfully"}