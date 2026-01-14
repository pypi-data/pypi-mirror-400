from datetime import datetime
from collections import defaultdict

try:
    from pyda.api import FutureApi
except ImportError as e:
    raise ImportError(
        "The proprietary broker SDK `pyda` is required.\n"
        "Please install it from your broker before using async-execution-da."
    ) from e
try:
    from pyda.api.td_constant import (
        DERIVATIVE_TDY_TIF,
        DERIVATIVE_LIMIT_ORDER,
        DERIVATIVE_CONTRACT_CATEGORY_SPREAD,
    )
except ImportError as e:
    raise ImportError(
        "The proprietary broker SDK `pyda` is required.\n"
        "Please install it before using async-execution-da.\n"
        "This project does not bundle broker SDKs."
    ) from e

class MyFutureApi(FutureApi):
    """实现期货API接口类"""

    def __init__(self, userid: str, password: str, author_code: str, computer_name: str, software_name: str, software_version: str, tag50: str) -> None:
        """构造函数"""
        super().__init__()

        self.userid = userid
        self.password = password
        self.author_code = author_code
        self.computer_name = computer_name
        self.software_name = software_name
        self.software_version = software_version
        self.tag50 = tag50

        self.login_status: bool = False
        self.connect_status: bool = False

        self.reqid = 0
        self.local_no: int = int(datetime.now().strftime("%m%d%H%M") + "000000")
        self.currency_account_map: defaultdict = defaultdict(str)
        self.exchange_contract_page: defaultdict = defaultdict(int)
        self.localid_sysid_map: defaultdict = defaultdict(tuple)

    def login(self) -> None:
        """登录期货服务器"""
        login_info = {
            "UserId": self.userid,
            "UserPwd": self.password,
            "AuthorCode": self.author_code,
            "ComputerName": self.computer_name,
            "SoftwareName": self.software_name,
            "SoftwareVersion": self.software_version,
        }
        self.reqid += 1
        self.reqUserLogin(login_info, self.reqid)

    def send_order(self, symbol: str, exchange: str, side: str, price: float, volume: int, currency: str) -> None:
        """发送订单"""
        account_no: str = self.currency_account_map[currency]
        if not account_no:
            print(f"币种 {currency} 未找到对应账户")
            return

        self.local_no += 1
        order_req = {
            "UserId": self.userid,
            "AccountNo": account_no,
            "LocalNo": str(self.local_no),
            "ExchangeCode": exchange,
            "ContractCode": symbol,
            "BidAskFlag": side,
            "OrderPrice": str(price),
            "OrderQty": str(volume),
            "OrderType": DERIVATIVE_LIMIT_ORDER,
            "TIF": DERIVATIVE_TDY_TIF,
            "Tag50": self.userid
            #,
            #"ContractCategory":DERIVATIVE_CONTRACT_CATEGORY_SPREAD
        }
        self.reqid += 1
        self.reqOrderInsert(order_req, self.reqid)

    def modify_order(self, local_id: str, modified_price: float, modified_volume: int, symbol: str, exchange: str, side: str, price: float, volume: int, currency: str) -> None:
        """修改订单"""
        account_no: str = self.currency_account_map[currency]
        if not account_no:
            print(f"币种 {currency} 未找到对应账户")
            return

        system_no, order_no = self.localid_sysid_map[local_id]
        if not system_no or not order_no:
            print("系统号，订单号不能为空")
            return

        modify_req = {
            "UserId": self.userid,
            "LocalNo": local_id,
            "OrderNo": order_no,
            "SystemNo": system_no,
            "AccountNo": account_no,
            "ModifyPrice": str(modified_price),
            "ModifyQty": str(modified_volume),
            "OrderPrice": str(price),
            "OrderQty": str(volume),
            "ExchangeCode": exchange,
            "ContractCode": symbol,
            "BidAskFlag": side,
            "OrderType": DERIVATIVE_LIMIT_ORDER,
        }
        self.reqid += 1
        self.reqOrderModify(modify_req, self.reqid)

    def cancel_order(self, local_id: str, currency: str) -> None:
        """取消订单"""
        account_no: str = self.currency_account_map[currency]
        if not account_no:
            print(f"币种 {currency} 未找到对应账户")
            return

        system_no, order_no = self.localid_sysid_map[local_id]
        if not system_no or not order_no:
            print("系统号，订单号不能为空")
            return

        cancel_req = {
            "UserId": self.userid,
            "LocalNo": local_id,
            "OrderNo": order_no,
            "SystemNo": system_no,
            "AccountNo": account_no,
        }
        self.reqid += 1
        self.reqOrderCancel(cancel_req, self.reqid)

    def verify_code(self) -> None:
        """校验密码"""
        req = {
            "Type": "I",
            "Question": "1",
            "Answer": "2",
            "VerifyCode": "0",
            "MobileNumber": "18621908120",
            "UserId": self.userid,
            "UserPwd": self.password,   
        }
        self.reqid += 1
        self.reqVerifyCode(req, self.reqid)

    def safe_verify(self) -> None:
        """安全验证"""
        req = {
            "Type": "1",
            "Question": "1",
            "Answer": "song_pass_1234",
            "SaveMac": "1",
            "UserId": self.userid,
            "UserPwd": self.password,   
        }
        self.reqid += 1
        self.reqSafeVerify(req, self.reqid)

    def set_verify_qa(self) -> None:
        """设置验证问题答案"""
        req = {
            "Type": "1",
            "Question": "1",
            "Answer": "song_pass_1234",
            "SaveMac": "1",
            "UserId": self.userid,
            "UserPwd": self.password,   
        }
        self.reqid += 1
        self.reqSetVerifyQA(req, self.reqid)

    def change_password(self) -> None:
        """修改密码"""
        req = {
            "UserId": self.userid,
            "OldPassword": self.password,
            "NewPassword": self.password,
        }
        self.reqid += 1
        self.reqPasswordUpdate(req, self.reqid)

    def query_account(self) -> None:
        """查询账户信息"""
        self.reqid += 1
        self.reqQryCapital({}, self.reqid)

    def query_position(self, ) -> None:
        """查询持仓信息"""
        self.reqid += 1
        self.reqQryPosition({}, self.reqid)

    def query_position_total(self) -> None:
        """查询持仓合计信息"""
        da_req: dict = {"AccountNo": self.userid}

        self.reqid += 1
        self.reqQryTotalPosition(da_req, self.reqid)

    def query_order(self) -> None:
        """查询委托信息"""
        da_req: dict = {"UserId": self.userid}
    
        self.reqid += 1
        self.reqQryOrder(da_req, self.reqid)

    def query_trade(self, lastfilledno: str = "") -> None:
        """查询成交信息"""
        da_req: dict = {
            "UserId": self.userid,
            "lastFilledNo": lastfilledno
        }

        self.reqid += 1
        self.reqQryTrade(da_req, self.reqid)

    def query_contract(self, exchange: str, page: int = 0) -> None:
        """查询合约信息"""
        req = {
            "ExchangeNo": exchange,
            "PageIndex": page * 1000
        }
        self.reqid += 1
        self.reqQryInstrument(req, self.reqid)

    def query_exchange(self) -> None:
        """查询交易所信息"""
        self.reqid += 1
        self.reqQryExchange({}, self.reqid)

    def query_currency(self) -> None:
        """查询币种信息"""
        self.reqid += 1
        self.reqQryCurrency({}, self.reqid)

    def query_version(self) -> None:
        """查询版本信息"""
        self.reqid += 1
        self.reqQryVersion({}, self.reqid)

    def query_commodity(self) -> None:
        """查询商品信息"""
        self.reqid += 1
        self.reqQryCommodity({}, self.reqid)

    def query_exchange_time(self) -> None:
        """查询交易所时间"""
        self.reqid += 1
        self.reqQryExchangeTime({}, self.reqid)

    def query_commodity_time(self, exchange: str, commodity: str = "") -> None:
        """查询商品时间"""
        req = {
            "ExchangeNo": exchange,
            "CommodityNo": commodity
        }
        self.reqid += 1
        self.reqQryCommodityTime(req, self.reqid)

    def query_strategy(self, exchange: str) -> None:
        """查询策略信息"""
        req = {
            "ExchangeNo": exchange,
        }
        self.reqid += 1
        self.reqQryStrategy(req, self.reqid)

    def query_strategy_detail(self, strategy_commodity_no: str) -> None:
        """查询策略细节信息"""
        req = {
            "StrategyCommodityNo": strategy_commodity_no,
        }
        self.reqid += 1
        self.reqQryStrategyDetail(req, self.reqid)

    def query_question(self) -> None:
        """查询问题信息"""
        self.reqid += 1
        self.reqGetQuestion({}, self.reqid)

    def onFrontConnected(self) -> None:
        """服务器连接成功回调"""
        print("服务器连接成功")
        self.connect_status = True
        self.login()

    def onFrontDisconnected(self, iReason: int) -> None:
        """服务器连接断开回调"""
        self.connect_status = False
        self.login_status = False
        print(f"连接断开, 原因 = {iReason}")

    def onHeartBeatWarning(self, time_lapse: int) -> None:
        """心跳超时警告回调"""
        print(f"心跳超时警告, 时间间隔 = {time_lapse}")

    def onRspUserLogin(self, error: dict, reqid: int, last: bool) -> None:
        """用户登录响应回调"""
        if not error["ErrorID"]:
            self.login_status = True
            print("交易服务器登录成功")
        else:
            self.login_status = False
            print(f"交易服务器登录失败，错误信息: {error}")

    def onRspUserLogout(self, error: dict, reqid: int, last: bool) -> None:
        """用户登出回报"""
        if error.get("ErrorID", 0) == 0:
            self.login_status = False
            print("交易服务器登出成功")
        else:
            print(f"交易服务器登出失败: ErrorID = {error['ErrorID']}, ErrorMsg = {error['ErrorMsg']}")

    def onRspAccount(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """用户登录回报"""
        if error["ErrorID"]:
            print(f"onRspAccount: ErrorID = {error['ErrorID']}, ErrorMsg = {error['ErrorMsg']}")

        else:
            print(data['CurrencyNo'], end=".\n" if last else ";")
            self.currency_account_map[data["CurrencyNo"]] = data["AccountNo"]

            if last:
                print("获取资金账户完成")

    def onRspOrderInsert(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """订单录入响应回调"""
        
        # 格式化当前时间为字符串，包含年、月、日、小时、分钟、秒和毫秒
        # %f 代表微秒，我们通过切片操作取前3位来获取毫秒
        current_timestamp_ms = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"OnRspOrderInsert: time={current_timestamp_ms},ErrorID = {error['ErrorID']}, OrderNo = {data['OrderNo']}, SystemNo = {data['SystemNo']}, LocalNo = {data['LocalNo']}")

        if error["ErrorID"]:
            print(f"错误原因：{error['ErrorMsg']}")
        else:
            self.localid_sysid_map[data["LocalNo"]] = (data["SystemNo"], data["OrderNo"])

    def onRspOrderModify(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """订单修改响应回调"""
        print(f"OnRspOrderModify: ErrorID = {error['ErrorID']}, UserId = {data['UserId']}")

        if error["ErrorID"]:
            print(f"错误原因：{error['ErrorMsg']}")

    def onRspOrderCancel(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """订单撤销响应回调"""
        print(f"OnRspOrderCancel: ErrorID = {error['ErrorID']}, SystemNo = {data['SystemNo']}")

        if error["ErrorID"]:
            print(f"错误原因：{error['ErrorMsg']}")

    def onRspQryInstrument(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """合约查询响应回调"""
        if error["ErrorID"]:
            print(f"ErrorID = {error['ErrorID']}, ErrorMsg = {error['ErrorMsg']}")
            print("-----------Over------------")
        else:
            print(f"ExchangeName= {data['ExchangeName']}, CommodityNo= {data['CommodityNo']}")
            if last:
                self.exchange_contract_page[data["ExchangeNo"]] += 1
                self.query_contract(data["ExchangeNo"], self.exchange_contract_page[data["ExchangeNo"]])

    def onRspQryPosition(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """持仓查询回报"""
        print(f"ClientNo= {data['ClientNo']}, ContractNo= {data['ContractNo']}, CurrencyNo= {data['CurrencyNo']}, HoldVol= {data['HoldVol']}, HoldPrice= {data['HoldPrice']}")
        if last:
            print("-----------Over------------")

    def onRspQryOrder(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """委托查询回报"""
        # 将时间戳转换为毫秒，并转换为整数
        current_timestamp_ms = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"time={current_timestamp_ms},UserId= {data['UserId']}, OrderState= {data['OrderState']}, OrderNo= {data['OrderNo']}, SystemNo= {data['SystemNo']}, LocalNo= {data['LocalNo']}, OrderPrice= {data['OrderPrice']}")
        if last:
            print("-----------Over------------")

    def onRspQryTrade(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """成交查询回报"""
        if error["ErrorID"]:
            print(f"ErrorID = {error['ErrorID']}, ErrorMsg = {error['ErrorMsg']}")
            print("-----------Over------------")
        else:
            print(f"FilledNo= {data['FilledNo']}, FilledPrice= {data['FilledPrice']}")
            if last:
                self.query_trade(data["FilledNo"])

    def onRspQryCapital(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """资金查询回报"""
        print(f"Currency= {data['CurrencyNo']}, TodayInitialBalance= {data['TodayInitialBalance']}, CanCashOutMoneyAmount= {data['CanCashOutMoneyAmount']}")
        if last:
            print("-----------Over------------")

    def onRspQryExchange(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """交易所查询回报"""
        print(f"ExchangeNo= {data['ExchangeNo']}, ExchangeName= {data['ExchangeName']}")
        if last:
            print("-----------Over------------")

    def onRspQryCurrency(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """币种查询回报"""
        print(f"CurrencyNo= {data['CurrencyNo']}, CurrencyName= {data['CurrencyName']}")
        if last:
            print("-----------Over------------")

    def onRspQryVersion(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """版本查询响应回调"""
        print(f"Version= {data['Version']}, MustUpdate= {data['MustUpdate']}")

    def onRspQuestion(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """问题查询响应回调"""
        print(f"QuestionId= {data['QuestionId']}, QuestionCN= {data['QuestionCN']}, QuestionEN= {data['QuestionEN']}")

    def onRspQryTotalPosition(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """持仓合计查询回报"""
        print(f"AccountNo= {data['AccountNo']}, CurrPrice= {data['CurrPrice']}, FilledQty= {data['FilledQty']}, ProfitLoss= {data['ProfitLoss']}, OrderNo= {data['OrderNo']}")
        if last:
            print("-----------Over------------")

    def onRspQryCommodity(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """商品查询响应回调"""
        print(f"ExchangeNo= {data['ExchangeNo']}, ExchangeNo2= {data['ExchangeNo2']}, Name= {data['Name']}, RegDate= {data['RegDate']}")

    def onRspQryExchangeTime(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """交易所时间查询响应回调"""
        print(f"ExchangeNo= {data['ExchangeNo']}, SummerBegin= {data['SummerBegin']}, WinterBegin= {data['WinterBegin']}")
        if last:
            print("-----------Over------------")

    def onRspQryCommodityTime(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """商品时间查询响应回调"""
        print(f"ExchangeNo= {data['ExchangeNo']}, CommodityNo= {data['CommodityNo']}, Summer= {data['Summer']}, CrossTrade= {data['CrossTrade']}, Opendate= {data['Opendate']}, Closingdate= {data['Closingdate']}")
        if last:
            print("-----------Over------------")

    def onRspQryStrategy(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """策略查询响应回调"""
        print(f"CommodityCode= {data['CommodityCode']}, ExchangeNo= {data['ExchangeNo']}, ContractNo= {data['ContractNo']}, ContractFName= {data['ContractFName']}")
        if last:
            print("-----------Over------------")

    def onRspQryStrategyDetail(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """策略细节查询回报"""
        print(f"StartegyCommodityNo= {data['StartegyCommodityNo']},StartegyContractNo={data['StartegyContractNo']},Price= {data['Price']},LegNum= {data['LegNum']},CommodityNo= {data['CommodityNo']},ContractNo= {data['ContractNo']}")
        if last:
            print("-----------Over------------")

    def onRtnTrade(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """交易推送"""
         # 将时间戳转换为毫秒，并转换为整数
        current_timestamp_ms = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"time={current_timestamp_ms},OnRtnTrade: UserId= {data['UserId']}, OrderNo= {data['OrderNo']}, FilledPrice= {data['FilledPrice']}")
        if last:
            print("-----------Over------------")

    def onRtnOrder(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """订单推送"""
         # 将时间戳转换为毫秒，并转换为整数
        current_timestamp_ms = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"OnRtnOrder:time={current_timestamp_ms}, OrderNo= {data['OrderNo']}, FilledQty= {data['FilledQty']}, FilledAvgPrice= {data['FilledAvgPrice']}")
        if last:
            print("-----------Over------------")

    def onRtnCapital(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """资金更新推送"""
        print(f"OnRtnCapital: AccountNo= {data['AccountNo']}, OrderNo= {data['OrderNo']}")
        if last:
            print("-----------Over------------")

    def onRtnPosition(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """持仓更新推送"""
        print(f"OnRtnPosition: AccountNo= {data['AccountNo']}, OrderNo= {data['OrderNo']}")
        if last:
            print("-----------Over------------")

    def onRspVerifyCode(self,error: dict, reqid: int, last: bool) -> None:
        """验证码响应回调"""
        print(f"ErrorID= {error['ErrorID']}, ErrorMsg= {error['ErrorMsg']}")

    def onRspSafeVerify(self, error: dict, reqid: int, last: bool) -> None:
        """安全验证响应回调"""
        print(f"ErrorID= {error['ErrorID']}, ErrorMsg= {error['ErrorMsg']}")

    def onRspSetVerifyQA(self, error: dict, reqid: int, last: bool) -> None:
        """设置验证问题响应回调"""
        self.safe_verify()
        print(f"ErrorID= {error['ErrorID']}, ErrorMsg= {error['ErrorMsg']}")

    def onRspPasswordUpdate(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """修改密码响应回调"""
        print(f"ErrorID= {error['ErrorID']}, ErrorMsg= {error['ErrorMsg']} UserId= {data['UserId']}")

    def onRspNeedVerify(self, bfirstlogin: bool, bhassetqa: bool) -> None:
        """需要验证响应回调"""
        self.login_status = True

        if bfirstlogin:
            print("首次登录，需要进行双重认证")
            self.set_verify_qa()

        if bhassetqa:
            print("已经设置认证问题答案")
