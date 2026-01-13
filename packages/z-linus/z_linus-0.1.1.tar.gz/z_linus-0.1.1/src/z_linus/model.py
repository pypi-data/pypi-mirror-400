from agno.models.openai.like import OpenAILike
import os

API_KEY = os.getenv("BIANXIE_API_KEY")
BASE_URL = os.getenv("BIANXIE_BASE")
ARK_API_KEY = os.getenv("ARK_API_KEY")
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
REASONING_EFFORT = os.getenv("reasoning_effort")


gemini_nothinking=OpenAILike(id="gemini-2.5-flash-preview-05-20-nothinking",name="gemini_nothinking",api_key=API_KEY,base_url=BASE_URL)
gemini_thinking  =OpenAILike(id="gemini-2.5-flash-preview-05-20-thinking",name="gemini_thinking",api_key=API_KEY,base_url=BASE_URL,reasoning_effort=REASONING_EFFORT)
doubao32         =OpenAILike(id="doubao-1-5-pro-32k-250115",name="doubao-1-5-32K",api_key=ARK_API_KEY,base_url=ARK_BASE_URL,reasoning_effort=REASONING_EFFORT)
gpt51            =OpenAILike(id ="gpt-5.1",name="gpt-5.1",api_key=API_KEY,base_url=BASE_URL)
gpt52            =OpenAILike(id ="gpt-5.2-chat-latest",name="gpt-5.2",api_key=API_KEY,base_url=BASE_URL)
