"""
Ensemble Forecaster

Combines multiple models and signals into unified forecasts.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging

from .core import (
    Signal, SignalGenerator, ForecastModel, ForecastResult,
    SignalDirection, TimeHorizon
)
from .signals import (
    TechnicalSignalGenerator,
    SentimentSignalGenerator,
    MacroSignalGenerator,
    MomentumReversionGenerator
)
from .models import (
    RidgeRegressor,
    ExponentialSmoother,
    MomentumModel,
    MeanReversionModel
)

logger = logging.getLogger(__name__)


class EnsembleForecaster:
    """
    Combines multiple models and signals into a unified forecast.
    
    Uses dynamic weighting based on:
    - Historical model performance
    - Current market regime
    - Signal agreement
    """
    
    def __init__(self):
        self.models: Dict[str, ForecastModel] = {
            'ridge': RidgeRegressor(alpha=1.0),
            'exp_smooth': ExponentialSmoother(),
            'momentum': MomentumModel(),
            'mean_reversion': MeanReversionModel()
        }
        
        self.model_weights: Dict[str, float] = {
            'ridge': 0.3,
            'exp_smooth': 0.3,
            'momentum': 0.2,
            'mean_reversion': 0.2
        }
        
        self.signal_generators: List[SignalGenerator] = [
            TechnicalSignalGenerator(),
            SentimentSignalGenerator(),
            MacroSignalGenerator(),
            MomentumReversionGenerator()
        ]
        
        self.category_weights: Dict[str, float] = {
            'technical': 0.35,
            'sentiment': 0.20,
            'macro': 0.20,
            'momentum': 0.25
        }
    
    def generate_forecast(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None,
        horizons: Optional[List[int]] = None
    ) -> ForecastResult:
        """
        Generate a complete forecast.
        
        Args:
            symbol: Stock symbol
            price_data: Historical OHLCV data
            context: Additional context (news, macro data, etc.)
            horizons: Forecast horizons in days (default: [1, 5, 10, 20, 60])
        """
        if horizons is None:
            horizons = [1, 5, 10, 20, 60]
        
        if context is None:
            context = {}
        
        if price_data.empty:
            raise ValueError("Price data cannot be empty")
        
        close = price_data['Close'] if 'Close' in price_data.columns else price_data['close']
        current_price = close.iloc[-1]
        
        # Generate signals
        all_signals = []
        for generator in self.signal_generators:
            try:
                signals = generator.generate(symbol, price_data, context)
                all_signals.extend(signals)
            except Exception as e:
                logger.warning(f"Signal generator {generator.category} failed: {e}")
        
        # Aggregate signals
        signal_breakdown = self._aggregate_signals(all_signals)
        
        # Calculate overall signal
        overall_signal = sum(
            signal_breakdown.get(cat, 0) * weight
            for cat, weight in self.category_weights.items()
        )
        
        # Fit models
        prices = close.values
        features = self._build_features(prices, all_signals)
        
        for model in self.models.values():
            try:
                model.fit(features, prices)
            except Exception as e:
                logger.warning(f"Model {model.name} failed to fit: {e}")
        
        # Generate predictions
        forecast_prices = {}
        forecast_returns = {}
        confidence_intervals = {}
        
        horizon_map = {
            1: TimeHorizon.INTRADAY,
            5: TimeHorizon.SHORT_TERM,
            10: TimeHorizon.SHORT_TERM,
            20: TimeHorizon.MEDIUM_TERM,
            60: TimeHorizon.LONG_TERM
        }
        
        for horizon in horizons:
            pred, lower, upper = self._ensemble_predict(
                features[-1:], 
                horizon, 
                current_price,
                overall_signal
            )
            
            horizon_enum = horizon_map.get(horizon, TimeHorizon.MEDIUM_TERM)
            forecast_prices[horizon_enum] = pred
            forecast_returns[horizon_enum] = (pred - current_price) / current_price
            confidence_intervals[horizon_enum] = (lower, upper)
        
        # Overall direction
        avg_return = np.mean(list(forecast_returns.values()))
        overall_confidence = self._calculate_confidence(all_signals, signal_breakdown)
        
        if avg_return > 0.05:
            direction = SignalDirection.STRONG_BULLISH
        elif avg_return > 0.01:
            direction = SignalDirection.BULLISH
        elif avg_return < -0.05:
            direction = SignalDirection.STRONG_BEARISH
        elif avg_return < -0.01:
            direction = SignalDirection.BEARISH
        else:
            direction = SignalDirection.NEUTRAL
        
        return ForecastResult(
            symbol=symbol,
            current_price=current_price,
            forecast_prices=forecast_prices,
            forecast_returns=forecast_returns,
            confidence_intervals=confidence_intervals,
            signal_breakdown=signal_breakdown,
            signals=all_signals,
            model_weights=self.model_weights.copy(),
            overall_direction=direction,
            overall_confidence=overall_confidence
        )
    
    def _aggregate_signals(self, signals: List[Signal]) -> Dict[str, float]:
        by_category: Dict[str, List[float]] = {}
        
        for signal in signals:
            if signal.category not in by_category:
                by_category[signal.category] = []
            by_category[signal.category].append(signal.weighted_value)
        
        return {
            cat: np.mean(values) if values else 0
            for cat, values in by_category.items()
        }
    
    def _build_features(
        self, 
        prices: np.ndarray, 
        signals: List[Signal]
    ) -> np.ndarray:
        n = len(prices)
        
        if n < 2:
            return np.zeros((max(n, 1), 1))
        
        features = []
        
        # Returns at various lookbacks
        for lb in [1, 5, 10, 20]:
            if n > lb:
                returns = np.zeros(n)
                returns[lb:] = (prices[lb:] - prices[:-lb]) / (prices[:-lb] + 1e-10)
                features.append(returns)
        
        # Volatility
        if n > 20:
            vol = np.zeros(n)
            for i in range(20, n):
                price_slice = prices[i-20:i]
                if len(price_slice) > 1:
                    daily_returns = np.diff(price_slice) / (price_slice[:-1] + 1e-10)
                    vol[i] = np.std(daily_returns) if len(daily_returns) > 0 else 0
            features.append(vol)
        
        # Signal values
        signal_values = [s.weighted_value for s in signals]
        if signal_values:
            avg_signal = np.mean(signal_values)
            features.append(np.full(n, avg_signal))
        
        if not features:
            features.append(np.zeros(n))
        
        return np.column_stack(features)
    
    def _ensemble_predict(
        self,
        features: np.ndarray,
        horizon: int,
        current_price: float,
        signal_adjustment: float
    ) -> Tuple[float, float, float]:
        predictions = []
        lowers = []
        uppers = []
        weights = []
        
        X = np.repeat(features, horizon, axis=0)
        
        for name, model in self.models.items():
            try:
                pred, lower, upper = model.predict_interval(X)
                if len(pred) > 0:
                    predictions.append(pred[-1])
                    lowers.append(lower[-1])
                    uppers.append(upper[-1])
                    weights.append(self.model_weights.get(name, 0.25))
            except Exception as e:
                logger.debug(f"Model {name} prediction failed: {e}")
                continue
        
        if not predictions:
            vol = 0.02 * np.sqrt(horizon)
            return (
                current_price * (1 + signal_adjustment * 0.1),
                current_price * (1 - 1.96 * vol),
                current_price * (1 + 1.96 * vol)
            )
        
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        ensemble_pred = np.average(predictions, weights=weights)
        ensemble_lower = np.average(lowers, weights=weights)
        ensemble_upper = np.average(uppers, weights=weights)
        
        signal_impact = signal_adjustment * 0.05 * np.sqrt(horizon)
        ensemble_pred = ensemble_pred * (1 + signal_impact)
        
        return ensemble_pred, ensemble_lower, ensemble_upper
    
    def _calculate_confidence(
        self, 
        signals: List[Signal], 
        breakdown: Dict[str, float]
    ) -> float:
        if not signals:
            return 0.3
        
        values = [s.value for s in signals]
        if len(values) > 1:
            agreement = 1 - np.std(values)
        else:
            agreement = 0.5
        
        avg_confidence = np.mean([s.confidence for s in signals])
        coverage = len(breakdown) / len(self.category_weights)
        
        overall = 0.4 * agreement + 0.4 * avg_confidence + 0.2 * coverage
        return np.clip(overall, 0.1, 0.9)
    
    def update_weights(
        self, 
        actuals: Dict[str, float], 
        predictions: Dict[str, float]
    ) -> None:
        """Update model weights based on performance."""
        errors = {}
        for name in self.models:
            if name in actuals and name in predictions:
                errors[name] = abs(actuals[name] - predictions[name])
        
        if not errors:
            return
        
        total_inv_error = sum(1 / (e + 0.01) for e in errors.values())
        
        for name, error in errors.items():
            self.model_weights[name] = (1 / (error + 0.01)) / total_inv_error
