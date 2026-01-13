"""
Strategies endpoint for LLM-generated strategies.

Creates strategies from natural language prompts using LangGraph + Anthropic + Modal.
Persists strategies to database with clean schema and minimal responses.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
import math

from app.core.middleware import get_current_user, get_optional_user
from app.core.logging import get_domain_logger
from app.core.config import settings
from app.db.connection import get_db
from app.db.strategies.tables_strategies import Strategy
from app.errors.exceptions import handle_validation_error, handle_not_found_error
from app.api.v1.schemas.strategies.schema_strategy import (
    StrategyCreateRequest,
    StrategyUpdateRequest,
    StrategyResponse,
    StrategyDetailResponse,
    StrategyHistoryResponse,
    StrategyMetricsResponse,
    StrategyUsage,
    StrategyAvailability,
)
from app.db.strategies import crud_strategies
from app.db.strategies.crud_strategies import calculate_script_hash
from app.services.internal.auth.user_service import charge_strategy_generation

logger = get_domain_logger("api", __name__)

router = APIRouter()


# ================================
# Helper Functions
# ================================


def calculate_billing_units(
    token_usage: Dict[str, int], duration_seconds: float
) -> Dict[str, Any]:
    """
    Calculate billing units for Stripe metering.

    Pricing Model (1 Unit = 1 cent):
    - Base Fee: 1 unit (API call)
    - Token Fee: 1 unit per 1000 tokens (input + output)
    - Compute Fee: 1 unit per second of Modal execution time
    """

    # 1. Base Fee
    base_units = 1

    # 2. Token Fee
    input_tokens = token_usage.get("input_tokens", 0)
    output_tokens = token_usage.get("output_tokens", 0)
    total_tokens = input_tokens + output_tokens
    token_units = math.ceil(total_tokens / 1000.0)

    # 3. Compute Fee
    compute_units = math.ceil(duration_seconds)

    # Total
    total_units = base_units + token_units + compute_units

    # Return ONLY billing data
    return {
        "units": total_units,
        "base": base_units,
        "tokens": token_units,
        "seconds": compute_units,
    }


async def report_usage_background(user_id: str, units: int):
    """Background task to report usage to Stripe via user service"""
    try:
        import uuid

        await charge_strategy_generation(uuid.UUID(user_id), units)
    except Exception as e:
        logger.error(f"Failed to report usage to Stripe: {e}")


def calculate_performance_metrics(history: Dict[str, Any]) -> Dict[str, float]:
    """Calculate performance metrics from history data"""
    if not history or "returns" not in history or not history["returns"]:
        return {
            "cagr": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
            "max_drawdown": 0.0,
            "trades": 0,
            "trading_days": 0,
        }

    returns = pd.Series(history["returns"])

    # Remove NaN values for calculations
    clean_returns = returns.dropna()

    if len(clean_returns) == 0:
        return {
            "cagr": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
            "max_drawdown": 0.0,
            "trades": 0,
            "trading_days": 0,
        }

    # CAGR
    cumulative_return = float((1 + clean_returns).prod() - 1)
    days = len(clean_returns)
    years = days / 252.0
    cagr = float((1 + cumulative_return) ** (1 / years) - 1) if years > 0 else 0.0

    # Volatility (using clean returns without NaN)
    volatility = float(clean_returns.std(ddof=1) * np.sqrt(252))

    # Sharpe
    sharpe = (
        float(cagr / volatility) if volatility > 0 and not np.isnan(volatility) else 0.0
    )

    # Drawdown (using clean returns)
    cum_series = (1 + clean_returns).cumprod()
    running_max = cum_series.cummax()
    drawdown = cum_series / running_max - 1
    max_drawdown = float(drawdown.min()) if len(drawdown) > 0 else 0.0

    # Trades (estimate from position changes)
    trades = 0
    if "positions" in history:
        positions = history["positions"]
        if len(positions) > 1:
            prev_pos = positions[0]
            for i in range(1, len(positions)):
                curr_pos = positions[i]
                if curr_pos != prev_pos:
                    trades += 1  # Rebalance
                prev_pos = curr_pos

    return {
        "cagr": cagr,
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "trades": trades,
        "trading_days": days,
    }


def build_strategy_response(strategy: Strategy) -> StrategyResponse:
    """Build strategy response with stored and computed fields"""
    try:
        # Handle nullable URL for embed code generation
        embed = None
        if strategy.url:
            # Extract base URL from stored URL for embed code
            # URL format: https://domain.com/strategy/{slug}
            base_url = (
                strategy.url.rsplit("/strategy/", 1)[0]
                if "/strategy/" in strategy.url
                else settings.FRONTEND_URL
            )
            if strategy.slug:
                embed = f'<iframe src="{base_url}/embed/{strategy.slug}" width="100%" height="400" frameborder="0" loading="lazy"></iframe>'

        return StrategyResponse(
            id=strategy.id,
            name=strategy.name,
            symbol=strategy.symbol,
            prompt=strategy.prompt,
            url=strategy.url,
            embed=embed,
            is_public=strategy.is_public,
            status=strategy.status or "executing",
            error=strategy.error,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at,
        )
    except Exception as e:
        logger.error(f"Error building strategy response: {str(e)}", exc_info=True)
        raise


def build_detail_response(strategy: Strategy) -> StrategyDetailResponse:
    """Build strategy detail response with stored and computed fields"""
    availability_data = None
    if strategy.history and "availability" in strategy.history:
        availability_data = strategy.history["availability"]

    # Handle nullable URL for embed code generation
    embed = None
    if strategy.url:
        # Extract base URL from stored URL for embed code
        base_url = (
            strategy.url.rsplit("/strategy/", 1)[0]
            if "/strategy/" in strategy.url
            else settings.FRONTEND_URL
        )
        if strategy.slug:
            embed = f'<iframe src="{base_url}/embed/{strategy.slug}" width="100%" height="400" frameborder="0" loading="lazy"></iframe>'

    return StrategyDetailResponse(
        id=strategy.id,
        name=strategy.name,
        symbol=strategy.symbol,
        prompt=strategy.prompt,
        url=strategy.url,
        embed=embed,
        is_public=strategy.is_public,
        status=strategy.status or "executing",
        error=strategy.error,
        created_at=strategy.created_at,
        updated_at=strategy.updated_at,
        script=strategy.script,
        usage=StrategyUsage(**strategy.usage) if strategy.usage else None,
        timing=strategy.timing,
        availability=StrategyAvailability(**availability_data)
        if availability_data
        else None,
    )


# ================================
# Endpoints
# ================================


@router.post(
    "",
    operation_id="createStrategy",
    summary="Create Strategy",
    response_model=StrategyResponse,
    status_code=201,
)
async def create_strategy(
    strategy_data: StrategyCreateRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new strategy from natural language prompt.

    Generates code via LLM, executes to create history, persists to database.
    Synchronous execution (user waits 10-50s).
    """

    user_id, _ = current_user

    # Generate correlation ID for tracing
    import uuid

    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Creating strategy for user {user_id}")

    # Validate input
    prompt = strategy_data.prompt.strip()
    if not prompt:
        raise handle_validation_error("empty_prompt", "Prompt cannot be empty")

    # STEP 1: Create record immediately (status='executing')
    db_strategy = crud_strategies.create_strategy_record(
        db=db,
        user_id=user_id,
        prompt=prompt,
    )
    strategy_id = db_strategy.id
    logger.info(f"[{correlation_id}] Created strategy record: {strategy_id}")

    try:
        # STEP 2: Run workflow
        from app.pipelines.strategies.workflow import run_agent_workflow

        initial_state = {
            "user_description": prompt,
            "user_id": str(user_id),
            "trace_id": correlation_id,
            "strategy_id": strategy_id,  # Pass ID for potential mid-workflow updates
            "user_name": strategy_data.name,
            "user_symbol": strategy_data.symbol,
            "timing": {},
        }

        logger.info(f"[{correlation_id}] Running workflow...")
        final_state = await run_agent_workflow(initial_state)

        # Check for workflow-level errors
        if final_state.get("error"):
            logger.error(f"Workflow failed: {final_state['error']}")
            crud_strategies.mark_strategy_failed(
                db=db,
                strategy_id=strategy_id,
                error_type="generation_failed",
                error_message=final_state["error"],
                traceback=final_state.get("execution_error"),
                code_excerpt=final_state.get("code_excerpt"),
                timing=final_state.get("timing"),
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "generation_failed",
                    "message": final_state["error"],
                    "strategy_id": strategy_id,  # Return ID for debugging
                },
            )

        # STEP 3: Update with generated code
        generated_code = final_state.get("generated_code", "")
        strategy_name = final_state.get("strategy_name")
        strategy_symbol = final_state.get("strategy_symbol")

        if not strategy_name or not strategy_symbol:
            crud_strategies.mark_strategy_failed(
                db=db,
                strategy_id=strategy_id,
                error_type="metadata_missing",
                error_message="Failed to extract strategy name/symbol",
                timing=final_state.get("timing"),
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "metadata_missing",
                    "message": "Failed to extract strategy name/symbol",
                    "strategy_id": strategy_id,
                },
            )

        logger.info(
            f"Strategy metadata - Name: {strategy_name}, Symbol: {strategy_symbol}"
        )

        script_hash = calculate_script_hash(generated_code)
        crud_strategies.update_strategy_code(
            db=db,
            strategy_id=strategy_id,
            script=generated_code,
            name=strategy_name,
            symbol=strategy_symbol,
            script_hash=script_hash,
        )

        # STEP 4: Check execution result
        execution_result = final_state.get("execution_result") or {}
        if execution_result.get("status") == "error":
            crud_strategies.mark_strategy_failed(
                db=db,
                strategy_id=strategy_id,
                error_type="execution_failed",
                error_message=execution_result.get("message", "Execution failed"),
                traceback=execution_result.get("traceback"),
                code_excerpt=execution_result.get("code_excerpt"),
                timing=final_state.get("timing"),
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "execution_failed",
                    "message": execution_result.get("message", "Execution failed"),
                    "strategy_id": strategy_id,
                },
            )

        # STEP 5: Update with execution results
        dates = execution_result.get("dates", [])
        returns = execution_result.get("returns", [])
        positions = execution_result.get("position_history", [])
        start_dates_data = execution_result.get("start_dates", {})

        history = {
            "dates": [str(d) for d in dates],
            "returns": returns,
            "positions": positions,
            "availability": {
                "partial": start_dates_data.get("partial_universe_start_date"),
                "complete": start_dates_data.get("complete_universe_start_date"),
            },
        }

        timing_data = final_state.get("timing", {})
        execution_timing = timing_data.get("n4_modal_execution", {})
        duration_seconds = execution_timing.get("duration_seconds", 0)
        token_usage = final_state.get("token_usage", {})
        usage_data = calculate_billing_units(token_usage, duration_seconds)

        crud_strategies.update_strategy_execution(
            db=db,
            strategy_id=strategy_id,
            history=history,
            usage=usage_data,
            timing=timing_data,
        )

        # STEP 6: Finalize as succeeded
        db_strategy = crud_strategies.finalize_strategy_success(
            db=db,
            strategy_id=strategy_id,
            frontend_url=settings.FRONTEND_URL,
        )

        # Report usage
        background_tasks.add_task(
            report_usage_background, str(user_id), usage_data["units"]
        )

        logger.info(f"[{correlation_id}] Strategy succeeded: {strategy_id}")
        return build_strategy_response(db_strategy)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        # Mark as failed with whatever timing data we have
        try:
            crud_strategies.mark_strategy_failed(
                db=db,
                strategy_id=strategy_id,
                error_type="internal_error",
                error_message=str(e),
            )
        except Exception:
            pass  # Don't mask original error
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Internal error: {str(e)}",
                "strategy_id": strategy_id,
            },
        )


@router.get(
    "",
    operation_id="listStrategies",
    summary="List Strategies",
    response_model=List[StrategyResponse],
)
async def list_strategies(
    status: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all strategies for the user with optional status filter"""

    user_id, _ = current_user

    # Validate status filter if provided
    valid_statuses = ["executing", "succeeded", "failed"]
    if status and status not in valid_statuses:
        raise handle_validation_error(
            "invalid_status",
            "Invalid status. Must be one of: executing, succeeded, failed"
        )

    strategies = crud_strategies.list_strategies(db, user_id, status)

    return [build_strategy_response(s) for s in strategies]


@router.get(
    "/{identifier}",
    operation_id="getStrategy",
    summary="Get Strategy",
    response_model=StrategyDetailResponse,
)
async def get_strategy(
    identifier: str,
    current_user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Get strategy by slug (public) or ID (owner)"""

    # Try public access by slug
    strategy = crud_strategies.get_strategy_by_slug(db, identifier)
    if strategy:
        if strategy.is_public:
            # Public access allowed
            return build_detail_response(strategy)
        elif current_user:
            user_id, _ = current_user
            if strategy.user_id == user_id:
                # Owner access allowed
                return build_detail_response(strategy)
        raise HTTPException(
            404, {"error": "not_found", "message": "Strategy not found"}
        )

    # Try private access by ID (requires auth)
    if current_user:
        user_id, _ = current_user
        strategy = crud_strategies.get_strategy_by_id(db, user_id, identifier)
        if strategy:
            return build_detail_response(strategy)

    raise handle_not_found_error("Strategy", identifier)


@router.get(
    "/{identifier}/history",
    operation_id="getStrategyHistory",
    summary="Get Strategy History",
    response_model=StrategyHistoryResponse,
)
async def get_strategy_history(
    identifier: str,
    current_user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Get daily price history for strategy (public or owner)"""

    # Try public access by slug
    strategy = crud_strategies.get_strategy_by_slug(db, identifier)
    if strategy:
        if strategy.is_public:
            # Public access allowed
            pass
        elif current_user:
            user_id, _ = current_user
            if strategy.user_id == user_id:
                # Owner access allowed
                pass
            else:
                raise HTTPException(
                    404, {"error": "not_found", "message": "Strategy not found"}
                )
        else:
            raise HTTPException(
                404, {"error": "not_found", "message": "Strategy not found"}
            )
    else:
        # Try private access by ID (requires auth)
        if current_user:
            user_id, _ = current_user
            strategy = crud_strategies.get_strategy_by_id(db, user_id, identifier)
            if not strategy:
                raise handle_not_found_error("Strategy", identifier)
        else:
            raise handle_not_found_error("Strategy", identifier)

    if not strategy.history:
        raise HTTPException(
            status_code=404,
            detail={"error": "no_history", "message": "Strategy has no history data"},
        )

    history_data = strategy.history or {}
    availability_data = history_data.get("availability")

    return StrategyHistoryResponse(
        dates=history_data.get("dates", []),
        returns=history_data.get("returns", []),
        positions=history_data.get("positions", []),
        availability=StrategyAvailability(**availability_data)
        if availability_data
        else None,
    )


@router.get(
    "/{identifier}/metrics",
    operation_id="getStrategyMetrics",
    summary="Get Strategy Metrics",
    response_model=StrategyMetricsResponse,
)
async def get_strategy_metrics(
    identifier: str,
    current_user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Get calculated performance metrics for strategy (public or owner)"""

    # Try public access by slug
    strategy = crud_strategies.get_strategy_by_slug(db, identifier)
    if strategy:
        if strategy.is_public:
            # Public access allowed
            pass
        elif current_user:
            user_id, _ = current_user
            if strategy.user_id == user_id:
                # Owner access allowed
                pass
            else:
                raise HTTPException(
                    404, {"error": "not_found", "message": "Strategy not found"}
                )
        else:
            raise HTTPException(
                404, {"error": "not_found", "message": "Strategy not found"}
            )
    else:
        # Try private access by ID (requires auth)
        if current_user:
            user_id, _ = current_user
            strategy = crud_strategies.get_strategy_by_id(db, user_id, identifier)
            if not strategy:
                raise handle_not_found_error("Strategy", identifier)
        else:
            raise handle_not_found_error("Strategy", identifier)

    # Calculate metrics on the fly from history
    metrics = calculate_performance_metrics(strategy.history)

    return StrategyMetricsResponse(**metrics)


@router.patch(
    "/{identifier}",
    operation_id="updateStrategy",
    summary="Update Strategy",
    response_model=StrategyResponse,
)
async def update_strategy(
    identifier: str,
    updates: StrategyUpdateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update strategy (owner only)"""
    user_id, _ = current_user

    # Must be owner
    strategy = crud_strategies.get_strategy_by_id(db, user_id, identifier)
    if not strategy:
        raise handle_not_found_error("Strategy", identifier)

    # Apply updates
    updated_strategy = crud_strategies.update_strategy(
        db, strategy, updates.name, updates.symbol, updates.is_public
    )

    return build_strategy_response(updated_strategy)


@router.delete(
    "/{identifier}",
    operation_id="deleteStrategy",
    summary="Delete Strategy",
    status_code=204,
)
async def delete_strategy(
    identifier: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete strategy"""

    user_id, _ = current_user
    success = crud_strategies.delete_strategy(db, user_id, identifier)

    if not success:
        raise handle_not_found_error("Strategy", identifier)

    return Response(status_code=204)
