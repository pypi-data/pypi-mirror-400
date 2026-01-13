from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from z_linus.model import gemini_thinking,gpt52
from pathlib import Path

from agno.tools.user_control_flow import UserControlFlowTools
from agno.tools.memory import MemoryTools
from agno.tools.reasoning import ReasoningTools
from z_linus.db import db


agent = Agent(
    id = "debug_agent",
    name= "debuger",
    role = "擅长解决常规的代码问题, 帮助用户debug, 具体问题具体分析",
    model=gemini_thinking,
    db=db,
    # instructions=[instruction],
    tools=[
        ReasoningTools(add_instructions=True,# 许多工具包都带有预先编写的指导，解释如何使用其工具。设置add_instructions=True将这些指令注入代理提示中
                       # ReasoningTools(enable_think=True, enable_analyze=True,
                       add_few_shot=True # 给定几个预编写好的 few - shot
                      ),
        MemoryTools(db=db, 
                    add_instructions=True,
                    add_few_shot=True,
                    enable_analyze=True,
                    enable_think=True,
                      ),
        UserControlFlowTools()
    ],
    markdown=True,
    add_history_to_context=True, # 控制是否携带上下文
)


