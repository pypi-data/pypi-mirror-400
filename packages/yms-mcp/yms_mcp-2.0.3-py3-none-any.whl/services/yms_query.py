#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YMS后端查询工具模块
提供Entry Ticket和Appointment查询功能
"""

import httpx
from typing import Dict, Any, Optional
from loguru import logger

from ..config.settings import settings
from ..managers.token import token_manager


def _build_url(base: str, path: str) -> str:
    """构建完整的URL"""
    if not base:
        return path or ""
    if not path:
        return base or ""
    return base.rstrip('/') + '/' + path.lstrip('/')


async def _make_http_post_request(url: str, headers: dict, json_data: dict) -> Dict[str, Any]:
    """内部HTTP POST请求辅助函数"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        logger.info(f"发送POST请求到: {url}")
        logger.info(f"请求体: {json_data}")

        response = await client.post(url, headers=headers, json=json_data)

        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应trace_id: {response.headers.get('traceid', 'N/A')}")

        # 如果是错误状态码，记录完整响应内容（在 raise_for_status 之前）
        if response.status_code >= 400:
            try:
                error_json = response.json()
                logger.error(f"HTTP错误响应: {error_json}")
            except Exception:
                logger.error(f"HTTP错误响应（原始文本）: {response.text}")

        response.raise_for_status()
        return response.json()


async def search_entry_tickets_data(
    page_num: int = 1,
    page_size: int = 20,
    entry_id: Optional[str] = None,
    keyword: Optional[str] = None,
    driver_id: Optional[str] = None,
    vehicle_id: Optional[str] = None,
    appointment_id: Optional[str] = None,
    tractor_no: Optional[str] = None,
    trailer_no: Optional[str] = None,
    container_no: Optional[str] = None,
    load_no: Optional[str] = None,
    entry_status: Optional[str] = None,
    appointment_status: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询 Entry Ticket 列表（内部数据函数）

    Args:
        page_num: 页码，默认1
        page_size: 每页大小，默认20
        entry_id: Entry Ticket ID
        keyword: 关键词搜索
        driver_id: 司机ID
        vehicle_id: 车辆ID
        appointment_id: 预约ID
        tractor_no: 车头编号
        trailer_no: 拖车编号
        container_no: 集装箱编号
        load_no: 装货单号
        entry_status: 入场状态
        appointment_status: 预约状态

    Returns:
        Dict: 查询结果字典
    """
    try:
        # 1. 获取有效的 access token
        access_token = await token_manager.get_valid_token()

        # 2. 构建请求体
        query_body = {
            "currentPage": page_num,
            "pageSize": page_size
        }

        # 添加可选参数（只添加非空值）
        if entry_id:
            query_body["entryId"] = entry_id
        if keyword:
            query_body["keyword"] = keyword
        if driver_id:
            query_body["driverId"] = driver_id
        if vehicle_id:
            query_body["vehicleId"] = vehicle_id
        if appointment_id:
            query_body["appointmentId"] = appointment_id
        if tractor_no:
            query_body["tractorNo"] = tractor_no
        if trailer_no:
            query_body["trailerNo"] = trailer_no
        if container_no:
            query_body["containerNo"] = container_no
        if load_no:
            query_body["loadNo"] = load_no
        if entry_status:
            query_body["entryStatus"] = entry_status
        if appointment_status:
            query_body["appointmentStatus"] = appointment_status

        # 3. 准备请求头
        headers = {
            "X-Tenant-ID": settings.yms_tenant_id,
            "X-Yard-ID": settings.yms_yard_id,
            "Item-Time-Zone": settings.yms_timezone,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # 4. 构建请求 URL
        search_url = _build_url(
            settings.yms_backend_url,
            '/workSpace/search-by-paging'
        )

        logger.info(f"查询 Entry Tickets: {search_url}")
        logger.info(f"查询参数: {query_body}")

        # 5. 发送请求
        result = await _make_http_post_request(search_url, headers, query_body)
        logger.info(f"查询成功，返回数据")

        # 检查业务状态码
        if not result.get('success', False) or result.get('code', -1) != 0:
            error_msg = result.get('msg', '查询失败')
            logger.error(f"Entry Ticket 查询失败: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "message": "查询失败"
            }

        # 返回数据
        data = result.get('data', {})
        return {
            "success": True,
            "data": data,
            "message": f"查询成功，共{data.get('total', 0)}条记录"
        }

    except Exception as e:
        # 检查是否是 HTTP 状态错误
        if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
            logger.error(f"Entry Ticket 查询 HTTP 错误: {e.response.status_code}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "message": "查询失败"
            }
        logger.error(f"Entry Ticket 查询异常: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "查询失败"
        }


async def search_appointments_data(
    page_num: int = 1,
    page_size: int = 20,
    appointment_id: Optional[str] = None,
    appointment_type: Optional[str] = None,
    carrier_id: Optional[str] = None,
    driver_id: Optional[str] = None,
    appointment_status: Optional[str] = None,
    customer_id: Optional[str] = None,
    entry_id: Optional[str] = None,
    reference_code: Optional[str] = None,
    keyword: Optional[str] = None,
    load_id: Optional[str] = None,
    receipt_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询 Appointment 列表（内部数据函数）

    Args:
        page_num: 页码，默认1
        page_size: 每页大小，默认20
        appointment_id: 预约ID
        appointment_type: 预约类型
        carrier_id: 承运商ID
        driver_id: 司机ID
        appointment_status: 预约状态
        customer_id: 客户ID
        entry_id: Entry Ticket ID
        reference_code: 参考代码
        keyword: 关键词搜索
        load_id: 装货单ID
        receipt_id: 收货单ID

    Returns:
        Dict: 查询结果字典
    """
    try:
        # 1. 获取有效的 access token
        access_token = await token_manager.get_valid_token()

        # 2. 构建请求体
        query_body = {
            "currentPage": page_num,
            "pageSize": page_size
        }

        # 添加可选参数（只添加非空值）
        if appointment_id:
            query_body["appointmentId"] = appointment_id
        if appointment_type:
            query_body["appointmentType"] = appointment_type
        if carrier_id:
            query_body["carrierId"] = carrier_id
        if driver_id:
            query_body["driverId"] = driver_id
        if appointment_status:
            query_body["appointmentStatus"] = appointment_status
        if customer_id:
            query_body["customerId"] = customer_id
        if entry_id:
            query_body["entryId"] = entry_id
        if reference_code:
            query_body["referenceCode"] = reference_code
        if keyword:
            query_body["keyword"] = keyword
        if load_id:
            query_body["loadId"] = load_id
        if receipt_id:
            query_body["receiptId"] = receipt_id

        # 3. 准备请求头
        headers = {
            "X-Tenant-ID": settings.yms_tenant_id,
            "X-Yard-ID": settings.yms_yard_id,
            "Item-Time-Zone": settings.yms_timezone,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # 4. 构建请求 URL
        search_url = _build_url(
            settings.yms_backend_url,
            '/level2/appointment/search-by-paging'
        )

        logger.info(f"查询 Appointments: {search_url}")
        logger.info(f"查询参数: {query_body}")

        # 5. 发送请求
        result = await _make_http_post_request(search_url, headers, query_body)
        logger.info(f"查询成功，返回数据")

        # 检查业务状态码
        if not result.get('success', False) or result.get('code', -1) != 0:
            error_msg = result.get('msg', '查询失败')
            logger.error(f"Appointment 查询失败: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "message": "查询失败"
            }

        # 返回数据
        data = result.get('data', {})
        return {
            "success": True,
            "data": data,
            "message": f"查询成功，共{data.get('total', 0)}条记录"
        }

    except Exception as e:
        # 检查是否是 HTTP 状态错误
        if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
            logger.error(f"Appointment 查询 HTTP 错误: {e.response.status_code}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "message": "查询失败"
            }
        logger.error(f"Appointment 查询异常: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "查询失败"
        }

