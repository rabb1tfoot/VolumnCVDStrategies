import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import datetime
import requests
import json

# 환경 변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

class AlertSystem:
    """경고 알림 시스템 (Telegram/Slack)"""
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        
    def send_alert(self, message, level='INFO'):
        """경고 메시지 전송"""
        if level in ['ERROR', 'CRITICAL']:
            if self.telegram_token and self.telegram_chat_id:
                self._send_telegram(f"[{level}] {message}")
            if self.slack_webhook:
                self._send_slack(f"[{level}] {message}")
                
    def _send_telegram(self, message):
        """Telegram 메시지 전송"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message
            }
            response = requests.post(url, data=payload)
            if response.status_code != 200:
                logging.error(f"Telegram alert failed: {response.text}")
        except Exception as e:
            logging.error(f"Telegram send error: {e}")
            
    def _send_slack(self, message):
        """Slack 메시지 전송"""
        try:
            payload = {'text': message}
            response = requests.post(
                self.slack_webhook,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                logging.error(f"Slack alert failed: {response.text}")
        except Exception as e:
            logging.error(f"Slack send error: {e}")

class TradingLogger:
    def __init__(self, name='trading_system'):
        """
        고도화된 거래 시스템 로거
        
        :param name: 로거 이름
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.alert_system = AlertSystem()
        
        # 로그 포맷 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 콘솔 핸들러 설정 (INFO 레벨 이상)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러 설정 (DEBUG 레벨 이상)
        log_dir = os.path.join(os.path.dirname(__file__), '../logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(
            log_dir,
            f"trading_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=20*1024*1024,  # 20MB
            backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
    def get_logger(self):
        """로거 객체 반환"""
        return self.logger
        
    def log_trade(self, action, symbol, amount, price=None, order_id=None):
        """거래 내역 상세 로깅"""
        message = f"TRADE {action} {amount} of {symbol}"
        if price:
            message += f" at {price}"
        if order_id:
            message += f" | Order ID: {order_id}"
        self.logger.info(message)
        
    def log_signal(self, signal_type, symbol, price, indicators):
        """매매 신호 상세 로깅"""
        message = f"SIGNAL {signal_type} for {symbol} at {price} | Indicators: "
        message += ', '.join([f"{k}={v:.4f}" for k, v in indicators.items()])
        self.logger.info(message)
        
    def log_api_call(self, endpoint, params, response_status, latency):
        """API 호출 로깅"""
        message = f"API {endpoint} - Status: {response_status} | "
        message += f"Params: {params} | Latency: {latency:.2f}ms"
        self.logger.debug(message)
        
    def log_error(self, error_msg, exc_info=False, alert=True):
        """오류 로깅 및 경고 전송"""
        self.logger.error(error_msg, exc_info=exc_info)
        if alert:
            self.alert_system.send_alert(error_msg, 'ERROR')
        
    def log_system_event(self, event, details=None, alert_level=None):
        """시스템 이벤트 로깅 및 경고 전송"""
        message = f"SYSTEM {event}"
        if details:
            message += f" | Details: {details}"
        self.logger.info(message)
        
        if alert_level:
            self.alert_system.send_alert(message, alert_level)
            
    def log_performance(self, metric, value, symbol=None):
        """성능 메트릭 로깅"""
        message = f"PERF {metric}"
        if symbol:
            message += f" [{symbol}]"
        message += f": {value:.4f}"
        self.logger.info(message)

# 전역 로거 인스턴스 생성
logger = TradingLogger().get_logger()

# 편의 함수
def log_trade(action, symbol, amount, price=None, order_id=None):
    TradingLogger().log_trade(action, symbol, amount, price, order_id)
    
def log_signal(signal_type, symbol, price, indicators):
    TradingLogger().log_signal(signal_type, symbol, price, indicators)
    
def log_api_call(endpoint, params, response_status, latency):
    TradingLogger().log_api_call(endpoint, params, response_status, latency)
    
def log_error(error_msg, exc_info=False, alert=True):
    TradingLogger().log_error(error_msg, exc_info, alert)
    
def log_system_event(event, details=None, alert_level=None):
    TradingLogger().log_system_event(event, details, alert_level)
    
def log_performance(metric, value, symbol=None):
    TradingLogger().log_performance(metric, value, symbol)

if __name__ == "__main__":
    # 로거 테스트
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # 커스텀 로깅 메소드 테스트
    log_trade('BUY', 'BTC/USDT', 0.1, 50000, 'ORDER123')
    log_signal('BUY', 'BTC/USDT', 49500, {'RSI': 30.5, 'Volume': 1200})
    log_api_call('/order', {'symbol': 'BTC/USDT'}, 200, 150.3)
    log_error("Critical API failure", alert=True)
    log_system_event("System startup", {"version": "1.0.0"}, 'INFO')
    log_performance("Sharpe Ratio", 1.75, 'BTC/USDT')