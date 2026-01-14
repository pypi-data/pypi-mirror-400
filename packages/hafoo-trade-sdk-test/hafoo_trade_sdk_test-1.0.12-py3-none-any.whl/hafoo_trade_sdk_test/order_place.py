import requests
import time
import uuid
from decimal import Decimal
from typing import Optional
from .encryption import generate_rsa_signature
from .constant import TrdSide, OrderType, TimeInForce, Session
from .model import OrderPlaceResp
from .device_info_qry import get_device_info


# -------------------------- 4. 核心下单HTTP请求函数--------------------------
def place_order_http(
    # 订单核心参数
    full_url: str,
    api_key: str,
    private_key_pem: str,
    price: Decimal,
    qty: Decimal,
    symbol: str,
    trd_side: TrdSide,
    order_type: OrderType = OrderType.LIMIT,
    trd_env: str = "TEST",  # 交易环境（PROD/TEST）
    acc_id: int = 0,
    time_in_force: TimeInForce = TimeInForce.DAY,
    session: Optional[Session] = "RTH"
) -> OrderPlaceResp:
    """
    发送POST下单请求（含签名认证），并解析响应为OrderPlaceResp实体
    :param price: 下单价格（Decimal类型，避免浮点误差）
    :param qty: 下单数量（Decimal类型，支持碎股场景）
    :param symbol: 股票代码（如HK.00700、US.AAPL）
    :param trd_side: 交易方向（TrdSide.BUY/SELL）
    :param order_type: 订单类型（默认普通订单）
    :param trd_env: 交易环境（默认生产环境）
    :param acc_id: 账户ID（默认0）
    :param remark: 订单备注（可选）
    :param time_in_force: 订单有效期（默认当日有效）
    :param session: 交易时段（美股专用，可选）
    :param api_key: 接口APIKey
    :param private_key_pem: PEM格式私钥（签名用）
    :return: 解析后的订单响应实体（OrderPlaceResp）
    :raises requests.exceptions.RequestException: HTTP请求异常
    :raises ValueError: 响应数据格式错误
    :raises Exception: 其他业务异常
    """
    # -------------------------- 步骤1：生成请求头参数（含签名）--------------------------
    # 时间戳：毫秒级字符串（与Java System.currentTimeMillis()一致）
    timestamp = str(int(time.time() * 1000))
    # 随机字符串：无横杠UUID（与Java UUID.randomUUID().toString().replace("-", "")一致）
    nonce = uuid.uuid4().hex
    # 生成SHA256withRSA签名
    signature = generate_rsa_signature(private_key_pem, api_key, timestamp, nonce)
    # 构造请求头（必须包含apikey、timestamp、nonce、signature）
    headers = {
        "apiKey": api_key,
        "timestamp": timestamp,
        "nonce": nonce,
        "signature": signature,
        "Content-Type": "application/json",  # JSON格式请求体
        "Accept": "application/json",         # 期望JSON格式响应
        "device_info": get_device_info(),
        "acc_id": str(acc_id)
    }
    # -------------------------- 步骤2：构造请求体（与服务端字段对齐）--------------------------
    # Decimal类型转字符串（避免JSON序列化丢失精度）
    request_body = {
        "price": str(price),
        "qty": str(qty),
        "symbol": symbol,
        "trd_side": trd_side.value,  # 枚举转字符串（服务端通常接收字符串）
        "order_type": order_type.value,
        "trd_env": trd_env,
        "acc_id": acc_id,
        "time_in_force": time_in_force.value,
        "session": session.value if session else None  # 可选字段
    }
    # 移除值为None的字段（避免服务端解析异常）
    request_body = {k: v for k, v in request_body.items() if v is not None}
    # -------------------------- 步骤3：发送POST请求--------------------------
    try:
        response = requests.post(
            url=full_url,
            headers=headers,
            json=request_body,  # 自动序列化JSON，设置Content-Type
            timeout=60  # 超时时间（避免长期阻塞，根据业务调整）
        )
        # 主动抛出HTTP错误（如404、500）
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"HTTP请求失败: {str(e)}，URL: {full_url}，请求体: {request_body}"
        ) from e
    # -------------------------- 步骤4：解析响应为OrderPlaceResp--------------------------
    try:
        resp_dict = response.json()
        # 假设服务端返回格式：{"code": 0, "data": {...订单数据...}}
        if 0!= resp_dict.get("code"):
            raise ValueError(f"接口返回失败: {resp_dict.get('msg', '未知错误')}")
        # 从响应字典构造实体类
        return OrderPlaceResp.from_list_resp(resp_dict["data"])
    except ValueError as e:
        raise ValueError(
            f"响应解析失败: {str(e)}，响应原始数据: {response.text}"
        ) from e
    except Exception as e:
        raise Exception(
            f"实体类构造失败: {str(e)}，响应原始数据: {response.text}"
        ) from e