import time
from json import JSONDecodeError
import requests


class API:

    @staticmethod
    def btc():
        try:
            bit_stamp_tick = requests.get('https://www.bitstamp.net/api/ticker/')
            status = bit_stamp_tick.status_code
        except ConnectionError:
            bit_stamp_tick = ""
            status = 404
            pass
        if status == 200:
            try:
                price_float = float(bit_stamp_tick.json()['last'])
                price_str = str(f"{int(price_float):,d}") + "." + str(
                    round(abs(price_float - int(price_float)), 1)).split(".")[1]
                return price_str, price_float
            except JSONDecodeError:
                return None
            except Exception:
                return None
        else:
            return None

    @staticmethod
    def currency_exchange(currency):
        try:
            url = "https://currency-exchange.p.rapidapi.com/exchange"
            querystring = {"q": "1.0", "from": "USD", "to": f"{currency}"}
            # SGD, CAD, EUR, MAD
            headers = {
                'x-rapidapi-host': "currency-exchange.p.rapidapi.com",
                'x-rapidapi-key': "18319ab852msh3867d3eff319f6ep12eaafjsn2e2826a86312"
                # visit the website https://rapidapi.com/ and get your own key, it's free :).
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
        except Exception:
            return None
        return float(response.text)



class ui:
    @staticmethod
    def xx():
        global old_btc_price
        for i in range(1, 2):
            updated_btc_price = API().btc()[1]
            if updated_btc_price > old_btc_price:
                print("up", updated_btc_price, old_btc_price)
            elif updated_btc_price < old_btc_price:
                print("down", updated_btc_price, old_btc_price)
            else:
                print(updated_btc_price, old_btc_price)
            old_btc_price = updated_btc_price if updated_btc_price is not None else old_btc_price


# ------------------------------

# ------------------------------

cc = API.currency_exchange("SGD")
print("xx ", cc, type(cc))

