import json
import httpx
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing_extensions import Annotated,List,Dict,Union,Tuple

from Utils.llm_utils import ask_llm
from Utils.stealth_amazon_scrapper import stealth_amazon_scraper
from Utils.stealth_flipkart_scrapper import stealth_flipkart_scrapper


executor = ThreadPoolExecutor(max_workers=2)

async def run_in_thread(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lambda: func(*args))

async def get_search_query(memo: Annotated[str,'The memo of the user requirement']
                           ) -> Annotated[Dict[str,str],"The search query dictionary for amazon and flipkart"]:
    message = f"""
Given the memo of the requirements that the user has create a search query for Amazon and Flipkart.
These search queries should be brief but exact so that we can find the perfect product for the user

Your response must be in the following JSON structure

{{
    'amazon': 'search string for amazon',
    'flipkart': 'search string for flipkart'
}}    

Memo of the user Requirement:
{memo}
"""

    response_data = await ask_llm(message=message)

    response = json.loads(response_data)
    
    return response


async def get_relevance(product_detail: Annotated[Dict[str,str],"The dictionary with the product detaisl"],
                          memo: Annotated[str,"The user requirement memo"]
                          ) -> Annotated[Dict[str,Union[bool,str]],"Dictionary with the product relevance details"]:
    
    message = f"""
Given the memo that captures the essence of the requirements that the user has with regards to buying a product, evaluate the given product details.
Your role is to figure out how relevant the product is to the user and output the following JSON structure

{{
    'relevant': true or false,
    'relevance_score': A score between 0 - 4 on how relevant the product is, 0 if it is not relevant
}}    

User Requirements:
{memo}

Product Details:
{product_detail}
"""

    response_data = await ask_llm(message=message)
    
    response = json.loads(response_data)
    
    if isinstance(response,list):
        response = response[0]
    
    if not isinstance(response,dict):
        return True,3
    
    return response['relevant'],response['relevance_score']


async def find_products(memo: Annotated[str,"The memo of the user requirement"]
                        ) -> Annotated[Tuple[List[Dict[str, str]], List[Dict[str, str]], List[str]], "The filtered products and metadata"]:
    
    try:
        search_strings = await get_search_query(memo=memo)
        
        amazon_task = asyncio.create_task(run_in_thread(stealth_amazon_scraper,search_strings['amazon']))
        flipkart_task = asyncio.create_task(run_in_thread(stealth_flipkart_scrapper,search_strings['flipkart']))
        
        amazon_results,flipkart_results = await asyncio.gather(amazon_task,flipkart_task)
        
        data = {"text": "Found 14 products. Filtering them this will take just a minute", "role": "Product_Finder"}
            
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/send_agent_text", json=data)
        
        combined_product_results = amazon_results + flipkart_results
        
        relevant_products = []
        
        #Not using multithreading on purpose cause cerebras free has limits
        for product_detail in combined_product_results:
            relevant,relevance_score = await get_relevance(product_detail,memo)
            
            if relevant:
                product_detail['relevance_score'] = relevance_score
                relevant_products.append(product_detail)
                
        
        relevant_products = sorted(relevant_products,key= lambda x : x['relevance_score'],reverse=True)
        top_3_products = relevant_products[:3]
        data = {"text": "Products filtered showing the top results relevant to you", "role": "Product_Finder"}
            
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/send_agent_text", json=data)
        
        all_product_names = [x['title'] for x in relevant_products] 
        all_products = {x['title'].lower():x for x in relevant_products}       

        return top_3_products,all_products,all_product_names
        
    except Exception as e:
        print(e)
        