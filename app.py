import asyncio
import os
import json
from typing import List, Dict, Any, Union
from contextlib import AsyncExitStack
import re

import gradio as gr
from gradio.components.chatbot import ChatMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=KEY)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class MCPClientWrapper:
    def __init__(self):
        self.session = None
        self.exit_stack = None
        self.tools = []
    
    def connect(self, server_path: str) -> str:
        return loop.run_until_complete(self._connect(server_path))
    
    async def _connect(self, server_path: str) -> str:
        if self.exit_stack:
            await self.exit_stack.aclose()
        
        self.exit_stack = AsyncExitStack()
        
        is_python = server_path.endswith('.py')
        command = "python" if is_python else "node"
        
        server_params = StdioServerParameters(
            command=command,
            args=[server_path],
            env={"PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        
        response = await self.session.list_tools()
        self.tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]
        
        tool_names = [tool["name"] for tool in self.tools]
        return f"Connected to MCP server. Available tools: {', '.join(tool_names)}"
    
    def process_message(self, message: str, history: List[Union[Dict[str, Any], ChatMessage]]) -> tuple:
        if not self.session:
            return history + [
                {"role": "user", "content": message}, 
                {"role": "assistant", "content": "Please connect to an MCP server first."}
            ], gr.Textbox(value="")
        
        new_messages = loop.run_until_complete(self._process_query(message, history))
        return history + [{"role": "user", "content": message}] + new_messages, gr.Textbox(value="")
    
    async def _process_query(self, message: str, history: List[Union[Dict[str, Any], ChatMessage]]):
        gemini_messages = []
        for msg in history:
            if isinstance(msg, ChatMessage):
                role, content = msg.role, msg.content
            else:
                role, content = msg.get("role"), msg.get("content")
            if role in ["user", "assistant", "system"]:
                gemini_messages.append({"role": role, "content": content})
        gemini_messages.append({"role": "user", "content": message})

        # Build tool list for prompt
        tool_list = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in self.tools])
        prompt = (
            "Use the tools with values that seem right to you, do not ask inout for every tool use unless necessary. You can make multiple tool calls if necessary to complete a task(one after another). You have access to the following tools:\n"
            + tool_list +
            "\n\nIf you want to use a tool, respond ONLY with a JSON object like this:\n"
            '{"tool_call": {"name": "<tool_name>", "args": {"param1": "value1"}}}'
            "\nOtherwise, answer as usual.\n\n"
            "Conversation so far:\n"
            + "\n".join([m["content"] for m in gemini_messages])
        )

        response = gemini_client.models.generate_content(
            model="gemini-2.5-pro-exp-03-25",
            contents=[prompt]
        )

        result_messages = []
        text = response.text.strip()

        # Try to detect a tool call (look for '"tool_call"' in the response)
        if '"tool_call"' in text:
            try:
                # Extract the first JSON object from the response
                json_match = re.search(r'\{[\s\S]*\}', text)
                if not json_match:
                    raise ValueError("No JSON object found in response.")
                cleaned = json_match.group(0)
                tool_json = json.loads(cleaned)
                tool_call = tool_json["tool_call"]
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                # Call the tool with a timeout
                try:
                    result = await asyncio.wait_for(self.session.call_tool(tool_name, tool_args), timeout=10)
                    tool_result = result.content
                except asyncio.TimeoutError:
                    result_messages.append({
                        "role": "assistant",
                        "content": f"Tool call '{tool_name}' timed out. Please try again or check the tool."
                    })
                    return result_messages
                # Send tool result back to Gemini
                followup_prompt = (
                    f"Tool result for {tool_name}: {tool_result}\nContinue the conversation."
                )
                followup_response = gemini_client.models.generate_content(
                    model="gemini-2.5-pro-exp-03-25",
                    contents=[followup_prompt]
                )
                result_messages.append({
                    "role": "assistant",
                    "content": followup_response.text.strip()
                })
            except Exception as e:
                result_messages.append({
                    "role": "assistant",
                    "content": f"Error parsing or executing tool call: {e}\nRaw response: {text}"
                })
        else:
            result_messages.append({
                "role": "assistant",
                "content": text
            })
        return result_messages

client = MCPClientWrapper()

def gradio_interface():
    with gr.Blocks(title="Photoshop MCP Client",theme="soft") as demo:
        gr.Markdown("# Photoshop Assistant")
        gr.Markdown("Connect to your Photoshop MCP server and chat with the assistant")
        
        with gr.Row(equal_height=True):
            with gr.Column(scale=4):
                server_path = gr.Textbox(
                    label="Server Script Path",
                    placeholder="Enter path to server script ",
                    value="psMCP.py"
                )
            with gr.Column(scale=1):
                connect_btn = gr.Button("Connect")
        
        status = gr.Textbox(label="Connection Status", interactive=False)
        
        chatbot = gr.Chatbot(
            value=[], 
            height=500,
            type="messages",
            show_copy_button=True,
            avatar_images=("👤", "🤖")
        )
        
        with gr.Row(equal_height=True):
            msg = gr.Textbox(
                label="Your Question",
                placeholder="Ask the assistant to help you with photoshop (eg open photoshop)",
                scale=4
            )
            clear_btn = gr.Button("Clear Chat", scale=1)
        
        connect_btn.click(client.connect, inputs=server_path, outputs=status)
        msg.submit(client.process_message, [msg, chatbot], [chatbot, msg])
        clear_btn.click(lambda: [], None, chatbot)
        
    return demo

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY not found in environment. Please set it in your .env file.")
    
    interface = gradio_interface()
    interface.launch(debug=True)