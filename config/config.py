CONFIG_PARAMS = {
    "mongodb_params": {
        "host": "localhost", #change later when move to cluster
        "port": 27017
    },
    "tda_api": {
        "resource_url": "https://api.tdameritrade.com/v1/marketdata/chains",
        "uri_params": "?apikey=FAZ4GPL25XE2CA5X1HPOUBGLXHRC9VK6&symbol={}&contractType=ALL&strikeCount=10&includeQuotes=TRUE&strategy=SINGLE&optionType=S"
    }
}


class Config(object):
    def __init__(self, key_params):
        self.params = CONFIG_PARAMS[key_params]