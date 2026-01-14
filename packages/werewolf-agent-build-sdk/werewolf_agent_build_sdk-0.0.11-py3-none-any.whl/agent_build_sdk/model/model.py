from typing import Optional

from pydantic import BaseModel

# 开始
STATUS_START = "start"
# 分配word
STATUS_DISTRIBUTION = "distribution"
# 轮次进行中
STATUS_ROUND = "round"
# 投票
STATUS_VOTE = "vote"
# 投票结果
STATUS_VOTE_RESULT = "vote_result"
# 游戏结果公布
STATUS_RESULT = "result"


class AgentReq(BaseModel):
    # 消息（包括主持人消息，其它玩家的消息）
    message: Optional[str] = None
    # 玩家名称
    name: Optional[str] = None
    # 状态
    status: Optional[str] = None
    # 分配的词
    word: Optional[str] = None
    # 当前轮次
    round: Optional[int] = None


class AgentResp(BaseModel):
    success: bool
    result: Optional[str] = None
    errMsg: Optional[str] = None
