import os
import time
import ccxt
from dotenv import load_dotenv
from .custom_logger import logger  # 로깅 모듈에서 logger 가져오기

# 환경 변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

class OrderExecutor:
    def __init__(self):
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.symbol = os.getenv('TRADE_SYMBOL', 'BTC/USDT')
        self.trade_amount = float(os.getenv('TRADE_AMOUNT', 100))
        
        # Bybit 연결 초기화 (선물 거래)
        self.exchange = ccxt.bybit({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'
            }
        })
        self.local_order_state = {}  # 로컬 주문 상태 추적
        
    def execute_with_retry(self, func, max_retries=5, *args, **kwargs):
        """지수 백오프 재시도 로직"""
        retry = 0
        while retry < max_retries:
            try:
                return func(*args, **kwargs)
            except ccxt.RateLimitExceeded as e:
                wait = 2 ** retry
                logger.warning(f"Rate limit exceeded. Retrying in {wait} seconds...")
                time.sleep(wait)
                retry += 1
            except ccxt.NetworkError as e:
                logger.error(f"Network error: {e}. Reconnecting...")
                self.reconnect()
                retry += 1
            except ccxt.InsufficientFunds as e:
                logger.error(f"Insufficient funds: {e}")
                return None
            except ccxt.InvalidOrder as e:
                logger.error(f"Invalid order parameters: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        logger.error(f"Operation failed after {max_retries} retries")
        return None
        
    def reconnect(self):
        """거래소 연결 재설정"""
        try:
            self.exchange = ccxt.bybit({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            })
            logger.info("Exchange connection reestablished")
            self.sync_order_state()  # 재연결 후 주문 상태 동기화
            return True
        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            return False
            
    def sync_order_state(self):
        """주문 상태 동기화 (네트워크 단절 후 복구 시)"""
        try:
            open_orders = self.exchange.fetch_open_orders(self.symbol)
            for order in open_orders:
                self.local_order_state[order['id']] = order['status']
            logger.info(f"Synced {len(open_orders)} open orders")
        except Exception as e:
            logger.error(f"Order state sync failed: {e}")
        
    def place_market_order(self, side, amount=None, stop_loss=None, take_profit=None, reduce_only=False):
        """
        시장가 주문 실행
        :param reduce_only: 포지션 청산 전용 주문 (기본값: False)
        """
        if amount is None:
            amount = self.trade_amount
            
        def _place_order():
            params = {
                'timeInForce': 'GTC',
                'reduceOnly': reduce_only
            }
            if stop_loss is not None:
                params['stopLoss'] = stop_loss
            if take_profit is not None:
                params['takeProfit'] = take_profit
                
            order = self.exchange.create_order(
                symbol=self.symbol,
                type='market',
                side=side,
                amount=amount,
                params=params
            )
            self.local_order_state[order['id']] = order['status']
            logger.info(f"Placed {side} market order: {order['id']} for {amount} {self.symbol}")
            logger.debug(f"Order params: {params}")
            return order
            
        return self.execute_with_retry(_place_order)
        
    def place_limit_order(self, side, price, amount=None, stop_loss=None, take_profit=None, reduce_only=False):
        """
        지정가 주문 실행 (GTC: Good Till Cancel)
        :param reduce_only: 포지션 청산 전용 주문 (기본값: False)
        """
        if amount is None:
            amount = self.trade_amount
            
        def _place_order():
            params = {
                'timeInForce': 'GTC',
                'reduceOnly': reduce_only
            }
            if stop_loss is not None:
                params['stopLoss'] = stop_loss
            if take_profit is not None:
                params['takeProfit'] = take_profit
                
            order = self.exchange.create_order(
                symbol=self.symbol,
                type='limit',
                side=side,
                amount=amount,
                price=price,
                params=params
            )
            self.local_order_state[order['id']] = order['status']
            logger.info(f"Placed {side} limit order at {price}: {order['id']} for {amount} {self.symbol}")
            logger.debug(f"Order params: {params}")
            return order
            
        return self.execute_with_retry(_place_order)
        
    def safe_market_order(self, side, amount=None, max_slippage=0.5):
        """
        슬리피지 보호가 적용된 안전한 시장가 주문
        :param max_slippage: 허용 최대 슬리피지 (%)
        """
        if amount is None:
            amount = self.trade_amount
            
        # 현재 호가창 가격 조회
        order_book = self.exchange.fetch_order_book(self.symbol)
        best_bid = order_book['bids'][0][0] if order_book['bids'] else None
        best_ask = order_book['asks'][0][0] if order_book['asks'] else None
        
        if not best_bid or not best_ask:
            logger.warning("Failed to get order book. Using regular market order")
            return self.place_market_order(side, amount)
            
        # 매수 주문 시: best_ask * (1 + max_slippage/100)
        # 매도 주문 시: best_bid * (1 - max_slippage/100)
        if side == 'buy':
            limit_price = best_ask * (1 + max_slippage/100)
            return self.place_limit_order(side, limit_price, amount)
        else:
            limit_price = best_bid * (1 - max_slippage/100)
            return self.place_limit_order(side, limit_price, amount)
            
    def close_all_positions(self, use_safe_order=False):
        """모든 포지션 청산 (안전 주문 옵션 포함)"""
        def _close_positions():
            positions = self.exchange.fetch_positions([self.symbol])
            for position in positions:
                contracts = float(position['contracts'])
                if contracts > 0:
                    side = 'sell' if position['side'] == 'long' else 'buy'
                    
                    if use_safe_order:
                        self.safe_market_order(side, contracts, reduce_only=True)
                    else:
                        self.place_market_order(side, contracts, reduce_only=True)
                        
                    logger.info(f"Closed {position['side']} position of {contracts} contracts")
            return True
            
        return self.execute_with_retry(_close_positions)
            
    def check_order_status(self, order_id):
        """주문 상태 확인"""
        # 로컬 상태 먼저 확인
        if order_id in self.local_order_state:
            status = self.local_order_state[order_id]
            if status in ['closed', 'canceled', 'expired']:
                return status
        
        # 거래소에서 상태 조회
        def _check_status():
            order = self.exchange.fetch_order(order_id, self.symbol)
            self.local_order_state[order_id] = order['status']
            return order['status']
            
        return self.execute_with_retry(_check_status)

if __name__ == "__main__":
    # 테스트 실행 (실제 주문은 발생하지 않음)
    executor = OrderExecutor()
    logger.info("Testing order execution...")
    
    # 시장가 매수 주문 시뮬레이션
    buy_order = executor.place_market_order('buy', 0.001)
    if buy_order:
        logger.info(f"Buy order placed: {buy_order}")
        
    # 포지션 청산 시뮬레이션
    executor.close_all_positions()