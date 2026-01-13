# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  playwright-helper
# FileName:     browser_pool.py
# Description:  浏览器池，一次起 Chrome，并发复用
# Author:       ASUS
# CreateDate:   2025/12/13
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import asyncio
from logging import Logger
from typing import Any, Optional, Dict
from playwright.async_api import Browser, async_playwright, Playwright


class BrowserPool:
    def __init__(
            self,
            *,
            size: int,
            logger: Logger,
            proxy: Optional[Dict[str, str]] = None,
            **launch_config: Any,
    ):
        self.size = size
        self.logger = logger
        self.proxy = proxy
        # 代理格式：proxy = {
        #     "server": "http://ip:port",       # HTTP 代理
        #     # 或
        #     "server": "https://ip:port",      # HTTPS 代理（较少见）
        #     # 或
        #     "server": "socks5://ip:port",     # SOCKS5 代理
        #     # 或
        #     "server": "socks4://ip:port",     # SOCKS4 代理
        #
        #     # 可选：如果代理需要认证
        #     "username": "your_user",
        #     "password": "your_pass"
        # }
        self.launch_config = launch_config
        self._queue: asyncio.Queue[Browser] = asyncio.Queue()
        self._started: bool = False
        self._playwright: Optional[Playwright] = None

    async def start(self, playwright: Playwright = None):
        if self._started:
            return

        if playwright:
            self._playwright = playwright

        if not self._playwright:
            self._playwright = await async_playwright().start()

        self.logger.debug(f"[BrowserPool] start size={self.size}")

        for i in range(self.size):
            self.logger.debug(f"[BrowserPool] launching browser {i}")
            browser_launch_config = {**self.launch_config}
            if self.proxy:
                browser_launch_config['proxy'] = self.proxy

            browser = await self._playwright.chromium.launch(
                **browser_launch_config
            )
            await self._queue.put(browser)

        self._started = True
        self.logger.debug("[BrowserPool] started")

    async def acquire(self) -> Browser:
        self.logger.debug("[BrowserPool] acquire waiting...")
        browser = await self._queue.get()
        self.logger.debug("[BrowserPool] acquire ok")
        return browser

    async def release(self, browser: Browser):
        self.logger.debug("[BrowserPool] release")
        await self._queue.put(browser)

    async def stop(self):
        self.logger.debug("[BrowserPool] stopping")
        while not self._queue.empty():
            browser = await self._queue.get()
            await browser.close()
        if self._playwright:
            await self._playwright.stop()
        self.logger.debug("[BrowserPool] stopped")
