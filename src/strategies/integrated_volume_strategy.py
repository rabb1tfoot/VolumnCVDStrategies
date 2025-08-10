import numpy as np
import pandas as pd
from jesse.strategies import Strategy
from jesse.services import logger
from jesse.indicators import rsi, sma

class IntegratedVolumeStrategy(Strategy):
    def __init__(self):
        super().__init__()
        # 전략 파라미터
        self.scalping_enabled = True
        self.swing_enabled = True
        self.risk_reward_ratio = 2.0

    def should_long(self) -> bool:
        # 통합 스캘핑 전략 조건
        if self.scalping_enabled and self._scalping_long_conditions():
            return True
            
        # 통합 스윙 전략 조건
        if self.swing_enabled and self._swing_long_conditions():
            return True
            
        return False

    def should_short(self) -> bool:
        # 숏 포지션은 예제 생략 (필요시 구현)
        return False

    def go_long(self):
        # 진입 가격
        entry_price = self.price
        
        # 포지션 크기 계산
        qty = self.calculate_position_size(entry_price)
        
        # 스캘핑 vs 스윙에 따른 손절/익절 설정
        if self._scalping_long_conditions():
            stop_loss = self._scalping_stop_loss(entry_price)
            take_profit = self._scalping_take_profit(entry_price)
        else:
            stop_loss = self._swing_stop_loss(entry_price)
            take_profit = self._swing_take_profit(entry_price)
        
        # 포지션 진입
        self.buy = qty, entry_price
        self.stop_loss = qty, stop_loss
        self.take_profit = qty, take_profit
        
        # 로깅
        logger.info(f"LONG 진입: {qty}@{entry_price}, SL: {stop_loss}, TP: {take_profit}")

    def update_position(self):
        # 추적 손절 또는 동적 익절 로직 추가 가능
        pass

    def _scalping_long_conditions(self) -> bool:
        """통합 스캘핑 전략 롱 조건"""
        # 1. 가격이 Volume Profile 주요 저항선(POC) 근접
        near_poc = self._is_near_poc(resistance=True)
        
        # 2. CVD 급격한 상승 (1분기준 20% 이상 증가)
        cvd_spike = self.cvd > self.cvd.shift(1) * 1.2
        
        # 3. OBV 상승 추세 (단기 이평 > 장기 이평)
        obv_trend = self.obv > sma(self.obv, 5) > sma(self.obv, 20)
        
        # 4. Market Profile Poor High/Single Prints 돌파
        mp_breakout = self._mp_poor_high_breakout()
        
        return near_poc and cvd_spike and obv_trend and mp_breakout

    def _swing_long_conditions(self) -> bool:
        """통합 스윙 전략 롱 조건"""
        # 1. 주간 Value Area 이탈
        weekly_va_break = self._weekly_value_area_break()
        
        # 2. OBV 강세 다이버전스
        obv_divergence = self._obv_bullish_divergence()
        
        # 3. CVD 강세 다이버전스
        cvd_divergence = self._cvd_bullish_divergence()
        
        # 4. Volume Profile 저거래량 구간 통과 확인
        lvz_pass = self._low_volume_zone_pass()
        
        return weekly_va_break and obv_divergence and cvd_divergence and lvz_pass

    def _scalping_stop_loss(self, entry_price: float) -> float:
        """스캘핑 전략 손절가 계산"""
        # 돌파 지지선 아래 0.5%
        return entry_price * 0.995

    def _scalping_take_profit(self, entry_price: float) -> float:
        """스캘핑 전략 익절가 계산"""
        # 위험-보상 비율 기반
        return entry_price * (1 + self.risk_reward_ratio * 0.005)

    def _swing_stop_loss(self, entry_price: float) -> float:
        """스윙 전략 손절가 계산"""
        # 주요 지지선 아래 1%
        return entry_price * 0.99

    def _swing_take_profit(self, entry_price: float) -> float:
        """스윙 전략 익절가 계산"""
        # Poor High 복구 지점 또는 위험-보상 비율
        return entry_price * (1 + self.risk_reward_ratio * 0.01)

    # --------------------- 보조 함수 ---------------------
    def _is_near_poc(self, resistance: bool = True, threshold: float = 0.005) -> bool:
        """Volume Profile POC 근접 여부"""
        current_poc = self.volume_profile.get_poc()
        price_diff = abs(self.close - current_poc) / current_poc
        if resistance:
            return self.close > current_poc and price_diff < threshold
        else:
            return self.close < current_poc and price_diff < threshold

    def _mp_poor_high_breakout(self) -> bool:
        """Market Profile Poor High/Single Prints 돌파"""
        # 구현 생략 (Market Profile 라이브러리 통합 필요)
        return True

    def _weekly_value_area_break(self) -> bool:
        """주간 Value Area 이탈"""
        # 구현 생략 (주간 데이터 분석 필요)
        return True

    def _obv_bullish_divergence(self) -> bool:
        """OBV 강세 다이버전스 감지"""
        # 가격 신저가 vs OBV 고저점 유지
        return self.low < self.low.shift(1) and self.obv > self.obv.shift(1)

    def _cvd_bullish_divergence(self) -> bool:
        """CVD 강세 다이버전스 감지"""
        # 가격 신저가 vs CVD 고저점 유지
        return self.low < self.low.shift(1) and self.cvd > self.cvd.shift(1)

    def _low_volume_zone_pass(self) -> bool:
        """저거래량 구간 통과 확인"""
        # Volume Profile 저거래량 영역 통과 로직
        return True

    def calculate_position_size(self, entry_price: float) -> float:
        """위험 관리 기반 포지션 크기 계산"""
        risk_per_trade = 0.01  # 거래당 위험 1%
        account_equity = self.balance
        risk_amount = account_equity * risk_per_trade
        
        if self._scalping_long_conditions():
            stop_loss = self._scalping_stop_loss(entry_price)
        else:
            stop_loss = self._swing_stop_loss(entry_price)
            
        risk_per_share = entry_price - stop_loss
        return round(risk_amount / risk_per_share, 4)

    @property
    def obv(self):
        """On-Balance Volume"""
        return self.candles[:, 5]  # OBV 데이터

    @property
    def cvd(self):
        """Cumulative Volume Delta"""
        return self.candles[:, 6]  # CVD 데이터

    @property
    def volume_profile(self):
        """Volume Profile 객체"""
        # 실제 구현에서는 Volume Profile 계산 로직 필요
        class DummyProfile:
            def get_poc(self):
                return self.candles[-50:].mean()
        return DummyProfile()