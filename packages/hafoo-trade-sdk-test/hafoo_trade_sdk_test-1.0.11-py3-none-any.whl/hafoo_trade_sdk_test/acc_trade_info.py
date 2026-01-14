import requests
import time
import uuid
from .encryption import generate_rsa_signature
from .model import  AccEnTrdInfoResp, AccEnTrdInfoReq
from .device_info_qry import get_device_info



# -------------------------- 5. 核心可买可卖查询HTTP请求函数 --------------------------
def qry_acc_trad_info_http(
    full_url: str,    
    api_key: str,
    private_key_pem: str,
    trad_req: AccEnTrdInfoReq
) -> AccEnTrdInfoResp:
    """
    发送可买可卖查询POST请求（含签名认证），返回解析后的实体
    :param api_key: 接口APIKey
    :param private_key_pem: PEM格式私钥
    :param trad_req: 可买可卖查询请求实体
    :return: 解析后的可买可卖信息（AccEnTrdInfoResp）
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
        "acc_id": str(trad_req.acc_id)
    }

    # -------------------------- 步骤2：构造请求体 --------------------------
    try:
        request_body = trad_req.to_dict()  # 自动完成参数校验
    except ValueError as e:
        raise ValueError(f"可买可卖查询参数错误: {str(e)}") from e

    # -------------------------- 步骤3：发送POST请求 --------------------------
    try:
        response = requests.post(
            url=full_url,
            headers=headers,
            json=request_body,
            timeout=60
        )
        response.raise_for_status()  # 抛出HTTP错误
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"可买可卖查询HTTP失败: {str(e)}，URL: {full_url}，请求体: {request_body}"
        ) from e

    # -------------------------- 步骤4：解析响应 --------------------------
    try:
        resp_dict = response.json()
        if resp_dict.get("code") != 0:
            raise ValueError(f"接口返回失败: {resp_dict.get('msg', '未知错误')}")

        trad_data = resp_dict.get("data", {})
        if not trad_data:
            raise ValueError("可买可卖查询响应数据为空")

        return AccEnTrdInfoResp.from_list_resp(trad_data)
    except ValueError as e:
        raise ValueError(
            f"响应解析失败: {str(e)}，原始数据: {response.text}"
        ) from e
    except Exception as e:
        raise Exception(
            f"实体构造失败: {str(e)}，原始数据: {response.text}"
        ) from e


