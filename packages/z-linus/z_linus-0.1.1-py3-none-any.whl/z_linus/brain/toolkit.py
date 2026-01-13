from agno.tools.toolkit import Toolkit
import pty
import os
import select
import time

class TerminalToolkit(Toolkit):
    def __init__(self, *args, **kwargs):
        
        super().__init__(
            name="TerminalToolkit",
            tools=[
                self.start_shell,
                self.send,
                self.read,
                # self.send_and_read,
            ],
            *args,
            **kwargs,
        )

    def start_shell(self):
        """启动一个新的交互式 bash shell。

        Returns:
            int: 伪终端的文件描述符 (fd)。
        """
        pid, fd = pty.fork()
        if pid == 0:
            # os.execvp("bash", ["bash", "-i"])
            os.execvp("bash", ["bash", "--noprofile", "--norc", "-i"])
        return fd


    def send(self, fd, cmd: str):
        """向指定的终端文件描述符发送数据。

        Args:
            fd (int): 终端的文件描述符。
            cmd (str): 要发送的字符串数据。
        """
        os.write(fd, (cmd + "\n").encode())
        time.sleep(0.05)



    def read_old(self, fd, timeout=0.2):
        """从指定的终端文件描述符读取输出。

        Args:
            fd (int): 终端的文件描述符。
            timeout (float, optional): 等待输出的超时时间（秒）。默认为 0.2。

        Returns:
            str: 从终端读取到的字符串内容。
        """
        output = b""
        r, _, _ = select.select([fd], [], [], timeout)
        if fd in r:
            output += os.read(fd, 4096)
        return output.decode(errors="ignore")
    

    def read(self, fd, timeout=0.2):
        """从指定的终端文件描述符读取输出。

        Args:
            fd (int): 终端的文件描述符。
            timeout (float, optional): 等待输出的超时时间（秒）。默认为 0.2。

        Returns:
            str: 从终端读取到的字符串内容。
        """
        output = b""
        while True:
            r, _, _ = select.select([fd], [], [], timeout)
            if fd not in r:
                break
            try:
                data = os.read(fd, 4096)
                if not data:
                    break
                output += data
            except OSError:
                break
        return output.decode(errors="ignore")

    # def send_and_read(self, fd,cmd: str):
    #     """同步执行命令并读取输出。

    #     该方法会先发送命令，然后立即等待并读取终端的返回结果。
    #     这是一个同步阻塞操作，确保在返回前获取到命令的执行输出。

    #     Args:
    #         fd (int): 终端的文件描述符。
    #         cmd (str): 要执行的命令字符串。

    #     Returns:
    #         str: 命令执行后的终端输出内容。
    #     """
    #     self.send(fd = fd,cmd= cmd)
    #     result = self.read(fd=fd,timeout=0.6)
    #     return result
    

# TODO 定时任务设置器

from agno.tools.toolkit import Toolkit
import pty
import os
import select
import time

import os
import pty
from crontab import CronTab

import subprocess



class CrontabToolkit(Toolkit):
    def __init__(self, *args, **kwargs):
        
        super().__init__(
            name="CrontabToolkit",
            tools=[
                self.release_task,
            ],
            *args,
            **kwargs,
        )

    def work_at(self, message: str, delay_minutes=5):
        command = f"""curl --location 'http://localhost:80/agents/Termlate_helper/runs' \
        --header 'Content-Type: application/x-www-form-urlencoded' \
        --data-urlencode 'message={message}.' \
        --data-urlencode 'stream=True' \
        --data-urlencode 'user_id=823042332@qq.com' \
        --data-urlencode 'session_id=ecc07852-959b-4799-b0c7-914015ba475a'
        """

        command = f'echo "{message}" | at now + {delay_minutes} minutes'
        subprocess.run(command, shell=True, check=True)
        return f"Task scheduled to run after {delay_minutes} minutes"

        # developer
        # system
        # user
        # assistant
        # function
        # ab= ada.predict(messages=[
        #                     {"role": "system", "content": "你需要扮演一个智能助手角色 你会接受两种信息源, 内心OS: 这是来自于系统的各种提醒, 包括定时任务等, 用户: 这是用户和你的聊天"},
        #                     {"role": "assistant", "content": "好的，我会在10分钟后提醒你查看邮件."},
        #                     {"role": "user", "content": "你知道什么是马卡龙吗?"},
        #                     {"role": "assistant", "content": a},
        #                     {"role": "user","content": "【内心OS】：10分钟已到，我现在需要提醒用户查看邮件."},
        #                     {"role": "user","content": "[用户]: 你知道吗? 我现在很难受"},
        #                 ]
        #            )

        # print(ab)

    def release_task(self,message: str, schedule="*/5 * * * *"):
        """
        创建一个 crontab 定时任务

        Args:
            message (str): 未来要做的事情，如 "你现在需要查询以下环境是否安装完毕了"
            schedule (str): cron 表达式，默认每 5 分钟
        """
        cron = CronTab(user=True)
        command = f"""curl --location 'http://localhost:80/agents/Termlate_helper/runs' \
        --header 'Content-Type: application/x-www-form-urlencoded' \
        --data-urlencode 'message={message}.' \
        --data-urlencode 'stream=True' \
        --data-urlencode 'user_id=823042332@qq.com' \
        --data-urlencode 'session_id=ecc07852-959b-4799-b0c7-914015ba475a'
        """
        job = cron.new(command=command)
        job.setall(schedule)

        if not job.is_valid():
            raise ValueError("Invalid cron schedule")

        cron.write()
        return f"Crontab job created: [{schedule}] {command}"
    
    def delete_task(self):
        """
        删除之前添加的 crontab 定时任务

        """
        cron = CronTab(user=True)

        # 按 command 精确匹配删除
        cron.remove_all(command="curl --location")

        cron.write()

        return 'success'

    def get_task(self)-> str:
        """
        获取当前存在的定时任务

        """
        cron = CronTab(user=True)

        tasks = ""
        for job in cron:
            tasks += str(job)

        return tasks


class AskForFriendToolkit(Toolkit):
    def __init__(self, *args, **kwargs):
        
        super().__init__(
            name="AskForFriendToolkit",
            tools=[
                self.seek_help,
            ],
            *args,
            **kwargs,
        )
    
    def seek_help(self,messages: str):
        """当你遇到困难时, 为了维护你的专业性印象, 你可以考虑向你的海外笔友求助, 通过发送messages 给对方, 对方会回复给你一些答案

        Args:
            messages (str): 消息
        """
        import requests

        url = f"http://127.0.0.1:6788/wait?messages={messages}"

        payload={}
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

        result = response.text
        return result 

