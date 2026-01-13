# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  playwright-helper
# FileName:     base_po.py
# Description:  po对象基础类
# Author:       ASUS
# CreateDate:   2025/12/13
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import asyncio
from logging import Logger
from typing import List, Any, cast, Dict
from playwright.async_api import Page, Locator, TimeoutError as PlaywrightTimeoutError, Request, Response


class BasePo(object):
    __page: Page

    def __init__(self, page: Page, url: str):
        self.url = url
        self.__page = page

    def get_page(self) -> Page:
        return self.__page

    def is_current_page(self) -> bool:
        return self.iss_current_page(self.__page, self.url)

    def get_url_domain(self) -> str:
        if isinstance(self.__page, Page):
            page_slice: List[str] = self.__page.url.split("/")
            return f"{page_slice[0]}://{page_slice[2]}"
        else:
            raise AttributeError("PO对象中的page属性未被初始化")

    def get_url(self) -> str:
        if self.__page.url.find("://") != -1:
            return self.__page.url.split("?")[0]
        else:
            return self.__page.url

    @staticmethod
    def iss_current_page(page: Page, url: str) -> bool:
        if isinstance(page, Page):
            page_url_prefix = page.url.split("?")[0]
            url_prefix = url.split("?")[0]
            if page_url_prefix.endswith(url_prefix):
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    async def exists(locator):
        return await locator.count() > 0

    @staticmethod
    async def exists_one(locator):
        return await locator.count() == 1

    async def get_locator(self, selector: str, timeout: float = 3.0) -> Locator:
        """
        获取页面元素locator
        :param selector: 选择器表达式
        :param timeout: 超时时间（秒）
        :return: 元素对象
        :return:
        """
        locator = self.__page.locator(selector)
        try:
            await locator.first.wait_for(state='visible', timeout=timeout * 1000)
            return locator
        except (PlaywrightTimeoutError,):
            raise PlaywrightTimeoutError(f"元素 '{selector}' 未在 {timeout} 秒内找到")
        except Exception as e:
            raise RuntimeError(f"检查元素时发生错误: {str(e)}")

    @staticmethod
    async def get_sub_locator(locator: Locator, selector: str, timeout: float = 3.0) -> Locator:
        """
        获取页面locator的子locator
        :param locator: 页面Locator对象
        :param selector: 选择器表达式
        :param timeout: 超时时间（秒）
        :return: 元素对象
        :return:
        """
        locator_inner = locator.locator(selector)
        try:
            await locator_inner.first.wait_for(state='visible', timeout=timeout * 1000)
            return locator_inner
        except (PlaywrightTimeoutError,):
            raise PlaywrightTimeoutError(f"元素 '{selector}' 未在 {timeout} 秒内找到")
        except Exception as e:
            raise RuntimeError(f"检查元素时发生错误: {str(e)}")

    @classmethod
    async def handle_po_cookie_tip(cls, page: Any, logger: Logger, timeout: float = 3.0,
                                   selectors: List[str] = None) -> None:
        selectors_inner: List[str] = [
            '//div[@id="isReadedCookie"]/button',
            '//button[@id="continue-btn"]/span[normalize-space(text())="同意"]'
        ]
        if selectors:
            selectors_inner.extend(selectors)
        for selector in selectors_inner:
            try:
                page_inner = cast(cls, page)
                cookie: Locator = await cls.get_locator(self=page_inner, selector=selector, timeout=timeout)
                logger.info(
                    f'找到页面中存在cookie提示：[本网站使用cookie，用于在您的电脑中储存信息。这些cookie可以使网站正常运行，以及帮助我们改进用户体验。使用本网站，即表示您接受放置这些cookie。]')
                await cookie.click(button="left")
                logger.info("【同意】按钮点击完成")
                await asyncio.sleep(1)
                return
            except (Exception,):
                pass

    async def url_wait_for(self, url: str, timeout: float = 3.0) -> None:
        """
        url_suffix格式：
            /shopping/oneway/SHA,PVG-URC/2026-01-08
            https://www.ceair.com/shopping/oneway/SHA,PVG-URC/2026-01-08
        :param url:
        :param timeout:
        :return:
        """
        for _ in range(int(timeout) * 10):
            if self.iss_current_page(page=self.__page, url=url):
                return
            await asyncio.sleep(delay=0.1)
        if url.find("://") == -1:
            url = self.get_url_domain() + url
        raise RuntimeError(f"无法打开/加载页面<{url}>")

    async def capture_network_by_keywords(
            self,
            keywords: List[str],
            include_post_data: bool = False,
            include_response_body: bool = True
    ) -> List[Dict[str, Any]]:
        """
        异步监听页面网络请求，捕获 URL 包含指定关键字的请求和响应。
        :param keywords: 关键字列表，如 ["order", "booking"]
        :param include_post_data: 是否包含 POST 请求体
        :param include_response_body: 是否包含响应体（自动尝试 JSON 或 text）
        :return: 匹配的请求/响应记录列表
        """
        captured_records = []

        def should_capture(url: str) -> bool:
            return any(kw in url for kw in keywords)

        async def handle_request(request: Request):
            if should_capture(request.url):
                record = {
                    "type": "request",
                    "url": request.url,
                    "method": request.method,
                    "resource_type": request.resource_type,
                    "headers": dict(request.headers),
                }
                if include_post_data and request.post_data:
                    record["post_data"] = request.post_data
                captured_records.append(record)

        async def handle_response(response: Response):
            if should_capture(response.url):
                record = {
                    "type": "response",
                    "url": response.url,
                    "status": response.status,
                    "status_text": response.status_text,
                    "headers": dict(response.headers),
                    "request_url": response.request.url,
                }
                if include_response_body:
                    try:
                        # 尝试解析为 JSON（异步）
                        body = await response.json()
                        record["body"] = body
                        record["body_type"] = "json"
                    except (Exception,):
                        try:
                            # 否则作为文本（异步）
                            text = await response.text()
                            record["body"] = text
                            record["body_type"] = "text"
                        except (Exception,):
                            record["body"] = ""
                            record["body_type"] = "binary_or_error"
                captured_records.append(record)

        # 注册监听器（Playwright 会自动处理 async 回调）
        self.__page.on("request", handle_request)
        self.__page.on("response", handle_response)

        return captured_records
