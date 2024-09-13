import requests
import time
import hashlib
import hmac
import json
import os

class BybitDemoSession:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api-demo.bybit.com"

    def _generate_signature(self, params):
        param_str = '&'.join([f'{k}={params[k]}' for k in sorted(params)])
        return hmac.new(self.api_secret.encode('utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def send_request(self, method, endpoint, params=None):
        if params is None:
            params = {}

        params['api_key'] = self.api_key
        params['timestamp'] = self._get_timestamp()
        params['sign'] = self._generate_signature(params)

        if method == "GET":
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
        elif method == "POST":
            response = requests.post(f"{self.base_url}{endpoint}", json=params)
        else:
            raise ValueError("Unsupported HTTP method")

        return response.json()

    def get_historical_data(self, symbol, interval, limit):
        try:
            endpoint = "/v5/market/kline"
            params = {
                "category": "linear",
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            response = self.send_request("GET", endpoint, params)
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")
            return response['result']['list']
        except Exception as e:
            print(f"Ошибка при получении исторических данных: {e}")
            return None
        
    def set_leverage(self, symbol, leverage):
        try:
            endpoint = "/v5/position/set-leverage"
            params = {
                "category": "linear",
                "symbol": symbol,
                "buyLeverage": str(leverage),
                "sellLeverage": str(leverage)
            }
            response = self.send_request("POST", endpoint, params)
            if response['retCode'] != 0:
                # If the error is 'leverage not modified', treat it as a non-critical issue
                if response['retMsg'] == 'leverage not modified':
                    print(f"Leverage is already set to {leverage}x for {symbol}.")
                else:
                    raise Exception(f"API Error: {response['retMsg']}")
            else:
                print(f"Leverage set to {leverage}x for {symbol}.")
        except Exception as e:
            print(f"Error setting leverage: {e}")


    def place_order(self, symbol, side, qty, current_price, leverage, stop_loss=None, take_profit=None):
        try:
            # Set leverage before placing an order
            self.set_leverage(symbol, leverage=leverage)

            endpoint = "/v5/order/create"
            position_mode = "one_way"  # Adjust based on your account settings

            # Determine position index based on position mode
            if position_mode == "hedge":
                position_idx = 1 if side.lower() == 'buy' else 2
            else:
                position_idx = 0

            # Use Limit orders
            order_type = "Limit"
            time_in_force = "GTC"  # Good 'Til Canceled for Limit orders

            # Adjust price to improve likelihood of execution
            # For Buy orders, set price slightly below current price
            # For Sell orders, set price slightly above current price
            if side.lower() == 'buy':
                price = current_price * 0.9999  # Slightly below current price
            else:
                price = current_price * 1.0001  # Slightly above current price

            # Round the price to the appropriate tick size (e.g., 2 decimal places)
            price = round(price, 2)

            # Prepare order parameters
            order_params = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": str(qty),
                "price": str(price),
                "positionIdx": position_idx,
                "timeInForce": time_in_force
            }

            # Include tpslMode when setting TP/SL
            if stop_loss or take_profit:
                order_params["tpslMode"] = "Full"  # Apply TP/SL to the entire position

            # Include stop loss parameters
            if stop_loss:
                order_params["stopLoss"] = str(stop_loss)
                order_params["slTriggerBy"] = "LastPrice"
                order_params["slOrderType"] = "Market"  # Use Market order for SL execution

            # Include take profit parameters
            if take_profit:
                order_params["takeProfit"] = str(take_profit)
                order_params["tpTriggerBy"] = "LastPrice"
                order_params["tpOrderType"] = "Market"  # Use Market order for TP execution

            response = self.send_request("POST", endpoint, order_params)
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")

            return response['result']
        except Exception as e:
            print(f"Error placing order: {e}")
            return None







    def get_open_positions(self, symbol):
        try:
            endpoint = "/v5/position/list"
            params = {
                "category": "linear",
                "symbol": symbol
            }
            response = self.send_request("GET", endpoint, params)
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")

            positions = response['result']['list']
            active_positions = [pos for pos in positions if float(pos['size']) > 0]

            if active_positions:
                print("Active Open Positions:")
                print(json.dumps(active_positions, indent=4))
            else:
                print("No opened positions.")

            return active_positions
        except Exception as e:
            print(f"Ошибка при получении позиций: {e}")
            return None
        



    def get_open_orders(self, symbol):
        try:
            endpoint = "/v5/order/realtime"
            params = {
                "category": "linear",
                "symbol": symbol
            }
            response = self.send_request("GET", endpoint, params)
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")

            open_orders = response['result']['list']
            current_time = time.time()
            orders_to_cancel = []

            for order in open_orders:
                created_time = int(order['createdTime']) / 1000
                if current_time - created_time > 180:  # 180 seconds = 3 minutes
                    orders_to_cancel.append(order)

            if orders_to_cancel:
                for order in orders_to_cancel:
                    self.cancel_order(order['orderId'], symbol)
                    print(f"Order {order['orderId']} cancelled as it was older than 3 minutes.")
            else:
                print("No orders older than 3 minutes.")

            return open_orders
        except Exception as e:
            print(f"Ошибка при получении лимитных ордеров: {e}")
            return None

    def cancel_order(self, order_id, symbol):
        try:
            endpoint = "/v5/order/cancel"
            params = {
                "category": "linear",
                "symbol": symbol,
                "orderId": order_id
            }
            response = self.send_request("POST", endpoint, params)
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")
            print(f"Order {order_id} successfully cancelled.")
        except Exception as e:
            print(f"Ошибка при отмене ордера {order_id}: {e}")

    def get_last_closed_position(self, symbol):
        try:
            endpoint = "/v5/position/list"
            params = {
                "category": "linear",
                "symbol": symbol
            }
            response = self.send_request("GET", endpoint, params)
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")

            positions = response['result']['list']
            closed_positions = [pos for pos in positions if float(pos['size']) == 0]

            if closed_positions:
                last_closed_position = max(closed_positions, key=lambda x: int(x['updatedTime']))
                return last_closed_position
            else:
                return None
        except Exception as e:
            print(f"Error fetching last closed position: {e}")
            return None
        
    def get_real_time_price(self, symbol):
        try:
            endpoint = "/v5/market/tickers"
            params = {
                "category": "linear",
                "symbol": symbol
            }
            response = self.send_request("GET", endpoint, params)
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")
            return float(response['result']['list'][0]['lastPrice'])
        except Exception as e:
            print(f"Ошибка при получении текущей цены: {e}")
            return None