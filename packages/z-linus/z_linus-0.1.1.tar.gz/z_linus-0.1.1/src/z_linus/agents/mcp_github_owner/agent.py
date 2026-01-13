from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from z_linus.model import gemini_thinking
from z_linus.db import db
from pathlib import Path
from agno.tools.mcp import MCPTools
import asyncio
from textwrap import dedent
from mcp import StdioServerParameters





# AI Control
id = "agno_knowledge_1"
# AI Control End


BASE_DIR = Path(__file__).resolve().parent
prompt_path = BASE_DIR / "prompt.txt"
with open(prompt_path,'r') as f:
    instruction = f.read()
    instruction = dedent(instruction)


'''
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "mcp/github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "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"
      }
    }
  }
}
'''
server_params = StdioServerParameters(
  command="docker",
  args=[
      "run",
      "-i",
      "--rm",
      "-e",
      "GITHUB_PERSONAL_ACCESS_TOKEN",
      "mcp/github"
      ],
  env={
        "GITHUB_PERSONAL_ACCESS_TOKEN": "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"
      }
)

agent = Agent(
    id = id,
    user_id=None,
    session_id=None,
    # session_state={"shopping_list": []},
    model=gemini_thinking,
    db=db,
    instructions=[instruction],
    tools=[MCPTools(server_params=server_params)], # 没有关闭
    markdown=True,
    add_history_to_context=True, # 控制是否携带上下文
    # debug_mode = True,
)

# async with MCPTools(server_params=server_params) as mcp_tools:
#     agent = Agent(

if __name__ == "__main__":
    message ="告诉我, 我现在有哪些私有项目  https://github.com/zxfpro"
    asyncio.run(
        agent.aprint_response(message, stream=True)
    )




"""
{
  "mcpServers": {
    "puppeteer": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--init",
        "-e",
        "DOCKER_CONTAINER=true",
        "mcp/puppeteer"
      ]
    }
  }
}
"""




{
  "mcpServers": {
    "shell": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "mcp-shell:latest"],
      "env": {
        "MCP_SHELL_SECURITY_ENABLED": "true",
        "MCP_SHELL_LOG_LEVEL": "info"
      }
    }
  }
}

# 开不了

{
  "mcpServers": {
    "mcp-tasks": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "flesler/mcp-tasks"
      ]
    }
  }
}
