# @Time    : 2025/4/28 19:13
# @Author  : YQ Tsui
# @File    : xt_datapub.py
# @Purpose :
import os
from abc import ABC
import time
import json
from typing import Literal

from threading import Lock
import numpy as np
from datetime import datetime
from xtquant import xtdata, xtdatacenter as xtdc
from filelock import FileLock, Timeout
from copy import deepcopy

from vnpy.event import EventEngine, Event
from vnpy.trader.event import EVENT_GATEWAY_CONNECTED
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.object import (
    SubscribeRequest,
    ContractData,
    TickData,
    OrderData,
    OptionType,
)

from vnpy.trader.constant import Exchange, Product
from vnpy.trader.utility import ZoneInfo, get_file_path, round_to


EXCHANGE_VT2XT: dict[Exchange, str] = {
    Exchange.SSE: "SH",
    Exchange.SZSE: "SZ",
    Exchange.BSE: "BJ",
    Exchange.SHFE: "SF",
    Exchange.CFFEX: "IF",
    Exchange.INE: "INE",
    Exchange.DCE: "DF",
    Exchange.CZCE: "ZF",
    Exchange.GFEX: "GF",
}

EXCHANGE_XT2VT: dict[str, Exchange] = {v: k for k, v in EXCHANGE_VT2XT.items()}
EXCHANGE_XT2VT.update(
    {
        "CFFEX": Exchange.CFFEX,
        "SHFE": Exchange.SHFE,
        "CZCE": Exchange.CZCE,
        "DCE": Exchange.DCE,
        "GFEX": Exchange.GFEX,
        "SHO": Exchange.SSE,
        "SZO": Exchange.SZSE,
    }
)

ACCOUNT_TYPE_EXCHANGE_MAP: dict[str, list[Exchange]] = {
    "STOCK": [Exchange.SSE, Exchange.SZSE, Exchange.BSE],
    "CREDIT": [Exchange.SSE, Exchange.SZSE, Exchange.BSE],
    "FUTURE": [Exchange.SHFE, Exchange.CFFEX, Exchange.INE, Exchange.DCE, Exchange.CZCE, Exchange.GFEX],
    "STOCK_OPTION": [Exchange.SSE, Exchange.SZSE],
}

# 其他常量
CHINA_TZ = ZoneInfo("Asia/Shanghai")  # 中国时区


# 全局缓存字典
symbol_contract_map: dict[(str, Exchange), ContractData] = {}  # 合约数据
symbol_limit_map: dict[str, tuple[float, float]] = {}  # 涨跌停价
account_type_symbol_map: dict[str, set[tuple[str, Exchange]]] = {}  # 账号类型对应的合约代码

EVENT_CONTRACT_READY = "xt_contract_ready"  # 合约准备就绪事件


class XtGatewayBase(BaseGateway, ABC):
    @property
    def exchanges(self) -> list[Exchange]:
        """查询交易所"""
        return ACCOUNT_TYPE_EXCHANGE_MAP.get(self.account_type, [])

    def __init__(self, event_engine: EventEngine, gateway_name: str) -> None:
        """构造函数"""
        super().__init__(event_engine, gateway_name)

        self.trading: bool = False
        self.orders: dict[str, OrderData] = {}

        self.md_api: XtMdApi | None = None
        self.td_api = None

        # MdApi参数
        self.ip: str = ""
        self.port: int = 0
        self.token: str = ""
        self.server_pool_list: list[str] = []
        self.contract_ready: bool = False

        # 共用参数
        self.account_type: str = ""
        self.fut_option_active: bool = False

    def subscribe(self, req: SubscribeRequest) -> None:
        """订阅行情"""
        self.md_api.subscribe(req, self.gateway_name)

    def process_timer_event(self, event) -> None:
        """定时事件处理"""
        self.count += 1
        if self.count < 2:
            return
        self.count = 0

        func = self.query_functions.pop(0)
        func()
        self.query_functions.append(func)

    def on_market_data_connected(self) -> None:
        """行情服务器连接成功回调"""
        event: Event = Event(EVENT_GATEWAY_CONNECTED, data=self.gateway_name)
        self.event_engine.put(event)

    def on_contract_ready(self) -> None:
        """合约信息查询完成回调"""
        if not self.contract_ready and self.trading and self.td_api and self.gateway_name in getattr(self.td_api, "gateways", {}):
            self.init_query()
        self.contract_ready = True


class XtMdApi:
    """行情API"""

    lock_filename = "xt_lock"
    lock_filepath = get_file_path(lock_filename)

    def __init__(self) -> None:
        """构造函数"""
        self.gateways: dict[str, XtGatewayBase] = {}

        self.inited: bool = False

        self.ip: str = ""
        self.port: int = 0
        self.token: str = ""

        self.xtdc_client = None

        self.accu_volumes: dict[str, int] = {}

        self.account_types_required: dict[str, set[str]] = {}
        self.fut_option_active: bool = False

        self.gateway_subscriptions: dict[tuple[str, Exchange], set[str]] = {}

    def has_account_type(self, account_type: Literal["STOCK", "FUTURE", "STOCK_OPTION", "CREDIT"]) -> bool:
        """检查是否存在该账号类型"""
        return account_type in self.account_types_required

    def add_gateway(self, gateway: XtGatewayBase) -> None:
        self.gateways[gateway.gateway_name] = gateway
        self.account_types_required.setdefault(gateway.account_type, set()).add(gateway.gateway_name)
        if self.inited:
            gateway.write_log("行情接口已经初始化，开始查询合约信息")
            self.query_contracts(gateway)
            gateway.on_market_data_connected()

    def remove_gateway(self, gateway: XtGatewayBase) -> None:
        """移除网关"""
        self.gateways.pop(gateway.gateway_name, None)
        self.account_types_required[gateway.account_type].discard(gateway.gateway_name)
        if not self.account_types_required[gateway.account_type]:
            self.account_types_required.pop(gateway.account_type)

    def onMarketData(self, data: dict) -> None:
        """行情推送回调"""

        def parse_data_dict(xt_symbol, d: dict) -> TickData:
            symbol, xt_exchange = xt_symbol.split(".")
            exchange = EXCHANGE_XT2VT[xt_exchange]

            tick: TickData = TickData(
                symbol=symbol,
                exchange=exchange,
                datetime=generate_datetime(d["time"]),
                volume=d["volume"],
                turnover=d["amount"],
                open_interest=d["openInt"],
                gateway_name="",
                localtime=datetime.now(CHINA_TZ),
            )

            contract = symbol_contract_map[(tick.symbol, tick.exchange)]
            tick.name = contract.name

            bp_data: list = d["bidPrice"]
            ap_data: list = d["askPrice"]
            bv_data: list = d["bidVol"]
            av_data: list = d["askVol"]

            tick.bid_price_1 = round_to(bp_data[0], contract.pricetick)
            tick.bid_price_2 = round_to(bp_data[1], contract.pricetick)
            tick.bid_price_3 = round_to(bp_data[2], contract.pricetick)
            tick.bid_price_4 = round_to(bp_data[3], contract.pricetick)
            tick.bid_price_5 = round_to(bp_data[4], contract.pricetick)

            tick.ask_price_1 = round_to(ap_data[0], contract.pricetick)
            tick.ask_price_2 = round_to(ap_data[1], contract.pricetick)
            tick.ask_price_3 = round_to(ap_data[2], contract.pricetick)
            tick.ask_price_4 = round_to(ap_data[3], contract.pricetick)
            tick.ask_price_5 = round_to(ap_data[4], contract.pricetick)

            tick.bid_volume_1 = bv_data[0]
            tick.bid_volume_2 = bv_data[1]
            tick.bid_volume_3 = bv_data[2]
            tick.bid_volume_4 = bv_data[3]
            tick.bid_volume_5 = bv_data[4]

            tick.ask_volume_1 = av_data[0]
            tick.ask_volume_2 = av_data[1]
            tick.ask_volume_3 = av_data[2]
            tick.ask_volume_4 = av_data[3]
            tick.ask_volume_5 = av_data[4]

            tick.last_price = round_to(d["lastPrice"], contract.pricetick)
            tick.open_price = round_to(d["open"], contract.pricetick)
            tick.high_price = round_to(d["high"], contract.pricetick)
            tick.low_price = round_to(d["low"], contract.pricetick)
            tick.pre_close = round_to(d["lastClose"], contract.pricetick)

            if tick.vt_symbol in symbol_limit_map:
                tick.limit_up, tick.limit_down = symbol_limit_map[tick.vt_symbol]

            # 判断收盘状态
            tick.extra = {
                "market_closed": False,
            }

            if contract.product == Product.ETF:
                tick.extra["iopv"] = d.get("pe", np.nan)

            # 非衍生品可以通过openInt字段判断证券状态
            if contract.product not in {Product.FUTURES, Product.OPTION}:
                if "openInt" in d and d["openInt"] in {1, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23}:
                    tick.extra["status"] = d["openInt"]
                tick.extra["market_closed"] = d["openInt"] == 15
            # 衍生品该字段为持仓量，需要通过结算价判断
            elif d["settlementPrice"] > 0:
                tick.extra["market_closed"] = True
            return tick

        def distribute_ticks(tick: TickData) -> None:
            """分发Tick数据到关联网关"""
            for gateway_name in self.gateway_subscriptions.get((tick.symbol, tick.exchange), set()):
                gateway = self.gateways[gateway_name]
                gw_tick = deepcopy(tick)
                gw_tick.gateway_name = gateway_name
                gateway.on_tick(gw_tick)

        for xt_symbol, buf in data.items():
            if isinstance(buf, dict):
                tick = parse_data_dict(xt_symbol, buf)
                tick.last_volume = max(0, tick.volume - self.accu_volumes.get(tick.vt_symbol, 0))
                distribute_ticks(tick)
                self.accu_volumes[tick.vt_symbol] = tick.volume
            elif isinstance(buf, list):
                for d in buf:
                    tick = parse_data_dict(xt_symbol, d)
                    tick.last_volume = max(0, tick.volume - self.accu_volumes.get(tick.vt_symbol, 0))
                    distribute_ticks(tick)
                    self.accu_volumes[tick.vt_symbol] = tick.volume

    def write_collective_log(self, message: str) -> None:
        """群发日志消息到所有关联网关"""
        for gw in self.gateways.values():
            gw.write_log(message)

    def connect(
        self,
        ip: str,
        port: int,
        token: str,
        server_pool: list[str] = None,
    ) -> None:
        """连接"""
        self.ip = ip
        self.port = port
        self.token = token

        if self.inited:
            self.write_collective_log("行情接口已经初始化，请勿重复操作")
            return
        self.write_collective_log("开始启动行情服务，请稍等")

        if not 5000 <= self.port <= 65535:
            self.port = 58609
        xtdata.watch_xtquant_status(self.on_connection_status)
        if not self._connect_to_existing_xtdc(self.ip, self.port):
            if self.ip in {"127.0.0.1", "localhost"}:
                try:
                    _, self.port = self.init_xtdc(server_pool)
                    self.xtdc_client = xtdata.connect(port=self.port)
                    if self.xtdc_client.is_connected():
                        self.write_collective_log("迅投研数据服务初始化成功")
                    else:
                        self.write_collective_log("迅投研数据服务初始化失败，请检查日志")
                except Exception as e:
                    self.write_collective_log(str(e))
            else:
                self.write_collective_log(f"远程迅投研数据服务{self.ip}:{self.port}连接失败")

    def _connect_to_existing_xtdc(self, ip: str, port: int) -> bool:
        """连接到已经存在的行情服务"""
        try:
            self.xtdc_client = xtdata.connect(ip, port)
            if self.xtdc_client.is_connected():
                self.write_collective_log("连接到已经存在的行情服务")
                # self.inited = True
                return True
            self.write_collective_log("找不到已经存在的行情服务")
            self.xtdc_client = None
            return False
        except Exception:
            self.xtdc_client = None
            return False

    def get_lock(self) -> bool:
        """获取文件锁，确保单例运行"""
        self.lock = FileLock(self.lock_filepath)

        try:
            self.lock.acquire(timeout=1)
            return True
        except Timeout:
            return False

    def init_xtdc(self, server_pool: list[str] = None) -> tuple[str, int]:
        """初始化xtdc服务进程"""
        if not self.get_lock():
            return 0

        # 设置token
        xtdc.set_token(self.token)

        # 设置是否只连接VIP服务器
        if isinstance(server_pool, list) and len(server_pool) > 0:
            xtdc.set_allow_optmize_address(server_pool)

        # 开启使用期货真实夜盘时间
        xtdc.set_future_realtime_mode(True)
        # 执行初始化，但不启动默认58609端口监听
        xtdc.init(start_local_service=False)

        port_res = xtdc.listen(port=(self.port, self.port + 50))
        return port_res

    def on_connection_status(self, info_dict: dict) -> None:
        """连接状态回调"""
        if self.inited:
            if info_dict["status"] != "connected":
                error_info = json.loads(info_dict.get("error", "{}"))
                if bool(error_info):
                    self.write_collective_log(f"[{error_info['error id']}]{error_info['error']}")
                self.inited = False
                self.write_collective_log(f"行情服务（{info_dict['address']}）连接断开")
        elif info_dict["status"] == "connected":
            time.sleep(1)
            for _attempt in range(5):
                if self.xtdc_client:
                    if self.xtdc_client.is_connected():
                        self.write_collective_log(f"行情服务（{info_dict['address']}）连接成功")
                        self.inited = True
                        for gw in self.gateways.values():
                            gw.write_log("开始查询合约信息")
                            self.query_contracts(gw)
                            gw.on_market_data_connected()
                        break
                else:
                    self.write_collective_log(f"等待客户端完全连接：尝试{_attempt + 1}/5")
                    time.sleep(1)
            else:
                self.write_collective_log(f"行情服务（{info_dict['address']}）连接失败，请检查日志")

    def query_contracts(self, gateway: XtGatewayBase) -> None:
        """查询合约信息"""
        gateway.write_log(f"[{gateway.gateway_name}]开始查询合约")

        if gateway.account_type in account_type_symbol_map and (
            self.fut_option_active or gateway.account_type != "FUTURE" or not gateway.fut_option_active
        ):
            gateway.write_log(f"{gateway.account_type}合约信息已经查询，复用历史数据")
            for key in account_type_symbol_map[gateway.account_type]:
                contract = symbol_contract_map[key]
                gateway.on_contract(contract)
            gateway.write_log("合约信息查询成功")
            gateway.on_contract_ready()
            return

        if gateway.account_type in {"STOCK", "CREDIT"}:
            self.query_stock_contracts(gateway)
        elif gateway.account_type == "FUTURE":
            self.query_future_contracts(gateway)
            if self.fut_option_active:
                self.query_future_option_contracts(gateway)
        elif gateway.account_type == "STOCK_OPTION":
            self.query_option_contracts(gateway)
        else:
            gateway.write_log(f"未知账号类型{gateway.account_type}，无法查询合约信息")
            return

        gateway.write_log("合约信息查询成功")
        gateway.on_contract_ready()

    @staticmethod
    def query_stock_contracts(gateway: XtGatewayBase) -> None:
        """查询股票合约信息"""
        xt_symbols: list[str] = []
        markets: list = ["沪深A股", "沪深转债", "沪深ETF", "沪深指数", "京市A股"]

        for i in markets:
            names: list = xtdata.get_stock_list_in_sector(i)
            xt_symbols.extend(names)

        for xt_symbol in xt_symbols:
            # 筛选需要的合约
            product = None
            symbol, xt_exchange = xt_symbol.split(".")

            if xt_exchange == "SZ":
                if xt_symbol.startswith(("00", "30")):
                    product = Product.EQUITY
                elif xt_symbol.startswith("15"):
                    product = Product.ETF
                else:
                    product = Product.INDEX
            elif xt_exchange == "SH":
                if xt_symbol.startswith(("60", "68")):
                    product = Product.EQUITY
                elif xt_symbol.startswith("51"):
                    product = Product.ETF
                else:
                    product = Product.INDEX
            elif xt_exchange == "BJ":
                product = Product.EQUITY

            exch = EXCHANGE_XT2VT[xt_exchange]
            if (symbol, exch) in symbol_contract_map:
                contract: ContractData = symbol_contract_map[(symbol, exch)]
                if gateway.gateway_name not in contract.gateway_names:
                    contract.gateway_names.append(gateway.gateway_name)
                    gateway.on_contract(contract)
                continue

            if not product:
                continue

            # 生成并推送合约信息
            data: dict = xtdata.get_instrument_detail(xt_symbol)
            pricetick = data["PriceTick"]
            vol_step = 100
            if product == Product.ETF:
                pricetick = 0.001
            if product == Product.INDEX:
                vol_step = 1

            if data is None:
                gateway.write_log(f"合约{xt_symbol}信息查询失败")
                continue

            if abs(data["PriceTick"] - pricetick) > 1e-5:
                print("symbol:", xt_symbol, "pricetick:", data["PriceTick"], "reset to:", pricetick)

            contract: ContractData = ContractData(
                symbol=symbol,
                exchange=exch,
                name=data["InstrumentName"],
                product=product,
                size=data["VolumeMultiple"],
                pricetick=pricetick,
                min_volume=vol_step,
                volume_step=vol_step,
                history_data=False,
                net_position=True,
                gateway_name=gateway.gateway_name,
            )

            symbol_contract_map[(symbol, exch)] = contract
            symbol_limit_map[contract.vt_symbol] = (
                data["UpStopPrice"],
                data["DownStopPrice"],
            )

            gateway.on_contract(contract)
            account_type_symbol_map.setdefault("STOCK", set()).add((symbol, exch))
        # 信用账号使用相同的合约信息
        account_type_symbol_map["CREDIT"] = account_type_symbol_map["STOCK"]

    @staticmethod
    def _query_future_exchange_contracts(gateway: XtGatewayBase, markets: list[str], account_type: str) -> None:
        """查询期货合约信息"""
        xt_symbols: list[str] = []

        for i in markets:
            names: list = xtdata.get_stock_list_in_sector(i)
            xt_symbols.extend(names)

        for xt_symbol in xt_symbols:
            # 筛选需要的合约
            product = None
            symbol, xt_exchange = xt_symbol.split(".")

            exch = EXCHANGE_XT2VT[xt_exchange]

            if (symbol, exch) in symbol_contract_map:
                contract: ContractData = symbol_contract_map[(symbol, exch)]
                if gateway.gateway_name not in contract.gateway_names:
                    contract.gateway_names.append(gateway.gateway_name)
                    gateway.on_contract(contract)
                continue

            if xt_exchange == "ZF" and len(symbol) > 6 and "&" not in symbol:
                product = Product.OPTION
            elif xt_exchange in ("IF", "GF") and "-" in symbol:
                product = Product.OPTION
            elif xt_exchange in ("DF", "INE", "SF") and ("C" in symbol or "P" in symbol) and "SP" not in symbol:
                product = Product.OPTION
            else:
                product = Product.FUTURES

            # 生成并推送合约信息
            if product == Product.OPTION:
                data: dict = xtdata.get_instrument_detail(xt_symbol, True)
            else:
                data: dict = xtdata.get_instrument_detail(xt_symbol)
            if data is None:
                gateway.write_log(f"合约{xt_symbol}信息查询失败")
                continue

            if not data["ExpireDate"] and "00" not in symbol:
                continue

            if product == Product.OPTION:
                contract: ContractData = process_futures_option(data, symbol, exch, gateway.gateway_name)
            else:
                contract: ContractData = ContractData(
                    symbol=symbol,
                    exchange=exch,
                    name=data["InstrumentName"],
                    product=product,
                    size=data["VolumeMultiple"],
                    pricetick=data["PriceTick"],
                    history_data=False,
                    gateway_name=gateway.gateway_name,
                )
            if contract:
                symbol_contract_map[(symbol, exch)] = contract
                symbol_limit_map[contract.vt_symbol] = (
                    data["UpStopPrice"],
                    data["DownStopPrice"],
                )
                gateway.on_contract(contract)
                account_type_symbol_map.setdefault(account_type, set()).add((symbol, exch))

    def query_future_contracts(self, gateway: XtGatewayBase) -> None:
        """查询期货合约信息"""

        markets: list = [
            "中金所期货",
            "上期所期货",
            "能源中心期货",
            "大商所期货",
            "郑商所期货",
            "广期所期货",
        ]
        self._query_future_exchange_contracts(gateway, markets, "FUTURE")

    def query_future_option_contracts(self, gateway: XtGatewayBase) -> None:
        """查询期货期权合约信息"""
        markets: list[str] = [
            "中金所期权",
            "上期所期权",
            "能源中心期权",
            "大商所期权",
            "郑商所期权",
            "广期所期权",
        ]
        self._query_future_exchange_contracts(gateway, markets, "FUTURE_OPTION")

    @staticmethod
    def query_option_contracts(gateway: XtGatewayBase) -> None:
        """查询期权合约信息"""
        xt_symbols: list[str] = []

        markets: list[str] = [
            "上证期权",
            "深证期权",
        ]

        for i in markets:
            names: list = xtdata.get_stock_list_in_sector(i)
            xt_symbols.extend(names)

        for xt_symbol in xt_symbols:
            """"""
            _, xt_exchange = xt_symbol.split(".")

            symbol, xt_exchange = xt_symbol.split(".")
            exch = EXCHANGE_XT2VT[xt_exchange]

            if (symbol, exch) in symbol_contract_map:
                contract: ContractData = symbol_contract_map[(symbol, exch)]
                if gateway.gateway_name not in contract.gateway_names:
                    contract.gateway_names.append(gateway.gateway_name)
                    gateway.on_contract(contract)
                continue

            # 筛选期权合约合约（ETF期权代码为8位）
            if len(symbol) != 8:
                return None

            # 查询转换数据
            data: dict = xtdata.get_instrument_detail(xt_symbol, True)

            name: str = data["InstrumentName"]
            if "购" in name:
                option_type = OptionType.CALL
            elif "沽" in name:
                option_type = OptionType.PUT
            else:
                return None

            if "A" in name:
                option_index = str(data["OptExercisePrice"]) + "-A"
            else:
                option_index = str(data["OptExercisePrice"]) + "-M"

            contract: ContractData = ContractData(
                symbol=data["InstrumentID"],
                exchange=exch,
                name=data["InstrumentName"],
                product=Product.OPTION,
                size=data["VolumeMultiple"],
                pricetick=data["PriceTick"],
                min_volume=data["MinLimitOrderVolume"],
                option_strike=data["OptExercisePrice"],
                option_listed=datetime.strptime(data["OpenDate"], "%Y%m%d"),
                expiry=datetime.strptime(data["ExpireDate"], "%Y%m%d"),
                option_portfolio=data["OptUndlCode"] + "_O",
                option_index=option_index,
                option_type=option_type,
                option_underlying=data["OptUndlCode"] + "-" + str(data["ExpireDate"])[:6],
                gateway_name=gateway.gateway_name,
            )

            symbol_limit_map[contract.vt_symbol] = (data["UpStopPrice"], data["DownStopPrice"])

            if contract:
                symbol_contract_map[(contract.symbol, contract.exchange)] = contract
                gateway.on_contract(contract)

    def subscribe(self, req: SubscribeRequest, gateway_name: str) -> None:
        """订阅行情"""
        if (req.symbol, req.exchange) not in symbol_contract_map:
            return

        if (req.symbol, req.exchange) in self.gateway_subscriptions:
            self.gateway_subscriptions[(req.symbol, req.exchange)].add(gateway_name)
            return  # 已经订阅过该合约

        xt_exchange: str = EXCHANGE_VT2XT[req.exchange]
        if xt_exchange in {"SH", "SZ"} and len(req.symbol) > 6:
            xt_exchange += "O"

        xt_symbol: str = req.symbol + "." + xt_exchange

        # xtdata.subscribe_quote(stock_code=xt_symbol, period="tick", callback=self.onMarketData)
        xtdata.subscribe_whole_quote([xt_symbol], callback=self.onMarketData)
        self.gateway_subscriptions[(req.symbol, req.exchange)] = {gateway_name}

    def close(self) -> None:
        """关闭"""
        if self.inited:
            xtdata.disconnect()
            self.inited = False

        if hasattr(self, "lock"):
            self.lock.release(force=True)

        if hasattr(self, "lock_filepath"):
            try:
                os.remove(self.lock_filepath)
            except Exception:
                pass


def generate_datetime(timestamp: int, millisecond: bool = True) -> datetime:
    """生成本地时间"""
    if millisecond:
        dt: datetime = datetime.fromtimestamp(timestamp / 1000)
    else:
        dt: datetime = datetime.fromtimestamp(timestamp)
    dt: datetime = dt.replace(tzinfo=CHINA_TZ)
    return dt


def process_futures_option(data: dict, symbol: str, exch: Exchange, gateway_name: str) -> ContractData | None:
    """处理期货期权"""
    # 筛选期权合约
    option_strike: float = data["OptExercisePrice"]
    if not option_strike:
        return None

    # 移除产品前缀
    ix = 0
    for ix, w in enumerate(symbol):  # noqa
        if w.isdigit():
            break

    suffix: str = symbol[ix:]

    # 过滤非期权合约
    if "(" in symbol or " " in symbol:
        return None

    # 判断期权类型
    if "C" in suffix:
        option_type = OptionType.CALL
    elif "P" in suffix:
        option_type = OptionType.PUT
    else:
        return None

    # 获取期权标的
    if "-" in symbol:
        option_underlying: str = symbol.split("-")[0]
    else:
        option_underlying: str = data["OptUndlCode"]

    # 转换数据
    contract: ContractData = ContractData(
        symbol=data["InstrumentID"],
        exchange=exch,
        name=data["InstrumentName"],
        product=Product.OPTION,
        size=data["VolumeMultiple"],
        pricetick=data["PriceTick"],
        min_volume=data["MinLimitOrderVolume"],
        option_strike=data["OptExercisePrice"],
        option_listed=datetime.strptime(data["OpenDate"], "%Y%m%d"),
        expiry=datetime.strptime(data["ExpireDate"], "%Y%m%d"),
        option_index=str(data["OptExercisePrice"]),
        option_type=option_type,
        option_underlying=option_underlying,
        gateway_name=gateway_name,
    )

    if contract.exchange == Exchange.CZCE:
        contract.option_portfolio = data["ProductID"][:-1]
    else:
        contract.option_portfolio = data["ProductID"]

    symbol_limit_map[contract.vt_symbol] = (data["UpStopPrice"], data["DownStopPrice"])

    return contract


class XtMdApiManager:
    """XT API管理器"""

    def __init__(self):
        """构造函数"""
        self.md_apis: dict[str, XtMdApi] = {}
        self.md_api_user: dict[str, set[str]] = {}
        self.manager_lock = Lock()

    def get_md_api(self, gateway: XtGatewayBase) -> XtMdApi:
        """注册行情API"""
        key = (gateway.ip, gateway.port)
        if key not in self.md_apis:
            self.manager_lock.acquire(timeout=300)
            try:
                gateway.write_log(f"创建新的行情连接{gateway.ip}:{gateway.port}")
                self.md_apis[key] = XtMdApi()
                self.md_apis[key].add_gateway(gateway)
                self.md_apis[key].connect(
                    gateway.ip,
                    gateway.port,
                    gateway.token,
                    gateway.server_pool_list,
                )
            except Exception as e:
                gateway.write_log(f"创建行情接口时发生异常：{str(e)}")
            finally:
                self.manager_lock.release()
        else:
            gateway.write_log(f"复用已有行情接口{gateway.ip}:{gateway.port}")
            self.md_apis[key].add_gateway(gateway)

        self.md_api_user.setdefault(key, set()).add(gateway.gateway_name)
        return self.md_apis[key]

    def remove_gateway(self, gateway: XtGatewayBase):
        """移除网关"""
        # 移除行情API关联
        md_key = (gateway.ip, gateway.port)
        md_api = self.md_apis.get(md_key, None)
        if md_api:
            self.manager_lock.acquire(timeout=300)
            try:
                md_api.remove_gateway(gateway)
                self.md_api_user.get(md_key, set()).discard(gateway.gateway_name)
                gateway.write_log("已从行情接口移除网关关联")
                if not self.md_api_user[md_key]:
                    # 如果没有用户使用该API，则关闭并删除
                    md_api.close()
                    self.md_apis.pop(md_key, None)
                    self.md_api_user.pop(md_key, None)
            except Exception as e:
                gateway.write_log(f"移除网关关联时发生异常：{str(e)}")
            finally:
                self.manager_lock.release()


xt_md_api_manager = XtMdApiManager()
