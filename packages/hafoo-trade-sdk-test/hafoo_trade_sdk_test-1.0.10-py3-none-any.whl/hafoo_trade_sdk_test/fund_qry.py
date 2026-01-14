import requests
import time
import uuid
from .encryption import generate_rsa_signature
from .model import FundQryReq, FundQryResp
from .device_info_qry import get_device_info




# -------------------------- 5. 核心资金查询HTTP请求函数 --------------------------
def qry_fund_info_http(
    full_url: str,
    api_key: str,
    private_key_pem: str,
    fund_req: FundQryReq
) -> FundQryResp:
    """
    发送资金查询POST请求（含签名认证），返回解析后的资金实体
    :param api_key: 接口APIKey
    :param private_key_pem: PEM格式私钥
    :param fund_req: 资金查询请求实体（FundQryReq）
    :return: 解析后的资金信息实体（FundQryResp）
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
        "acc_id":str(fund_req.acc_id)
    }

    # -------------------------- 步骤2：构造请求体 --------------------------
    try:
        request_body = fund_req.to_dict()  # 自动完成参数校验
    except ValueError as e:
        raise ValueError(f"资金查询请求参数错误: {str(e)}") from e
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
            f"资金查询HTTP请求失败: {str(e)}，URL: {full_url}，请求体: {request_body}"
        ) from e

    # -------------------------- 步骤4：解析响应 --------------------------
    try:
        resp_dict = response.json()
        # 校验接口返回码（0为成功，与其他接口逻辑一致）
        if resp_dict.get("code") != 0:
            raise ValueError(f"资金查询接口返回失败: {resp_dict.get('msg', '未知错误')}")

        # 解析data字段（单个资金对象，非列表）
        fund_data = resp_dict.get("data", {})
        if not fund_data:
            raise ValueError("资金查询响应数据为空")

        return FundQryResp.from_list_resp(fund_data)
    except ValueError as e:
        raise ValueError(
            f"资金查询响应解析失败: {str(e)}，响应原始数据: {response.text}"
        ) from e
    except Exception as e:
        raise Exception(
            f"资金查询实体构造失败: {str(e)}，响应原始数据: {response.text}"
        ) from e
    

