from typing import Any, cast, Optional
from loguru import logger
from .bytecloud import ByteCloudHelper
import requests

class DFlowHelper:

    def __init__(self, bytecloud_helper: ByteCloudHelper) -> None:
        self.bytecloud_helper = bytecloud_helper

    def _build_headers(self, env: str) -> dict[str, str]:
        """
        构建请求头

        Args:
            env: 环境名称

        Returns:
            dict[str, str]: 请求头字典
        """
        jwt_token = self.bytecloud_helper.get_jwt_token(env)
        headers = {"x-jwt-token": jwt_token}
        return headers

    def _make_request(self, method: str, url: str, headers: dict[str, str], json_data: Optional[dict] = None) -> dict[str, Any]:
        """
        发送 HTTP 请求的通用方法

        Args:
            method: HTTP 方法 (GET/POST)
            url: 请求 URL
            headers: 请求头
            json_data: POST 请求的 JSON 数据

        Returns:
            dict[str, Any]: 解析后的 JSON 响应
        """
        response = None
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=json_data, headers=headers)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            # 检查响应状态码
            response.raise_for_status()

            # 解析 JSON 响应
            return response.json()

        except Exception as e:
            error_msg = f"_make_request occur error, error: {e}"
            if response is not None:
                error_msg += f", response.text: {response.text}"
            logger.warning(error_msg)
            raise

    def get_dflow_info(self, env: str, task_id: str) -> dict[str, Any]:
        """
        获取 DFlow 任务信息

        Args:
            env: 环境名称
            task_id: DFlow 任务 ID

        Returns:
            dict[str, Any]: DFlow 任务信息，包含 create_time 等字段
        """
        # 构建 API URL
        url = "https://cloud.bytedance.net/api/v1/bytedts/api/bytedts/v3/DescribeTaskInfo"

        # 准备请求头
        headers = self._build_headers(env)

        # 构建请求数据
        json_data = {"id": int(task_id)}

        response_data = self._make_request("POST", url, headers, json_data)

        logger.info(f"get_dflow_info {env} {task_id}, message: {response_data.get('message')}")

        try:
            data = cast(dict, response_data.get("data", {}))
            task = cast(dict, data.get("task", {}))
            # 提取核心信息
            filtered_data = {
                "task_id": task.get("id", ""),
                "status": task.get("status", ""),
                "create_time": task.get("create_time", 0),
            }

            return filtered_data

        except (KeyError, AttributeError, Exception) as e:
            raise Exception(f"无法从响应中提取 DFlow 任务信息数据: {str(e)}")

    def generate_task_url(self, env: str, task_id: str) -> str:
        """
        获取 DFlow 任务详情页面的 URL

        Args:
            env: 环境名称
            task_id: DFlow 任务 ID

        Returns:
            str: DFlow 任务详情页面的 URL
        """
        # 根据环境生成对应的 scope 参数
        return f"https://cloud.bytedance.net/bytedts/datasync/detail/{task_id}?scope={env}"
