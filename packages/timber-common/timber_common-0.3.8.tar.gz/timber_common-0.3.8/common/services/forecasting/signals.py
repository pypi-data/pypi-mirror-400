"""
Signal Generators

Pluggable signal generators for different data domains.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime

from .core import Signal, SignalGenerator, TimeHorizon


class TechnicalSignalGenerator(SignalGenerator):
    """
    Generates signals from technical indicators.
    
    Covers:
    - Trend indicators (MA crossovers, ADX)
    - Momentum indicators (RSI, MACD, Stochastic)
    - Volatility indicators (Bollinger Bands, ATR)
    - Volume indicators (OBV, Volume trends)
    """
    
    @property
    def category(self) -> str:
        return "technical"
    
    def generate(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        context: Dict[str, Any]
    ) -> List[Signal]:
        signals = []
        
        if price_data is None or price_data.empty or len(price_data) < 50:
            return signals
        
        df = price_data.copy()
        if 'Close' in df.columns:
            close = df['Close']
        elif 'close' in df.columns:
            close = df['close']
        else:
            return signals
        
        signals.extend(self._trend_signals(df, close))
        signals.extend(self._momentum_signals(df, close))
        signals.extend(self._volatility_signals(df, close))
        
        if 'Volume' in df.columns:
            volume = df['Volume']
        elif 'volume' in df.columns:
            volume = df['volume']
        else:
            volume = None
        
        if volume is not None:
            signals.extend(self._volume_signals(df, close, volume))
        
        return signals
    
    def _trend_signals(self, df: pd.DataFrame, close: pd.Series) -> List[Signal]:
        signals = []
        
        ma_20 = close.rolling(20).mean()
        ma_50 = close.rolling(50).mean()
        ma_200 = close.rolling(200).mean()
        
        if len(close) >= 200:
            ma_ratio = (ma_50.iloc[-1] / ma_200.iloc[-1]) - 1
            cross_signal = np.clip(ma_ratio * 10, -1, 1)
            price_vs_ma = (close.iloc[-1] - ma_200.iloc[-1]) / ma_200.iloc[-1]
            trend_confidence = min(abs(price_vs_ma) * 5, 1.0)
            
            signals.append(Signal(
                name="ma_crossover",
                value=cross_signal,
                confidence=trend_confidence,
                horizon=TimeHorizon.MEDIUM_TERM,
                category=self.category,
                metadata={'ma_50': ma_50.iloc[-1], 'ma_200': ma_200.iloc[-1]}
            ))
        
        if len(close) >= 20:
            short_trend = (close.iloc[-1] - ma_20.iloc[-1]) / ma_20.iloc[-1]
            signals.append(Signal(
                name="short_trend",
                value=np.clip(short_trend * 20, -1, 1),
                confidence=0.6,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category
            ))
        
        if len(close) >= 14:
            returns = close.pct_change()
            adx_proxy = abs(returns.rolling(14).mean()) / returns.rolling(14).std()
            adx_proxy = adx_proxy.fillna(0)
            trend_strength = np.clip(adx_proxy.iloc[-1], 0, 1)
            direction = np.sign(returns.rolling(14).mean().iloc[-1])
            
            signals.append(Signal(
                name="trend_strength",
                value=direction * trend_strength,
                confidence=trend_strength,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category
            ))
        
        return signals
    
    def _momentum_signals(self, df: pd.DataFrame, close: pd.Series) -> List[Signal]:
        signals = []
        
        # RSI
        if len(close) >= 14:
            delta = close.diff()
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            avg_gain = gains.rolling(14).mean()
            avg_loss = losses.rolling(14).mean()
            
            rs = avg_gain / avg_loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            rsi_value = rsi.iloc[-1]
            
            if rsi_value < 30:
                rsi_signal = (30 - rsi_value) / 30
            elif rsi_value > 70:
                rsi_signal = (70 - rsi_value) / 30
            else:
                rsi_signal = 0
            
            signals.append(Signal(
                name="rsi",
                value=np.clip(rsi_signal, -1, 1),
                confidence=abs(rsi_signal) * 0.8 + 0.2,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category,
                metadata={'rsi': rsi_value}
            ))
        
        # MACD
        if len(close) >= 26:
            ema_12 = close.ewm(span=12, adjust=False).mean()
            ema_26 = close.ewm(span=26, adjust=False).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            histogram = macd_line - signal_line
            
            macd_normalized = histogram.iloc[-1] / close.iloc[-1] * 100
            
            signals.append(Signal(
                name="macd",
                value=np.clip(macd_normalized * 10, -1, 1),
                confidence=0.7,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category,
                metadata={
                    'macd': macd_line.iloc[-1],
                    'signal': signal_line.iloc[-1],
                    'histogram': histogram.iloc[-1]
                }
            ))
        
        # Stochastic
        if 'High' in df.columns:
            high = df['High']
        elif 'high' in df.columns:
            high = df['high']
        else:
            high = None
            
        if 'Low' in df.columns:
            low = df['Low']
        elif 'low' in df.columns:
            low = df['low']
        else:
            low = None
        
        if len(close) >= 14 and high is not None and low is not None:
            lowest_low = low.rolling(14).min()
            highest_high = high.rolling(14).max()
            
            stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
            stoch_d = stoch_k.rolling(3).mean()
            stoch_value = stoch_k.iloc[-1]
            
            if stoch_value < 20:
                stoch_signal = (20 - stoch_value) / 20
            elif stoch_value > 80:
                stoch_signal = (80 - stoch_value) / 20
            else:
                stoch_signal = 0
            
            signals.append(Signal(
                name="stochastic",
                value=np.clip(stoch_signal, -1, 1),
                confidence=abs(stoch_signal) * 0.7 + 0.3,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category,
                metadata={'stoch_k': stoch_value, 'stoch_d': stoch_d.iloc[-1]}
            ))
        
        return signals
    
    def _volatility_signals(self, df: pd.DataFrame, close: pd.Series) -> List[Signal]:
        signals = []
        
        # Bollinger Bands
        if len(close) >= 20:
            ma_20 = close.rolling(20).mean()
            std_20 = close.rolling(20).std()
            
            upper_band = ma_20 + 2 * std_20
            lower_band = ma_20 - 2 * std_20
            
            current_price = close.iloc[-1]
            band_width = upper_band.iloc[-1] - lower_band.iloc[-1]
            
            band_position = (current_price - lower_band.iloc[-1]) / band_width * 2 - 1
            bb_signal = -band_position * 0.8
            
            signals.append(Signal(
                name="bollinger_bands",
                value=np.clip(bb_signal, -1, 1),
                confidence=abs(band_position) * 0.6 + 0.2,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category,
                metadata={
                    'upper': upper_band.iloc[-1],
                    'lower': lower_band.iloc[-1],
                    'position': band_position
                }
            ))
        
        # Volatility regime
        if len(close) >= 60:
            vol_20 = close.pct_change().rolling(20).std() * np.sqrt(252)
            vol_60 = close.pct_change().rolling(60).std() * np.sqrt(252)
            
            vol_ratio = vol_20.iloc[-1] / vol_60.iloc[-1] if vol_60.iloc[-1] > 0 else 1
            
            if vol_ratio > 1.2:
                vol_signal = -0.3
            elif vol_ratio < 0.8:
                vol_signal = 0.2
            else:
                vol_signal = 0
            
            signals.append(Signal(
                name="volatility_regime",
                value=vol_signal,
                confidence=0.5,
                horizon=TimeHorizon.MEDIUM_TERM,
                category=self.category,
                metadata={'vol_20': vol_20.iloc[-1], 'vol_60': vol_60.iloc[-1]}
            ))
        
        return signals
    
    def _volume_signals(
        self,
        df: pd.DataFrame,
        close: pd.Series,
        volume: pd.Series
    ) -> List[Signal]:
        signals = []
        
        if len(volume) >= 20:
            vol_ma = volume.rolling(20).mean()
            vol_ratio = volume.iloc[-1] / vol_ma.iloc[-1] if vol_ma.iloc[-1] > 0 else 1
            
            price_change = close.pct_change().iloc[-1]
            
            if vol_ratio > 1.5:
                vol_signal = np.sign(price_change) * 0.5
            else:
                vol_signal = 0
            
            signals.append(Signal(
                name="volume_confirmation",
                value=np.clip(vol_signal, -1, 1),
                confidence=min(vol_ratio / 2, 1.0),
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category,
                metadata={'volume_ratio': vol_ratio}
            ))
            
            # OBV trend
            obv = (np.sign(close.diff()) * volume).cumsum()
            obv_trend = (obv.iloc[-1] - obv.iloc[-20]) / abs(obv.iloc[-20]) if obv.iloc[-20] != 0 else 0
            
            signals.append(Signal(
                name="obv_trend",
                value=np.clip(obv_trend * 5, -1, 1),
                confidence=0.5,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category
            ))
        
        return signals


class SentimentSignalGenerator(SignalGenerator):
    """
    Generates signals from news and social sentiment data.
    
    Expects context to contain:
    - 'news': List of news items with 'sentiment_score' or raw text
    - 'social': Social media sentiment data
    """
    
    @property
    def category(self) -> str:
        return "sentiment"
    
    def generate(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        context: Dict[str, Any]
    ) -> List[Signal]:
        signals = []
        
        news = context.get('news', [])
        social = context.get('social', {})
        
        if news:
            signals.extend(self._news_signals(news))
        
        if social:
            signals.extend(self._social_signals(social))
        
        return signals
    
    def _news_signals(self, news: List[Dict]) -> List[Signal]:
        signals = []
        
        if not news:
            return signals
        
        sentiments = []
        recency_weights = []
        now = datetime.utcnow()
        
        for i, item in enumerate(news[:20]):
            if 'sentiment_score' in item:
                score = item['sentiment_score']
            elif 'sentiment' in item:
                score = item['sentiment']
            else:
                score = self._estimate_sentiment(
                    item.get('title', '') + ' ' + item.get('summary', '')
                )
            
            sentiments.append(score)
            
            if 'published_utc' in item and item['published_utc']:
                try:
                    pub_time = datetime.fromisoformat(
                        item['published_utc'].replace('Z', '+00:00')
                    ).replace(tzinfo=None)
                    hours_ago = (now - pub_time).total_seconds() / 3600
                    weight = np.exp(-hours_ago / 48)
                except:
                    weight = 0.5
            else:
                weight = 1.0 / (i + 1)
            
            recency_weights.append(weight)
        
        if sentiments:
            weights = np.array(recency_weights)
            weights = weights / weights.sum()
            
            weighted_sentiment = np.average(sentiments, weights=weights)
            sentiment_std = np.std(sentiments) if len(sentiments) > 1 else 0.5
            
            consistency = 1 - min(sentiment_std, 1)
            volume_factor = min(len(news) / 10, 1)
            confidence = consistency * 0.6 + volume_factor * 0.4
            
            signals.append(Signal(
                name="news_sentiment",
                value=np.clip(weighted_sentiment, -1, 1),
                confidence=confidence,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category,
                metadata={
                    'article_count': len(news),
                    'sentiment_std': sentiment_std
                }
            ))
            
            if len(sentiments) >= 5:
                recent = np.mean(sentiments[:5])
                older = np.mean(sentiments[5:10]) if len(sentiments) >= 10 else np.mean(sentiments)
                momentum = recent - older
                
                signals.append(Signal(
                    name="news_momentum",
                    value=np.clip(momentum * 2, -1, 1),
                    confidence=0.5,
                    horizon=TimeHorizon.SHORT_TERM,
                    category=self.category
                ))
        
        return signals
    
    def _social_signals(self, social: Dict) -> List[Signal]:
        signals = []
        
        if 'sentiment' in social:
            signals.append(Signal(
                name="social_sentiment",
                value=np.clip(social['sentiment'], -1, 1),
                confidence=social.get('confidence', 0.4),
                horizon=TimeHorizon.INTRADAY,
                category=self.category
            ))
        
        if social.get('trending', False):
            direction = np.sign(social.get('sentiment', 0))
            signals.append(Signal(
                name="social_trending",
                value=direction * 0.3,
                confidence=0.3,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category
            ))
        
        return signals
    
    def _estimate_sentiment(self, text: str) -> float:
        """Simple keyword-based sentiment estimation."""
        text = text.lower()
        
        positive = [
            'surge', 'jump', 'rally', 'gain', 'rise', 'beat', 'exceed',
            'strong', 'growth', 'upgrade', 'bullish', 'positive', 'profit',
            'record', 'high', 'outperform', 'buy', 'recommend', 'success'
        ]
        
        negative = [
            'fall', 'drop', 'plunge', 'decline', 'miss', 'weak', 'loss',
            'downgrade', 'bearish', 'negative', 'concern', 'risk', 'sell',
            'crash', 'low', 'underperform', 'warning', 'cut', 'fail'
        ]
        
        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)
        
        total = pos_count + neg_count
        return (pos_count - neg_count) / total if total > 0 else 0.0


class MacroSignalGenerator(SignalGenerator):
    """
    Generates signals from macroeconomic and sector data.
    
    Covers:
    - Sector/Industry trends
    - Political/regulatory environment
    - Geographic considerations
    - Economic indicators
    """
    
    @property
    def category(self) -> str:
        return "macro"
    
    def generate(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        context: Dict[str, Any]
    ) -> List[Signal]:
        signals = []
        
        if context.get('sector'):
            signals.extend(self._sector_signals(context['sector']))
        
        if context.get('industry'):
            signals.extend(self._industry_signals(context['industry']))
        
        if context.get('political'):
            signals.extend(self._political_signals(context['political']))
        
        if context.get('geographic'):
            signals.extend(self._geographic_signals(context['geographic']))
        
        if context.get('economic'):
            signals.extend(self._economic_signals(context['economic']))
        
        return signals
    
    def _sector_signals(self, data: Dict) -> List[Signal]:
        signals = []
        
        if 'performance_1m' in data:
            perf = data['performance_1m']
            signals.append(Signal(
                name="sector_momentum",
                value=np.clip(perf * 5, -1, 1),
                confidence=0.6,
                horizon=TimeHorizon.MEDIUM_TERM,
                category=self.category,
                metadata={'sector': data.get('name', 'unknown')}
            ))
        
        if 'rotation_score' in data:
            signals.append(Signal(
                name="sector_rotation",
                value=np.clip(data['rotation_score'], -1, 1),
                confidence=0.5,
                horizon=TimeHorizon.MEDIUM_TERM,
                category=self.category
            ))
        
        return signals
    
    def _industry_signals(self, data: Dict) -> List[Signal]:
        signals = []
        
        if 'trend' in data:
            trend_map = {'growing': 0.5, 'stable': 0, 'declining': -0.5}
            trend_value = trend_map.get(data['trend'], 0)
            
            signals.append(Signal(
                name="industry_trend",
                value=trend_value,
                confidence=0.5,
                horizon=TimeHorizon.LONG_TERM,
                category=self.category,
                metadata={'industry': data.get('name', 'unknown')}
            ))
        
        if 'competitive_score' in data:
            signals.append(Signal(
                name="competitive_position",
                value=np.clip(data['competitive_score'], -1, 1),
                confidence=0.4,
                horizon=TimeHorizon.STRATEGIC,
                category=self.category
            ))
        
        return signals
    
    def _political_signals(self, data: Dict) -> List[Signal]:
        signals = []
        
        if 'regulatory_risk' in data:
            signals.append(Signal(
                name="regulatory_risk",
                value=-np.clip(data['regulatory_risk'], 0, 1),
                confidence=0.5,
                horizon=TimeHorizon.LONG_TERM,
                category=self.category
            ))
        
        if 'policy_impact' in data:
            signals.append(Signal(
                name="policy_impact",
                value=np.clip(data['policy_impact'], -1, 1),
                confidence=data.get('confidence', 0.4),
                horizon=TimeHorizon.MEDIUM_TERM,
                category=self.category,
                metadata={'policy_type': data.get('type', 'general')}
            ))
        
        if 'trade_exposure' in data:
            exposure = data['trade_exposure']
            trade_sentiment = data.get('trade_sentiment', 0)
            
            signals.append(Signal(
                name="trade_policy",
                value=np.clip(trade_sentiment * exposure, -1, 1),
                confidence=0.4 * exposure,
                horizon=TimeHorizon.MEDIUM_TERM,
                category=self.category
            ))
        
        return signals
    
    def _geographic_signals(self, data: Dict) -> List[Signal]:
        signals = []
        
        if 'concentration' in data:
            regions = data['concentration']
            regional_scores = []
            
            for region, weight in regions.items():
                region_score = data.get(f'{region}_outlook', 0)
                regional_scores.append(region_score * weight)
            
            if regional_scores:
                geo_signal = sum(regional_scores)
                signals.append(Signal(
                    name="geographic_outlook",
                    value=np.clip(geo_signal, -1, 1),
                    confidence=0.4,
                    horizon=TimeHorizon.MEDIUM_TERM,
                    category=self.category
                ))
        
        if 'fx_impact' in data:
            signals.append(Signal(
                name="currency_impact",
                value=np.clip(data['fx_impact'], -1, 1),
                confidence=0.3,
                horizon=TimeHorizon.MEDIUM_TERM,
                category=self.category
            ))
        
        return signals
    
    def _economic_signals(self, data: Dict) -> List[Signal]:
        signals = []
        
        if 'cycle_phase' in data:
            phase_map = {
                'expansion': 0.5,
                'peak': 0,
                'contraction': -0.5,
                'trough': 0.3
            }
            phase_value = phase_map.get(data['cycle_phase'], 0)
            
            signals.append(Signal(
                name="economic_cycle",
                value=phase_value,
                confidence=0.5,
                horizon=TimeHorizon.LONG_TERM,
                category=self.category
            ))
        
        if 'rate_direction' in data:
            direction_map = {'rising': -0.3, 'stable': 0, 'falling': 0.3}
            rate_signal = direction_map.get(data['rate_direction'], 0)
            
            signals.append(Signal(
                name="interest_rates",
                value=rate_signal,
                confidence=0.6,
                horizon=TimeHorizon.MEDIUM_TERM,
                category=self.category
            ))
        
        return signals


class MomentumReversionGenerator(SignalGenerator):
    """Generates pure price-based momentum and mean reversion signals."""
    
    @property
    def category(self) -> str:
        return "momentum"
    
    def generate(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        context: Dict[str, Any]
    ) -> List[Signal]:
        signals = []
        
        if price_data is None or price_data.empty or len(price_data) < 60:
            return signals
        
        if 'Close' in price_data.columns:
            close = price_data['Close']
        elif 'close' in price_data.columns:
            close = price_data['close']
        else:
            return signals
        
        signals.extend(self._momentum_signals(close))
        signals.extend(self._reversion_signals(close))
        
        return signals
    
    def _momentum_signals(self, close: pd.Series) -> List[Signal]:
        signals = []
        
        lookbacks = [5, 10, 20, 60]
        
        for lb in lookbacks:
            if len(close) >= lb:
                momentum = (close.iloc[-1] / close.iloc[-lb]) - 1
                
                horizon = (
                    TimeHorizon.INTRADAY if lb <= 5 else
                    TimeHorizon.SHORT_TERM if lb <= 20 else
                    TimeHorizon.MEDIUM_TERM
                )
                
                signals.append(Signal(
                    name=f"momentum_{lb}d",
                    value=np.clip(momentum * 5, -1, 1),
                    confidence=0.5,
                    horizon=horizon,
                    category=self.category
                ))
        
        if len(close) >= 20:
            mom_5 = (close / close.shift(5) - 1).iloc[-1]
            mom_5_prev = (close / close.shift(5) - 1).iloc[-5]
            acceleration = mom_5 - mom_5_prev
            
            signals.append(Signal(
                name="momentum_acceleration",
                value=np.clip(acceleration * 10, -1, 1),
                confidence=0.4,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category
            ))
        
        return signals
    
    def _reversion_signals(self, close: pd.Series) -> List[Signal]:
        signals = []
        
        if len(close) >= 50:
            ma_50 = close.rolling(50).mean()
            distance = (close.iloc[-1] - ma_50.iloc[-1]) / ma_50.iloc[-1]
            
            if abs(distance) > 0.1:
                reversion_signal = -np.sign(distance) * min(abs(distance), 0.3)
            else:
                reversion_signal = 0
            
            signals.append(Signal(
                name="ma_reversion",
                value=reversion_signal,
                confidence=min(abs(distance) * 2, 0.7),
                horizon=TimeHorizon.MEDIUM_TERM,
                category=self.category,
                metadata={'distance_from_ma': distance}
            ))
        
        if len(close) >= 20:
            rolling_high = close.rolling(20).max()
            rolling_low = close.rolling(20).min()
            
            range_val = rolling_high.iloc[-1] - rolling_low.iloc[-1]
            range_pos = (close.iloc[-1] - rolling_low.iloc[-1]) / (range_val + 1e-10)
            
            if range_pos > 0.9:
                reversion = -(range_pos - 0.5) * 0.8
            elif range_pos < 0.1:
                reversion = (0.5 - range_pos) * 0.8
            else:
                reversion = 0
            
            signals.append(Signal(
                name="range_reversion",
                value=np.clip(reversion, -1, 1),
                confidence=abs(reversion) * 0.8,
                horizon=TimeHorizon.SHORT_TERM,
                category=self.category
            ))
        
        return signals
