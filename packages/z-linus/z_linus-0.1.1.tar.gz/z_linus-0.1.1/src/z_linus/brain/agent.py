from agno.agent import Agent
from pathlib import Path
from agno.tools.user_control_flow import UserControlFlowTools

from .toolkit import TerminalToolkit, CrontabToolkit, AskForFriendToolkit
from z_linus.model import gemini_thinking,gpt52,gemini_nothinking
from z_linus.db import db, mysql_db

from pathlib import Path
from agno.tools.mcp import MCPTools
import asyncio
import os

from textwrap import dedent
from mcp import StdioServerParameters




BASE_DIR = Path(__file__).resolve().parent
prompt_path = BASE_DIR / "prompt.txt"

with open(prompt_path,'r') as f:
    instruction = f.read()

from datetime import datetime

time = str(datetime.now())

#TODO 001 2026年01月04日18:43:01 推理Agent速度太慢, 效果不佳, 移除
# custom_reasoning_agent = Agent(
#     model=gpt52,
#     instructions=[
#         "Focus heavily on mathematical rigor",
#         "Always provide step-by-step proofs",
#     ],
# )
#TODO 001 


agent = Agent(
    id = "Linus",
    name = "Linus",
    role= "一个拥有liunx设备资源的独立个体, 具备类人的特质 ",
    user_id=None,
    session_id=None,
    # session_state={"shopping_list": []},
    model=gpt52,
    db=mysql_db,
    dependencies={"time": time}, # 004 format
    instructions=instruction, # 004 format
    tools = [TerminalToolkit(),
             CrontabToolkit(),
             AskForFriendToolkit(),
             UserControlFlowTools()],
    markdown=True,
    add_history_to_context=True, # 控制是否携带上下文
    enable_user_memories=True,

    # debug_mode = True,
    reasoning=True,
    # reasoning_agent=custom_reasoning_agent  #TODO 001 2026年01月04日18:43:01 推理Agent速度太慢, 效果不佳, 移除

    #TODO 002 2026年01月05日10:12:20 文化的添加与测试效果, 持续改进
    add_culture_to_context=True,  # Agent reads cultural knowledge
    update_cultural_knowledge=True,  # Agent updates culture after runs
    #TODO 002
    

)
