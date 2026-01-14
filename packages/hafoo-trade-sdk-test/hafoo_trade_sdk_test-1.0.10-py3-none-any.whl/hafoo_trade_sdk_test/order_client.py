from decimal import Decimal
from typing import Optional, List
from .order_place import place_order_http
from .order_modify import replace_order_http
from .order_qry import qry_ord_list_http
from .order_deal_qry import qry_deal_list_http
from .order_fare_qry import qry_fare_http
from .fund_qry import qry_fund_info_http
from .acc_trade_info import qry_acc_trad_info_http
from .pos_qry import qry_position_http
from .model import OrderPlaceResp, OrderReplaceResp, OrderReplaceReq, OrdQryReq, OrdQryResp, DealReq, DealResp, PosReq, PosResp, FareReq, FareResp, FundQryReq, FundQryResp, AccEnTrdInfoReq, AccEnTrdInfoResp
from .constant import TrdSide, OrderType, TimeInForce, Session

# -------------------------- 核心下单函数 --------------------------
def place_order(
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
    return place_order_http(
            full_url=full_url,
            api_key=api_key,
            private_key_pem=private_key_pem,  # 去除私钥前后空格
            price=price,
            qty=qty,
            symbol=symbol,
            trd_side=trd_side,
            order_type=order_type,  # 限价订单
            trd_env=trd_env,               # 模拟环境
            acc_id=acc_id,               # 账户ID
            time_in_force=time_in_force,  # 当日有效
            session=session                # 港股无需交易时段
        )

# -------------------------- 核心改撤单函数 --------------------------
def replace_order(
    full_url:str,
    api_key: str,
    private_key_pem: str,
    replace_req: OrderReplaceReq
) -> OrderReplaceResp:
    return replace_order_http(
            full_url=full_url,
            api_key=api_key,
            private_key_pem=private_key_pem.strip(),
            replace_req=replace_req
        )

# -------------------------- 核心订单查询请求函数 --------------------------
def qry_ord_list(
    full_url:str,
    api_key: str,
    private_key_pem: str,
    ord_qry_req: OrdQryReq
) -> List[OrdQryResp]:
    return qry_ord_list_http(full_url, api_key, private_key_pem.strip(), ord_qry_req) 


# -------------------------- 核心成交查询请求函数 --------------------------
def qry_deal_list(
    full_url: str,
    api_key: str,
    private_key_pem: str,
    deal_req: DealReq
) -> List[DealResp]:
    return qry_deal_list_http(full_url,api_key, private_key_pem.strip(), deal_req)


# -------------------------- 核心费用查询请求函数 --------------------------
def qry_fare(
    full_url: str,   
    api_key: str,
    private_key_pem: str,
    fare_req: FareReq
) -> List[FareResp]:
    return qry_fare_http(full_url, api_key, private_key_pem.strip(), fare_req)

# -------------------------- 核心持仓查询请求函数 --------------------------
def qry_position(
    full_url: str,   
    api_key: str,
    private_key_pem: str,
    pos_req: PosReq
) -> List[PosResp]:
    return qry_position_http(full_url,api_key,private_key_pem,pos_req)

# -------------------------- 核心资金查询请求函数 --------------------------
def qry_fund_info(
    full_url: str,
    api_key: str,
    private_key_pem: str,
    fund_req: FundQryReq
) -> FundQryResp:
    return qry_fund_info_http(full_url, api_key, private_key_pem.strip(), fund_req)

# -------------------------- 核心可买可卖查询请求函数 --------------------------
def qry_acc_trad_info(
    full_url: str,    
    api_key: str,
    private_key_pem: str,
    trad_req: AccEnTrdInfoReq
) -> AccEnTrdInfoResp:
    return qry_acc_trad_info_http(full_url, api_key, private_key_pem.strip(), trad_req)
