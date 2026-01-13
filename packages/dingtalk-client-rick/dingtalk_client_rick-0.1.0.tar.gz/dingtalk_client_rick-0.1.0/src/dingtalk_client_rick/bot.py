import json
from dataclasses import dataclass
from typing import Dict, Any, List
from .base import DingTalk


class BaseMessage:
    """钉钉基础消息类"""

    msg_type: str = "sampleMarkdown"

    def as_dict(self) -> Dict[str, Any]:
        """将消息转换为字典格式"""
        # 移除msg_type,其他组合为字典
        msg_param = {k: v for k, v in self.__dict__.items() if k != "msg_type"}
        return {
            "msgKey": self.msg_type,
            "msgParam": json.dumps(msg_param, ensure_ascii=False),
        }


@dataclass
class TextMessage(BaseMessage):
    """钉钉文本消息类"""

    content: str
    msg_type: str = "sampleText"


@dataclass
class MarkdownMessage(BaseMessage):
    """钉钉Markdown消息类"""

    title: str
    text: str
    msg_type: str = "sampleMarkdown"


class Bot(DingTalk):

    def send_text_message(
        self, userids: List[str], message: BaseMessage
    ) -> Dict[str, Any]:
        """发送文本消息"""
        endpoint = "/v1.0/robot/oToMessages/batchSend"
        body = {
            "robotCode": self.app_key,
            "userIds": userids,
            **message.as_dict(),
        }
        return self.post(endpoint, json=body)
