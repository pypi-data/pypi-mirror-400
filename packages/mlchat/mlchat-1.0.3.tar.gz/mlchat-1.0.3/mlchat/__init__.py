import asyncio
import anyio
from pydantic import BaseModel
import json
import warnings
from mcp import ClientSession, StdioServerParameters
from openai import AsyncOpenAI, NOT_GIVEN
from loguru import logger as _log
from typing import AsyncIterator
from contextlib import AsyncExitStack
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client 
from mcp.client.streamable_http import streamable_http_client
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk,ChoiceDeltaToolCall, ChoiceDeltaToolCallFunction
from .extension import DialogueMessager, aget_trace, aget_title, ToolCeil, Messager

    
class _ToolCallStream(BaseModel):
    id: str
    name: str
    arguments: str =''
    
    def arg_add(self, data: ChoiceDeltaToolCall):
        if not data: return
        if not data.id:
            self.arguments += data.function.arguments or ''
        else:
            self.id = data.id
            if data.function.name: self.name = data.function.name
            self.arguments = data.function.arguments or ''
    
    def to_cdtc(self, index:int)->ChoiceDeltaToolCall:
        return ChoiceDeltaToolCall(index=index, id=self.id, 
                                   function=ChoiceDeltaToolCallFunction(arguments=self.arguments or '{}', name=self.name),
                                   type='function')
            
class AchatIt:
    def __init__(self, ait:AsyncIterator[Messager]):
        self._it = ait
    
    async def __anext__(self)->Messager:
        return await self._it.__anext__()
    
    def __aiter__(self):
        return self
    
    async def to_list(self, get_dict=False)->list[Messager|dict]:
        return [(mes.to_messager() if get_dict else mes) async for mes in self]
    
    async def first(self)->Messager:
        async for mes in self:
            if mes.is_finish: return mes
    
    async def last(self)->Messager:
        return (await self.to_list())[-1]

class MCPClient:
    def __init__(self, base_url, model, api_key='EMPTY', logger=None):
        self.exit_stack = AsyncExitStack()
        self.model = model
        self.aclient = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.server_session:dict[str, ClientSession] = {}  # 存储多个服务端会话
        self.server_tool:dict[str, list[str]] = {}
        self.available_tool:dict[str, ToolCeil] = {}
        self.tool_session = {}
        self.logger=logger or _log
    
    @property
    def tool_keys(self)->list[str]:
        return list(self.available_tool.keys())
    
    @property
    def tool_values(self)->list[ToolCeil]:
        return list(self.available_tool.values())
    
    async def _connect_to_server(self, server_name, session:ClientSession, strict:bool|None):
        await session.initialize()
        self.server_session[server_name]=session
        # 更新工具映射
        response = await session.list_tools()
        server_tools = []
        for tool in response.tools:
            # 构建统一的工具列表
            key = tool.name
            self.available_tool[key] = ToolCeil.from_mcp_tool(tool, strict=strict)
            self.logger.debug(self.available_tool[key])
            self.tool_session[tool.name] = session
            server_tools.append(key)
        self.server_tool[server_name] = server_tools
        self.logger.info(f"已连接到MCP服务器 - {server_name}\n{server_tools}")
        
    async def connect_to_stdio_server(self, server_name:str, command:str, *args: str, env:dict=None, strict:bool|None=None):
        server_params = StdioServerParameters(command=command, args=args, env=env)
        read_stream, write_stream = await self.exit_stack.enter_async_context(stdio_client(server_params))
        session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        return await self._connect_to_server(server_name, session, strict)
    
    async def connect_to_http_server(self, server_name:str, url:str, strict:bool|None=None, **kwargs):
        read_stream, write_stream,_ = await self.exit_stack.enter_async_context(streamable_http_client(url, **kwargs))
        session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        return await self._connect_to_server(server_name, session, strict)
    
    async def connect_to_sse_server(self, server_name:str, url:str, strict:bool|None=None, **kwargs):
        read_stream, write_stream = await self.exit_stack.enter_async_context(sse_client(url, **kwargs))
        session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        return await self._connect_to_server(server_name, session, strict)
    
    async def connect_to_config(self, config_or_path:dict|str, strict:bool|None=None):
        if isinstance(config_or_path, str):
            with open(config_or_path, encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = config_or_path
        for server_name, server_config in config['mcpServers'].items():
            if server_config.get("command"):
                await self.connect_to_stdio_server(server_name, server_config["command"], *server_config.get("args",[]), 
                                                   env=server_config.get("env"), strict=strict)
            elif server_config.get("url"):
                if server_config.get("type", 'http').lower() == 'sse':
                    await self.connect_to_sse_server(server_name, server_config["url"], strict=strict)
                else:
                    await self.connect_to_http_server(server_name, server_config["url"], strict=strict)
            else:
                warnings.warn(f"未指定command或url, 无法连接到 MCP 服务器 {server_name}")
    
    def set_tool_description(self, name:str, description:str):
        """重新设置工具描述"""
        self.available_tool[name].description = description
    
    async def _call_tool(self, tool_call):
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        # 根据工具名称找到对应的服务端
        session:ClientSession = self.tool_session[tool_name]
        self.logger.info(f"tool: {tool_name} args: {tool_args}")
        try:
            result = await session.call_tool(tool_name, tool_args)
        except anyio.ClosedResourceError:
            self.logger.info(f'{tool_name} 重新连接...')
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
        return tool_call.id, tool_name, tool_args, result.content
    
    def get_tool_choice(self, *tool_names:str):
        """部分模型并不支持单个或多个工具指定"""
        if not tool_names: 
            return 'auto'
        elif len(tool_names)==1: 
            return {
                "type": "function",
                "function": {"name": tool_names[0]}
            }
        else:
            return {
                'type': 'allowed_tools',
                'allowed_tools': {
                    'mode':'required',
                    'tools':[{ "type": "function", "function": { "name": tool_name }} for tool_name in tool_names]
                }
            }
        
    def chat(self, messages:list[Messager|dict], max_tool_num=3, use_tool_name:str|list[str]=None,
                    ban_tools:list[str]=None, custom_tools:list[ToolCeil]=None, **kwargs)->AchatIt:
        """调用大模型处理用户查询，并根据返回的 tools 列表调用对应工具。
        支持多次工具调用，直到所有工具调用完成。
        流式输出
        Args:
            query (str): 查询
            max_num (int, optional): 最大工具调用次数. Defaults to 3.
            user_tool (str): 强制调用工具title或name, 没有则该参数无效
            custom_tools (list[ToolCeil]): 自定义调用的工具组, 设置该参数则本身的工具不会调用
        Yields:
            str: 结果词语
        """
        async def _chat():
            the_messages = []
            for message in messages:
                mer = Messager(**message) if isinstance(message, dict) else message
                the_messages.append(mer.to_messager())
            available_tools = [tool.to_tool() for tool in (custom_tools if custom_tools else self.tool_values) if not ban_tools or tool.name not in ban_tools]
            # 循环处理工具调用
            for i in range(max_tool_num+1):
                tool_choice = 'auto'
                # 超出最大调用工具限制, 最后一次不再加载工具
                if i<max_tool_num:
                    # 仅首次会调用指定工具
                    if i==0 and use_tool_name:
                        tool_choice = self.get_tool_choice(*([use_tool_name] if isinstance(use_tool_name, str) else use_tool_name))
                else:
                    available_tools = None
                tcdt:dict[int, _ToolCallStream] = {}
                chunk:ChatCompletionChunk
                message = Messager(role="assistant", is_finish=False)
                async for chunk in await self.aclient.chat.completions.create(
                                        model=self.model,
                                        messages=the_messages,
                                        tools=available_tools,
                                        tool_choice=tool_choice if available_tools else NOT_GIVEN,
                                        **kwargs,
                                        stream=True
                                    ):
                    if chunk.choices:
                        message.chunk = chunk.choices[0].delta.content or ''
                        tool_calls = chunk.choices[0].delta.tool_calls
                    else:
                        message.chunk, tool_calls = '', None
                    if tool_calls:
                        for tool_call in tool_calls:
                            if tcdt.get(tool_call.index) is None: 
                                tcdt[tool_call.index] = _ToolCallStream(id=tool_call.id,name=tool_call.function.name)
                            tcdt[tool_call.index].arg_add(tool_call)
                    message.content += message.chunk
                    yield message
                message.tool_calls = [data.to_cdtc(index) for index,data in tcdt.items()] or None
                message.is_finish = True
                yield message
                the_messages.append(message.to_messager())
                # 没有工具调用则结束
                if not message.tool_calls: break
                # 执行实际工具调用
                for tool_call_id, tool_name, tool_args, rcs in await asyncio.gather(*[self._call_tool(tool_call) for tool_call in message.tool_calls]):
                    # 将工具调用的结果添加到 messages 中, 暂时只处理文本返回内容
                    for rc in rcs:
                        tmessage = Messager(role="tool", content=rc.text, name=tool_name, args=tool_args, tool_call_id=tool_call_id, is_finish=True)
                        yield tmessage
                        the_messages.append(tmessage.to_messager())
        
        return AchatIt(_chat())
        
    async def close(self):
        await self.exit_stack.aclose()
        self.server_session.clear()
    
    async def get_summary_title(self, historys:list[DialogueMessager])->str:
        """根据最近的历史记录生成总结性的标题"""
        if not historys: return ''
        return await aget_title(self.aclient, self.model, historys)
    
    async def get_traces(self, historys:list[DialogueMessager], trace_num:int=3)->list[str]:
        """根据最近的历史记录生成追问"""
        if not historys: return []
        return await aget_trace(self.aclient, self.model, historys, trace_num=trace_num)
    