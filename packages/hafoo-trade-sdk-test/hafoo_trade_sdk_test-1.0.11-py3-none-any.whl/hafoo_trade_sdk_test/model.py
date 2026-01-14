from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, List
import re
from .constant import TrdSide, OrderType, OrderStatus, TimeInForce, Session, ModifyOrderOp, TrdEnv, TrdMarket, Currency, DealStatus, PositionSide 


# -------------------------- 2. 订单响应实体类（OrderPlaceResp）--------------------------
@dataclass
class OrderPlaceResp:
    """订单提交响应实体类"""
    trd_side: TrdSide          # 交易方向
    order_type: OrderType      # 订单类型
    order_status: OrderStatus  # 订单状态
    order_id: str              # 订单号
    symbol: str                  # 股票代码
    stock_name: str            # 股票名称
    qty: Decimal               # 订单数量
    price: Decimal             # 订单价格
    create_time: str           # 创建时间（格式：yyyy-MM-dd HH:mm:ss）
    updated_time: str          # 最后更新时间（格式：yyyy-MM-dd HH:mm:ss）
    deal_qty: Decimal         # 成交数量
    deal_balance: Decimal  # 成交金额
    time_in_force: TimeInForce    # 有效期限
    session: Optional[Session] = None  # 交易时段（美股专用，可选）
    @classmethod
    def from_single_dict(cls, single_order_dict: Dict) -> "OrderPlaceResp":
        """解析单个订单字典"""
        try:
            # 必选字段校验
            required_fields = ["trd_side", "order_type", "order_status", "order_id",
                               "symbol", "qty", "price", "create_time", "updated_time",
                               "deal_qty", "deal_balance"]
            for field in required_fields:
                if field not in single_order_dict:
                    raise KeyError(f"缺少必选字段: {field}")
            # 枚举值转换
            try:
                trd_side = TrdSide(single_order_dict["trd_side"])
                order_type = OrderType(single_order_dict["order_type"])
                order_status = OrderStatus(single_order_dict["order_status"])
                time_in_force = TimeInForce(single_order_dict["time_in_force"]) if single_order_dict.get("time_in_force") else None
                session = Session(single_order_dict["session"]) if single_order_dict.get("session") else None
            except ValueError as e:
                raise ValueError(f"枚举值无效: {e}")
            # 构造实体
            return cls(
                trd_side=trd_side,
                order_type=order_type,
                order_status=order_status,
                order_id=single_order_dict["order_id"],
                symbol=single_order_dict["symbol"],
                stock_name=single_order_dict.get("stock_name"),
                qty=Decimal(str(single_order_dict["qty"])),
                price=Decimal(str(single_order_dict["price"])),
                create_time=single_order_dict["create_time"],
                updated_time=single_order_dict["updated_time"],
                deal_qty=Decimal(str(single_order_dict["deal_qty"])),
                deal_balance=Decimal(str(single_order_dict["deal_balance"])),
                time_in_force=time_in_force,
                session=session
            )
        except Exception as e:
            order_id = single_order_dict.get("order_id", "未知订单")
            raise ValueError(f"解析订单 {order_id} 失败: {str(e)}") from e
    @classmethod
    def from_list_resp(cls, order_list: list) -> list['OrderPlaceResp']:
        """解析包含订单列表的完整响应"""
        try:
            if not order_list:
                raise ValueError("订单列表为空")
            # 获取并校验订单列表
            if not isinstance(order_list, list):
                raise TypeError(f"预期订单列表，实际收到: {type(order_list).__name__}")
            # 解析所有订单
            orders = []
            errors = []
            for idx, order_dict in enumerate(order_list):
                try:
                    orders.append(cls.from_single_dict(order_dict))
                except Exception as e:
                    errors.append(f"第{idx+1}个订单: {str(e)}")
            # 处理解析错误
            if errors:
                raise ValueError(f"部分订单解析失败: {'; '.join(errors)}")
            return orders
        except Exception as e:
            raise ValueError(f"解析订单列表失败: {str(e)}") from e
    def __str__(self) -> str:
        """自定义打印格式，便于日志查看"""
        return (f"OrderPlaceResp(order_id={self.order_id}, symbol={self.symbol}, "
                f"trd_side={self.trd_side.value}, status={self.order_status.value}, "
                f"qty={self.qty}, price={self.price}, deal_qty={self.deal_qty})")
    


# -------------------------- 改撤单请求实体类（OrderReplaceReq）--------------------------
@dataclass
class OrderReplaceReq:
    """改单/撤单请求实体类"""
    modify_order_op: ModifyOrderOp  # 操作类型（修改/撤单）
    order_id: str                   # 订单号（必填）
    trd_env: TrdEnv                 # 交易环境（必填）
    acc_id: int                     # 账户ID（必填）
    qty: Decimal   # 改单后数量（仅修改时必填）
    price: Decimal # 改单后价格（仅修改时必填）

    def to_dict(self) -> Dict:
        """转换为请求字典（处理Decimal和枚举）"""
        req_dict = {
            "modify_order_op": self.modify_order_op.value,
            "order_id": self.order_id,
            "trd_env": self.trd_env.value,
            "acc_id": self.acc_id,
            "qty": str(self.qty),
            "price": str(self.price)
        }
        # 仅修改订单时添加数量和价格（撤单无需这两个字段）
        if self.modify_order_op == ModifyOrderOp.MODIFY:
            if self.qty is None or self.price is None:
                raise ValueError("修改订单时，qty和price不能为空")
            req_dict["qty"] = str(self.qty)  # Decimal转字符串避免精度丢失
            req_dict["price"] = str(self.price)
        return req_dict


# -------------------------- 改撤单响应实体类（OrderReplaceResp）--------------------------
@dataclass
class OrderReplaceResp:
    """改单/撤单响应实体类"""
    trd_env: TrdEnv  # 交易环境
    order_id: str    # 订单号

    @classmethod
    def from_dict(cls, resp_data: Dict) -> "OrderReplaceResp":
        """从响应数据解析实体（适配 data 为列表的情况）"""
        try:
            # 核心修改：如果 data 是列表，取第一个元素（根据响应数据格式）
            if isinstance(resp_data, list):
                if not resp_data:  # 列表为空时抛出异常
                    raise ValueError("响应数据列表为空")
                resp_data = resp_data[0]  # 取列表第一个元素作为实际数据字典

            # 校验必选字段
            required_fields = ["trd_env", "order_id"]
            for field in required_fields:
                if field not in resp_data:
                    raise KeyError(f"缺少必选字段: {field}")
            
            # 转换枚举值
            trd_env = TrdEnv(resp_data["trd_env"])
            return cls(
                trd_env=trd_env,
                order_id=resp_data["order_id"]
            )
        except Exception as e:
            raise ValueError(f"解析改撤单响应失败: {str(e)}") from e

    def __str__(self) -> str:
        return f"OrderReplaceResp(order_id={self.order_id}, trd_env={self.trd_env.value})"



# -------------------------- 2. 订单查询请求实体（OrdQryReq）--------------------------
@dataclass
class OrdQryReq:
    """订单查询请求实体"""
    trd_env: TrdEnv                          # 交易环境（必填）
    acc_id: int                              # 账户ID（必填）
    order_id: Optional[str] = None           # 订单号过滤（可选）
    order_market: Optional[TrdMarket] = None # 市场过滤（可选）
    status_filter_list: Optional[List[OrderStatus]] = None  # 订单状态过滤（可选）
    symbol: Optional[str] = None             # 标的代码过滤（可选，格式：HK.00700）

    def to_dict(self) -> Dict:
        """转换为请求字典（含参数校验+枚举值处理）"""
        # 1. 校验标的代码格式（规则：前缀.代码，如HK.00700）
        if self.symbol and not self._is_valid_symbol(self.symbol):
            raise ValueError(f"标的代码格式错误，示例：HK.00700，US.TSLA，当前：{self.symbol}")

        # 2. 构造基础请求字典
        req_dict = {
            "trd_env": self.trd_env.value,
            "acc_id": self.acc_id
        }

        # 3. 处理可选字段（仅当值不为None时添加）
        if self.order_id:
            req_dict["order_id"] = self.order_id
        if self.order_market:
            req_dict["order_market"] = self.order_market.value
        if self.symbol:
            req_dict["symbol"] = self.symbol

        # 4. 处理状态过滤列表（转换为枚举值字符串列表）
        if self.status_filter_list:
            if not isinstance(self.status_filter_list, list):
                raise TypeError("status_filter_list 必须是 OrderStatus 枚举列表")
            req_dict["status_filter_list"] = [status.value for status in self.status_filter_list]

        return req_dict

    @staticmethod
    def _is_valid_symbol(symbol: str) -> bool:
        """校验标的代码格式（ ^[a-zA-Z]+\\.[a-zA-Z0-9 _\\.]+$）"""
        pattern = r"^[a-zA-Z]+\.[a-zA-Z0-9 _\.]+$"
        return re.match(pattern, symbol) is not None


# -------------------------- 3. 订单查询响应实体（OrdQryResp）--------------------------
@dataclass
class OrdQryResp:
    """订单查询响应实体"""
    trd_side: TrdSide              # 交易方向
    order_type: OrderType          # 订单类型
    order_status: OrderStatus      # 订单状态
    order_id: str                  # 订单唯一标识
    symbol: str                    # 标的代码（如HK.00700）
    order_market: TrdMarket        # 订单所属市场
    qty: Decimal                   # 订单数量
    price: Decimal                 # 订单价格
    currency: Currency             # 货币类型
    create_time: str               # 订单创建时间（yyyy-MM-dd HH:mm:ss）
    deal_qty: Decimal             # 已成交数量
    deal_balance: Decimal          # 成交金额
    time_in_force: TimeInForce     # 订单有效期限
    remark: Optional[str] = None   # 订单备注（可选）
    session: Optional[Session] = None  # 交易时段（可选）

    @classmethod
    def from_single_dict(cls, ord_dict: Dict) -> "OrdQryResp":
        """解析单个订单查询响应字典"""
        try:
            # 1. 必选字段校验
            required_fields = [
                "trd_side", "order_type", "order_status", "order_id", 
                "symbol", "order_market", "qty", "price", "currency", 
                "create_time", "deal_qty", "deal_balance", "time_in_force"
            ]
            for field in required_fields:
                if field not in ord_dict:
                    raise KeyError(f"缺少订单必选字段: {field}")

            # 2. 枚举值转换（兼容接口返回的大小写，处理无效值）
            def parse_enum(enum_cls, value, field_name: str) -> Enum:
                try:
                    return enum_cls(value.upper() if isinstance(value, str) else value)
                except ValueError:
                    raise ValueError(f"订单{ord_dict['order_id']}的{field_name}枚举值无效: {value}")

            trd_side = parse_enum(TrdSide, ord_dict["trd_side"], "trd_side")
            order_type = parse_enum(OrderType, ord_dict["order_type"], "order_type")
            order_status = parse_enum(OrderStatus, ord_dict["order_status"], "order_status")
            order_market = parse_enum(TrdMarket, ord_dict["order_market"], "order_market")
            currency = parse_enum(Currency, ord_dict["currency"], "currency")
            time_in_force = parse_enum(TimeInForce, ord_dict["time_in_force"], "time_in_force")
            session = parse_enum(Session, ord_dict["session"], "session") if ord_dict.get("session") else None

            # 3. Decimal类型转换（避免浮点误差，支持字符串/数字类型的返回值）
            def to_decimal(value, field_name: str) -> Decimal:
                try:
                    return Decimal(str(value))
                except Exception as e:
                    raise ValueError(f"订单{ord_dict['order_id']}的{field_name}值无效: {value}，错误: {str(e)}")

            qty = to_decimal(ord_dict["qty"], "qty")
            price = to_decimal(ord_dict["price"], "price")
            deal_qty = to_decimal(ord_dict["deal_qty"], "deal_qty")
            deal_balance = to_decimal(ord_dict["deal_balance"], "deal_balance")

            # 4. 构造响应实体
            return cls(
                trd_side=trd_side,
                order_type=order_type,
                order_status=order_status,
                order_id=ord_dict["order_id"],
                symbol=ord_dict["symbol"],
                order_market=order_market,
                qty=qty,
                price=price,
                currency=currency,
                create_time=ord_dict["create_time"],
                deal_qty=deal_qty,
                deal_balance=deal_balance,
                remark=ord_dict.get("remark"),
                time_in_force=time_in_force,
                session=session
            )
        except Exception as e:
            raise ValueError(f"解析订单{ord_dict.get('order_id', '未知订单')}失败: {str(e)}") from e

    @classmethod
    def from_list_resp(cls, ord_list: List[Dict]) -> List["OrdQryResp"]:
        """解析订单列表响应（适配接口返回的data为列表）"""
        try:
            if not ord_list:
                return []  # 空列表返回空（允许无订单数据场景）
            # 校验列表类型
            if not isinstance(ord_list, list):
                raise TypeError(f"预期订单列表，实际收到: {type(ord_list).__name__}")
            # 批量解析订单
            orders = []
            errors = []
            for idx, ord_dict in enumerate(ord_list):
                try:
                    orders.append(cls.from_single_dict(ord_dict))
                except Exception as e:
                    errors.append(f"第{idx+1}个订单: {str(e)}")

            # 处理部分解析失败
            if errors:
                raise ValueError(f"部分订单解析失败: {'; '.join(errors)}")

            return orders
        except Exception as e:
            raise ValueError(f"解析订单列表失败: {str(e)}") from e

    def __str__(self) -> str:
        """自定义打印格式，便于日志查看"""
        return (f"OrdQryResp(order_id={self.order_id}, symbol={self.symbol}, "
                f"trd_side={self.trd_side.value}, status={self.order_status.value}, "
                f"qty={self.qty}, price={self.price}, deal_qty={self.deal_qty}, "
                f"currency={self.currency.value}, market={self.order_market.value})")

 
# -------------------------- 2. 成交查询请求实体（DealReq）--------------------------
@dataclass
class DealReq:
    """成交查询请求实体"""
    trd_env: TrdEnv                  # 交易环境（必填）
    acc_id: int                      # 账户ID（必填）
    symbol: Optional[str] = None     # 标的代码过滤（可选，格式：HK.00700）
    deal_market: Optional[TrdMarket] = None  # 成交市场过滤（可选）

    def to_dict(self) -> Dict:
        """转换为请求字典（含参数校验+枚举值处理）"""
        # 1. 校验标的代码格式（规则：前缀.代码，如HK.00700）
        if self.symbol and not self._is_valid_symbol(self.symbol):
            raise ValueError(f"标的代码格式错误，示例：HK.00700，US.TSLA，当前：{self.symbol}")

        # 2. 构造基础请求字典（必填字段）
        req_dict = {
            "trd_env": self.trd_env.value,
            "acc_id": self.acc_id
        }

        # 3. 处理可选字段（仅当值不为None时添加）
        if self.symbol:
            req_dict["symbol"] = self.symbol
        if self.deal_market:
            req_dict["deal_market"] = self.deal_market.value

        return req_dict

    @staticmethod
    def _is_valid_symbol(symbol: str) -> bool:
        """校验标的代码格式（^[a-zA-Z]+\\.[a-zA-Z0-9 _\\.]+$）"""
        pattern = r"^[a-zA-Z]+\.[a-zA-Z0-9 _\.]+$"
        return re.match(pattern, symbol) is not None


# -------------------------- 3. 成交查询响应实体（DealResp）--------------------------
@dataclass
class DealResp:
    """成交查询响应实体"""
    trd_side: TrdSide              # 交易方向
    deal_id: str                   # 成交号（唯一标识）
    order_id: str                  # 关联订单号
    symbol: str                    # 股票代码（如HK.00700）
    stock_name: Optional[str]      # 股票名称（可选）
    deal_market: TrdMarket         # 成交所属市场
    qty: Decimal                   # 成交数量
    price: Decimal                 # 成交价格
    create_time: str               # 成交时间（格式：yyyy-MM-dd HH:mm:ss）
    status: DealStatus             # 成交状态（正常/已取消）
    counter_broker_id: Optional[str] = None  # 对手经纪号（可选）


    @classmethod
    def from_single_dict(cls, deal_dict: Dict) -> "DealResp":
        """解析单个成交记录字典"""
        try:
            # 1. 必选字段校验
            required_fields = [
                "trd_side", "deal_id", "order_id", "symbol", 
                "deal_market", "qty", "price", "create_time", "status"
            ]
            for field in required_fields:
                if field not in deal_dict:
                    raise KeyError(f"缺少成交必选字段: {field}")

            # 2. 枚举值转换（兼容接口返回的大小写，处理无效值）
            def parse_enum(enum_cls, value, field_name: str) -> Enum:
                try:
                    return enum_cls(value.upper() if isinstance(value, str) else value)
                except ValueError:
                    raise ValueError(f"成交{deal_dict['deal_id']}的{field_name}枚举值无效: {value}")

            trd_side = parse_enum(TrdSide, deal_dict["trd_side"], "trd_side")
            deal_market = parse_enum(TrdMarket, deal_dict["deal_market"], "deal_market")
            status = parse_enum(DealStatus, deal_dict["status"], "status")

            # 3. Decimal类型转换（避免浮点误差，支持字符串/数字类型的返回值）
            def to_decimal(value, field_name: str) -> Decimal:
                try:
                    return Decimal(str(value))
                except Exception as e:
                    raise ValueError(f"成交{deal_dict['deal_id']}的{field_name}值无效: {value}，错误: {str(e)}")

            qty = to_decimal(deal_dict["qty"], "qty")
            price = to_decimal(deal_dict["price"], "price")

            # 4. 构造响应实体（处理可选字段）
            return cls(
                trd_side=trd_side,
                deal_id=deal_dict["deal_id"],
                order_id=deal_dict["order_id"],
                symbol=deal_dict["symbol"],
                stock_name=deal_dict.get("stock_name"),  # 可选字段
                deal_market=deal_market,
                qty=qty,
                price=price,
                create_time=deal_dict["create_time"],
                counter_broker_id=deal_dict.get("counter_broker_id"),  # 可选字段
                status=status
            )
        except Exception as e:
            deal_id = deal_dict.get("deal_id", "未知成交")
            raise ValueError(f"解析成交{deal_id}失败: {str(e)}") from e

    @classmethod
    def from_list_resp(cls, deal_list: List[Dict]) -> List["DealResp"]:
        """解析成交列表响应（适配接口返回的data为列表）"""
        try:
            # 校验列表类型
            if not deal_list:
                return []  # 空列表返回空（允许无成交数据场景）
            if not isinstance(deal_list, list):
                raise TypeError(f"预期成交列表，实际收到: {type(deal_list).__name__}")

            # 批量解析成交记录
            deals = []
            errors = []
            for idx, deal_dict in enumerate(deal_list):
                try:
                    deals.append(cls.from_single_dict(deal_dict))
                except Exception as e:
                    errors.append(f"第{idx+1}条成交记录: {str(e)}")

            # 处理部分解析失败
            if errors:
                raise ValueError(f"部分成交记录解析失败: {'; '.join(errors)}")

            return deals
        except Exception as e:
            raise ValueError(f"解析成交列表失败: {str(e)}") from e

    def __str__(self) -> str:
        """自定义打印格式，便于日志查看"""
        return (f"DealResp(deal_id={self.deal_id}, order_id={self.order_id}, "
                f"symbol={self.symbol}, trd_side={self.trd_side.value}, "
                f"qty={self.qty}, price={self.price}, status={self.status.value}, "
                f"time={self.create_time}, market={self.deal_market.value})")   
    


# -------------------------- 2. 费用查询请求实体（FareReq）--------------------------
@dataclass
class FareReq:
    """费用查询请求实体"""
    trd_env: TrdEnv              # 交易环境（必填）
    acc_id: int                  # 账户ID（必填）
    order_id_list: List[str]     # 订单号列表（必填，至少包含一个订单号）

    def to_dict(self) -> Dict:
        """转换为请求字典（含参数校验）"""
        # 校验订单号列表非空
        if not isinstance(self.order_id_list, list) or len(self.order_id_list) == 0:
            raise ValueError("订单号列表不能为空")
        # 校验订单号格式（简单判断非空字符串）
        for idx, order_id in enumerate(self.order_id_list):
            if not isinstance(order_id, str) or not order_id.strip():
                raise ValueError(f"第{idx+1}个订单号无效（不能为空）")

        return {
            "order_id_list": self.order_id_list,
            "trd_env": self.trd_env.value,
            "acc_id": self.acc_id
        }


# -------------------------- 3. 费用查询响应实体（FareResp）--------------------------
@dataclass
class FareResp:
    """费用查询响应实体"""
    order_id: str                # 订单号
    fee_amount: Decimal          # 总费用
    fee_details: List[str]       # 收费明细（格式：[('收费项1', 金额), ...]）

    @classmethod
    def from_single_dict(cls, fare_dict: Dict) -> "FareResp":
        """解析单个订单的费用字典"""
        try:
            # 必选字段校验
            required_fields = ["order_id", "fee_amount", "fee_details"]
            for field in required_fields:
                if field not in fare_dict:
                    raise KeyError(f"缺少费用必选字段: {field}")

            # 校验明细格式（必须是列表）
            if not isinstance(fare_dict["fee_details"], list):
                raise TypeError(f"订单{fare_dict['order_id']}的收费明细必须是列表，实际为{type(fare_dict['fee_details'])}")

            # 转换总费用为Decimal（处理字符串/数字类型）
            fee_amount = Decimal(str(fare_dict["fee_amount"]))

            return cls(
                order_id=fare_dict["order_id"],
                fee_amount=fee_amount,
                fee_details=fare_dict["fee_details"]  # 直接保留列表格式
            )
        except Exception as e:
            order_id = fare_dict.get("order_id", "未知订单")
            raise ValueError(f"解析订单{order_id}的费用信息失败: {str(e)}") from e

    @classmethod
    def from_list_resp(cls, fare_list: List[Dict]) -> List["FareResp"]:
        """解析费用列表响应"""
        try:
            if not fare_list:
                return []  # 空列表返回空（允许无费用数据场景）
            if not isinstance(fare_list, list):
                raise TypeError(f"预期费用列表，实际收到: {type(fare_list).__name__}")

            # 批量解析费用信息
            fares = []
            errors = []
            for idx, fare_dict in enumerate(fare_list):
                try:
                    fares.append(cls.from_single_dict(fare_dict))
                except Exception as e:
                    errors.append(f"第{idx+1}条费用记录: {str(e)}")

            if errors:
                raise ValueError(f"部分费用记录解析失败: {'; '.join(errors)}")

            return fares
        except Exception as e:
            raise ValueError(f"解析费用列表失败: {str(e)}") from e

    def __str__(self) -> str:
        """自定义打印格式，便于日志查看"""
        details_str = "\n  ".join(self.fee_details)
        return (f"FareResp(order_id={self.order_id}, 总费用={self.fee_amount}, \n"
                f"  收费明细: \n  {details_str})")    


# -------------------------- 2. 持仓查询请求实体（PosReq）--------------------------
@dataclass
class PosReq:
    """持仓查询请求实体"""
    trd_env: TrdEnv                # 交易环境（必填）
    acc_id: int                    # 账户ID（必填）
    symbol: Optional[str] = None   # 标的证券（可选，格式：HK.00700）
    position_market: Optional[TrdMarket] = None  # 市场（可选）

    def to_dict(self) -> Dict:
        """转换为请求字典（处理枚举+格式校验）"""
        # 校验标的代码格式（规则：前缀+点+代码，如HK.00700）
        if self.symbol and not self._is_valid_symbol(self.symbol):
            raise ValueError(f"标的代码格式错误，示例：HK.00700，US.TSLA，当前：{self.symbol}")

        req_dict = {
            "trd_env": self.trd_env.value,
            "acc_id": self.acc_id
        }
        # 可选字段：仅当值不为None时添加
        if self.symbol:
            req_dict["symbol"] = self.symbol
        if self.position_market:
            req_dict["position_market"] = self.position_market.value

        return req_dict

    @staticmethod
    def _is_valid_symbol(symbol: str) -> bool:
        """校验标的代码格式"""
        import re
        pattern = r"^[a-zA-Z]+\.[a-zA-Z0-9 _\.]+$"
        return re.match(pattern, symbol) is not None


# -------------------------- 3. 持仓查询响应实体（PosResp）--------------------------
@dataclass
class PosResp:
    """持仓查询响应实体"""
    position_side: PositionSide    # 持仓方向
    symbol: str                    # 股票代码
    stock_name: Optional[str]      # 股票名称（可选）
    position_market: TrdMarket     # 持仓所属市场
    qty: Decimal                   # 持有数量
    can_sell_qty: Decimal          # 可卖数量
    currency: Currency             # 交易货币
    nominal_price: Decimal         # 市价
    cost_price: Decimal            # 摊薄成本价
    market_val: Decimal            # 市值
    pl_val: Optional[Decimal] = None          # 盈亏金额（可选）
    today_pl_val: Optional[Decimal] = None    # 今日盈亏金额（可选）
    unrealized_pl: Optional[Decimal] = None   # 未实现盈亏（可选）
    realized_pl: Optional[Decimal] = None     # 已实现盈亏（可选）

    @classmethod
    def from_single_dict(cls, pos_dict: Dict) -> "PosResp":
        """解析单个持仓字典"""
        try:
            # 必选字段校验
            required_fields = [
                "position_side", "symbol", "position_market", 
                "qty", "can_sell_qty", "currency", 
                "nominal_price", "cost_price", "market_val"
            ]
            for field in required_fields:
                if field not in pos_dict:
                    raise KeyError(f"缺少持仓必选字段: {field}")

            # 枚举值转换（处理可能的大小写问题，兼容接口返回）
            def parse_enum(enum_cls, value):
                try:
                    return enum_cls(value.upper() if isinstance(value, str) else value)
                except ValueError:
                    raise ValueError(f"{enum_cls.__name__} 枚举值无效: {value}")

            position_side = parse_enum(PositionSide, pos_dict["position_side"])
            position_market = parse_enum(TrdMarket, pos_dict["position_market"])
            currency = parse_enum(Currency, pos_dict["currency"])

            # Decimal类型转换（避免浮点误差，处理字符串/数字类型的返回值）
            def to_decimal(value) -> Decimal:
                return Decimal(str(value)) if value is not None else None

            # 构造实体
            return cls(
                position_side=position_side,
                symbol=pos_dict["symbol"],
                stock_name=pos_dict.get("stock_name"),  # 可选字段
                position_market=position_market,
                qty=to_decimal(pos_dict["qty"]),
                can_sell_qty=to_decimal(pos_dict["can_sell_qty"]),
                currency=currency,
                nominal_price=to_decimal(pos_dict["nominal_price"]),
                cost_price=to_decimal(pos_dict["cost_price"]),
                market_val=to_decimal(pos_dict["market_val"]),
                pl_val=to_decimal(pos_dict.get("pl_val")),  # 可选字段
                today_pl_val=to_decimal(pos_dict.get("today_pl_val")),
                unrealized_pl=to_decimal(pos_dict.get("unrealized_pl")),
                realized_pl=to_decimal(pos_dict.get("realized_pl"))
            )
        except Exception as e:
            symbol = pos_dict.get("symbol", "未知标的")
            raise ValueError(f"解析持仓 {symbol} 失败: {str(e)}") from e

    @classmethod
    def from_list_resp(cls, pos_list: List[Dict]) -> List["PosResp"]:
        """解析持仓列表响应（适配接口返回的data为列表）"""
        try:
            if not pos_list:
                return []  # 空列表返回空（不抛异常，允许无持仓场景）
            # 校验列表类型
            if not isinstance(pos_list, list):
                raise TypeError(f"预期持仓列表，实际收到: {type(pos_list).__name__}")

            # 批量解析持仓
            positions = []
            errors = []
            for idx, pos_dict in enumerate(pos_list):
                try:
                    positions.append(cls.from_single_dict(pos_dict))
                except Exception as e:
                    errors.append(f"第{idx+1}个持仓: {str(e)}")

            # 处理部分解析失败
            if errors:
                raise ValueError(f"部分持仓解析失败: {'; '.join(errors)}")

            return positions
        except Exception as e:
            raise ValueError(f"解析持仓列表失败: {str(e)}") from e

    def __str__(self) -> str:
        """自定义打印格式，输出所有字段，便于日志查看"""
        return (
            f"PosResp("
            f"position_side={self.position_side.value}, "
            f"symbol={self.symbol}, "
            f"stock_name={self.stock_name}, "
            f"position_market={self.position_market.value}, "
            f"qty={self.qty}, "
            f"can_sell_qty={self.can_sell_qty}, "
            f"currency={self.currency.value}, "
            f"nominal_price={self.nominal_price}, "
            f"cost_price={self.cost_price}, "
            f"market_val={self.market_val}, "
            f"pl_val={self.pl_val}, "
            f"today_pl_val={self.today_pl_val}, "
            f"unrealized_pl={self.unrealized_pl}, "
            f"realized_pl={self.realized_pl}"
            f")"
        )


# -------------------------- 2. 资金查询请求实体（FundQryReq）--------------------------
@dataclass
class FundQryReq:
    """资金查询请求实体"""
    trd_env: TrdEnv                # 交易环境（必填）
    acc_id: int                    # 账户ID（必填）
    currency: Optional[Currency] = None  # 计价货币（可选，不填则查所有货币）

    def to_dict(self) -> Dict:
        """转换为请求字典（含参数校验）"""
        # 校验必填字段
        if not self.trd_env:
            raise ValueError("交易环境（trd_env）不能为空")
        if self.acc_id <= 0:
            raise ValueError("账户ID（acc_id）必须为正整数")

        # 构造请求字典
        req_dict = {
            "trd_env": self.trd_env.value,
            "acc_id": self.acc_id
        }
        # 可选字段：仅当货币不为None时添加
        if self.currency:
            req_dict["currency"] = self.currency.value

        return req_dict


# -------------------------- 3. 资金查询响应实体（FundQryResp）--------------------------
@dataclass
class FundQryResp:
    """资金查询响应实体"""
    # 核心购买力字段
    power: Decimal                  # 最大购买力
    max_power_short: Decimal        # 卖空购买力
    net_cash_power: Decimal         # 现金购买力
    # 资产市值字段
    securities_assets: Decimal      # 证券资产净值
    market_val: Decimal             # 证券市值
    pending_asset: Decimal          # 在途资产
    # 资金冻结与提现字段
    frozen_cash: Decimal            # 冻结资金
    avl_withdrawal_cash: Decimal    # 现金可提
    max_withdrawal: Decimal        # 最大可提
    # 保证金字段
    initial_margin: Decimal         # 初始保证金
    maintenance_margin: Decimal     # 维持保证金
    # 分货币现金与可提（港元/美元/人民币）
    hk_cash: Decimal                # 港元现金
    hk_avl_withdrawal_cash: Decimal # 港元可提
    us_cash: Decimal                # 美元现金
    us_avl_withdrawal_cash: Decimal # 美元可提
    cn_cash: Decimal                # 人民币现金
    cn_avl_withdrawal_cash: Decimal # 人民币可提
    # 计价货币
    currency: Currency              # 计价货币

    @classmethod
    def from_dict(cls, fund_dict: Dict) -> "FundQryResp":
        """从响应字典解析资金实体"""
        try:
            # 1. 必选字段校验
            required_fields = [
                "power", "max_power_short", "net_cash_power", 
                "securities_assets", "market_val", "pending_asset",
                "frozen_cash", "avl_withdrawal_cash", "max_withdrawal",
                "initial_margin", "maintenance_margin",
                "hk_cash", "hk_avl_withdrawal_cash",
                "us_cash", "us_avl_withdrawal_cash",
                "cn_cash", "cn_avl_withdrawal_cash", "currency"
            ]
            for field in required_fields:
                if field not in fund_dict:
                    raise KeyError(f"缺少资金必选字段: {field}")

            # 2. Decimal类型转换（统一处理字符串/数字，避免浮点误差）
            def to_decimal(value, field_name: str) -> Decimal:
                try:
                    # 处理可能的None或空字符串（默认转为0）
                    if value in (None, "", "null"):
                        return Decimal("0")
                    return Decimal(str(value))
                except Exception as e:
                    raise ValueError(f"资金字段{field_name}值无效: {value}，错误: {str(e)}")

            # 3. 枚举转换（货币类型）
            try:
                currency = Currency(fund_dict["currency"].upper() if isinstance(fund_dict["currency"], str) else fund_dict["currency"])
            except ValueError:
                raise ValueError(f"货币枚举值无效: {fund_dict['currency']}")

            # 4. 构造资金实体
            return cls(
                # 核心购买力
                power=to_decimal(fund_dict["power"], "power"),
                max_power_short=to_decimal(fund_dict["max_power_short"], "max_power_short"),
                net_cash_power=to_decimal(fund_dict["net_cash_power"], "net_cash_power"),
                # 资产市值
                securities_assets=to_decimal(fund_dict["securities_assets"], "securities_assets"),
                market_val=to_decimal(fund_dict["market_val"], "market_val"),
                pending_asset=to_decimal(fund_dict["pending_asset"], "pending_asset"),
                # 资金冻结与提现
                frozen_cash=to_decimal(fund_dict["frozen_cash"], "frozen_cash"),
                avl_withdrawal_cash=to_decimal(fund_dict["avl_withdrawal_cash"], "avl_withdrawal_cash"),
                max_withdrawal=to_decimal(fund_dict["max_withdrawal"], "max_withdrawal"),
                # 保证金
                initial_margin=to_decimal(fund_dict["initial_margin"], "initial_margin"),
                maintenance_margin=to_decimal(fund_dict["maintenance_margin"], "maintenance_margin"),
                # 港元字段
                hk_cash=to_decimal(fund_dict["hk_cash"], "hk_cash"),
                hk_avl_withdrawal_cash=to_decimal(fund_dict["hk_avl_withdrawal_cash"], "hk_avl_withdrawal_cash"),
                # 美元字段
                us_cash=to_decimal(fund_dict["us_cash"], "us_cash"),
                us_avl_withdrawal_cash=to_decimal(fund_dict["us_avl_withdrawal_cash"], "us_avl_withdrawal_cash"),
                # 人民币字段
                cn_cash=to_decimal(fund_dict["cn_cash"], "cn_cash"),
                cn_avl_withdrawal_cash=to_decimal(fund_dict["cn_avl_withdrawal_cash"], "cn_avl_withdrawal_cash"),
                # 计价货币
                currency=currency
            )
        except Exception as e:
            raise ValueError(f"解析资金信息失败: {str(e)}") from e

    def __str__(self) -> str:
        """自定义打印格式，突出核心资金信息"""
        return (
            f"FundQryResp(计价货币={self.currency.value}\n"
            f"  核心购买力：最大购买力={self.power}，现金购买力={self.net_cash_power}\n"
            f"  资产情况：证券净值={self.securities_assets}，证券市值={self.market_val}\n"
            f"  提现能力：现金可提={self.avl_withdrawal_cash}，最大可提={self.max_withdrawal}\n"
            f"  分货币现金：港元={self.hk_cash}，美元={self.us_cash}，人民币={self.cn_cash})"
        )
    
    @classmethod
    def from_list_resp(cls, fund_list: List[Dict]) -> List["FundQryResp"]:
        """解析资金列表响应（适配接口返回的data为列表）"""
        try:
            if not fund_list:
                return []  # 空列表返回空（不抛异常，允许无资金场景）
            # 校验列表类型
            if not isinstance(fund_list, list):
                raise TypeError(f"预期资金列表，实际收到: {type(fund_list).__name__}")

            # 批量解析资金
            positions = []
            errors = []
            for idx, fund_dict in enumerate(fund_list):
                try:
                    positions.append(cls.from_dict(fund_dict))
                except Exception as e:
                    errors.append(f"第{idx+1}资金信息: {str(e)}")

            # 处理部分解析失败
            if errors:
                raise ValueError(f"部分资金信息解析失败: {'; '.join(errors)}")

            return positions
        except Exception as e:
            raise ValueError(f"解析资金信息列表失败: {str(e)}") from e
        


# -------------------------- 2. 可买可卖查询请求实体（AccEnTrdInfoReq）--------------------------
@dataclass
class AccEnTrdInfoReq:
    """可买可卖查询请求实体"""
    acc_id: int                      # 账户ID（必填）
    symbol: str                      # 证券代码（必填，格式：HK.00700）
    trd_env: TrdEnv                  # 交易环境（必填）
    order_type: Optional[OrderType] = None  # 订单类型（可选）
    price: Optional[Decimal] = None   # 报价（可选）
    session: Optional[Session] = None # 美股交易时段（可选）

    def to_dict(self) -> Dict:
        """转换为请求字典（含参数校验）"""
        # 1. 校验必填字段
        if self.acc_id <= 0:
            raise ValueError("账户ID（acc_id）必须为正整数")
        if not self.symbol:
            raise ValueError("证券代码（symbol）不能为空")
        if not self.trd_env:
            raise ValueError("交易环境（trd_env）不能为空")

        # 2. 校验证券代码格式（
        if not self._is_valid_symbol(self.symbol):
            raise ValueError(f"标的代码格式错误，示例：HK.00700，US.TSLA，当前：{self.symbol}")

        # 3. 构造请求字典（处理枚举和Decimal）
        req_dict = {
            "acc_id": self.acc_id,
            "symbol": self.symbol,
            "trd_env": self.trd_env.value
        }

        # 4. 处理可选字段
        if self.order_type:
            req_dict["order_type"] = self.order_type.value
        if self.price is not None:  # 允许价格为0（如市价单）
            req_dict["price"] = str(self.price)
        if self.session:
            req_dict["session"] = self.session.value

        return req_dict

    @staticmethod
    def _is_valid_symbol(symbol: str) -> bool:
        """校验证券代码格式（regexp: ^[a-zA-Z]+\\.[a-zA-Z0-9 _\\.]+$）"""
        pattern = r"^[a-zA-Z]+\.[a-zA-Z0-9 _\.]+$"
        return re.match(pattern, symbol) is not None


# -------------------------- 3. 可买可卖查询响应实体（AccEnTrdInfoResp）--------------------------
@dataclass
class AccEnTrdInfoResp:
    """可买可卖查询响应实体"""
    max_cash_buy: Decimal               # 现金可买数量
    max_cash_and_margin_buy: Decimal    # 最大可买数量（现金+融资）
    max_position_sell: Decimal          # 持仓可卖数量
    max_sell_short: Decimal             # 可卖空数量
    max_buy_back: Decimal               # 平仓需买入数量
    session: Optional[Session] = None   # 交易时段（仅美股）

    @classmethod
    def from_dict(cls, resp_dict: Dict) -> "AccEnTrdInfoResp":
        """从响应字典解析实体（处理Decimal和枚举）"""
        try:
            # 1. 必选字段校验
            required_fields = [
                "max_cash_buy", "max_cash_and_margin_buy", 
                "max_position_sell", "max_sell_short", "max_buy_back"
            ]
            for field in required_fields:
                if field not in resp_dict:
                    raise KeyError(f"缺少可买可卖必选字段: {field}")

            # 2. Decimal转换（支持字符串/数字，默认0）
            def to_decimal(value, field_name: str) -> Decimal:
                try:
                    if value in (None, "", "null"):
                        return Decimal("0")
                    return Decimal(str(value))
                except Exception as e:
                    raise ValueError(f"字段{field_name}值无效: {value}，错误: {str(e)}")

            # 3. 枚举转换（交易时段）
            session = None
            if "session" in resp_dict and resp_dict["session"]:
                try:
                    session = Session(resp_dict["session"].upper())
                except ValueError:
                    raise ValueError(f"交易时段枚举值无效: {resp_dict['session']}")

            # 4. 构造实体
            return cls(
                max_cash_buy=to_decimal(resp_dict["max_cash_buy"], "max_cash_buy"),
                max_cash_and_margin_buy=to_decimal(resp_dict["max_cash_and_margin_buy"], "max_cash_and_margin_buy"),
                max_position_sell=to_decimal(resp_dict["max_position_sell"], "max_position_sell"),
                max_sell_short=to_decimal(resp_dict["max_sell_short"], "max_sell_short"),
                max_buy_back=to_decimal(resp_dict["max_buy_back"], "max_buy_back"),
                session=session
            )
        except Exception as e:
            raise ValueError(f"解析可买可卖信息失败: {str(e)}") from e
        
    @classmethod
    def from_list_resp(cls, fund_list: List[Dict]) -> List["AccEnTrdInfoResp"]:
        """解析可买可卖列表响应（适配接口返回的data为列表）"""
        try:
            if not fund_list:
                return []  # 空列表返回空（不抛异常，允许无可买可卖场景）
            # 校验列表类型
            if not isinstance(fund_list, list):
                raise TypeError(f"预期可买可卖列表，实际收到: {type(fund_list).__name__}")

            # 批量解析可买可卖
            positions = []
            errors = []
            for idx, fund_dict in enumerate(fund_list):
                try:
                    positions.append(cls.from_dict(fund_dict))
                except Exception as e:
                    errors.append(f"第{idx+1}可买可卖信息: {str(e)}")

            # 处理部分解析失败
            if errors:
                raise ValueError(f"部分可买可卖信息解析失败: {'; '.join(errors)}")

            return positions
        except Exception as e:
            raise ValueError(f"解析可买可卖信息列表失败: {str(e)}") from e

    def __str__(self) -> str:
        """自定义打印格式，突出核心可交易数量"""
        return (
            f"AccEnTrdInfoResp(symbol相关可交易信息\n"
            f"  可买：现金可买={self.max_cash_buy}，最大可买（含融资）={self.max_cash_and_margin_buy}\n"
            f"  可卖：持仓可卖={self.max_position_sell}，可卖空={self.max_sell_short}\n"
            f"  平仓：需买入={self.max_buy_back}，交易时段={self.session.value if self.session else '无'})"
        )        