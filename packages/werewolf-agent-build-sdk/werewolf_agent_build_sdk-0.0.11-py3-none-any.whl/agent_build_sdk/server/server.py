import uvicorn
from fastapi import FastAPI

from agent_build_sdk.model.werewolf_model import AgentReq, AgentResp

from agent_build_sdk.sdk.agent import BasicAgent
from agent_build_sdk.utils.logger import logger
from fastapi.responses import HTMLResponse
import re
import markdown2


def remove_text_between_dashes(text):
    # 使用正则表达式去除被 --- 包裹的内容
    cleaned_text = re.sub(r'---.*?---', '', text, flags=re.DOTALL)
    return cleaned_text

class EndpointServer:
    def __init__(self, agent: BasicAgent):
        self.app = FastAPI()
        self.agent = agent

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @self.app.get("/", response_class=HTMLResponse)
        async def read_root():
            with open("README.md", "r", encoding="utf-8") as f:
                readme_content = f.read()

            readme_content = remove_text_between_dashes(readme_content)

            # 将 Markdown 格式转换为 HTML
            html_content = markdown2.markdown(readme_content, extras=["fenced-code-blocks", "tables"])
            # return HTMLResponse(content=html_content)
            # 返回 HTML 响应
            return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://github.githubassets.com/assets/github-dark.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css">
        <title>Markdown to HTML</title>
        <style>
            /* 适应样式 */
            .markdown-body {{
                box-sizing: border-box;
                min-width: 200px;
                max-width: 800px;
                margin: 0 auto;
                padding: 45px;
            }}
        </style>
    </head>
    <body>
        <article class="markdown-body">
            {html_content}
        </article>
    </body>
    </html>
    """)

        @self.app.post("/agent/init")
        def init(req: AgentReq) -> AgentResp:
            self.agent.memory.clear()
            return AgentResp(success=True, result=self.agent.model_name)

        @self.app.post("/agent/getModelName")
        def get_model_name(req: AgentReq) -> AgentResp:
            return AgentResp(success=True, result=self.agent.model_name)
        # interact
        @self.app.post("/agent/interact")
        def interact(req: AgentReq) -> AgentResp:
            return self.agent.interact(req)

        # perceive
        @self.app.post("/agent/perceive")
        def perceive(req: AgentReq):
            try:
                self.agent.perceive(req)
                return AgentResp(success=True)
            except Exception as e:
                logger.error(f"invoke perceive error.", e)
                return AgentResp(success=False, errMsg=f"perceive error {e}")

        @self.app.post("/agent/checkHealth")
        def checkHealth(req: AgentReq):
            return AgentResp(success=True)

    def start(self):
        uvicorn.run(self.app, host="0.0.0.0", port=7860)

