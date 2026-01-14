from typing import Optional

from pydantic import BaseModel

# 添加狼人杀游戏状态
STATUS_START = "start"  # 游戏开始 分配角色
STATUS_NIGHT = "night"  # 夜晚阶段
STATUS_WOLF_SPEECH = "wolf_speech" # 狼人之间发言
STATUS_SKILL = "skill"  # 技能使用
STATUS_SKILL_RESULT = "skill_result"  # 技能结果
STATUS_NIGHT_INFO = "night_info"  # 夜晚信息
STATUS_DAY = "day"  # 白天阶段
STATUS_DISCUSS = "discuss"  # 讨论阶段
STATUS_VOTE = "vote"  # 投票
STATUS_VOTE_RESULT = "vote_result" # 投票结果
STATUS_RESULT = "result" # 游戏结果公布
STATUS_SHERIFF_SPEECH = "sheriff_speech" # 警长竞选发言
STATUS_SHERIFF = "sheriff" # 警长
STATUS_SHERIFF_VOTE = "sheriff_vote" # 警长投票
STATUS_SHERIFF_ELECTION = "sheriff_election" # 警长竞选
STATUS_SHERIFF_PK = "sheriff_pk" # 警长pk发言
STATUS_SHERIFF_SPEECH_ORDER = "sheriff_speech_order" # 警长发言顺序
STATUS_HUNTER = "hunter" # 猎人开枪
STATUS_HUNTER_RESULT = "hunter_result"



class AgentReq(BaseModel):
    # 消息（包括主持人消息，其它玩家的消息）
    message: Optional[str] = None
    # 玩家名称
    name: Optional[str] = None
    # 状态
    status: Optional[str] = None
    # 角色名称
    role: Optional[str] = None
    # 当前轮次
    round: Optional[int] = None


class AgentResp(BaseModel):
    success: bool
    result: Optional[str] = None
    # 技能释放玩家
    skillTargetPlayer: Optional[str] = None
    errMsg: Optional[str] = None
