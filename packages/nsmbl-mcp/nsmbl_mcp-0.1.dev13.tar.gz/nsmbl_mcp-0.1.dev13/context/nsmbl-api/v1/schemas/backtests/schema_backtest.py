from typing import Optional, Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class BacktestRequest(BaseModel):
    """Request model for backtest endpoint using hierarchical target identification"""
    target_id: str = Field(
        ...,
        description="Target ID (asset symbol, strategy ID, etc.)",
        example="VTI"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Backtest start date (optional - uses full history if not provided)"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Backtest end date (optional - uses full history if not provided)"
    )
    initial_capital: float = Field(
        100000.0,
        gt=0,
        description="Initial capital for backtest (must be > 0)"
    )

    @model_validator(mode='after')
    def validate_dates(self):
        """Ensure date range is valid when both dates are provided"""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")
        return self


# Removed EquityPoint and AllocationPoint classes - using simple dictionaries instead
# Equity points: {"date": "2023-01-01T00:00:00Z", "value": 100000.0}
# Allocation points: {"date": "2023-01-01T00:00:00Z", "positions": {"VTI": 0.6, "VEA": 0.4}}


class BacktestConfig(BaseModel):
    """Configuration used for the backtest with hierarchical target structure"""
    target_id: str = Field(..., description="Target ID that was backtested")
    target_type: str = Field(..., description="Target type (asset or strategy)")
    target_subtype: str = Field(..., description="Target subtype (stock/basket/tactical/etc.)")
    target_symbol: Optional[str] = Field(None, description="Target symbol")
    target_name: Optional[str] = Field(None, description="Target name")
    start_date: Optional[datetime] = Field(None, description="Backtest start date")
    end_date: Optional[datetime] = Field(None, description="Backtest end date")
    initial_capital: float = Field(..., description="Initial capital used")


class BacktestMetrics(BaseModel):
    """Performance metrics from the backtest"""
    final_value: float = Field(..., description="Final portfolio value")
    total_return: float = Field(..., description="Total return percentage (decimal)")
    annualized_return: Optional[float] = Field(None, description="Annualized return percentage (decimal)")
    volatility: Optional[float] = Field(None, description="Volatility (standard deviation)")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    max_drawdown: Optional[float] = Field(None, description="Maximum drawdown (decimal)")


class BacktestHistory(BaseModel):
    """Historical data from the backtest"""
    equity: List[Dict[str, Any]] = Field(..., description="Daily portfolio values as simple dictionaries")
    allocations: List[Dict[str, Any]] = Field(..., description="Position allocations over time as simple dictionaries")


class BacktestInfo(BaseModel):
    """Execution information and timing details"""
    created_at: Optional[datetime] = Field(None, description="When the backtest was created")
    started_at: Optional[datetime] = Field(None, description="When execution started")
    finished_at: Optional[datetime] = Field(None, description="When execution finished")
    queued_seconds: Optional[float] = Field(None, description="Time spent in queue")
    execution_seconds: Optional[float] = Field(None, description="Time spent executing")
    completion_seconds: Optional[float] = Field(None, description="Total time from creation to completion")
    warnings: List[str] = Field(default_factory=list, description="Execution warnings")
    errors: List[str] = Field(default_factory=list, description="Execution errors")


class BacktestSummary(BaseModel):
    """Summary of backtest results for list endpoints"""
    backtest_id: str = Field(..., description="Unique backtest identifier")
    backtest_status: str = Field(..., description="Current backtest status")
    backtest_config: BacktestConfig = Field(..., description="Configuration used for the backtest")
    backtest_metrics: BacktestMetrics = Field(..., description="Performance metrics")
    backtest_info: BacktestInfo = Field(..., description="Execution timing and status")


class BacktestResults(BaseModel):
    """Complete backtest results with organized structure"""
    backtest_id: str = Field(..., description="Unique backtest identifier")
    backtest_status: str = Field(..., description="Current backtest status")
    backtest_config: BacktestConfig = Field(..., description="Configuration used for the backtest")
    backtest_metrics: BacktestMetrics = Field(..., description="Performance metrics")
    backtest_history: BacktestHistory = Field(..., description="Historical equity and allocation data")
    backtest_info: BacktestInfo = Field(..., description="Execution timing and status")


class BacktestRequestExample(BaseModel):
    """Example backtest requests for different target types"""

    class Config:
    json_schema_extra = {
        "examples": [
            {
                "name": "Asset Backtest - Full History",
                "description": "Backtest a single asset using all available data",
                "value": {
                    "target_id": "VTI",
                    "initial_capital": 100000.0
                }
            },
            {
                "name": "Asset Backtest - Date Range",
                "description": "Backtest a single asset for specific date range",
                "value": {
                    "target_id": "AAPL",
                    "start_date": "2023-01-01T00:00:00Z",
                    "end_date": "2023-12-31T23:59:59Z",
                    "initial_capital": 100000.0
                }
            },
            {
                "name": "Basket Strategy Backtest",
                "description": "Backtest a basket strategy",
                "value": {
                    "target_id": "sb-12345678-1234-5678-9abc-123456789012",
                    "initial_capital": 100000.0
                }
            },
            {
                "name": "Tactical Strategy Backtest",
                "description": "Backtest a tactical strategy",
                "value": {
                    "target_id": "st-87654321-4321-8765-dcba-987654321098",
                    "initial_capital": 100000.0
                }
            }
        ]
    }
