

from agno.team import Team
from z_linus.agents import debuger_agent,grammer_agent, github_agent
from z_linus.brain import agent
from z_linus.model import gemini_thinking

team = Team(
    name="News and Weather Team",
    model=gemini_thinking,
    instructions="Coordinate with team members to provide comprehensive information. Delegate tasks based on the user's request.",
    members=[
        agent,
        debuger_agent,
        grammer_agent,
        github_agent,

    ],
    share_member_interactions=True,  # 成员可看到彼此输出
    # delegate_to_all_members=False,    # 同时委派给所有成员
    )