from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from z_linus.model import gemini_thinking
from z_linus.db import db
from pathlib import Path
from agno.tools.mcp import MCPTools
from textwrap import dedent
from mcp import StdioServerParameters


BASE_DIR = Path(__file__).resolve().parent
prompt_path = BASE_DIR / "prompt.txt"
with open(prompt_path,'r') as f:
    instruction = f.read()
    instruction = dedent(instruction)


server_params = StdioServerParameters(
  command="npx",
  args=["-y", "@modelcontextprotocol/server-github"],
)

agent = Agent(
    id = "github_",
    name= "github_manager",
    role = "可以访问任何的公开github仓库,并浏览其中的信息, 同时可以管理自己的gihub仓库",
    user_id=None,
    session_id=None,
    # session_state={"shopping_list": []},
    model=gemini_thinking,
    db=db,
    instructions=['''
You are a GitHub assistant. Help users explore repositories and their activity.

- Use headings to organize your responses
- Be concise and focus on relevant information
'''],
    tools=[MCPTools(server_params=server_params)], # 没有关闭
    markdown=True,
    add_history_to_context=True, # 控制是否携带上下文
    # debug_mode = True,
)
