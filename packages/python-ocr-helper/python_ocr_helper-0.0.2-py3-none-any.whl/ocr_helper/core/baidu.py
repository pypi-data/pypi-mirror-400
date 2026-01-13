# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  python-ocr-helper
# FileName:     baidu.py
# Description:  百度api模块
# Author:       zhouhanlin
# CreateDate:   2025/12/27
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import json
from typing import Optional, Dict, Any
from http_helper.client.async_proxy import HttpClientFactory
from ocr_helper.utils.image_utils import image_to_base64_with_check


class ApiAuth(object):

    def __init__(
            self, *, api_key: str, secret_key: str, protocol: Optional[str] = None, domain: Optional[str] = None,
            timeout: Optional[int] = None, retry: Optional[int] = None, enable_log: Optional[bool] = None
    ):
        self._retry = retry or 0
        self._domain = domain or "aip.baidubce.com"
        self._api_key = api_key
        self._timeout = timeout or 60
        self._protocol = protocol or "https"
        self._secret_key = secret_key
        self._http_client: Optional[HttpClientFactory] = None
        self._enable_log = enable_log if enable_log is not None else True

    @property
    def http_client(self):
        return self._get_http_client()

    def _get_http_client(self) -> HttpClientFactory:
        """延迟获取 HTTP 客户端"""
        if self._http_client is None:
            self._http_client = HttpClientFactory(
                protocol=self._protocol,
                domain=self._domain,
                timeout=self._timeout,
                retry=self._retry,
                enable_log=self._enable_log
            )
        return self._http_client

    async def get_access_token(self, is_end: Optional[bool] = None):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        params = {"grant_type": "client_credentials", "client_id": self._api_key, "client_secret": self._secret_key}
        client = self._get_http_client()
        return await client.request(
            method="post",
            url="/oauth/2.0/token",
            params=params,
            is_end=is_end if is_end is not None else True
        )


class ImageContentOCR(ApiAuth):

    @property
    def headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '
        }

    async def submit_request(
            self, *, question: str, image_path: Optional[str] = None, image_base64: Optional[str] = None,
            token: Optional[str] = None, is_end: Optional[bool] = None
    ) -> Dict[str, Any]:
        if not image_path and not image_base64:
            raise RuntimeError("必须要传递<image_path | image_base64>参数中的其中一个")
        if image_path:
            image = image_to_base64_with_check(image_path=image_path, urlencoded=False)
            image_base64 = image.get("base64")
        if token is None:
            response = await self.get_access_token(is_end=False)
            token = response.get("access_token")
            if not token:
                raise RuntimeError(str(response))
        payload = json.dumps({
            "image": image_base64,
            "question": question,
        }, ensure_ascii=False)
        url = "/rest/2.0/image-classify/v1/image-understanding/request?access_token=" + token
        return await self.http_client.request(
            method="post",
            url=url,
            headers=self.headers,
            data=payload.encode("utf-8"),
            is_end=True if is_end is None else is_end
        )

    async def get_result(
            self, task_id: str, token: Optional[str] = None, is_end: Optional[bool] = None
    ) -> Dict[str, Any]:
        if token is None:
            response = await self.get_access_token(is_end=False)
            token = response.get("access_token")
            if not token:
                raise RuntimeError(str(response))
        url = "/rest/2.0/image-classify/v1/image-understanding/get-result?access_token=" + token
        payload = json.dumps({
            "task_id": task_id
        }, ensure_ascii=False)
        return await self.http_client.request(
            method="post",
            url=url,
            headers=self.headers,
            data=payload.encode("utf-8"),
            is_end=True if is_end is None else is_end
        )
