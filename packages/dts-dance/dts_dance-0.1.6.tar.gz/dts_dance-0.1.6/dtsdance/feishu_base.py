from datetime import datetime, timedelta
import threading
from typing import Optional
from loguru import logger
import requests

URL_FEISHU_OPEN_API: str = "https://fsopen.bytedance.net/open-apis"


class FeishuBase:
    """飞书基础类，传入机器人认证信息，支持自动token续期管理"""

    def __init__(self, bot_app_id: str, bot_app_secret: str):
        """
        初始化飞书基础类
        """
        self.tenant_access_token: Optional[str] = None
        self.token_expire_time: Optional[datetime] = None
        self._token_lock = threading.Lock()

        self.bot_app_id = bot_app_id
        self.bot_app_secret = bot_app_secret

    def _get_tenant_access_token(self) -> str:
        """
        获取tenant_access_token

        Returns:
            tenant_access_token字符串

        Raises:
            Exception: 获取token失败时抛出异常
        """
        url = f"{URL_FEISHU_OPEN_API}/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.bot_app_id, "app_secret": self.bot_app_secret}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"获取tenant_access_token失败: {result.get('msg')}")

            token = result.get("tenant_access_token")
            expire_in = result.get("expire", 7200)  # 默认2小时过期

            # 设置过期时间，提前5分钟刷新
            self.token_expire_time = datetime.now() + timedelta(seconds=expire_in - 300)

            logger.info(f"成功获取tenant_access_token，过期时间: {self.token_expire_time}")
            return token

        except requests.RequestException as e:
            logger.warning(f"请求tenant_access_token失败: {e}")
            raise Exception(f"网络请求失败: {e}")
        except Exception as e:
            logger.warning(f"获取tenant_access_token失败: {e}")
            raise

    def get_access_token(self) -> str:
        """
        获取有效的access token，自动处理续期

        Returns:
            有效的tenant_access_token
        """
        with self._token_lock:
            # 检查token是否存在或已过期
            if self.tenant_access_token is None or self.token_expire_time is None or datetime.now() >= self.token_expire_time:

                logger.info("Token不存在或已过期，重新获取")
                self.tenant_access_token = self._get_tenant_access_token()

            return self.tenant_access_token

    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        发起API请求的通用方法

        Args:
            method: HTTP方法
            endpoint: API端点
            **kwargs: 其他请求参数

        Returns:
            Response对象
        """
        url = f"{URL_FEISHU_OPEN_API}{endpoint}"

        # 获取有效token
        token = self.get_access_token()
        # logger.debug(f"使用token: {token} 发送请求: {method} {url}")

        # 设置认证头
        headers = kwargs.get("headers", {"Content-Type": "application/json"})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers

        try:
            response = requests.request(method, url, **kwargs)
            # logger.debug(f"response_json: {response.json()}")
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"API请求失败: {method} {url}, error: {e}")
            raise
