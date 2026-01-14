import os
from random import shuffle

from agent_build_sdk.builder import AgentBuilder
from agent_build_sdk.model.model import AgentResp, AgentReq, STATUS_DISTRIBUTION, STATUS_ROUND, STATUS_VOTE, \
    STATUS_START, STATUS_VOTE_RESULT, STATUS_RESULT
from agent_build_sdk.sdk.agent import BasicAgent
from agent_build_sdk.sdk.agent import format_prompt
from prompts import DESC_PROMPT, VOTE_PROMPT
from agent_build_sdk.utils.logger import logger
import json

class HumanRecord:
    def __init__(self, filename='meta/simple_spy_chinese/human_records.json'):
        with open(filename) as f:
            data = json.load(f)

        human_record = set()
        short_human_record = set()
        for record in data:
            # pdb.set_trace()

            human = None
            machine = []
            for person, duty in record['agent_types'].items():
                if duty == 'human':
                    human = person
                else:
                    machine.append(person)

            if record['spy'] == human:
                continue

            for line in record['description'][human]:
                shuffle(machine)
                human_record.add((record['common_word'], line, record['description'][machine[0]][0]))

                if '。' not in line and len(line) < 6:
                    short_human_record.add((record['common_word'], line, record['description'][machine[0]][0]))

        self.human_record = list(human_record)
        self.short_human_record = list(short_human_record)

    def sample(self, num=3, type='common'):
        if type == 'common':
            sampled = self.human_record[:num]
            shuffle(self.human_record)
        elif type == 'short':
            sampled = self.short_human_record[:num]
            shuffle(self.short_human_record)

        return sampled

def check_and_update_result(result, othersSpeck):
    if othersSpeck:
        othersSpeck = othersSpeck[:-1]
        history_speeches = othersSpeck.split('#')
        for speech in history_speeches:
            if len(set(result) - set(speech)) <= 1:
                result += '的。'
                # logger.info("spy interact result: {}".format(result))
                return result
    # logger.info("spy interact result: {}".format(result))
    return result

class SpyAgent(BasicAgent):

    def __init__(self, name):

        super().__init__(name)

    def perceive(self, req=AgentReq):
        logger.info("spy perceive: {}".format(req))
        if req.status == STATUS_START:  # 开始新的一局比赛
            undercoverProbability = 16
            logger.info("-----------------------")
            if self.memory.has_variable("undercoverProbability"):
                undercoverProbability = self.memory.load_variable("undercoverProbability")
                logger.info('自己是卧底的概率：{}！'.format(undercoverProbability))
            #undercoverProbability = self.memory.load_variable("name", default='xiaomingming')
            self.memory.clear()
            #logger.info('上轮比赛的名字：{}！'+undercoverProbability)
            self.memory.set_variable("undercoverProbability",undercoverProbability)
            self.memory.set_variable("name", req.message)
            self.memory.append_history(
                '主持人: 女士们先生们，欢迎来到《谁是卧底》游戏！我们有一个由6名玩家组成的小组，在其中有一名卧底。让我们开始吧！每个人都会收到一张纸。其中5人的纸上拥有相同的单词，而卧底则会收到含义上相似的单词。我们将大多数人拿到的单词称为"公共词"，将卧底拿到的单词称为"卧底词"。一旦你拿到了你的单词，首先需要根据其他人的发言判断自己是否拿到了卧底词。如果判断自己拿到了卧底词，请猜测公共词是什么，然后描述公共词来混淆视听，避免被投票淘汰。如果判断自己拿到了公共词，请思考如何巧妙地描述它而不泄露它，不能让卧底察觉，也要给同伴暗示。每人每轮用一句话描述自己拿到的词语，每个人的描述禁止重复，话中不能出现所持词语。每轮描述完毕，所有在场的人投票选出怀疑是卧底的那个人，得票数最多的人出局。卧底出局则游戏结束，若卧底未出局，游戏继续。现在游戏开始。')
        elif req.status == STATUS_DISTRIBUTION:  # 分配单词
            self.memory.set_variable("word", req.word)
            self.memory.append_history(
                '主持人: 你好，{}，你分配到的单词是:{}'.format(self.memory.load_variable("name"), req.word))
        elif req.status == STATUS_ROUND:  # 发言环节
            if req.name:
                # 其他玩家发言
                self.memory.append_history(req.name + ': ' + req.message)
                othersSpeak = req.message
                if self.memory.has_variable("othersSpeak"):
                    othersSpeak = self.memory.load_variable("othersSpeak") + "#" + othersSpeak
                self.memory.set_variable("othersSpeak",othersSpeak)
                logger.info('其他人的发言为:{}'.format(othersSpeak))
            else:
                # 主持人发言
                self.memory.append_history('主持人: 现在进入第{}轮。'.format(str(req.round)))
                self.memory.append_history('主持人: 每个玩家描述自己分配到的单词。')
        elif req.status == STATUS_VOTE:  # 投票环节
            self.memory.append_history(req.name + ': ' + req.message)
        elif req.status == STATUS_VOTE_RESULT:  # 投票环节
            if req.name:
                self.memory.append_history('主持人: 投票结果是：{}。'.format(req.name))
            else:
                self.memory.append_history('主持人: 无人出局。')
        elif req.status == STATUS_RESULT:
            undercoverProbability = self.memory.load_variable('undercoverProbability')
            if '卧底是'+self.memory.load_variable("name") in req.message:
                logger.info('本局自己是卧底，增加卧底的概率内容填充！我是:{}<--------'.format(str(self.memory.load_variable("name"))))
                # 如果自己拿到过卧底词，则直接给自己的可能的概率置为 0
                self.memory.set_variable('undercoverProbability', 0)
            elif '卧底是' in req.message:
                logger.info('本轮至今还未拿到卧底词，则增加卧底概率！我是:{}<--------'.format(str(self.memory.load_variable("name"))))
                if self.memory.load_variable('undercoverProbability') != 0:
                    self.memory.set_variable('undercoverProbability', self.memory.load_variable('undercoverProbability') + 16)
            self.memory.append_history(req.message)
            logger.info('-----------本局结束，此时我为卧底的概率{}-----------'.format(undercoverProbability))
            #self.memory.append_history(req.message)
        else:
            raise NotImplementedError

    def interact(self, req=AgentReq) -> AgentResp:
        logger.info("spy interact: {}".format(req))
        othersSpeck=''
        if self.memory.has_variable("othersSpeak"):
            othersSpeck=self.memory.load_variable("othersSpeak")
        #self.memory.load_variable("othersSpeak")
        samples = self.human_record.sample(type="short")
        case = '（注意，请你描述的言简意赅的，并且严格模仿真实人类的描述语法/标点使用，这是几个具体的描述例子：1. {} '.format(
            samples[0][1])
        case += '2. {} '.format(samples[1][1])
        case += '3. {}）'.format(samples[2][1])
        if req.status == STATUS_ROUND:


            return AgentResp(success=True, result="我是一条测试语句", errMsg=None)


        elif req.status == STATUS_VOTE:
            self.memory.append_history('主持人: 到了投票的时候了。每个人，请指向你认为可能是卧底的人。')
            choices = [name for name in req.message.split(",") if name != self.memory.load_variable("name")]  # 排除自己
            self.memory.set_variable("choices", choices)
            prompt = format_prompt(VOTE_PROMPT, {"name": self.memory.load_variable("name"),
                                                 "choices": choices,
                                                 "history": "\n".join(self.memory.load_history())
                                                 })
            logger.info("prompt:" + prompt)
            result = 'test'
            if not result:
                if choices:
                    result = choices[0]
                else:
                    result = "No choices available"
            logger.info("spy interact result: {}".format(result))
            return AgentResp(success=True, result=result, errMsg=None)
        else:
            raise NotImplementedError


if __name__ == '__main__':
    name = 'A'
    code = "123"
    agent_builder = AgentBuilder(name, code, agent=SpyAgent(name), mock=False)
    agent_builder.start()
