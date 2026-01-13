# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 10:18
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 10:18
# Thanks for your comments!

import json
import logging
import traceback

import aiohttp

logger = logging.getLogger(__name__)


async def async_post_request_json(server_url, json_params, data=None, headers=None, proxy=None, verify_ssl=None,
                                  **kwargs):
    try:
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Async HTTP Client (aiohttp)"
        }
        headers = {**default_headers, **(headers or {})}
        async with aiohttp.ClientSession() as session:
            async with session.post(url=server_url, json=json_params, data=data, headers=headers, proxy=proxy,
                                    verify_ssl=verify_ssl, **kwargs) as res:
                response = await res.text()
                if res.status != 200:
                    return False, response
                res = json.loads(response)
                return True, res
    except Exception as e:
        logger.error(f"async_post_request: {server_url} failed with err:{traceback.format_exc()}")
        return False, str(e)


async def async_post_request(server_url, json_params=None, data=None, headers=None, proxy=None, verify_ssl=None,
                             **kwargs):
    try:
        # logger.info(f"request url: {server_url}, data:{data} headers:{headers}, proxy:{proxy}")
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Async HTTP Client (aiohttp)"
        }
        headers = {**default_headers, **(headers or {})}
        async with aiohttp.ClientSession() as session:
            async with session.post(url=server_url, json=json_params, data=data, headers=headers, proxy=proxy,
                                    verify_ssl=verify_ssl, **kwargs) as res:
                response = await res.text()
                return res.status, response
    except Exception as e:
        logger.error(f"async_post_request: {server_url} failed with err:{traceback.format_exc()}")
        return None, str(e)


async def async_get_request(server_url, verify_ssl=None, **kwargs):
    try:
        # logger.info(f"request url: {server_url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url=server_url, verify_ssl=verify_ssl, **kwargs) as res:
                response = await res.text()
                # logger.info(f"response url:{server_url}, data: {response}")
                return res.status, json.loads(response)
    except Exception as e:
        logger.error(f"async_get_request: {server_url} failed with err:{traceback.format_exc()}")
        return None, str(e)
