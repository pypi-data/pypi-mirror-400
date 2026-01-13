"""
Strategies v2 endpoint for agentic, natural-language-driven strategy backtesting.

This is a beta endpoint that operates independently from the existing strategy system.
It accepts natural language strategy descriptions and uses LangGraph + Anthropic + Modal
to generate, validate, and execute backtests in a sandboxed environment.

Phase 1: Stateless execution with no database persistence.
"""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing_extensions import Literal

from app.core.middleware import get_current_user
from app.core.logging import get_domain_logger
from app.core.config import settings
from app.errors.exceptions import handle_validation_error

logger = get_domain_logger("api", __name__)

router = APIRouter()


# ================================
# Pydantic Models
# ================================


class StrategyV2Request(BaseModel):
    """Request model for natural-language strategy creation"""

    strategy_description: str = Field(
        ...,
        description="Natural language description of the investment strategy",
        min_length=10,
        max_length=2000,
    )

    @field_validator("strategy_description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description is not empty after stripping whitespace"""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Strategy description cannot be empty")
        if len(stripped) < 10:
            raise ValueError("Strategy description must be at least 10 characters")
        return stripped


class StrategyV2Response(BaseModel):
    """Response model for strategy execution results"""

    status: Literal["completed", "error"] = Field(
        ..., description="Status of the strategy execution"
    )
    dates: Optional[List[date]] = Field(
        None, description="Array of dates for the backtest equity curve (ISO format)"
    )
    returns: Optional[List[float]] = Field(
        None, description="Array of daily fractional returns aligned with dates"
    )
    start_dates: Optional[dict] = Field(
        None, description="Start dates metadata (partial/complete universe)"
    )
    message: Optional[str] = Field(
        None, description="Error message if status is 'error'"
    )
    code_excerpt: Optional[str] = Field(
        None, description="Excerpt of generated code if error occurred during execution"
    )
    generated_code: Optional[str] = Field(
        None,
        description="Complete generated code if execution was successful (for validation)",
    )
    timing: Optional[dict] = Field(
        None, description="Performance timing breakdown by pipeline step"
    )


# ================================
# Endpoint
# ================================


@router.post(
    "",
    operation_id="createStrategyV2",
    summary="Create Agentic Strategy (Beta)",
    response_model=StrategyV2Response,
    status_code=200,
    responses={
        200: {
            "description": "Strategy executed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "completed",
                        "dates": ["2020-01-02", "2020-01-03", "2020-01-06"],
                        "returns": [0.0, 0.0054, -0.0021],
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "validation_error",
                            "message": "Strategy description must be at least 10 characters",
                        }
                    }
                }
            },
        },
        500: {
            "description": "Execution error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Strategy execution failed: Missing 'close' column in prices_df",
                        "code_excerpt": "Line 45: close = prices_df['close']",
                    }
                }
            },
        },
    },
)
async def create_strategy_v2(
    strategy_data: StrategyV2Request, current_user=Depends(get_current_user)
):
    """
    Execute a natural-language strategy description using agentic backtesting.

    **Beta Feature:** This endpoint uses LangGraph + Anthropic Claude to generate
    vectorbt-based backtest code from natural language, then executes it in a
    Modal sandbox environment.

    **Phase 1 Limitations:**
    - Stateless execution (no database persistence)
    - Fixed universe (SPY only for initial implementation)
    - Daily timeframe only
    - Returns full equity curve in response (not paginated)

    **Example Descriptions:**
    - "Buy and hold SPY"
    - "Buy SPY when close is above 50-day moving average, sell when below"
    - "Simple momentum strategy on SPY"
    """

    user_id, _ = current_user

    # Feature gate check
    if not settings.FEATURE_AGENTIC_STRATEGIES_V2_ENABLED:
        logger.warning(
            f"Agentic strategies v2 disabled, rejecting request from user {user_id}"
        )
        raise HTTPException(
            status_code=503,
            detail={
                "error": "feature_disabled",
                "message": "Agentic strategies v2 endpoint is currently disabled",
            },
        )

    # Generate correlation ID for tracing
    import uuid

    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Processing v2 strategy request for user {user_id}")

    try:
        # Import workflow here to avoid circular dependencies
        from app.pipelines.strategies.workflow import run_agent_workflow

        # Validate input
        description = strategy_data.strategy_description.strip()
        if not description:
            raise handle_validation_error(
                "empty_description", "Strategy description cannot be empty"
            )

        # Initialize agent state
        initial_state = {
            "user_description": description,
            "user_id": user_id,
            "trace_id": correlation_id,
            "timing": {},  # Initialize timing dict for workflow nodes
        }

        # Run the agent workflow with timeout tracking
        import time

        start_time = time.time()
        logger.info(
            f"[{correlation_id}] Starting agent workflow for strategy: {description[:50]}..."
        )

        final_state = await run_agent_workflow(initial_state)

        elapsed_time = time.time() - start_time
        logger.info(
            f"[{correlation_id}] Agent workflow completed in {elapsed_time:.2f}s"
        )

        # Check for errors in final state
        if final_state.get("error"):
            error_msg = final_state["error"]
            code_excerpt = final_state.get("code_excerpt")

            logger.error(f"Strategy execution failed: {error_msg}")

            return StrategyV2Response(
                status="error", message=error_msg, code_excerpt=code_excerpt
            )

        # Extract execution result (use `or {}` to handle explicit None)
        execution_result = final_state.get("execution_result") or {}

        if execution_result.get("status") == "error":
            return StrategyV2Response(
                status="error",
                message=execution_result.get("message", "Unknown execution error"),
                code_excerpt=execution_result.get("code_excerpt"),
            )

        # Parse dates and returns from execution result
        dates = execution_result.get("dates", [])
        returns = execution_result.get("returns", [])

        # Convert date strings to date objects if needed
        if dates and isinstance(dates[0], str):
            from datetime import datetime

            dates = [datetime.fromisoformat(d).date() for d in dates]

        logger.info(
            f"[{correlation_id}] Strategy executed successfully: {len(dates)} data points returned"
        )

        return StrategyV2Response(
            status="completed",
            dates=dates,
            returns=returns,
            start_dates=execution_result.get(
                "start_dates"
            ),  # Include start dates metadata
            generated_code=final_state.get("generated_code"),  # Include for validation
            timing=final_state.get("timing"),  # Include timing breakdown
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in strategy v2 endpoint: {str(e)}", exc_info=True
        )
        return StrategyV2Response(status="error", message=f"Internal error: {str(e)}")
