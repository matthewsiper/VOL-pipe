from config.config import Config

import requests

CONFIG = Config("tda_api")


class SurfaceWorker(object):
    def __init__(self):
        self.raw_url = CONFIG.params["resource_url"] + CONFIG.params["uri_params"]

    def run(self, ticker='', mode='batch', start_time=""):
        try:
            if mode == 'batch':
                if start_time:
                    return self.get_opt_data(ticker, start_time=start_time)
                return self.get_opt_data(ticker)
            elif mode == 'replay':
                return self.get_opt_data(ticker)
        except:
            msg = f'Error in run mode {mode} for tickers {ticker}'
            raise Exception(msg)

    def get_opt_data(self, ticker, start_time=""):
        try:
            resource_url = self.raw_url.format(ticker)
            res = requests.get(resource_url).json()
            surface_dict = {}
            surface_dict["symbol"] = res["symbol"]
            surface_dict["quoteTime"] = res["underlying"]["quoteTime"]
            call_exp_date_map = res["callExpDateMap"]
            put_exp_date_map = res["putExpDateMap"]

            exp_idx = 0
            expiry_dict = {}

            for expiry, call in call_exp_date_map.items():
                formatted_expiry = expiry.split(":")[0]
                calls_per_expiry = []
                for strike, call_list in call.items():
                    calls_per_expiry.append({"strike": strike, "symbol": call_list[0]["symbol"],
                                                                 "mark": call_list[0]["mark"], "volatility": call_list[0]["volatility"],
                                                                 "delta": call_list[0]["delta"],  "gamma": call_list[0]["gamma"],
                                                                 "vega": call_list[0]["vega"], "theta": call_list[0]["theta"]})
                expiry_dict[formatted_expiry] = calls_per_expiry
                exp_idx += 1
                if exp_idx > 8:
                    break
            surface_dict["calls"] = expiry_dict

            exp_idx = 0
            expiry_dict = {}
            for expiry, put in put_exp_date_map.items():
                formatted_expiry = expiry.split(":")[0]
                puts_per_expiry = []
                for strike, put_list in put.items():
                    puts_per_expiry.append({"strike": strike, "symbol": put_list[0]["symbol"],
                                            "mark": put_list[0]["mark"], "volatility": put_list[0]["volatility"],
                                            "delta": put_list[0]["delta"],  "gamma": put_list[0]["gamma"],
                                            "vega": put_list[0]["vega"], "theta": put_list[0]["theta"]})
                expiry_dict[formatted_expiry] = puts_per_expiry
                exp_idx += 1
                if exp_idx > 8:
                    break
            surface_dict["puts"] = expiry_dict
            if start_time:
                surface_dict["start_time"] = start_time
            return surface_dict
        except:
            msg = "Error in get_opt_data"
            raise Exception(msg)
