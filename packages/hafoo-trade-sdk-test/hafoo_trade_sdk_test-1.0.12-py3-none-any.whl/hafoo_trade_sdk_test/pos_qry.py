import requests
import time
import uuid
from typing import List
from .encryption import generate_rsa_signature
from .model import PosReq, PosResp
from .device_info_qry import get_device_info



# -------------------------- 5. 核心持仓查询HTTP请求函数 --------------------------
def qry_position_http(
    full_url: str,   
    api_key: str,
    private_key_pem: str,
    pos_req: PosReq
) -> List[PosResp]:
    """
    发送持仓查询POST请求（含签名认证），返回解析后的持仓列表
    :param api_key: 接口APIKey
    :param private_key_pem: PEM格式私钥（签名用）
    :param pos_req: 持仓查询请求实体（PosReq）
    :return: 解析后的持仓列表（List[PosResp]，无持仓时返回空列表）
    :raises requests.exceptions.RequestException: HTTP请求异常
    :raises ValueError: 请求参数错误或响应解析失败
    :raises Exception: 其他业务异常
    """
    # -------------------------- 步骤1：生成请求头（含签名，与下单逻辑一致）--------------------------
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
        "acc_id": str(pos_req.acc_id)
    }

    # -------------------------- 步骤2：构造请求体（从PosReq转换）--------------------------
    try:
        request_body = pos_req.to_dict()  # 自动校验标的格式
    except ValueError as e:
        raise ValueError(f"持仓查询请求参数错误: {str(e)}") from e
    # -------------------------- 步骤3：发送POST请求 --------------------------
    try:
        response = requests.post(
            url=full_url,
            headers=headers,
            json=request_body,
            timeout=60  # 超时时间，适配查询类接口
        )
        response.raise_for_status()  # 抛出HTTP错误（4xx/5xx）
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"持仓查询HTTP请求失败: {str(e)}，URL: {full_url}，请求体: {request_body}"
        ) from e

    # -------------------------- 步骤4：解析响应为持仓列表 --------------------------
    try:
        resp_dict = response.json()
        # 校验接口返回码（0为成功，与下单逻辑一致）
        if resp_dict.get("code") != 0:
            raise ValueError(f"持仓查询接口返回失败: {resp_dict.get('msg', '未知错误')}")

        # 解析data字段（列表类型）
        pos_list = resp_dict.get("data", [])
        return PosResp.from_list_resp(pos_list)
    except ValueError as e:
        raise ValueError(
            f"持仓响应解析失败: {str(e)}，响应原始数据: {response.text}"
        ) from e
    except Exception as e:
        raise Exception(
            f"持仓实体构造失败: {str(e)}，响应原始数据: {response.text}"
        ) from e

