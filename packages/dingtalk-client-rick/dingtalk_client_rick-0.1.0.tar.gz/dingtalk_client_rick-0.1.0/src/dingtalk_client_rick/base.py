import requests
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from cachetools import TTLCache
from jsonpath_ng import parse

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DingTalk:
    """
    钉钉API客户端
    自动管理token，支持常用API调用
    """

    def __init__(
        self,
        app_key: str = None,
        app_secret: str = None,
    ):
        self.app_key = app_key or os.getenv("AppKey")
        self.app_secret = app_secret or os.getenv("AppSecret")
        self.base_url = "https://api.dingtalk.com"
        self.base_url_v2 = "https://oapi.dingtalk.com"

        # 使用TTLCache管理token缓存
        self._token_cache = TTLCache(maxsize=1, ttl=7100)  # 7100秒，比7200少100秒

    def _get_token(self) -> str:
        """获取有效的access_token，自动刷新"""
        try:
            # 尝试从缓存获取
            token = self._token_cache.get("access_token")
            if token:
                return token
        except KeyError:
            pass

        # 缓存中没有或已过期，刷新token
        return self._refresh_token()

    def _refresh_token(self) -> str:
        """刷新access_token"""
        url = f"{self.base_url}/v1.0/oauth2/accessToken"
        data = {"appKey": self.app_key, "appSecret": self.app_secret}

        response = requests.post(url, json=data)
        result = response.json()

        if "accessToken" in result:
            access_token = result["accessToken"]
            expire_in = result.get("expireIn", 7200)

            # 存入缓存，设置TTL比实际过期时间少100秒
            self._token_cache["access_token"] = access_token

            logger.info(f"Token刷新成功，有效期: {expire_in}秒")
            return access_token
        else:
            logger.error(f"获取token失败: {result}")
            raise Exception(f"获取token失败: {result}")

    def _build_url(self, endpoint: str) -> str:
        """构建完整URL"""
        if endpoint.startswith("http"):
            return endpoint
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        if "v1.0" in endpoint:
            return f"{self.base_url}/{endpoint}"
        else:
            return f"{self.base_url_v2}/{endpoint}"

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """统一的请求方法"""
        # 自动添加token到headers
        headers = kwargs.get("headers", {})
        params = kwargs.get("params", {})

        if "v1.0" in endpoint:
            headers["x-acs-dingtalk-access-token"] = self._get_token()
        else:
            params["access_token"] = self._get_token()

        kwargs.update({"headers": headers, "params": params})

        # 构建完整URL
        url = self._build_url(endpoint)

        # 发送请求
        response = requests.request(method, url, **kwargs)

        # 处理响应
        try:
            result = response.json()
        except Exception:  # ignore
            result = {"error": "Invalid JSON response", "raw": response.text}

        # 检查错误
        if result.get("errcode", 0) != 0:
            logger.error(f"API调用失败: {result}")
            raise Exception(f"API调用失败: {result}")

        # 记录日志
        logger.debug(f"请求: {method} {url}")
        logger.debug(f"响应: {result}")

        return result

    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PUT请求"""
        return self._request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE请求"""
        return self._request("DELETE", endpoint, **kwargs)

    def parse_jsonpath(self, jsonpath: str) -> parse:
        """解析JSONPath表达式"""
        return parse(jsonpath)
