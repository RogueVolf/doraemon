# backend.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import websockets
import uvicorn
from pydantic import BaseModel
from typing import Any
from typing_extensions import List,Dict

from orchestrator import doraemon

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class QuestionData(BaseModel):
    question: str
    
class AgentText(BaseModel):
    text: str
    role: str
    
class Product_Details(BaseModel):
    product_details: List[Dict[Any,Any]]
    
active_connection: WebSocket = None
user_input_queue = asyncio.Queue()  # Shared queue between WebSocket and agent
task_started = False
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global active_connection,task_started
    await websocket.accept()
    active_connection = websocket
    try:
        while True:
            message = await websocket.receive_text()
            if not task_started:
                asyncio.create_task(doraemon(message))
                task_started = True
            else:
                await user_input_queue.put(message)  # Push user reply into the queue
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        active_connection = None

@app.post("/ask_user")
async def ask_user(data: AgentText):
    await active_connection.send_json(data.model_dump())
    
    user_text = await user_input_queue.get()
    
    return {"answer":user_text}

@app.post("/send_agent_text")
async def send_agent_text(data: AgentText):

    await active_connection.send_json(data.model_dump())
    
    return {"status": True}

@app.post("/add_product_details")
async def add_product_details(data: Product_Details):
    product_details = data.product_details
    
    await active_connection.send_json(product_details)
    
    return {"status": True}

@app.get("/session_complete")
async def session_complete():
    global task_started
    task_started = False
    
    
if __name__ == '__main__':
    uvicorn.run('backend:app', log_level='debug', reload=True)



