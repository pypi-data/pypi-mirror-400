from order_client import place_order, replace_order, qry_ord_list, qry_deal_list, qry_fare, qry_position, qry_fund_info, qry_acc_trad_info 
from decimal import Decimal
from constant import TrdSide, OrderType, TimeInForce, Session, ModifyOrderOp, TrdEnv, TrdMarket, Currency 
from model import OrderReplaceReq, OrdQryReq, DealReq, PosReq, FareReq, FundQryReq, AccEnTrdInfoReq
import time

# 延时函数
def high_precision_sleep(seconds):
    start = time.perf_counter()
    while time.perf_counter() - start < seconds:
        pass  # 空循环等待

# -------------------------- 5. 使用示例--------------------------
if __name__ == "__main__":

    full_url = "http://10.10.181.166:8098/quanta/trd/placeOrder"
    # full_url = "http://127.0.0.1:8098/quanta/trd/placeOrder"
    # -------------------------- 配置参数（实际项目中需从配置文件/环境变量读取）--------------------------
    # 1. 接口认证配置
    API_KEY = "hf_f3b9aa5cd5154a94968b54fd2830c577"  # 实际APIKey
    # PEM格式私钥
    PRIVATE_KEY_PEM = """
    MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDmEDJT0R11dNx3QmGIvOz3Qzpv5LvnWqpTke12IL+Lr4Mlw/lde28t7JBiA01itrFzDuUKGh0jsQ9AK506F4aUNYtT0fRzZJZ5rGT6cf4/WJXq6GxH4a4cV7hMb+zS6KXqGS07hBskbE2sFMhylKyXXrA2sGSloiQVHzNY00y3W8Gr7VaOWYv3FI+HrzndUuzC1LCxhjjUM8IbYcW79R7FJJLQyQq55nYzoyn7RFTUh8LOPHtbCCJfqxIUz+8KQmp7QMFzxlcaPJGHCdRHRM4aIBPkVzmh1RPSkrBQzjYeqoBMLwKFX/qGp7z5DyoRKm8mYos7iQ2xYYl2If86S7O7AgMBAAECggEBAJNUUfZtFzFtyfWxk+ZOHm5mJhkb4N1SqXrlG62nYSLiHdlke9/KuTMuqHOr67XIizDEnBZxDLIbpEmS5JgcErn85CGkdagkBV0b8nqT357PawpJF3ac5rQN1N9WWdHi3MVipB3WBs+3b7JAiPEflrtFDxGmun17rSG9nlNG1X0hVaccW0WELXwJZufXOE2G1dule6arpZkPrU4jv3vNSfYy61rsw2YwyU8JhijsBENfYUuXjkyAgp0S5m8gSrWsWE4lAXJ0nh4fAVR4Uwt/njubI9G1ncUU1KQzTZzlmqCdbIG7WKO7vTpMbwL9e6bkaqCPbEI5MlLVxtWMgQW3g3kCgYEA+FKc1r9urZ7BmUZpdAb9sB+LlsTjO1YHPrhpWgT42GRqiLtmXG7TrFv3cUUfvGp0LUddJ0fnBODKXftJQ9AovQ7nR8OpCSfQA5HXD5dWj2qwwy5PnOoYbZNK6vYJIPvzghiy0B8xYIBN7EmCYUQK6xtGOAwAp/gZF1caRkB9yAUCgYEA7S0RHuDJddMczwzq70GKiLeKa+wXjGrr4l3lJEuxQXI+8wiX9chRd2GTIdy5BOuWnuiN9WNas8DIRV1n1340HSSiClQJ2uIQVG2iOcj3TftpMdQ4hegS3WUObzsqcFG8xlhHmLc4i2KcidD95nAHSNI30tyLBeP7BhfDaHhXGL8CgYEA2lnyNVaxIJO3Umq6sV6wVdz3JkTMNlGoHzuSz6gNlGF/1+lI0cBV+noHs57/j/LfYy0cOT0dY4myCD+8pZd1KwDe15ixmy5Z17m2rKv7XjKHaajgMm8ZuchJmR9s2YcSEPRcz2qORXesjTf6IELvgtpBvWi4bvpWPdLGdL2inG0CgYEAzObxcpbLFcL0kaBcW6Vo9OJ0cPaABazd6ywpaakHEz6LSdXzysBsOVIQFeIl6i1KbDEHa6eRVdhIbTzcGJ0MktzyLTAbb4F8kCRDUd7gYPvCDu2Eg5NSsPi8drZL3MuQ5l6gRDyOWkUwbhQjNnE0qeILnl0wsj8awFHJXTkSLesCgYAfn/jL8oim5PP7bbiVDmoravW0CVo3mHCHv1bW3xgXf+C1lckmr3q/F57iZHuAkcJEBnJvy+VkYcH5K3+0SRaoOrvB0WSpy9DVu98zYvhJ699RlBjzjKczbg2qllwbEp4jhMw0KGEznfdF3t23+l1X/Jt5CWvg6v/gqpW9doWD9w==
    """
    # 2. 订单参数配置（示例：买入腾讯控股）
    order_price = Decimal("200")  # 下单价格
    order_qty = Decimal("100")       # 下单数量
    stock_code = "US.AAPL"         # 股票代码
    trade_side = TrdSide.BUY        # 交易方向：买入
    # -------------------------- 调用下单函数--------------------------
    try:
        # 发送下单请求并获取响应
        order_resp = place_order(
            full_url=full_url,
            api_key=API_KEY,
            private_key_pem=PRIVATE_KEY_PEM.strip(),  # 去除私钥前后空格
            price=order_price,
            qty=order_qty,
            symbol=stock_code,
            trd_side=trade_side,
            order_type=OrderType.LIMIT,  # 限价订单
            trd_env="TEST",               # 模拟环境
            acc_id=3000002059,               # 账户ID
            time_in_force=TimeInForce.DAY,  # 当日有效
            session=Session.RTH                # 港股无需交易时段
        )
        # 打印成功结果
        print(order_resp)
    except Exception as e:
        # 捕获所有异常并打印（实际项目中建议用日志框架记录）
        print(f"下单失败: {str(e)}")

    # 间隔1s
    high_precision_sleep(1)

    full_url = "http://10.10.181.166:8098/quanta/trd/replaceOrder"
    # full_url = "http://127.0.0.1:8098/quanta/trd/replaceOrder"
    # 1. 接口认证配置
    API_KEY = "hf_f3b9aa5cd5154a94968b54fd2830c577"  # 实际APIKey
    # PEM格式私钥
    PRIVATE_KEY_PEM = """
    MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDmEDJT0R11dNx3QmGIvOz3Qzpv5LvnWqpTke12IL+Lr4Mlw/lde28t7JBiA01itrFzDuUKGh0jsQ9AK506F4aUNYtT0fRzZJZ5rGT6cf4/WJXq6GxH4a4cV7hMb+zS6KXqGS07hBskbE2sFMhylKyXXrA2sGSloiQVHzNY00y3W8Gr7VaOWYv3FI+HrzndUuzC1LCxhjjUM8IbYcW79R7FJJLQyQq55nYzoyn7RFTUh8LOPHtbCCJfqxIUz+8KQmp7QMFzxlcaPJGHCdRHRM4aIBPkVzmh1RPSkrBQzjYeqoBMLwKFX/qGp7z5DyoRKm8mYos7iQ2xYYl2If86S7O7AgMBAAECggEBAJNUUfZtFzFtyfWxk+ZOHm5mJhkb4N1SqXrlG62nYSLiHdlke9/KuTMuqHOr67XIizDEnBZxDLIbpEmS5JgcErn85CGkdagkBV0b8nqT357PawpJF3ac5rQN1N9WWdHi3MVipB3WBs+3b7JAiPEflrtFDxGmun17rSG9nlNG1X0hVaccW0WELXwJZufXOE2G1dule6arpZkPrU4jv3vNSfYy61rsw2YwyU8JhijsBENfYUuXjkyAgp0S5m8gSrWsWE4lAXJ0nh4fAVR4Uwt/njubI9G1ncUU1KQzTZzlmqCdbIG7WKO7vTpMbwL9e6bkaqCPbEI5MlLVxtWMgQW3g3kCgYEA+FKc1r9urZ7BmUZpdAb9sB+LlsTjO1YHPrhpWgT42GRqiLtmXG7TrFv3cUUfvGp0LUddJ0fnBODKXftJQ9AovQ7nR8OpCSfQA5HXD5dWj2qwwy5PnOoYbZNK6vYJIPvzghiy0B8xYIBN7EmCYUQK6xtGOAwAp/gZF1caRkB9yAUCgYEA7S0RHuDJddMczwzq70GKiLeKa+wXjGrr4l3lJEuxQXI+8wiX9chRd2GTIdy5BOuWnuiN9WNas8DIRV1n1340HSSiClQJ2uIQVG2iOcj3TftpMdQ4hegS3WUObzsqcFG8xlhHmLc4i2KcidD95nAHSNI30tyLBeP7BhfDaHhXGL8CgYEA2lnyNVaxIJO3Umq6sV6wVdz3JkTMNlGoHzuSz6gNlGF/1+lI0cBV+noHs57/j/LfYy0cOT0dY4myCD+8pZd1KwDe15ixmy5Z17m2rKv7XjKHaajgMm8ZuchJmR9s2YcSEPRcz2qORXesjTf6IELvgtpBvWi4bvpWPdLGdL2inG0CgYEAzObxcpbLFcL0kaBcW6Vo9OJ0cPaABazd6ywpaakHEz6LSdXzysBsOVIQFeIl6i1KbDEHa6eRVdhIbTzcGJ0MktzyLTAbb4F8kCRDUd7gYPvCDu2Eg5NSsPi8drZL3MuQ5l6gRDyOWkUwbhQjNnE0qeILnl0wsj8awFHJXTkSLesCgYAfn/jL8oim5PP7bbiVDmoravW0CVo3mHCHv1bW3xgXf+C1lckmr3q/F57iZHuAkcJEBnJvy+VkYcH5K3+0SRaoOrvB0WSpy9DVu98zYvhJ699RlBjzjKczbg2qllwbEp4jhMw0KGEznfdF3t23+l1X/Jt5CWvg6v/gqpW9doWD9w==
    """

    # -------------------------- 1. 撤单示例 --------------------------
    try:
        # 构造撤单请求（操作类型为CANCEL，无需填写qty和price）
        cancel_req = OrderReplaceReq(
            modify_order_op=ModifyOrderOp.CANCEL,
            order_id="20251023.10000085",  # 需撤单的订单号
            trd_env=TrdEnv.TEST,
            acc_id=3000002059,
            qty=Decimal("100"),  # 新的订单数量
            price=Decimal("600")  # 新的订单价格
        )

        # 发送撤单请求
        cancel_resp = replace_order(
            full_url=full_url,
            api_key=API_KEY,
            private_key_pem=PRIVATE_KEY_PEM.strip(),
            replace_req=cancel_req
        )

        print(cancel_resp)
    except Exception as e:
        print(f"撤单失败: {str(e)}")

    # 间隔1s
    high_precision_sleep(1)
    # -------------------------- 2. 改单示例 --------------------------
    try:
        # 构造改单请求（操作类型为MODIFY，需填写新的qty和price）
        modify_req = OrderReplaceReq(
            modify_order_op=ModifyOrderOp.MODIFY,
            order_id="20251022.10000030",  # 需修改的订单号
            trd_env=TrdEnv.TEST,
            acc_id=3000002059,
            qty=Decimal("200"),  # 新的订单数量
            price=Decimal("590")  # 新的订单价格
        )

        # 发送改单请求
        modify_resp = replace_order(
            full_url=full_url,
            api_key=API_KEY,
            private_key_pem=PRIVATE_KEY_PEM.strip(),
            replace_req=modify_req
        )

        print(modify_resp)
    except Exception as e:
        print(f"改单失败: {str(e)}")


    # -------------------------- 订单查询使用示例 --------------------------
    # -------------------------- 步骤3：发送POST请求 --------------------------
    full_url = "http://10.10.181.166:8098/quanta/qry/qryOrdList"  # 订单查询接口URL
    # full_url = "http://127.0.0.1:8098/quanta/qry/qryOrdList"
    # -------------------------- 配置参数（与其他接口共用）--------------------------
    # 1. 接口认证配置
    API_KEY = "hf_f3b9aa5cd5154a94968b54fd2830c577"  # 实际APIKey
    # PEM格式私钥
    PRIVATE_KEY_PEM = """
    MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDmEDJT0R11dNx3QmGIvOz3Qzpv5LvnWqpTke12IL+Lr4Mlw/lde28t7JBiA01itrFzDuUKGh0jsQ9AK506F4aUNYtT0fRzZJZ5rGT6cf4/WJXq6GxH4a4cV7hMb+zS6KXqGS07hBskbE2sFMhylKyXXrA2sGSloiQVHzNY00y3W8Gr7VaOWYv3FI+HrzndUuzC1LCxhjjUM8IbYcW79R7FJJLQyQq55nYzoyn7RFTUh8LOPHtbCCJfqxIUz+8KQmp7QMFzxlcaPJGHCdRHRM4aIBPkVzmh1RPSkrBQzjYeqoBMLwKFX/qGp7z5DyoRKm8mYos7iQ2xYYl2If86S7O7AgMBAAECggEBAJNUUfZtFzFtyfWxk+ZOHm5mJhkb4N1SqXrlG62nYSLiHdlke9/KuTMuqHOr67XIizDEnBZxDLIbpEmS5JgcErn85CGkdagkBV0b8nqT357PawpJF3ac5rQN1N9WWdHi3MVipB3WBs+3b7JAiPEflrtFDxGmun17rSG9nlNG1X0hVaccW0WELXwJZufXOE2G1dule6arpZkPrU4jv3vNSfYy61rsw2YwyU8JhijsBENfYUuXjkyAgp0S5m8gSrWsWE4lAXJ0nh4fAVR4Uwt/njubI9G1ncUU1KQzTZzlmqCdbIG7WKO7vTpMbwL9e6bkaqCPbEI5MlLVxtWMgQW3g3kCgYEA+FKc1r9urZ7BmUZpdAb9sB+LlsTjO1YHPrhpWgT42GRqiLtmXG7TrFv3cUUfvGp0LUddJ0fnBODKXftJQ9AovQ7nR8OpCSfQA5HXD5dWj2qwwy5PnOoYbZNK6vYJIPvzghiy0B8xYIBN7EmCYUQK6xtGOAwAp/gZF1caRkB9yAUCgYEA7S0RHuDJddMczwzq70GKiLeKa+wXjGrr4l3lJEuxQXI+8wiX9chRd2GTIdy5BOuWnuiN9WNas8DIRV1n1340HSSiClQJ2uIQVG2iOcj3TftpMdQ4hegS3WUObzsqcFG8xlhHmLc4i2KcidD95nAHSNI30tyLBeP7BhfDaHhXGL8CgYEA2lnyNVaxIJO3Umq6sV6wVdz3JkTMNlGoHzuSz6gNlGF/1+lI0cBV+noHs57/j/LfYy0cOT0dY4myCD+8pZd1KwDe15ixmy5Z17m2rKv7XjKHaajgMm8ZuchJmR9s2YcSEPRcz2qORXesjTf6IELvgtpBvWi4bvpWPdLGdL2inG0CgYEAzObxcpbLFcL0kaBcW6Vo9OJ0cPaABazd6ywpaakHEz6LSdXzysBsOVIQFeIl6i1KbDEHa6eRVdhIbTzcGJ0MktzyLTAbb4F8kCRDUd7gYPvCDu2Eg5NSsPi8drZL3MuQ5l6gRDyOWkUwbhQjNnE0qeILnl0wsj8awFHJXTkSLesCgYAfn/jL8oim5PP7bbiVDmoravW0CVo3mHCHv1bW3xgXf+C1lckmr3q/F57iZHuAkcJEBnJvy+VkYcH5K3+0SRaoOrvB0WSpy9DVu98zYvhJ699RlBjzjKczbg2qllwbEp4jhMw0KGEznfdF3t23+l1X/Jt5CWvg6v/gqpW9doWD9w==
    """

    # -------------------------- 示例1：查询指定订单号的订单 --------------------------
    try:
        ord_qry_req1 = OrdQryReq(
            trd_env=TrdEnv.TEST,          # 测试环境
            acc_id=3000002059,           # 账户ID
            order_market=TrdMarket.HK
        )
        # 发送查询请求
        ord_list1 = qry_ord_list(full_url, API_KEY, PRIVATE_KEY_PEM.strip(), ord_qry_req1)
        # 打印结果
        print("="*60)
        print(f"查询结果:")
        for ord_resp in ord_list1:
            print(ord_resp)
    except Exception as e:
        print(f"示例1查询失败: {str(e)}")        



# -------------------------- 成交查询使用示例 --------------------------
    full_url = "http://10.10.181.166:8098/quanta/qry/qryDealInfo"  # 成交查询接口URL（与需求一致）
    # full_url = "http://127.0.0.1:8098/quanta/qry/qryDealInfo"  # 成交查询接口URL（与需求一致）
    # -------------------------- 配置参数（实际项目中需从配置文件/环境变量读取）--------------------------
    # 1. 接口认证配置
    API_KEY = "hf_f3b9aa5cd5154a94968b54fd2830c577"  # 实际APIKey
    # PEM格式私钥
    PRIVATE_KEY_PEM = """
    MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDmEDJT0R11dNx3QmGIvOz3Qzpv5LvnWqpTke12IL+Lr4Mlw/lde28t7JBiA01itrFzDuUKGh0jsQ9AK506F4aUNYtT0fRzZJZ5rGT6cf4/WJXq6GxH4a4cV7hMb+zS6KXqGS07hBskbE2sFMhylKyXXrA2sGSloiQVHzNY00y3W8Gr7VaOWYv3FI+HrzndUuzC1LCxhjjUM8IbYcW79R7FJJLQyQq55nYzoyn7RFTUh8LOPHtbCCJfqxIUz+8KQmp7QMFzxlcaPJGHCdRHRM4aIBPkVzmh1RPSkrBQzjYeqoBMLwKFX/qGp7z5DyoRKm8mYos7iQ2xYYl2If86S7O7AgMBAAECggEBAJNUUfZtFzFtyfWxk+ZOHm5mJhkb4N1SqXrlG62nYSLiHdlke9/KuTMuqHOr67XIizDEnBZxDLIbpEmS5JgcErn85CGkdagkBV0b8nqT357PawpJF3ac5rQN1N9WWdHi3MVipB3WBs+3b7JAiPEflrtFDxGmun17rSG9nlNG1X0hVaccW0WELXwJZufXOE2G1dule6arpZkPrU4jv3vNSfYy61rsw2YwyU8JhijsBENfYUuXjkyAgp0S5m8gSrWsWE4lAXJ0nh4fAVR4Uwt/njubI9G1ncUU1KQzTZzlmqCdbIG7WKO7vTpMbwL9e6bkaqCPbEI5MlLVxtWMgQW3g3kCgYEA+FKc1r9urZ7BmUZpdAb9sB+LlsTjO1YHPrhpWgT42GRqiLtmXG7TrFv3cUUfvGp0LUddJ0fnBODKXftJQ9AovQ7nR8OpCSfQA5HXD5dWj2qwwy5PnOoYbZNK6vYJIPvzghiy0B8xYIBN7EmCYUQK6xtGOAwAp/gZF1caRkB9yAUCgYEA7S0RHuDJddMczwzq70GKiLeKa+wXjGrr4l3lJEuxQXI+8wiX9chRd2GTIdy5BOuWnuiN9WNas8DIRV1n1340HSSiClQJ2uIQVG2iOcj3TftpMdQ4hegS3WUObzsqcFG8xlhHmLc4i2KcidD95nAHSNI30tyLBeP7BhfDaHhXGL8CgYEA2lnyNVaxIJO3Umq6sV6wVdz3JkTMNlGoHzuSz6gNlGF/1+lI0cBV+noHs57/j/LfYy0cOT0dY4myCD+8pZd1KwDe15ixmy5Z17m2rKv7XjKHaajgMm8ZuchJmR9s2YcSEPRcz2qORXesjTf6IELvgtpBvWi4bvpWPdLGdL2inG0CgYEAzObxcpbLFcL0kaBcW6Vo9OJ0cPaABazd6ywpaakHEz6LSdXzysBsOVIQFeIl6i1KbDEHa6eRVdhIbTzcGJ0MktzyLTAbb4F8kCRDUd7gYPvCDu2Eg5NSsPi8drZL3MuQ5l6gRDyOWkUwbhQjNnE0qeILnl0wsj8awFHJXTkSLesCgYAfn/jL8oim5PP7bbiVDmoravW0CVo3mHCHv1bW3xgXf+C1lckmr3q/F57iZHuAkcJEBnJvy+VkYcH5K3+0SRaoOrvB0WSpy9DVu98zYvhJ699RlBjzjKczbg2qllwbEp4jhMw0KGEznfdF3t23+l1X/Jt5CWvg6v/gqpW9doWD9w==
    """

    # -------------------------- 示例1：查询指定标的的成交记录（如HK.00700） --------------------------
    try:
        deal_req1 = DealReq(
            trd_env=TrdEnv.TEST,          # 测试环境
            acc_id=3000002059,            # 账户ID
            symbol="HK.00700",            # 腾讯控股（精准过滤标的）
            deal_market=TrdMarket.HK      # 香港市场（过滤市场）
        )
        # 发送查询请求
        deal_list1 = qry_deal_list(full_url, API_KEY, PRIVATE_KEY_PEM.strip(), deal_req1)
        # 打印结果
        print("="*60)
        print(f"查询账户{deal_req1.acc_id}（{deal_req1.trd_env.value}）HK.00700成交记录:")
        if not deal_list1:
            print("未查询到该标的的成交记录")
        else:
            for deal in deal_list1:
                print(deal)
    except Exception as e:
        print(f"示例1查询失败: {str(e)}")

    # -------------------------- 示例2：查询账户所有成交记录（无过滤条件） --------------------------
    try:
        deal_req2 = DealReq(
            trd_env=TrdEnv.TEST,
            acc_id=3000002059
        )
        deal_list2 = qry_deal_list(full_url, API_KEY, PRIVATE_KEY_PEM.strip(), deal_req2)
        print("\n" + "="*60)
        print(f"查询账户{deal_req2.acc_id}（{deal_req2.trd_env.value}）所有成交记录:")
        if not deal_list2:
            print("未查询到任何成交记录")
        else:
            # 按成交时间倒序排列（最新成交在前）
            deal_list2_sorted = sorted(deal_list2, key=lambda x: x.create_time, reverse=True)
            for deal in deal_list2_sorted:
                print(deal)
    except Exception as e:
        print(f"示例2查询失败: {str(e)}")



    # -------------------------- 6. 费用查询使用示例 --------------------------
    # -------------------------- 步骤3：发送POST请求 --------------------------
    full_url = "http://10.10.181.166:8098/quanta/qry/qryFare"  # 费用查询接口URL
    # full_url = "http://127.0.0.1:8098/quanta/qry/qryFare"  # 费用查询接口URL
    # 1. 接口认证配置
    API_KEY = "hf_f3b9aa5cd5154a94968b54fd2830c577"  # 实际APIKey
    # PEM格式私钥
    PRIVATE_KEY_PEM = """
    MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDmEDJT0R11dNx3QmGIvOz3Qzpv5LvnWqpTke12IL+Lr4Mlw/lde28t7JBiA01itrFzDuUKGh0jsQ9AK506F4aUNYtT0fRzZJZ5rGT6cf4/WJXq6GxH4a4cV7hMb+zS6KXqGS07hBskbE2sFMhylKyXXrA2sGSloiQVHzNY00y3W8Gr7VaOWYv3FI+HrzndUuzC1LCxhjjUM8IbYcW79R7FJJLQyQq55nYzoyn7RFTUh8LOPHtbCCJfqxIUz+8KQmp7QMFzxlcaPJGHCdRHRM4aIBPkVzmh1RPSkrBQzjYeqoBMLwKFX/qGp7z5DyoRKm8mYos7iQ2xYYl2If86S7O7AgMBAAECggEBAJNUUfZtFzFtyfWxk+ZOHm5mJhkb4N1SqXrlG62nYSLiHdlke9/KuTMuqHOr67XIizDEnBZxDLIbpEmS5JgcErn85CGkdagkBV0b8nqT357PawpJF3ac5rQN1N9WWdHi3MVipB3WBs+3b7JAiPEflrtFDxGmun17rSG9nlNG1X0hVaccW0WELXwJZufXOE2G1dule6arpZkPrU4jv3vNSfYy61rsw2YwyU8JhijsBENfYUuXjkyAgp0S5m8gSrWsWE4lAXJ0nh4fAVR4Uwt/njubI9G1ncUU1KQzTZzlmqCdbIG7WKO7vTpMbwL9e6bkaqCPbEI5MlLVxtWMgQW3g3kCgYEA+FKc1r9urZ7BmUZpdAb9sB+LlsTjO1YHPrhpWgT42GRqiLtmXG7TrFv3cUUfvGp0LUddJ0fnBODKXftJQ9AovQ7nR8OpCSfQA5HXD5dWj2qwwy5PnOoYbZNK6vYJIPvzghiy0B8xYIBN7EmCYUQK6xtGOAwAp/gZF1caRkB9yAUCgYEA7S0RHuDJddMczwzq70GKiLeKa+wXjGrr4l3lJEuxQXI+8wiX9chRd2GTIdy5BOuWnuiN9WNas8DIRV1n1340HSSiClQJ2uIQVG2iOcj3TftpMdQ4hegS3WUObzsqcFG8xlhHmLc4i2KcidD95nAHSNI30tyLBeP7BhfDaHhXGL8CgYEA2lnyNVaxIJO3Umq6sV6wVdz3JkTMNlGoHzuSz6gNlGF/1+lI0cBV+noHs57/j/LfYy0cOT0dY4myCD+8pZd1KwDe15ixmy5Z17m2rKv7XjKHaajgMm8ZuchJmR9s2YcSEPRcz2qORXesjTf6IELvgtpBvWi4bvpWPdLGdL2inG0CgYEAzObxcpbLFcL0kaBcW6Vo9OJ0cPaABazd6ywpaakHEz6LSdXzysBsOVIQFeIl6i1KbDEHa6eRVdhIbTzcGJ0MktzyLTAbb4F8kCRDUd7gYPvCDu2Eg5NSsPi8drZL3MuQ5l6gRDyOWkUwbhQjNnE0qeILnl0wsj8awFHJXTkSLesCgYAfn/jL8oim5PP7bbiVDmoravW0CVo3mHCHv1bW3xgXf+C1lckmr3q/F57iZHuAkcJEBnJvy+VkYcH5K3+0SRaoOrvB0WSpy9DVu98zYvhJ699RlBjzjKczbg2qllwbEp4jhMw0KGEznfdF3t23+l1X/Jt5CWvg6v/gqpW9doWD9w==
    """

    # -------------------------- 查询示例：查询多个订单的费用 --------------------------
    try:
        # 构造费用查询请求（查询TEST环境下3000888318账户的多个订单费用）
        fare_req = FareReq(
            trd_env=TrdEnv.TEST,
            acc_id=3000002059,
            order_id_list=[
                "20251027.10000051",  # 订单1
                "20251023.10000084"  # 订单1
            ]
        )

        # 发送查询请求
        fare_resp_list = qry_fare(
            full_url=full_url,
            api_key=API_KEY,
            private_key_pem=PRIVATE_KEY_PEM.strip(),
            fare_req=fare_req
        )

        # 打印结果
        print("="*50)
        print(f"账户3000002059（TEST环境）的订单费用查询结果:")
        if not fare_resp_list:
            print("未查询到费用数据")
        else:
            for fare in fare_resp_list:
                print(fare)
                print("-"*50)  # 分隔多个订单的费用信息
    except Exception as e:
        print(f"费用查询失败: {str(e)}")



    # -------------------------- 6. 持仓查询使用示例 --------------------------
    # -------------------------- 步骤3：发送POST请求 --------------------------
    full_url = "http://10.10.181.166:8098/quanta/qry/qryPosition"

    # full_url = "http://127.0.0.1:8098/quanta/qry/qryPosition"  # 持仓查询接口URL
    # 1. 接口认证配置
    API_KEY = "hf_f3b9aa5cd5154a94968b54fd2830c577"  # 实际APIKey
    # PEM格式私钥
    PRIVATE_KEY_PEM = """
    MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDmEDJT0R11dNx3QmGIvOz3Qzpv5LvnWqpTke12IL+Lr4Mlw/lde28t7JBiA01itrFzDuUKGh0jsQ9AK506F4aUNYtT0fRzZJZ5rGT6cf4/WJXq6GxH4a4cV7hMb+zS6KXqGS07hBskbE2sFMhylKyXXrA2sGSloiQVHzNY00y3W8Gr7VaOWYv3FI+HrzndUuzC1LCxhjjUM8IbYcW79R7FJJLQyQq55nYzoyn7RFTUh8LOPHtbCCJfqxIUz+8KQmp7QMFzxlcaPJGHCdRHRM4aIBPkVzmh1RPSkrBQzjYeqoBMLwKFX/qGp7z5DyoRKm8mYos7iQ2xYYl2If86S7O7AgMBAAECggEBAJNUUfZtFzFtyfWxk+ZOHm5mJhkb4N1SqXrlG62nYSLiHdlke9/KuTMuqHOr67XIizDEnBZxDLIbpEmS5JgcErn85CGkdagkBV0b8nqT357PawpJF3ac5rQN1N9WWdHi3MVipB3WBs+3b7JAiPEflrtFDxGmun17rSG9nlNG1X0hVaccW0WELXwJZufXOE2G1dule6arpZkPrU4jv3vNSfYy61rsw2YwyU8JhijsBENfYUuXjkyAgp0S5m8gSrWsWE4lAXJ0nh4fAVR4Uwt/njubI9G1ncUU1KQzTZzlmqCdbIG7WKO7vTpMbwL9e6bkaqCPbEI5MlLVxtWMgQW3g3kCgYEA+FKc1r9urZ7BmUZpdAb9sB+LlsTjO1YHPrhpWgT42GRqiLtmXG7TrFv3cUUfvGp0LUddJ0fnBODKXftJQ9AovQ7nR8OpCSfQA5HXD5dWj2qwwy5PnOoYbZNK6vYJIPvzghiy0B8xYIBN7EmCYUQK6xtGOAwAp/gZF1caRkB9yAUCgYEA7S0RHuDJddMczwzq70GKiLeKa+wXjGrr4l3lJEuxQXI+8wiX9chRd2GTIdy5BOuWnuiN9WNas8DIRV1n1340HSSiClQJ2uIQVG2iOcj3TftpMdQ4hegS3WUObzsqcFG8xlhHmLc4i2KcidD95nAHSNI30tyLBeP7BhfDaHhXGL8CgYEA2lnyNVaxIJO3Umq6sV6wVdz3JkTMNlGoHzuSz6gNlGF/1+lI0cBV+noHs57/j/LfYy0cOT0dY4myCD+8pZd1KwDe15ixmy5Z17m2rKv7XjKHaajgMm8ZuchJmR9s2YcSEPRcz2qORXesjTf6IELvgtpBvWi4bvpWPdLGdL2inG0CgYEAzObxcpbLFcL0kaBcW6Vo9OJ0cPaABazd6ywpaakHEz6LSdXzysBsOVIQFeIl6i1KbDEHa6eRVdhIbTzcGJ0MktzyLTAbb4F8kCRDUd7gYPvCDu2Eg5NSsPi8drZL3MuQ5l6gRDyOWkUwbhQjNnE0qeILnl0wsj8awFHJXTkSLesCgYAfn/jL8oim5PP7bbiVDmoravW0CVo3mHCHv1bW3xgXf+C1lckmr3q/F57iZHuAkcJEBnJvy+VkYcH5K3+0SRaoOrvB0WSpy9DVu98zYvhJ699RlBjzjKczbg2qllwbEp4jhMw0KGEznfdF3t23+l1X/Jt5CWvg6v/gqpW9doWD9w==
    """

    # -------------------------- 示例1：查询指定账户的所有持仓 --------------------------
    try:
        # 构造持仓查询请求（查询TEST环境下3000002059账户的所有持仓）
        all_pos_req = PosReq(
            trd_env=TrdEnv.TEST,
            acc_id=3000002059,
            # 不填symbol和position_market，查询所有持仓
        )

        # 发送查询请求
        all_positions = qry_position(
            full_url=full_url,
            api_key=API_KEY,
            private_key_pem=PRIVATE_KEY_PEM.strip(),
            pos_req=all_pos_req
        )

        # 打印结果
        print("="*50)
        if not all_positions:
            print("无持仓")
        else:
            for pos in all_positions:
                print(pos)
    except Exception as e:
        print(f"查询所有持仓失败: {str(e)}")

    # -------------------------- 示例2：查询指定标的的持仓（如HK.00700）--------------------------
    try:
        # 构造请求（指定标的+市场）
        specific_pos_req = PosReq(
            trd_env=TrdEnv.TEST,
            acc_id=3000002059,
            symbol="HK.00700",  # 腾讯控股
            position_market=TrdMarket.HK  # 香港市场
        )

        # 发送查询请求
        specific_positions = qry_position(
            full_url=full_url,
            api_key=API_KEY,
            private_key_pem=PRIVATE_KEY_PEM.strip(),
            pos_req=specific_pos_req
        )

        # 打印结果
        print("\n" + "="*50)
        print(f"账户3000002059（TEST环境）HK.00700持仓:")
        if not specific_positions:
            print("该标的无持仓")
        else:
            for pos in specific_positions:
                print(pos)
    except Exception as e:
        print(f"查询HK.00700持仓失败: {str(e)}")




    # -------------------------- 资金查询使用示例 --------------------------
    full_url = "http://10.10.181.166:8098/quanta/qry/qryFundInfo"  # 资金查询接口URL
    # full_url = "http://127.0.0.1:8098/quanta/qry/qryFundInfo"  # 资金查询接口URL
    # 1. 接口认证配置
    API_KEY = "hf_f3b9aa5cd5154a94968b54fd2830c577"  # 实际APIKey
    # PEM格式私钥
    PRIVATE_KEY_PEM = """
    MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDmEDJT0R11dNx3QmGIvOz3Qzpv5LvnWqpTke12IL+Lr4Mlw/lde28t7JBiA01itrFzDuUKGh0jsQ9AK506F4aUNYtT0fRzZJZ5rGT6cf4/WJXq6GxH4a4cV7hMb+zS6KXqGS07hBskbE2sFMhylKyXXrA2sGSloiQVHzNY00y3W8Gr7VaOWYv3FI+HrzndUuzC1LCxhjjUM8IbYcW79R7FJJLQyQq55nYzoyn7RFTUh8LOPHtbCCJfqxIUz+8KQmp7QMFzxlcaPJGHCdRHRM4aIBPkVzmh1RPSkrBQzjYeqoBMLwKFX/qGp7z5DyoRKm8mYos7iQ2xYYl2If86S7O7AgMBAAECggEBAJNUUfZtFzFtyfWxk+ZOHm5mJhkb4N1SqXrlG62nYSLiHdlke9/KuTMuqHOr67XIizDEnBZxDLIbpEmS5JgcErn85CGkdagkBV0b8nqT357PawpJF3ac5rQN1N9WWdHi3MVipB3WBs+3b7JAiPEflrtFDxGmun17rSG9nlNG1X0hVaccW0WELXwJZufXOE2G1dule6arpZkPrU4jv3vNSfYy61rsw2YwyU8JhijsBENfYUuXjkyAgp0S5m8gSrWsWE4lAXJ0nh4fAVR4Uwt/njubI9G1ncUU1KQzTZzlmqCdbIG7WKO7vTpMbwL9e6bkaqCPbEI5MlLVxtWMgQW3g3kCgYEA+FKc1r9urZ7BmUZpdAb9sB+LlsTjO1YHPrhpWgT42GRqiLtmXG7TrFv3cUUfvGp0LUddJ0fnBODKXftJQ9AovQ7nR8OpCSfQA5HXD5dWj2qwwy5PnOoYbZNK6vYJIPvzghiy0B8xYIBN7EmCYUQK6xtGOAwAp/gZF1caRkB9yAUCgYEA7S0RHuDJddMczwzq70GKiLeKa+wXjGrr4l3lJEuxQXI+8wiX9chRd2GTIdy5BOuWnuiN9WNas8DIRV1n1340HSSiClQJ2uIQVG2iOcj3TftpMdQ4hegS3WUObzsqcFG8xlhHmLc4i2KcidD95nAHSNI30tyLBeP7BhfDaHhXGL8CgYEA2lnyNVaxIJO3Umq6sV6wVdz3JkTMNlGoHzuSz6gNlGF/1+lI0cBV+noHs57/j/LfYy0cOT0dY4myCD+8pZd1KwDe15ixmy5Z17m2rKv7XjKHaajgMm8ZuchJmR9s2YcSEPRcz2qORXesjTf6IELvgtpBvWi4bvpWPdLGdL2inG0CgYEAzObxcpbLFcL0kaBcW6Vo9OJ0cPaABazd6ywpaakHEz6LSdXzysBsOVIQFeIl6i1KbDEHa6eRVdhIbTzcGJ0MktzyLTAbb4F8kCRDUd7gYPvCDu2Eg5NSsPi8drZL3MuQ5l6gRDyOWkUwbhQjNnE0qeILnl0wsj8awFHJXTkSLesCgYAfn/jL8oim5PP7bbiVDmoravW0CVo3mHCHv1bW3xgXf+C1lckmr3q/F57iZHuAkcJEBnJvy+VkYcH5K3+0SRaoOrvB0WSpy9DVu98zYvhJ699RlBjzjKczbg2qllwbEp4jhMw0KGEznfdF3t23+l1X/Jt5CWvg6v/gqpW9doWD9w==
    """

    # -------------------------- 示例1：查询指定货币的资金信息（港元） --------------------------
    try:
        fund_req1 = FundQryReq(
            trd_env=TrdEnv.TEST,          # 测试环境
            acc_id=3000002059,            # 账户ID
            currency=Currency.HKD         # 指定查询港元资金
        )
        # 发送查询请求
        fund_resp1 = qry_fund_info(full_url, API_KEY, PRIVATE_KEY_PEM.strip(), fund_req1)
        # 打印结果
        print("="*60)
        print("示例1：指定港元的资金查询结果:")
        print(fund_resp1)
    except Exception as e:
        print(f"示例1查询失败: {str(e)}")        
  


    full_url = "http://10.10.181.166:8098/quanta/qry/qryAccTradInfo"  # 可买可卖查询URL
    # 1. 接口认证配置
    API_KEY = "hf_f3b9aa5cd5154a94968b54fd2830c577"  # 实际APIKey
    # PEM格式私钥
    PRIVATE_KEY_PEM = """
    MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDmEDJT0R11dNx3QmGIvOz3Qzpv5LvnWqpTke12IL+Lr4Mlw/lde28t7JBiA01itrFzDuUKGh0jsQ9AK506F4aUNYtT0fRzZJZ5rGT6cf4/WJXq6GxH4a4cV7hMb+zS6KXqGS07hBskbE2sFMhylKyXXrA2sGSloiQVHzNY00y3W8Gr7VaOWYv3FI+HrzndUuzC1LCxhjjUM8IbYcW79R7FJJLQyQq55nYzoyn7RFTUh8LOPHtbCCJfqxIUz+8KQmp7QMFzxlcaPJGHCdRHRM4aIBPkVzmh1RPSkrBQzjYeqoBMLwKFX/qGp7z5DyoRKm8mYos7iQ2xYYl2If86S7O7AgMBAAECggEBAJNUUfZtFzFtyfWxk+ZOHm5mJhkb4N1SqXrlG62nYSLiHdlke9/KuTMuqHOr67XIizDEnBZxDLIbpEmS5JgcErn85CGkdagkBV0b8nqT357PawpJF3ac5rQN1N9WWdHi3MVipB3WBs+3b7JAiPEflrtFDxGmun17rSG9nlNG1X0hVaccW0WELXwJZufXOE2G1dule6arpZkPrU4jv3vNSfYy61rsw2YwyU8JhijsBENfYUuXjkyAgp0S5m8gSrWsWE4lAXJ0nh4fAVR4Uwt/njubI9G1ncUU1KQzTZzlmqCdbIG7WKO7vTpMbwL9e6bkaqCPbEI5MlLVxtWMgQW3g3kCgYEA+FKc1r9urZ7BmUZpdAb9sB+LlsTjO1YHPrhpWgT42GRqiLtmXG7TrFv3cUUfvGp0LUddJ0fnBODKXftJQ9AovQ7nR8OpCSfQA5HXD5dWj2qwwy5PnOoYbZNK6vYJIPvzghiy0B8xYIBN7EmCYUQK6xtGOAwAp/gZF1caRkB9yAUCgYEA7S0RHuDJddMczwzq70GKiLeKa+wXjGrr4l3lJEuxQXI+8wiX9chRd2GTIdy5BOuWnuiN9WNas8DIRV1n1340HSSiClQJ2uIQVG2iOcj3TftpMdQ4hegS3WUObzsqcFG8xlhHmLc4i2KcidD95nAHSNI30tyLBeP7BhfDaHhXGL8CgYEA2lnyNVaxIJO3Umq6sV6wVdz3JkTMNlGoHzuSz6gNlGF/1+lI0cBV+noHs57/j/LfYy0cOT0dY4myCD+8pZd1KwDe15ixmy5Z17m2rKv7XjKHaajgMm8ZuchJmR9s2YcSEPRcz2qORXesjTf6IELvgtpBvWi4bvpWPdLGdL2inG0CgYEAzObxcpbLFcL0kaBcW6Vo9OJ0cPaABazd6ywpaakHEz6LSdXzysBsOVIQFeIl6i1KbDEHa6eRVdhIbTzcGJ0MktzyLTAbb4F8kCRDUd7gYPvCDu2Eg5NSsPi8drZL3MuQ5l6gRDyOWkUwbhQjNnE0qeILnl0wsj8awFHJXTkSLesCgYAfn/jL8oim5PP7bbiVDmoravW0CVo3mHCHv1bW3xgXf+C1lckmr3q/F57iZHuAkcJEBnJvy+VkYcH5K3+0SRaoOrvB0WSpy9DVu98zYvhJ699RlBjzjKczbg2qllwbEp4jhMw0KGEznfdF3t23+l1X/Jt5CWvg6v/gqpW9doWD9w==
    """

    # -------------------------- 示例1：查询港股可买可卖（腾讯控股，限价单） --------------------------
    try:
        trad_req1 = AccEnTrdInfoReq(
            acc_id=3000002059,
            symbol="HK.00700",  # 腾讯控股
            trd_env=TrdEnv.TEST,
            order_type=OrderType.ELO,  # 限价单
            price=Decimal("600")  # 报价600港元
            # 港股无需session，不填
        )
        trad_resp1 = qry_acc_trad_info(full_url, API_KEY, PRIVATE_KEY_PEM.strip(), trad_req1)
        print("="*60)
        print("示例1：腾讯控股（HK.00700）可买可卖信息:")
        print(trad_resp1)
    except Exception as e:
        print(f"示例1查询失败: {str(e)}")  
