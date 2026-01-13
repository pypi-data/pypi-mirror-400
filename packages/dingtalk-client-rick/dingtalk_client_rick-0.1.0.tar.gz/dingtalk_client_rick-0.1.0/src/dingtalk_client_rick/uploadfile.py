from typing import Dict
from .base import DingTalk
import requests
import os
from pathlib import Path
import hashlib
import logging
from tqdm import tqdm  # 可选，用于进度条
import time

logger = logging.getLogger(__name__)


class AiUploadFile(DingTalk):
    """Aitable文件上传客户端 - 增强版"""

    def __init__(self, docId: str, unionId: str, *args, **kwargs) -> None:
        """
        初始化Aitable文件上传客户端
        :param docId: 文档ID (dentryUuid/documentId/workbookId/baseId)
        :param unionId: 操作人的unionId，可通过调用查询用户详情接口
        """
        self.docId = docId
        self.unionId = unionId
        self.baseId = kwargs.get("baseId", "")  # 从kwargs中获取baseId
        super().__init__(*args, **kwargs)

        # 上传配置
        self.chunk_size = 1024 * 1024  # 1MB分块
        self.max_retries = 3
        self.timeout = 30  # 超时时间

    def get_upload_url(self, size: int, mediaType: str, resourceName: str) -> Dict:
        """
        获取文件上传URL 第一步
        :param size: 文件大小
        :param mediaType: 文件媒体类型
        :param resourceName: 文件名
        :return: 上传结果
        """
        endpoint = f"/v1.0/doc/docs/resources/{self.docId}/uploadInfos/query"
        params = {"operatorId": self.unionId}
        data = {
            "size": size,
            "mediaType": mediaType,
            "resourceName": resourceName,
        }

        try:
            response = self.post(endpoint, params=params, json=data)

            if response.get("success"):
                return {
                    "status": "success",
                    "data": response.get("result", {}),
                    "message": "获取上传URL成功",
                }
            else:
                return {
                    "status": "error",
                    "message": response.get("message", "获取上传URL失败"),
                    "code": response.get("code", "UNKNOWN_ERROR"),
                }

        except Exception as e:
            logger.error(f"获取上传URL失败: {str(e)}")
            return {"status": "error", "message": f"网络请求失败: {str(e)}"}

    def upload_file(
        self,
        uploadUrl: str,
        file_path: str,
        show_progress: bool = True,
        media_type: str = "application/octet-stream",
    ) -> Dict:
        """
        将本地文件上传到第一步返回的uploadUrl中

        :param uploadUrl: 上传URL
        :param file_path: 文件路径
        :param show_progress: 是否显示进度条
        :param media_type: 文件媒体类型
        :return: 上传结果
        """
        try:
            # 1. 验证文件
            validation_result = self._validate_file(file_path)
            if validation_result["status"] != "success":
                return validation_result

            file_size = validation_result["size"]
            file_name = validation_result["name"]

            # 2. 根据文件大小选择上传策略
            if file_size <= self.chunk_size:
                return self._upload_single_file(
                    uploadUrl,
                    file_path,
                    file_name,
                    file_size,
                    show_progress,
                    media_type,
                )
            else:
                return self._upload_chunked_file(
                    uploadUrl,
                    file_path,
                    file_name,
                    file_size,
                    show_progress,
                    media_type,
                )

        except Exception as e:
            logger.exception(f"上传文件失败: {str(e)}")
            return {"status": "error", "message": f"上传失败: {str(e)}"}

    def _validate_file(self, file_path: str) -> Dict:
        """验证文件"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {"status": "error", "message": f"文件不存在: {file_path}"}

            # 检查文件是否可读
            if not os.access(file_path, os.R_OK):
                return {"status": "error", "message": f"文件不可读: {file_path}"}

            # 获取文件信息
            file_size = os.path.getsize(file_path)
            file_name = Path(file_path).name

            # 检查文件大小限制（假设最大1GB）
            MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB
            if file_size > MAX_FILE_SIZE:
                return {
                    "status": "error",
                    "message": f"文件过大: {file_size}字节，最大支持{MAX_FILE_SIZE}字节",
                }

            return {
                "status": "success",
                "size": file_size,
                "name": file_name,
                "path": file_path,
            }

        except Exception as e:
            return {"status": "error", "message": f"文件验证失败: {str(e)}"}

    def _upload_single_file(
        self,
        uploadUrl: str,
        file_path: str,
        file_name: str,
        file_size: int,
        show_progress: bool,
        media_type: str,
    ) -> Dict:
        """上传单个文件（小文件）"""
        try:
            # 计算文件哈希（可选）
            # file_hash = self._calculate_file_hash(file_path)

            # 读取文件内容
            with open(file_path, "rb") as f:
                file_content = f.read()

            # 设置请求头
            # 注意：对于OSS预签名URL上传，Content-Type必须与获取URL时一致
            # 移除自定义header，避免签名校验失败
            headers = {
                "Content-Type": media_type,
                "Content-Length": str(file_size),
            }

            # 显示进度条
            if show_progress:
                print(f"正在上传文件: {file_name} ({file_size}字节)")

            # 发送PUT请求
            response = requests.put(
                uploadUrl, data=file_content, headers=headers, timeout=self.timeout
            )

            return self._handle_upload_response(response, file_name, file_size)

        except requests.exceptions.Timeout:
            return {"status": "error", "message": "上传超时"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "网络连接错误"}
        except Exception as e:
            return {"status": "error", "message": f"上传失败: {str(e)}"}

    def _upload_chunked_file(
        self,
        uploadUrl: str,
        file_path: str,
        file_name: str,
        file_size: int,
        show_progress: bool,
        media_type: str,
    ) -> Dict:
        """分块上传文件（大文件）"""
        try:
            # 计算文件哈希
            file_hash = self._calculate_file_hash(file_path)

            # 计算分块数量
            total_chunks = (file_size + self.chunk_size - 1) // self.chunk_size

            # 初始化进度条
            progress_bar = None
            if show_progress:
                progress_bar = tqdm(
                    total=file_size, unit="B", unit_scale=True, desc=f"上传 {file_name}"
                )

            uploaded_size = 0

            with open(file_path, "rb") as f:
                for chunk_index in range(total_chunks):
                    # 读取分块
                    offset = chunk_index * self.chunk_size
                    f.seek(offset)
                    chunk_data = f.read(self.chunk_size)
                    chunk_size = len(chunk_data)

                    # 设置分块请求头
                    headers = {
                        "Content-Type": "application/octet-stream",  # 分块通常使用二进制流
                        "Content-Length": str(chunk_size),
                        "Content-Range": f"bytes {offset}-{offset+chunk_size-1}/{file_size}",
                    }

                    # 尝试上传分块（带重试）
                    chunk_uploaded = False
                    for attempt in range(self.max_retries):
                        try:
                            response = requests.put(
                                uploadUrl,
                                data=chunk_data,
                                headers=headers,
                                timeout=self.timeout,
                            )

                            if response.status_code in [200, 201, 206]:
                                chunk_uploaded = True
                                uploaded_size += chunk_size

                                # 更新进度条
                                if progress_bar:
                                    progress_bar.update(chunk_size)

                                break  # 上传成功，跳出重试循环
                            else:
                                logger.warning(
                                    f"分块{chunk_index}上传失败，重试{attempt+1}/{self.max_retries}"
                                )
                                time.sleep(1)  # 等待1秒后重试

                        except Exception as e:
                            logger.warning(f"分块{chunk_index}上传异常: {str(e)}")
                            time.sleep(1)

                    if not chunk_uploaded:
                        if progress_bar:
                            progress_bar.close()
                        return {
                            "status": "error",
                            "message": f"分块{chunk_index}上传失败，达到最大重试次数",
                        }

            # 关闭进度条
            if progress_bar:
                progress_bar.close()

            # 验证上传完整性
            if uploaded_size != file_size:
                return {
                    "status": "error",
                    "message": f"上传不完整: {uploaded_size}/{file_size}字节",
                }

            return {
                "status": "success",
                "message": "文件上传成功",
                "file_name": file_name,
                "file_size": file_size,
                "uploaded_size": uploaded_size,
                "file_hash": file_hash,
            }

        except Exception as e:
            if progress_bar:
                progress_bar.close()
            return {"status": "error", "message": f"分块上传失败: {str(e)}"}

    def _calculate_file_hash(self, file_path: str, algorithm: str = "md5") -> str:
        """计算文件哈希值"""
        hash_func = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            # 分块读取，避免内存溢出
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    def _handle_upload_response(
        self, response: requests.Response, file_name: str, file_size: int
    ) -> Dict:
        """处理上传响应"""
        try:
            if response.status_code in [200, 201]:
                # 尝试解析JSON响应
                try:
                    response_data = response.json()
                    return {
                        "status": "success",
                        "message": "文件上传成功",
                        "file_name": file_name,
                        "file_size": file_size,
                        "response": response_data,
                    }
                except Exception:
                    return {
                        "status": "success",
                        "message": "文件上传成功",
                        "file_name": file_name,
                        "file_size": file_size,
                        "response_text": response.text,
                    }
            else:
                return {
                    "status": "error",
                    "message": f"上传失败: HTTP {response.status_code}",
                    "status_code": response.status_code,
                    "response_text": response.text,
                }
        except Exception as e:
            return {"status": "error", "message": f"处理响应失败: {str(e)}"}

    def upload_file_complete(self, file_path: str, mediaType: str = None) -> Dict:
        """
        完整的文件上传流程（两步法）
        :param file_path: 文件路径
        :param mediaType: 文件类型，如果为None则自动检测
        :return: 完整的上传结果
        """
        try:
            # 1. 验证文件
            validation = self._validate_file(file_path)
            if validation["status"] != "success":
                return validation

            file_size = validation["size"]
            file_name = validation["name"]

            # 2. 自动检测媒体类型
            if mediaType is None:
                mediaType = self._detect_media_type(file_path)

            # 3. 获取上传URL
            url_result = self.get_upload_url(file_size, mediaType, file_name)
            if url_result["status"] != "success":
                return url_result

            upload_data = url_result.get("data", {})
            upload_url = upload_data.get("uploadUrl")
            resource_id = upload_data.get("resourceId")

            if not upload_url:
                return {"status": "error", "message": "未获取到上传URL"}

            # 4. 上传文件 可以异步上传结果需要的是第一步返回的数据
            upload_result = self.upload_file(
                upload_url, file_path, media_type=mediaType
            )
            # 期望的返回结果
            # {
            #       "filename": "pikaqiu.jpg", // 第一步传入的resourceName
            #       "size": 200, // 第一步传入的 size
            #       "type": "image/jpeg", // 第一步传入的mediaType
            #       "url": "xxx"，// 第一步返回的 resourceUrl，注意不是uploadUrl，例如 /core/api/resources/img/xxx
            #       "resourceId": "xxx" // 第一步返回的 resourceId，例如 9ee6c515-4ebd-47a0-b8c3-5383c4241d84
            # }
            # 5. 构造符合期望的返回结果
            if upload_result["status"] == "success":
                return {
                    "filename": file_name,
                    "size": file_size,
                    "type": mediaType,
                    "url": upload_data.get("resourceUrl"),
                    "resourceId": resource_id,
                }

            return upload_result

        except Exception as e:
            return {"status": "error", "message": f"完整上传流程失败: {str(e)}"}

    def _detect_media_type(self, file_path: str) -> str:
        """根据文件扩展名检测媒体类型"""
        extension = Path(file_path).suffix.lower()

        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".txt": "text/plain",
            ".csv": "text/csv",
        }

        return media_types.get(extension, "application/octet-stream")
