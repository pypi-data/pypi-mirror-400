from .base import DingTalk
from typing import Dict, Any


class User(DingTalk):
    """
    用户管理类
    """

    # ========== 常用API方法 ==========

    def get_user_info(self, query: str) -> Dict[str, Any]:
        """获取用户信息"""
        endpoint = "/v1.0/contact/users/search"
        data = {"queryWord": query, "offset": 0, "size": 10, "fullMatchField": 1}
        return self.post(endpoint, json=data)

    def get_user_detail(self, userid: str) -> Dict[str, Any]:
        """获取用户详情"""
        endpoint = "topapi/v2/user/get"
        body = {"userid": userid}
        return self.post(endpoint, json=body)

    def get_union_id(self, userName: str) -> Dict[str, Any]:
        """获取用户unionid"""
        userids = self.get_user_info(userName).get("list", [])
        if not userids:
            return {"error": "用户不存在"}
        userid = userids[0]
        user_info = self.get_user_detail(userid)
        result = self.parse_jsonpath("$..result").find(user_info)[0].value
        return result
