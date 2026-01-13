from .bytecloud import ByteCloudHelper
import requests
import json
from typing import Dict, List
from loguru import logger


class SpaceXNotifier:
    """
    SpaceX 通知服务客户端，用于发送飞书消息
    """

    # 飞书机器人 webhook URL
    _SPACEX_DOMAIN = {
        "BOE": "spacex-api-boe.byted.org",
        "China-North": "spacex-api.byted.org",
        "Singapore-Central": "spacex-api-i18n.byted.org",
        "EUTTP": "spacex-api.tiktoke.org",
    }

    def __init__(self, bytecloud_helper: ByteCloudHelper):
        """
        初始化 SpaceX 通知客户端
        """
        self.bytecloud_helper = bytecloud_helper

    def send_feishu_message(self, env: str, feishu_content: Dict, feishu_groups: List[str]) -> str:
        """
        发送飞书消息

        Args:
            feishu_content: 飞书消息内容，包含卡片配置
            feishu_groups: 飞书群组 ID 列表

        Returns:
            str: 响应内容

        Raises:
            Exception: 请求失败时抛出异常
        """
        logger.debug(f"send_feishu_message env: {env}, feishu_content: {str(feishu_content)[:100]}..., feishu_groups: {feishu_groups}")

        body = {
            "product_name": "ByteDTS-Inspector",
            "notification_detail": [
                {
                    "channel": "Lark",
                    "content": json.dumps(feishu_content),
                    "lark_groups": feishu_groups,
                }
            ],
        }

        # 发送 HTTP POST 请求
        try:
            url = f"https://{self._SPACEX_DOMAIN[env]}/notification_service/api/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "X-Jwt-Token": self.bytecloud_helper.get_jwt_token(env),
            }

            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()

            print("response: {}".format(response.text))
            return response.text
        except Exception as e:
            print("发送消息时出错: {}".format(e))
            raise
