from agno.os import AgentOS
from fastapi import FastAPI
import asyncio
import requests
import json
import argparse

from z_linus.brain import agent 
from z_linus.db import mysql_db

from z_linus.team import team as teams

app = FastAPI()


default = 80

event = None
result = None
TIMEOUT = 60  # 超时时间（秒）

@app.post("/wait")
async def wait_for_input(messages: str):
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/7e02b778-c167-40ea-ace9-b5305dee50c8"

    global event, result

    # 每次 wait 都重新创建
    event = asyncio.Event()
    result = None
    
    data = {
        "msg_type": "text",
        "content": {
            "text": f"消息，{messages}"
        }
    }
    
    response = requests.post(
        webhook_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    
    print(response.text)

    try:
        await asyncio.wait_for(event.wait(), timeout=TIMEOUT)
        return {"result": result}
    except asyncio.TimeoutError:
        return {"result": "暂时没有回复,自己作主"}


@app.post("/input")
async def provide_input(data: str):
    global event, result

    # 没有在等待，直接拒绝
    if event is None or event.is_set():
        return {"error": "no active wait"}

    result = data
    event.set()   # 唤醒 /wait

    return {"status": "ok"}


# AG-UI
# from agno.os.interfaces.agui import AGUI # AG-UI

agent_os = AgentOS(
    id="debug_01",
    description="一个用于改错和提问",
    agents=[agent],
    teams=[teams],
    # workflows=[agno_workflow]
    base_app = app,
    #TODO 003 追踪服务器的设定
    tracing=True,
    tracing_db=mysql_db,
    #TODO 003
    a2a_interface=True,
)

app = agent_os.get_app()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        "port",
        metavar="PORT",
        type=int,
        nargs="?",  # 端口是可选的
        default=default,
        help=f"Specify alternate port [default: {default}]",
    )
    # 创建一个互斥组用于环境选择
    group = parser.add_mutually_exclusive_group()

    # 添加 --dev 选项
    group.add_argument(
        "--dev",
        action="store_true",  # 当存在 --dev 时，该值为 True
        help="Run in development mode (default).",
    )

    # 添加 --prod 选项
    group.add_argument(
        "--prod",
        action="store_true",  # 当存在 --prod 时，该值为 True
        help="Run in production mode.",
    )
    args = parser.parse_args()

    if args.prod:
        env = "prod"
    else:
        # 如果 --prod 不存在，默认就是 dev
        env = "dev"

    port = args.port
    print(port)
    if env == "dev":
        port += 100
        reload = True
        app_import_string = f"{__package__}.{__file__.split('/')[-1].split(".")[0]}:app"
    elif env == "prod":
        reload = False
        app_import_string = f"{__package__}.{__file__.split('/')[-1].split(".")[0]}:app"
    else:
        reload = False
        app_import_string = f"{__package__}.{__file__.split('/')[-1].split(".")[0]}:app"


    agent_os.serve(app=app_import_string,
                host = "0.0.0.0",
                port = port, 
                reload=reload)
