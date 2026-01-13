from typing import Dict, List
from .base import DingTalk


class AiTable(DingTalk):
    """Aitable表格客户端"""

    def __init__(self, baseId: str, unionId: str, *args, **kwargs) -> None:
        """
        初始化Aitable表格客户端
        :param baseId: 表格基础ID
        :param unionId: 表格操作者UnionID
        """
        self.baseId = baseId
        self.unionId = unionId
        super().__init__(*args, **kwargs)


class AiSheet(AiTable):
    """Aitable数据表客户端"""

    def __init__(self, sheetIdOrName: str = None, *args, **kwargs) -> None:
        """
        初始化Aitable数据表客户端
        :param sheetIdOrName: 数据表ID或名称
        """
        self.sheetIdOrName = sheetIdOrName
        super().__init__(*args, **kwargs)

    def list(self):
        """获取数据表记录
        :param sheetIdOrName: 数据表ID或名称
        """
        endpoint = f"/v1.0/notable/bases/{self.baseId}/sheets/"
        params = {"operatorId": self.unionId}
        return self.get(endpoint, params=params)


class AiRecord(AiSheet):
    """Aitable记录客户端"""

    def __init__(self, *args, **kwargs) -> None:
        """
        初始化Aitable记录客户端
        :param recordId: 记录ID
        """
        super().__init__(*args, **kwargs)

    def list(self, filter: Dict = {}):
        """获取记录
        https://open.dingtalk.com/document/development/api-notable-listrecords
        """
        endpoint = f"/v1.0/notable/bases/{self.baseId}/sheets/{self.sheetIdOrName}/records/list"
        params = {"operatorId": self.unionId}

        return self.post(endpoint, params=params, json=filter)

    def detail(self, recordId: str = None):
        """获取记录
        https://open.dingtalk.com/document/development/api-notable-getrecord
        :param recordId: 记录ID
        """
        endpoint = f"/v1.0/notable/bases/{self.baseId}/sheets/{self.sheetIdOrName}/records/{recordId}"
        params = {"operatorId": self.unionId}
        return self.get(endpoint, params=params)

    def create(self, records: List[Dict] = []):
        """创建记录
        https://open.dingtalk.com/document/development/api-notable-insertrecords
        :param records: 记录数据
        """
        endpoint = (
            f"/v1.0/notable/bases/{self.baseId}/sheets/{self.sheetIdOrName}/records"
        )
        params = {"operatorId": self.unionId}
        return self.post(endpoint, params=params, json={"records": records})

    def update(self, records: List[Dict] = []):
        """创建或更新记录
        https://open.dingtalk.com/document/development/api-notable-insertrecords
        :param records: 记录数据
        """
        endpoint = (
            f"/v1.0/notable/bases/{self.baseId}/sheets/{self.sheetIdOrName}/records"
        )
        params = {"operatorId": self.unionId}
        return self.put(endpoint, params=params, json={"records": records})

    def delete(self, recordIds: List[str] = []):
        """删除记录
        https://open.dingtalk.com/document/development/api-notable-deleterecord
        :param recordId: 记录ID
        """
        endpoint = f"/v1.0/notable/bases/{self.baseId}/sheets/{self.sheetIdOrName}/records/{self.recordId}"
        params = {"operatorId": self.unionId}
        return self.delete(endpoint, params=params)
