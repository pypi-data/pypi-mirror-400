import requests
import time
import uuid
from typing import List
from .encryption import generate_rsa_signature
from .model import OrdQryReq, OrdQryResp
from .device_info_qry import get_device_info


# -------------------------- 5. 核心订单查询HTTP请求函数 --------------------------
def qry_ord_list_http(
    full_url: str,   
    api_key: str,
    private_key_pem: str,
    ord_qry_req: OrdQryReq
) -> List[OrdQryResp]:
    """
    发送订单查询POST请求（含签名认证），返回解析后的订单列表
    :param api_key: 接口APIKey
    :param private_key_pem: PEM格式私钥
    :param ord_qry_req: 订单查询请求实体（OrdQryReq）
    :return: 解析后的订单列表（List[OrdQryResp]）
    :raises requests.exceptions.RequestException: HTTP请求异常
    :raises ValueError: 参数错误或响应解析失败
    :raises Exception: 其他业务异常
    """
    # -------------------------- 步骤1：生成请求头（含签名）--------------------------
    timestamp = str(int(time.time() * 1000))  # 毫秒级时间戳
    nonce = uuid.uuid4().hex  # 无横杠UUID
    signature = generate_rsa_signature(private_key_pem, api_key, timestamp, nonce)

    headers = {
        "apiKey": api_key,
        "timestamp": timestamp,
        "nonce": nonce,
        "signature": signature,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "device_info": get_device_info(),
        "acc_id": str(ord_qry_req.acc_id)
    }

    # -------------------------- 步骤2：构造请求体 --------------------------
    try:
        request_body = ord_qry_req.to_dict()  # 自动完成参数校验
    except ValueError as e:
        raise ValueError(f"订单查询请求参数错误: {str(e)}") from e
    # -------------------------- 步骤3：发送POST请求 --------------------------
    try:
        response = requests.post(
            url=full_url,
            headers=headers,
            json=request_body,
            timeout=60  # 超时时间，适配查询类接口
        )
        response.raise_for_status()  # 主动抛出HTTP错误（4xx/5xx）
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"订单查询HTTP请求失败: {str(e)}，URL: {full_url}，请求体: {request_body}"
        ) from e

    # -------------------------- 步骤4：解析响应 --------------------------
    try:
        resp_dict = response.json()
        # 校验接口返回码（0为成功，与其他接口逻辑一致）
        if resp_dict.get("code") != 0:
            raise ValueError(f"订单查询接口返回失败: {resp_dict.get('msg', '未知错误')}")

        # 解析data字段（列表类型，每个元素对应一个订单）
        ord_list = resp_dict.get("data", [])
        return OrdQryResp.from_list_resp(ord_list)
    except ValueError as e:
        raise ValueError(
            f"订单查询响应解析失败: {str(e)}，响应原始数据: {response.text}"
        ) from e
    except Exception as e:
        raise Exception(
            f"订单查询实体构造失败: {str(e)}，响应原始数据: {response.text}"
        ) from e


