import requests
import threading
import time
from typing import Dict
from loguru import logger
from typing import NamedTuple


class ByteCloudEnvInfo(NamedTuple):
    name: str
    endpoint: str
    token: str


class ByteCloudHelper:
    """
    ByteCloud Helper
    """

    # 每小时刷新一次，单位为秒
    _REFRESH_INTERVAL = 1 * 60 * 60

    def __init__(self, envs: dict[str, ByteCloudEnvInfo]):
        """
        初始化 ByteCloud Helper
        从配置文件加载所有环境的信息，并为每个环境初始化 JWT 令牌
        envs 中保存内容 list[(name, endpoint, token)]
        """
        self.envs = envs

        # 初始化线程锁，用于保护 jwt_tokens 的并发访问
        self.token_lock = threading.Lock()

        # 初始化 JWT 令牌缓存，按环境名称索引
        self.jwt_tokens: Dict[str, str] = {}

        # 更新所有环境的 JWT 令牌
        self._refresh_tokens()

        # 启动 JWT 令牌刷新线程
        self._start_refresh_thread()

    def _start_refresh_thread(self):
        """
        启动一个后台线程，定期刷新所有环境的 JWT 令牌
        """
        refresh_thread = threading.Thread(
            target=self._refresh_token_periodically,
            daemon=True,
            name="jwt-token-refresh",
        )
        refresh_thread.start()

    def _refresh_token_periodically(self):
        """
        定期刷新所有环境的 JWT 令牌的线程函数
        """
        while True:
            # 等待指定时间
            time.sleep(self._REFRESH_INTERVAL)
            self._refresh_tokens()

    def _refresh_tokens(self):
        """
        刷新所有环境的 JWT 令牌
        """
        logger.debug("开始刷新所有环境的 JWT 令牌...")

        for _, env in self.envs.items():
            try:
                # 刷新令牌
                new_token = self._acquire_jwt_token(env.endpoint, env.token)
                # 使用线程锁更新缓存中的 JWT 令牌
                with self.token_lock:
                    self.jwt_tokens[env.name] = new_token
                    logger.debug(f"环境 {env.name} 的 JWT 令牌成功刷新，新令牌: {new_token}")
            except Exception as e:
                logger.error(f"环境 {env.name} 的 JWT 令牌刷新失败: {e}")

        logger.debug(f"所有环境的 JWT 令牌已成功刷新。jwt_tokens: {self.jwt_tokens}")

    def _acquire_jwt_token(self, endpoint: str, token: str) -> str:
        """
        获取 JWT 令牌

        Args:
            token: 认证令牌
            endpoint: API 端点

        Returns:
            str: JWT 令牌
        """
        url = endpoint + "/auth/api/v1/jwt"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        }

        try:
            # 发送 GET 请求
            response = requests.get(url, headers=headers, timeout=60)
            # logger.debug(f"获取JWT令牌响应: response.text={response.text}")

            # 检查响应状态码
            if response.status_code != 200:
                raise Exception(f"获取JWT令牌失败。status_code: {response.status_code}, response.text: {response.text}")

            # 解析响应体
            response_json = response.json()
            if response_json.get("code", -1) != 0:
                raise Exception(f"获取JWT令牌失败: {response.text}")

            # 从响应头中获取 JWT 令牌
            jwt_token = response.headers.get("X-Jwt-Token")
            if not jwt_token:
                raise Exception("响应头中没有 X-Jwt-Token")

            return jwt_token

        except Exception as e:
            logger.error(f"获取JWT令牌时出错: {e}")
            raise

    def get_jwt_token(self, env: str) -> str:
        """
        获取指定环境的 JWT 令牌

        Args:
            env: 环境名称，如 'China-North', 'China-East', 'Singapore-Central' 等

        Returns:
            str: 当前有效的 JWT 令牌

        Raises:
            KeyError: 如果指定的环境不存在
        """
        # 使用线程锁保护并发访问
        with self.token_lock:
            if env not in self.jwt_tokens:
                raise KeyError(f"环境 {env} 的 JWT 令牌不存在")
            return self.jwt_tokens[env]

    def get_env_info(self, env: str) -> ByteCloudEnvInfo:
        """
        获取指定环境的信息

        Args:
            env: 环境名称

        Returns:
            ByteCloudEnvInfo: 指定环境的信息

        Raises:
            KeyError: 如果指定的环境不存在
        """
        if env not in self.envs:
            raise KeyError(f"环境 {env} 不存在")

        return self.envs[env]
