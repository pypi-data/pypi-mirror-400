import requests
import time
import uuid
from .encryption import generate_rsa_signature
from .model import OrderReplaceReq, OrderReplaceResp
from .device_info_qry import get_device_info

# -------------------------- 核心改撤单HTTP请求函数 --------------------------
def replace_order_http(
    full_url: str,
    api_key: str,
    private_key_pem: str,
    replace_req: OrderReplaceReq
) -> OrderReplaceResp:
    """
    发送改单/撤单POST请求（含签名认证），并解析响应为OrderReplaceResp实体
    :param api_key: 接口APIKey
    :param private_key_pem: PEM格式私钥（签名用）
    :param replace_req: 改撤单请求实体（OrderReplaceReq）
    :return: 解析后的改撤单响应实体
    :raises requests.exceptions.RequestException: HTTP请求异常
    :raises ValueError: 响应数据格式错误
    :raises Exception: 其他业务异常
    """
    # -------------------------- 步骤1：生成请求头参数（含签名）--------------------------
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
        "acc_id": str(replace_req.acc_id)
    }

    # -------------------------- 步骤2：构造请求体 --------------------------
    request_body = replace_req.to_dict()  # 从实体类转换为字典

    # -------------------------- 步骤3：发送POST请求 --------------------------
    try:
        response = requests.post(
            url=full_url,
            headers=headers,
            json=request_body,
            timeout=60
        )
        response.raise_for_status()  # 抛出HTTP错误（如404、500）

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"改撤单HTTP请求失败: {str(e)}，URL: {full_url}，请求体: {request_body}"
        ) from e

    # -------------------------- 步骤4：解析响应 --------------------------
    try:
        resp_dict = response.json()
        if resp_dict.get("code") != 0:
            raise ValueError(f"改撤单接口返回失败: {resp_dict.get('msg', '未知错误')}")

        # 解析响应为实体类
        return OrderReplaceResp.from_dict(resp_dict["data"])

    except ValueError as e:
        raise ValueError(
            f"改撤单响应解析失败: {str(e)}，响应原始数据: {response.text}"
        ) from e
    except Exception as e:
        raise Exception(
            f"改撤单实体构造失败: {str(e)}，响应原始数据: {response.text}"
        ) from e

