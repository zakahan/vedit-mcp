import os
import sys
import asyncio
from loguru import logger
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from contextlib import AsyncExitStack
from google.adk.agents import LlmAgent
from google.adk.runners import Runner

# # adk-sample pip install requirements
# google-adk==0.3.0
# litellm==1.67.2


# about path
PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
VEDIT_MCP_PATH = os.path.join(PROJECT_PATH, "vedit_mcp.py")    
sys.path.append(PROJECT_PATH)     # To solve the path dependency problem


AGENT_DESCRIPTION = """
You are a video editing expert. Now you need to perform the following task:
There is currently a whole video, which is a live broadcast recording of an anchor. You are to act as a video clipper and cut the video according to the provided clipping instruction requirements.
Here, video editing tools will be provided for you, and you can just call them.
"""

AGENT_INSTRUCTION = """
You need to perform the editing operation. I will provide you with the editing task description, and you need to manipulate the tools to cut out the video.
You don't need to worry about the storage location of the edited video. This will be reasonably determined by the tool. As for the input file location, you only need to enter the relative path.
"""



# mcp client
async def aget_video_editor_tools():
    """Gets tools from mcp server"""
    logger.debug("Attempting to connection to video editor mcp server...")

    tools, exist_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="python",
            args=[
                VEDIT_MCP_PATH
            ],
            env={
                # About `KB_BASE_PATH`: It is recommended to use absolute paths. If you use relative paths, 
                # they must be relative to the execute path.
                "KB_BASE_PATH": "kb",      
                "MCP_USING_LOGGER": "True",
                "LOGGER_FILE_DIR": "."  # Similar to KB_BASE_PATH, it is still a path relative to execute path.
            }
        )
    )
    logger.debug("Video Edit MCP Toolset Created Successfully.")
    
    return tools, exist_stack


def get_inference_model():
    # For the `model` parameter and cloud platform - related content, please refer to: https://google.github.io/adk-docs/agents/models/
    model_name = 'doubao-1-5-thinking-pro-250415'
    return LiteLlm(
        model=f"openai/{model_name}",
        api_key=os.getenv('OPENAI_API_KEY'),
        api_base="https://ark.cn-beijing.volces.com/api/v3"    # Here, the ByteDance Volcano Ark platform is used.
    )


async def aget_clip_agent()-> tuple[LlmAgent, AsyncExitStack]:
    tools, exit_stack = await aget_video_editor_tools()

    clip_agent = LlmAgent( 
        model=get_inference_model(),   
        name="clip_agent",
        description=AGENT_DESCRIPTION,
        instruction=AGENT_INSTRUCTION,
        tools=tools,
        output_key="clip_result"
    )
    return clip_agent, exit_stack


async def aexecute(text:str) -> str:
    session_service = InMemorySessionService()
    session_service.create_session(
        app_name='clip_agent',
        user_id='user_00',
        session_id='session_00'
    )

    clip_agent, exit_stack = await aget_clip_agent()
    runner = Runner(
        app_name="clip_agent",
        agent=clip_agent,
        session_service=session_service
    )
    prompt = f"""The user's command is as follows: {text}\n
    Note: After each task is completed, please call the task_endding method to end the process."""
    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    events_async = runner.run_async(
        session_id='session_00',
        user_id='user_00',
        new_message=content
    )
    async for event in events_async:
        logger.info(f"Event received: {str(event.content)}")
        if event.is_final_response():
            await exit_stack.aclose()
            return event.content.parts[0].text
        pass
    return "orz"



if __name__ == "__main__":
    # Here is an example to complete the task of intercepting a certain part of video content.
    # Note that the task_id must exist. If you don't input the task_id, unexpected situations may occur.

    text = f"""task_id: 001\nOriginal video address: raw/test.mp4. Please cut out the part of the video from the 10th second to the 20th second."""
    result = asyncio.run(aexecute(text=text))
    print(result)