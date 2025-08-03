import httpx
import requests

from agents.product_finder import find_products
from agents.doubt_solver import ask_doubt_solver
from agents.request_gatherer import ask_request_gatherer

async def doraemon(start_message: str):
    memo = await ask_request_gatherer(start_message)
    
    top_3_product, all_products, product_names = await find_products(memo)
    
    data = {"product_details": top_3_product}
    
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/add_product_details",json=data)
    
    data = {"text": "Do you have any doubts?", "role": "Doubt_Solver"}
    
    user_message = ""
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
        response = await client.post(url="http://localhost:8000/ask_user",json=data)
    
        
        response = response.json()

        user_message = response['answer']
    
    
    if "no" in user_message.lower().split():
        async with httpx.AsyncClient() as client:    
            response = await client.get("http://localhost:8000/session_complete")
        
        return
                
    is_complete,updated_memo = await ask_doubt_solver(user_message,product_names,all_products)
    
    if is_complete:
        async with httpx.AsyncClient() as client:
                
            response = await client.get("http://localhost:8000/session_complete")
        return
    else:
        await doraemon(updated_memo)
        