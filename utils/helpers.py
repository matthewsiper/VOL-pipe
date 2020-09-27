def get_data_for_graph(res, option_type='calls'):
    strikes = []
    expiries = []
    ivs = []
    for expiry_key, contracts_list in res[option_type].items():
        expiries.append(expiry_key)
        for contract_dict in contracts_list:
            strike = float(contract_dict["strike"])
            strikes.append(strike)
            iv = round(float(contract_dict["volatility"]), 2)
            ivs.append(iv)
    strikes = sorted(strikes)
    return {'strikes': strikes, 'expiries': expiries, 'ivs': ivs, "datetime": res["quoteTime"]}