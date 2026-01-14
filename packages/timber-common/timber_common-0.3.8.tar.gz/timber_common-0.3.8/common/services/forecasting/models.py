"""
Lightweight Forecasting Models

Pure numpy/scipy implementations for minimal memory footprint.
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional

from .core import ForecastModel


class RidgeRegressor(ForecastModel):
    """Ridge regression with uncertainty estimation."""
    
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.weights: Optional[np.ndarray] = None
        self.residual_std: float = 1.0
        self._n_features: int = 0
    
    @property
    def name(self) -> str:
        return "ridge"
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        min_len = min(len(X), len(y))
        X = X[:min_len]
        y = y[:min_len]
        
        if len(y) < 2:
            self._n_features = X.shape[1] if X.ndim > 1 else 1
            self.weights = np.array([np.mean(y) if len(y) > 0 else 0] + [0] * self._n_features)
            self.residual_std = 1.0
            return
        
        self._n_features = X.shape[1]
        X_bias = np.column_stack([np.ones(len(X)), X])
        
        n_features = X_bias.shape[1]
        identity = np.eye(n_features)
        identity[0, 0] = 0
        
        try:
            self.weights = np.linalg.solve(
                X_bias.T @ X_bias + self.alpha * identity,
                X_bias.T @ y
            )
            
            predictions = X_bias @ self.weights
            residuals = y - predictions
            self.residual_std = np.std(residuals) if len(residuals) > 1 else 1.0
        except np.linalg.LinAlgError:
            self.weights = np.zeros(n_features)
            self.weights[0] = np.mean(y)
            self.residual_std = np.std(y) if len(y) > 1 else 1.0
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.weights is None:
            return np.zeros(len(X) if X.ndim > 0 else 1)
        
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        expected_features = len(self.weights) - 1
        if X.shape[1] != expected_features:
            if X.shape[1] < expected_features:
                padding = np.zeros((X.shape[0], expected_features - X.shape[1]))
                X = np.column_stack([X, padding])
            else:
                X = X[:, :expected_features]
        
        X_bias = np.column_stack([np.ones(len(X)), X])
        return X_bias @ self.weights
    
    def predict_interval(
        self, 
        X: np.ndarray, 
        confidence: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        predictions = self.predict(X)
        z_score = stats.norm.ppf((1 + confidence) / 2)
        margin = z_score * self.residual_std
        
        return predictions, predictions - margin, predictions + margin


class ExponentialSmoother(ForecastModel):
    """Double exponential smoothing (Holt's method)."""
    
    def __init__(self, alpha: float = 0.3, beta: float = 0.1):
        self.alpha = alpha
        self.beta = beta
        self.level: float = 0.0
        self.trend: float = 0.0
        self.residual_std: float = 1.0
    
    @property
    def name(self) -> str:
        return "exp_smooth"
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if len(y) < 2:
            self.level = y[0] if len(y) > 0 else 0
            self.trend = 0
            return
        
        self.level = y[0]
        self.trend = y[1] - y[0]
        
        fitted = []
        for t in range(1, len(y)):
            forecast = self.level + self.trend
            fitted.append(forecast)
            
            new_level = self.alpha * y[t] + (1 - self.alpha) * (self.level + self.trend)
            self.trend = self.beta * (new_level - self.level) + (1 - self.beta) * self.trend
            self.level = new_level
        
        residuals = y[1:] - np.array(fitted)
        self.residual_std = np.std(residuals) if len(residuals) > 1 else 1.0
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        n_steps = len(X)
        predictions = np.array([
            self.level + (i + 1) * self.trend 
            for i in range(n_steps)
        ])
        return predictions
    
    def predict_interval(
        self, 
        X: np.ndarray, 
        confidence: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        predictions = self.predict(X)
        z_score = stats.norm.ppf((1 + confidence) / 2)
        
        horizons = np.arange(1, len(X) + 1)
        margins = z_score * self.residual_std * np.sqrt(horizons)
        
        return predictions, predictions - margins, predictions + margins


class MomentumModel(ForecastModel):
    """Simple momentum-based model assuming recent trends continue."""
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        self.momentum: float = 0.0
        self.volatility: float = 1.0
        self.last_price: float = 0.0
    
    @property
    def name(self) -> str:
        return "momentum"
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if len(y) < self.lookback:
            self.momentum = 0
            self.volatility = np.std(y) if len(y) > 1 else 1.0
            self.last_price = y[-1] if len(y) > 0 else 0
            return
        
        returns = np.diff(y) / (y[:-1] + 1e-10)
        self.momentum = np.mean(returns[-self.lookback:])
        self.volatility = np.std(returns[-self.lookback:])
        self.last_price = y[-1]
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        n_steps = len(X)
        predictions = self.last_price * (1 + self.momentum) ** np.arange(1, n_steps + 1)
        return predictions
    
    def predict_interval(
        self, 
        X: np.ndarray, 
        confidence: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        predictions = self.predict(X)
        z_score = stats.norm.ppf((1 + confidence) / 2)
        
        horizons = np.arange(1, len(X) + 1)
        margins = z_score * self.volatility * self.last_price * np.sqrt(horizons)
        
        return predictions, predictions - margins, predictions + margins


class MeanReversionModel(ForecastModel):
    """Mean reversion model using Ornstein-Uhlenbeck process intuition."""
    
    def __init__(self, halflife: int = 20):
        self.halflife = halflife
        self.mean: float = 0.0
        self.current: float = 0.0
        self.volatility: float = 1.0
        self.kappa: float = 0.0
    
    @property
    def name(self) -> str:
        return "mean_reversion"
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if len(y) < self.halflife:
            self.mean = np.mean(y) if len(y) > 0 else 0
            self.current = y[-1] if len(y) > 0 else 0
            self.volatility = np.std(y) if len(y) > 1 else 1.0
            self.kappa = np.log(2) / self.halflife
            return
        
        self.mean = np.mean(y[-self.halflife * 2:])
        self.current = y[-1]
        self.volatility = np.std(y[-self.halflife:])
        self.kappa = np.log(2) / self.halflife
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        n_steps = len(X)
        predictions = self.mean + (self.current - self.mean) * np.exp(
            -self.kappa * np.arange(1, n_steps + 1)
        )
        return predictions
    
    def predict_interval(
        self, 
        X: np.ndarray, 
        confidence: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        predictions = self.predict(X)
        z_score = stats.norm.ppf((1 + confidence) / 2)
        
        horizons = np.arange(1, len(X) + 1)
        decay = np.exp(-self.kappa * horizons)
        margins = z_score * self.volatility * np.sqrt(1 - decay ** 2)
        
        return predictions, predictions - margins, predictions + margins
