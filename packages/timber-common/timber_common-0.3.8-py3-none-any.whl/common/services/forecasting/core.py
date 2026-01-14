"""
Forecasting Core

Data structures, enums, and protocols for the forecasting system.
"""

import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum, auto
from datetime import datetime


class SignalDirection(Enum):
    """Direction of a trading signal."""
    STRONG_BEARISH = -2
    BEARISH = -1
    NEUTRAL = 0
    BULLISH = 1
    STRONG_BULLISH = 2


class TimeHorizon(Enum):
    """Forecast time horizons."""
    INTRADAY = auto()      # < 1 day
    SHORT_TERM = auto()    # 1-5 days
    MEDIUM_TERM = auto()   # 1-4 weeks
    LONG_TERM = auto()     # 1-3 months
    STRATEGIC = auto()     # 3+ months


@dataclass
class Signal:
    """
    A single signal contributing to the forecast.
    
    Attributes:
        name: Identifier for this signal
        value: Normalized signal value [-1, 1]
        confidence: Confidence in this signal [0, 1]
        horizon: Time horizon this signal applies to
        category: Signal category (technical, sentiment, macro, etc.)
        metadata: Additional signal-specific data
    """
    name: str
    value: float
    confidence: float
    horizon: TimeHorizon
    category: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.value = np.clip(self.value, -1.0, 1.0)
        self.confidence = np.clip(self.confidence, 0.0, 1.0)
    
    @property
    def weighted_value(self) -> float:
        """Signal value weighted by confidence."""
        return self.value * self.confidence


@dataclass
class ForecastResult:
    """
    Complete forecast output.
    """
    symbol: str
    current_price: float
    forecast_prices: Dict[TimeHorizon, float]
    forecast_returns: Dict[TimeHorizon, float]
    confidence_intervals: Dict[TimeHorizon, Tuple[float, float]]
    signal_breakdown: Dict[str, float]
    signals: List[Signal]
    model_weights: Dict[str, float]
    overall_direction: SignalDirection
    overall_confidence: float
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'symbol': self.symbol,
            'current_price': self.current_price,
            'forecast_prices': {h.name: p for h, p in self.forecast_prices.items()},
            'forecast_returns': {h.name: r for h, r in self.forecast_returns.items()},
            'confidence_intervals': {
                h.name: {'lower': ci[0], 'upper': ci[1]} 
                for h, ci in self.confidence_intervals.items()
            },
            'signal_breakdown': self.signal_breakdown,
            'overall_direction': self.overall_direction.name,
            'overall_confidence': self.overall_confidence,
            'model_weights': self.model_weights,
            'generated_at': self.generated_at.isoformat(),
            'signals': [
                {
                    'name': s.name,
                    'value': s.value,
                    'confidence': s.confidence,
                    'category': s.category,
                    'horizon': s.horizon.name
                }
                for s in self.signals
            ]
        }


class SignalGenerator(ABC):
    """Abstract base for signal generators."""
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Category name for signals from this generator."""
        pass
    
    @abstractmethod
    def generate(
        self,
        symbol: str,
        price_data: Any,
        context: Dict[str, Any]
    ) -> List[Signal]:
        """Generate signals from input data."""
        pass


class ForecastModel(ABC):
    """Abstract base for forecasting models."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass
    
    @abstractmethod
    def predict_interval(
        self, 
        X: np.ndarray, 
        confidence: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return (predictions, lower_bound, upper_bound)."""
        pass
