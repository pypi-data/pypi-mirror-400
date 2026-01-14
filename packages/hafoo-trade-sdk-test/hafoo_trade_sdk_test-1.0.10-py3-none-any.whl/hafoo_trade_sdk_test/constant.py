from enum import Enum
# -------------------------- 1. 枚举类定义（复用并补充）--------------------------
class TrdSide(Enum):
    """交易方向枚举"""
    BUY = "BUY"       # 买入
    SELL = "SELL"      # 卖出
    BUY_BACK = "BUY_BACK"  # 补回
    SELL_SHORT = "SELL_SHORT" # 卖空    
class OrderType(Enum):
    """订单类型枚举"""
    LIMIT = "LIMIT"
    """限价单：按指定价格或更优价格成交，未成交部分可在有效期内等待"""
    AUCTION = "AUCTION"
    """竞价市价单：集合竞价阶段的市价订单，优先保证成交，价格由竞价结果决定"""
    AUCTION_LIMIT = "AUCTION_LIMIT"
    """竞价限价单：集合竞价阶段的限价订单，价格不优于限价时成交"""
    ELO = "ELO"
    """增强限价单：可在指定价格或更优价格立即成交，未成交部分转为限价单"""
    SPECIAL_LIMIT = "SPECIAL_LIMIT"
    """特别限价单：仅在指定价格或更优价格成交，未成交部分自动取消"""
class OrderStatus(Enum):
    """订单状态枚举"""
    WAITING_SUBMIT = "WAITING_SUBMIT"
    """等待提交"""
    SUBMITTED = "SUBMITTED"
    """已提交，等待成交"""
    FILLED_PART = "FILLED_PART"
    """部分成交"""
    FILLED = "FILLED"
    """全部已成交"""
    CANCELLED_PART = "CANCELLED_PART"
    """部分成交，剩余部分已撤单"""
    CANCELLED_ALL = "CANCELLED_ALL"
    """全部已撤单，无成交"""
    FAILED = "FAILED"
    """下单失败，服务拒绝"""
    REVIEW_FAIL = "REVIEW_FAIL"
    """审核失败"""
class TimeInForce(Enum):
    """订单有效时间枚举"""
    DAY = "DAY"        # 当日有效
class Session(Enum):
    """交易时段枚举（美股专用）"""
    RTH = "RTH"        # 常规交易时段
    ALL = "ALL"     # 盘前、盘中、盘后交易
    OVERNIGHT = "OVERNIGHT"   # 夜盘交易
class TrdEnv(Enum):
    """交易环境枚举"""
    PROD = "PROD"  # 生产环境
    TEST = "TEST"  # 测试环境

class ModifyOrderOp(Enum):
    """改单操作类型枚举"""
    MODIFY = "MODIFY"  # 修改订单
    CANCEL = "CANCEL"  # 撤单

class TrdMarket(Enum):
    """市场枚举"""
    HK = "HK"          # 香港市场
    US = "US"          # 美国市场
    HKCC = "HKCC"      # 香港A股通市场
    MUTUAL = "MUTUAL"  # 基金
    VC = "VC"          # 虚拟货币市场

class Currency(Enum):
    """货币枚举"""
    HKD = "HKD"  # 港元
    USD = "USD"  # 美元
    CNY = "CNY"  # 在岸人民币

class Session(Enum):
    """交易时段枚举（美股专用）"""
    RTH = "RTH"        # 常规交易时段
    ALL = "ALL"     # 盘前、盘中、盘后交易
    OVERNIGHT = "OVERNIGHT"   # 夜盘交易    


class PositionSide(Enum):
    """持仓方向枚举"""
    NONE = "NONE"    # 未知方向
    LONG = "LONG"    # 多仓
    SHORT = "SHORT"  # 空仓

class DealStatus(Enum):
    """成交状态枚举"""
    OK = "OK"                # 正常
    CANCELLED = "CANCELLED"  # 成交被取消
