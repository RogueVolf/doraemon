import os
import uuid
import httpx
import asyncio
import requests
from dotenv import load_dotenv
from typing_extensions import Annotated
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console
from typing import Any, AsyncGenerator, Awaitable, Callable, ClassVar, Generator, Optional, Sequence, Union, cast
from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage,BaseAgentEvent, BaseChatMessage, HandoffMessage, TextMessage, UserInputRequestedEvent
from autogen_agentchat.agents import AssistantAgent,UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient


load_dotenv(".env")

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
        "role": "Request_Gatherer"
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


agent = AssistantAgent(
    name="Assistant_Agent",
    model_client=cerebras_client,
    system_message="""
You are an assistant agent designed to help a user do their shopping. You have to understand and create a short note after gathering details from the user to explain what product the user wants.
This memo will be used by other agents in their subsequent tasks to search, filter and find the best products to suggest to the user.
You are in a group chat with the user
While asking the user questions make sure you ask only one thing in one question. The user might be confused so do not overwhelm the user with a barrage of questions.   
Make sure to keep your questions to a minimum of 5 questions
When you are done with gathering all the requirements. Then your last response must be the memo of the user requirement and to terminate the word HOGAYA in your reply, do not merge this with a question complete your questions
Do not provide the memo in the same response with a question you might want to ask
""",
)

user_proxy = CustomUserProxyAgent(name="user",input_func=ask_user)

async def ask_request_gatherer(start_message: str):
    termination_token = TextMentionTermination("HOGAYA")
    
    team = RoundRobinGroupChat(participants=[agent,user_proxy],termination_condition=termination_token)
    
    stream = team.run_stream(task=start_message)
    
    last_message = None
    async for message in stream:
        last_message = message
    
    try:
        memo = last_message.messages[-1].content.replace("HOGAYA","")
        
        
        data = {"text": memo, "role": "Request_Gatherer"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/send_agent_text", json=data)
            
        return memo
    
    except Exception as e:
        print(e)