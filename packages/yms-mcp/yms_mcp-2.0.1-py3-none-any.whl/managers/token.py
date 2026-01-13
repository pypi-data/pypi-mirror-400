#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YMS 访问令牌管理器
负责登录、缓存、以及定时刷新 access token
"""

import asyncio
import time
from typing import Optional

import httpx
from loguru import logger

from ..config.settings import settings


def _build_url(base: str, path: str) -> str:
    if not base:
        return path or ""
    if not path:
        return base or ""
    return base.rstrip('/') + '/' + path.lstrip('/')


class TokenManager:
    """管理 YMS access token，支持后台定时刷新。"""

    def __init__(self):
        self._access_token: Optional[str] = None
        self._expire_time: float = 0
        self._refresh_task: Optional[asyncio.Task] = None
        self._login_lock = asyncio.Lock()

    async def login_and_get_token(self) -> str:
        """
        登录 YMS 并返回 access token，同时更新本地缓存与过期时间。
        """
        async with self._login_lock:
            login_data = {
                "username": settings.yms_username,
                "password": settings.yms_password
            }

            headers = {
                "X-Tenant-ID": settings.yms_tenant_id,
                "X-Yard-ID": settings.yms_yard_id,
                "Item-Time-Zone": settings.yms_timezone,
                "Content-Type": "application/json"
            }

            login_url = _build_url(
                settings.yms_backend_url,
                settings.yms_login_path
            )
            logger.info(f"尝试登录YMS系统: {login_url}")
            logger.info(f"登录用户: {login_data.get('username', '')}")

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        login_url,
                        headers=headers,
                        json=login_data
                    )
                    logger.info(f"登录响应状态码: {response.status_code}")
                    response.raise_for_status()

                    result = response.json()
                    if result.get('code', -1) != 0:
                        error_msg = result.get('msg', '登录失败')
                        logger.error(f"YMS登录失败: {error_msg}")
                        logger.error(f"完整响应: {result}")
                        raise ValueError(f"YMS登录失败: {error_msg}")

                    data = result.get('data', {})
                    access_token = data.get('accessToken')
                    if not access_token:
                        logger.error("登录响应中没有找到accessToken")
                        raise ValueError("登录响应中没有找到accessToken")

                    # 更新 token 与过期时间
                    current_time = time.time()
                    expire_seconds = settings.yms_token_expire_seconds
                    # 提前30秒过期
                    self._access_token = access_token
                    self._expire_time = current_time + expire_seconds - 30

                    token_prefix = (
                        access_token[:20]
                        if len(access_token) > 20 else access_token
                    )
                    token_suffix = (
                        access_token[-10:]
                        if len(access_token) > 10 else ""
                    )
                    expire_time_str = time.strftime(
                        '%Y-%m-%d %H:%M:%S',
                        time.localtime(self._expire_time)
                    )
                    msg = (
                        f"YMS登录成功，token已缓存: "
                        f"{token_prefix}...{token_suffix}"
                    )
                    logger.info(msg)
                    logger.info(f"Token过期时间: {expire_time_str}")
                    return access_token

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"YMS登录HTTP错误: {e.response.status_code} {e.response.text}"
                )
                raise ValueError(
                    f"YMS登录失败: HTTP {e.response.status_code} - "
                    f"{e.response.text}"
                )
            except httpx.HTTPError as e:
                logger.error(f"YMS登录网络错误: {e}")
                raise
            except Exception as e:
                logger.error(f"YMS登录异常: {e}")
                raise

    async def get_valid_token(self) -> str:
        """返回未过期 token；若不存在或过期则触发登录。"""
        current_time = time.time()
        if self._access_token and self._expire_time > current_time:
            remaining = int(self._expire_time - current_time)
            logger.info(f"使用缓存的token，剩余有效时间: {remaining}秒")
            return self._access_token

        if self._access_token:
            logger.info("token已过期，重新登录获取新token")
        else:
            logger.info("token不存在，首次登录获取token")
        return await self.login_and_get_token()

    async def _refresh_loop(self):
        """后台刷新循环：在过期前提前刷新；失败时指数退避重试。"""
        backoff = 5  # 初始退避秒
        max_backoff = 60
        while True:
            try:
                now = time.time()
                # 如果没有 token 或者即将过期，立即刷新
                if not self._access_token or self._expire_time - now <= 90:
                    await self.login_and_get_token()
                    backoff = 5  # 刷新成功恢复退避

                # 计算下一次睡眠：尽量在过期前60秒再次刷新
                sleep_seconds = max(
                    15,
                    int(self._expire_time - time.time() - 60)
                )
                logger.debug(f"Token刷新循环休眠 {sleep_seconds}s")
                await asyncio.sleep(sleep_seconds)
            except asyncio.CancelledError:
                logger.info("Token刷新任务已取消")
                raise
            except Exception as e:
                logger.error(f"Token刷新失败: {e}, {backoff}s后重试")
                await asyncio.sleep(backoff)
                backoff = min(max_backoff, backoff * 2)

    async def start(self):
        """启动后台刷新任务，并尽快预热一次登录。"""
        if self._refresh_task and not self._refresh_task.done():
            return
        try:
            # 预热：不阻塞启动太久，最多等待 10s
            logger.info("预热YMS token 登录…")
            await asyncio.wait_for(self.login_and_get_token(), timeout=10.0)
        except Exception as e:
            logger.warning(f"预热登录失败: {e}，将由后台任务继续重试")
        self._refresh_task = asyncio.create_task(self._refresh_loop())
        logger.info("✅ Token后台刷新任务已启动")

    async def stop(self):
        """停止后台刷新任务。"""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            self._refresh_task = None
            logger.info("✅ Token后台刷新任务已停止")


# 全局实例
token_manager = TokenManager()
# EOF
