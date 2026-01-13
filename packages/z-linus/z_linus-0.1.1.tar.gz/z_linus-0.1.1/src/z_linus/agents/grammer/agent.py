from agno.agent import Agent
from z_linus.model import gemini_thinking,gpt52,gemini_nothinking
from pathlib import Path
from z_linus.db import db

BASE_DIR = Path(__file__).resolve().parent
prompt_path = BASE_DIR / "prompt.txt"
with open(prompt_path,'r') as f:
    instruction = f.read()

agent = Agent(
    id = "grammer",
    name= "grammer_fa",
    role = "擅长语法问题, 通过一些说明来解释语法并给出代码示例",
    model=gpt52,
    db=db,
    instructions=[instruction],
    markdown=True,
    add_history_to_context=True, # 控制是否携带上下文
    enable_user_memories=True,
    # debug_mode = True,
)


