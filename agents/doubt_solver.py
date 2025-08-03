import os
import uuid
import httpx
import asyncio
import requests
from dotenv import load_dotenv
from typing_extensions import Annotated,Dict
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console
from typing import Any, AsyncGenerator, Awaitable, Callable, ClassVar, Generator, Optional, Sequence, Union, cast
from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage,BaseAgentEvent, BaseChatMessage, HandoffMessage, TextMessage, UserInputRequestedEvent
from autogen_agentchat.agents import AssistantAgent,UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient


load_dotenv(".env")
product_details = {}

class CustomUserProxyAgent(UserProxyAgent):
    def __init__(self, name, *, description = "A human user", input_func = None):
        super().__init__(name, description=description, input_func=input_func)
        
    async def on_messages_stream(
        self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
        """Handle incoming messages by requesting user input."""
        try:
            # Check for handoff first
            handoff = self._get_latest_handoff(messages)
            last_message = messages[-1].content
            prompt = last_message

            request_id = str(uuid.uuid4())

            input_requested_event = UserInputRequestedEvent(request_id=request_id, source=self.name)
            yield input_requested_event
            with UserProxyAgent.InputRequestContext.populate_context(request_id):
                user_input = await self._get_input(prompt, cancellation_token)

            # Return appropriate message type based on handoff presence
            if handoff:
                yield Response(chat_message=HandoffMessage(content=user_input, target=handoff.source, source=self.name))
            else:
                yield Response(chat_message=TextMessage(content=user_input, source=self.name))

        except asyncio.CancelledError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to get user input: {str(e)}") from e

def ask_user(prompt: str, cancellation_token: CancellationToken | None = None
             ) -> Annotated[str,"The answer from the user for this question"]:
    data = {
        "text": prompt,
        "role": "Doubt_Solver"
    }

    response = requests.post(url="http://localhost:8000/ask_user",json=data)
    
    if response.ok:
        response = response.json()

        response_data = { 'content': response["answer"], 'source': 'user' }
        
        message = TextMessage.model_validate(response_data)
        
        return message.content
    
    else:
        response_data = { 'content': "User not available to answer this query", 'source': 'user' }
        
        message = TextMessage.model_validate(response_data)
        
        return message.content

cerebras_client = OpenAIChatCompletionClient(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.environ["CEREBRAS_API_KEY"],
    model="llama-4-scout-17b-16e-instruct",
    model_info={
        "json_output": True,
        "function_calling": True,
        "vision": False,
        "family": "unknown",
        "structured_output": True,
    }
)

def view_product_details(title: Annotated[str,"The title of the product to view details for"]
                         ) -> Annotated[Dict[str,str],"The detailed product details dictionary"]:
    
    title = title.lower()
    
    for product_title in product_details.keys():
        if title in product_title:
            return product_details[product_title]

    else:
        return {"Failed":"Title not found"}

def suggest_product(title: Annotated[str,"The title of the product to suggest"]
                    ) -> Annotated[str,"True if the product was suggested successfully else False with reason why it failed"]:
    
    if title not in product_details:
        return "Title not found, cannot suggest the product"
    
    else:
        product = product_details[title]
        data = {"product_details": [product]}
        
        response = requests.post("http://localhost:8000/add_product_details",json=data)
        
        if response.ok:
            return "Product Suggested Successfully"
        else:
            return "Could not suggest product"
        

agent = AssistantAgent(
    name="Assistant_Agent",
    model_client=cerebras_client,
    description="The assistant agent to help the user",
    system_message="""
You are an assistant agent designed to solve the queries of the user and reinitate the search if you think that is required. Your first instinct should be to help the user choose from the list of products that you have details of.
The user is seeing the top three or less relevant products, you have to solve doubts in those products. If you think the user does not like any product, change the memo of the user requirement or suggest a new product from the list of all products you have
You will be provided this memo of the user requirement too.

You have been given 2 tools
The first tool is to view the detail of any product by providing its title, this tool is called view_product_details
The second tool is to suggest another product to the user from the list of all products provided to you, this tool is called suggest_product

Greet the user first and help them make a good choice
""",
    tools=[view_product_details,suggest_product]
)

user_proxy = CustomUserProxyAgent(name="User",description="The user agent",input_func=ask_user)

async def ask_doubt_solver(user_message,product_names,product_details_dict):
    termination_token = TextMentionTermination("HOGAYA")
    
    global product_details
    
    product_details = product_details_dict
    
    selector_prompt = """Select an agent to perform task.

{roles}

Current conversation context:
{history}

Read the above conversation, then select an agent from {participants} to perform the next task.
Only select one agent.

The Assistant_Agent is trying to help by solving the doubts of the User. Select the user agent when you think a question is being asked to the User or a text is meant for the User

"""
    
    team = SelectorGroupChat(participants=[agent,user_proxy],model_client=cerebras_client,selector_prompt=selector_prompt,
                             termination_condition=termination_token,allow_repeated_speaker=True)
    
    formatted_product_names = '\n'.join(product_names)
    stream = team.run_stream(task=f"User Doubt:\n{user_message}.\nAll Products:\n{formatted_product_names}")
    
    last_message = None
    async for message in stream:
        last_message = message
        print(last_message)
    
    try:
        last_message_content = last_message.messages[-1].content.replace("HOGAYA","")
        
        if 'updated_memo' in last_message_content:
            return False, last_message_content
        else:
            return True, last_message_content
    
    except Exception as e:
        print(e)