# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  http-helper
# FileName:     async_proxy.py
# Description:  客户端异步代理
# Author:       ASUS
# CreateDate:   2025/11/24
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import re
import json
import aiohttp
import asyncio
from yarl import URL
from urllib.parse import quote
from ..utils.log import logger
from typing import Any, Dict, Optional, List
from ..utils.http_execption import HttpClientError
from ..utils.reponse_handle_utils import get_html_title


class HttpClientFactory:
    __retry: int = 0

    def __init__(
            self,
            protocol: str = "https",
            domain: str = "api.weixin.qq.com",
            timeout: int = 10,
            retry: int = 0,
            enable_log: bool = False,
            cookie_jar: Optional[aiohttp.CookieJar] = None,
            playwright_state: Dict[str, Any] = None,
            proxy_config: Optional[Dict[str, str]] = None
    ):
        self.base_url = f"{protocol}://{domain}"
        self.protocol = protocol
        self.domain = domain
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.__retry = retry
        self.enable_log = enable_log
        self.proxy_url = self.build_proxy_url(proxy_config)

        # 初始化 session
        self.session = aiohttp.ClientSession(timeout=self.timeout, cookie_jar=cookie_jar or aiohttp.CookieJar())
        if playwright_state:
            self._load_playwright_cookies_to_aiohttp(playwright_state)
        self.valid_methods = {"get", "post", "put", "delete"}

    @staticmethod
    def build_proxy_url(proxy_config: Optional[Dict[str, str]]) -> Optional[str]:
        """
        将 {server, username, password} 转为 aiohttp 可用的代理 URL
        :param proxy_config: 格式如：
                            {
                                "server": "http://127.0.0.1:1234",
                                "username": "<USERNAME>",
                                "password": "<PASSWORD>",
                            }
        """
        if not proxy_config or not isinstance(proxy_config, dict) or not proxy_config.get("server"):
            return None

        server = proxy_config["server"].strip()
        # 去掉协议头（兼容带或不带 http:// 的情况）
        if server.startswith(("http://", "https://")):
            host_port = server.split("://", 1)[1]
        else:
            host_port = server

        if proxy_config.get("username") and proxy_config.get("password"):
            # URL 编码用户名和密码（防止 @ : / 等特殊字符破坏 URL）
            username = quote(proxy_config["username"], safe="")
            password = quote(proxy_config["password"], safe="")
            url = f"http://{username}:{password}@{host_port}"
        elif not proxy_config.get("username") and not proxy_config.get("password"):
            url = f"http://{host_port}"
        else:
            raise HttpClientError("代理参数缺失 username 或 password")
        return url

    def _load_playwright_cookies_to_aiohttp(self, playwright_state: Dict[str, Any]):
        """将 Playwright storage_state 中的 cookies 加载到 aiohttp session"""
        for ck in playwright_state.get("cookies", []):
            name = ck["name"]
            value = ck["value"]
            domain = ck["domain"]
            path = ck.get("path", "/")

            # 构造合法 URL 用于设置 cookie（主机名不能以 . 开头）
            host = domain.lstrip(".") if domain.startswith(".") else domain
            url = URL(f"{self.protocol}://{host}{path}")

            # 设置 cookie
            self.session.cookie_jar.update_cookies(cookies={name: value}, response_url=url)

    async def request(
            self,
            method: str,
            url: str,
            *,
            params: Dict[str, Any] = None,
            json_data: Any = None,
            data: Any = None,
            headers: Dict[str, str] = None,
            is_end: bool = True,
            has_cookie: bool = False,
            proxy_config: Optional[Dict[str, str]] = None,
            exception_keywords: Optional[List[str]] = None
    ) -> Any:
        if proxy_config:
            self.proxy_url = self.build_proxy_url(proxy_config)
        method = method.lower().strip()
        if method not in self.valid_methods:
            raise HttpClientError(f"Invalid Request method: {method}")

        full_url = f"{self.base_url}{url}"

        # 重试机制
        attempts = self.__retry + 1

        try:
            for attempt in range(1, attempts + 1):
                try:
                    if self.enable_log:
                        logger.debug(f"{method.upper()} Request {full_url} attempt {attempt}")

                    async with self.session.request(
                            method=method,
                            url=full_url,
                            proxy=self.proxy_url,
                            params=params or None,
                            json=json_data,
                            data=data,
                            headers=headers,
                    ) as resp:

                        # 非 2xx 抛异常
                        if resp.status >= 400:
                            error_text = self.parse_error_text(
                                exception_keywords=exception_keywords, error_text=await resp.text()
                            )
                            raise HttpClientError(error_text)

                        # 检查响应的 Content-Type
                        content_type = resp.headers.get("Content-Type", "").lower()

                        # 尝试 JSON 解码
                        if "application/json" in content_type or "text/json" in content_type:
                            try:
                                json_data = await resp.json(content_type=None)  # 忽略非法 content-type
                            except (Exception,):
                                text = await resp.text()
                                json_data = json.loads(text)
                        elif "text/html" in content_type:
                            # 纯文本类型
                            html = await resp.text()
                            json_data = {
                                "code": resp.status,
                                "message": get_html_title(html=html),
                                "data": html
                            }
                        else:
                            # 其他类型，默认视为二进制内容
                            # content = await resp.content.readany() # 只读当前缓冲区，可能只是部分数据，非阻塞、低级 API
                            content = await resp.read()  # 完整响应体
                            try:
                                text = content.decode('utf-8')
                            except UnicodeDecodeError:
                                text = content.decode('latin1')  # fallback
                            json_data = dict(code=resp.status, message=get_html_title(html=text), data=text)
                        if has_cookie is True:
                            # resp.headers 的类型是 CIMultiDict，getall() 在 key 不存在时会抛出 KeyError，因此需要给一个空list作为默认值
                            set_cookie_headers = resp.headers.getall("Set-Cookie", list())
                            json_data["cookies"] = set_cookie_headers[0] if len(
                                set_cookie_headers) == 1 else set_cookie_headers  # 返回列表
                        return json_data

                except Exception as e:
                    if attempt == attempts:
                        raise HttpClientError(f"Request failed after {attempts} attempts: {e}")
                    await asyncio.sleep(1 * attempt)  # 递增式重试间隔
        finally:
            if is_end is True:
                await self.close()

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    @staticmethod
    def parse_error_text(error_text: str, exception_keywords: Optional[List[str]] = None) -> str:
        if not exception_keywords:
            return error_text
        _exception_keywords = [
            r'<h3[^>]*class="font-bold"[^>]*>([^<]+)</h3>'
        ]
        if exception_keywords:
            _exception_keywords.extend(exception_keywords)
        for exception_keyword in _exception_keywords:
            match = re.search(exception_keyword, error_text)
            if match:
                error_text = match.group(1).strip()
                break
        # 尝试提取青岛航空的提示信息（可选增强）
        if "您的IP由于频繁访问已受限" in error_text:
            raise HttpClientError(f"IP blocked by QDAir: {error_text}")
        return error_text
