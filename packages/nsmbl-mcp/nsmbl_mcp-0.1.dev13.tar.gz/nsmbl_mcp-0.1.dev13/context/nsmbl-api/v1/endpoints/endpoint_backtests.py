from typing import Dict, Any, List, Tuple
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid
from datetime import datetime
import time
import logging
from app.core.logging import get_domain_logger


from app.db.connection import get_db
from app.core.middleware import get_current_user, get_current_user_with_usage_check
from app.db.auth.tables_auth import APIKey
from app.db.backtests.tables_backtests import Backtest
from app.db.backtests import crud_backtests
from app.api.v1.schemas.backtests.schema_backtest import BacktestRequest, BacktestResults, BacktestConfig, BacktestMetrics, BacktestHistory
from app.errors import (
    APIError,
    FeatureUnavailableError,
    handle_invalid_identifier_error,
    handle_invalid_stream_error,
    handle_unsupported_target_error,
    handle_backtest_failed_error,
    handle_retrieval_failed_error,
    handle_not_found_error,
    handle_usage_limit_exceeded_error,
    feature_gate
)
from app.core.utils import get_target_config, get_target_info_from_identifier
from app.db.backtests import crud_backtests
from app.services.internal.auth.user_service import check_usage_limits, charge_backtest_endpoint_call

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


def get_projected_usage_cents(target_subtype: str) -> int:
    """Get projected usage cost based on target subtype (business logic complexity)"""
    cost_mapping = {
        "stock": 60,  # Asset backtests
        "crypto": 60,  # Asset backtests
        "future": 60,  # Asset backtests
        "basket": 120,  # Strategy backtests - optimization complexity
        "tactical": 180,  # Strategy backtests - signal + optimization complexity
        "ensemble": 240,  # Strategy backtests - multi-strategy complexity
        "portfolio": 300  # Strategy backtests - highest complexity
    }
    return cost_mapping.get(target_subtype, 60)


@router.post(
    "",
    operation_id="createBacktest",
    summary="Create Backtest",
    status_code=201,
    response_model=dict,
    responses={
        201: {
            "description": "Backtest queued successfully",
            "content": {
                "application/json": {
                 "example": {
                     "backtest_id": "bt-12345678-1234-5678-9abc-123456789012",
                     "backtest_status": "queued",
                     "backtest_config": {
                         "target_id": "VTI",
                         "target_type": "asset",
                         "target_subtype": "stock",
                         "target_symbol": "VTI",
                         "target_name": "VTI",
                         "start_date": "2020-01-01T00:00:00",
                         "end_date": None,
                         "initial_capital": 100000.0
                     }
                 }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "invalid_stream",
                            "message": "Strategy not found: sb-DOES-NOT-EXIST"
                        }
                    }
                }
            },
        },
        500: {
            "description": "Internal error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "internal_error",
                            "message": "Backtest failed: unexpected error"
                        }
                    }
                }
            },
        },
    },
)
@limiter.limit("10/minute")
async def create_backtest(
    request: Request,
    backtest_request: BacktestRequest,
    current_user: Tuple[uuid.UUID, APIKey] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Queue a backtest for async processing with immediate response.

    Rate limit: 10/minute. Poll GET /backtests/{id} for completion. Status flow: queued → executing → completed/failed.
    """
    from app.core.config import settings

    logger = get_domain_logger('api', __name__)

    try:
        # Extract user_id from current_user tuple
        user_id, api_key = current_user

        # Get target information for hierarchical routing
        target_id = backtest_request.target_id
        target_info = get_target_info_from_identifier(target_id)
        target_type = target_info["target_type"]
        target_subtype = target_info["target_subtype"]

        logger.info(f"Queuing backtest - Target: {target_id}, Type: {target_type}, Subtype: {target_subtype}")

        # Early validation for strategies
        if target_type == "strategy":
            try:
                target_config = get_target_config(db, user_id, target_id)
                target_symbol = target_config["target_symbol"]
                target_name = target_config["target_name"]
            except ValueError as e:
                raise handle_invalid_stream_error(str(e))
        else:
            # For assets, we'll validate during backtest execution
            target_symbol = target_id  # Use symbol as is for assets
            target_name = target_id

        # Check concurrent backtest limit (10 max per user)
        from sqlalchemy import text
        concurrent_count = db.execute(text("""
  SELECT COUNT(*) FROM backtests
  WHERE user_id = :user_id AND backtest_status IN ('queued', 'executing')
  """), {"user_id": user_id}).scalar()

        if concurrent_count >= 10:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "concurrent_limit_exceeded",
                    "message": "Maximum 10 concurrent backtests allowed. Please wait for existing backtests to complete."
                }
            )

    # Calculate projected usage and validate limits
    projected_usage_cents = get_projected_usage_cents(target_subtype)

    # Get sum of projected usage from existing non-completed backtests
    existing_projected = db.execute(text("""
 SELECT COALESCE(SUM(projected_usage_cents), 0) FROM backtests
 WHERE user_id = :user_id AND backtest_status IN ('queued', 'executing')
 """), {"user_id": user_id}).scalar()

    total_projected_usage = existing_projected + projected_usage_cents

    # Enhanced usage check including projected usage
    if not await check_usage_limits(db, user_id, total_projected_usage):
    from app.services.internal.auth.user_service import get_usage_limit_error
    error_details = await get_usage_limit_error(db, user_id, total_projected_usage)
    if error_details:
    raise HTTPException(
        status_code=402,
        detail=error_details
    )
    else:
    raise HTTPException(
        status_code=402,
        detail={
            "error": "insufficient_funds",
            "message": "Usage limits exceeded."
        }
    )

    # Create backtest config for queuing with hierarchical target structure
    backtest_config = {
        "target_id": target_id,
        "target_type": target_type,
        "target_subtype": target_subtype,
        "target_symbol": target_symbol,
        "target_name": target_name,
        "start_date": backtest_request.start_date.isoformat() if backtest_request.start_date else None,
        "end_date": backtest_request.end_date.isoformat() if backtest_request.end_date else None,
        "initial_capital": backtest_request.initial_capital
    }

    # Create backtest record for Celery processing
    queued_backtest = crud_backtests.queue_backtest(db, user_id, backtest_config, projected_usage_cents)

    # BILLING CHARGE: Backtest creation is charged (1¢ per call)
    # Creating a backtest represents the core value we provide.
    # Users can then poll GET /backtests/{id} for free to check status and retrieve results.
    try:
    await charge_backtest_endpoint_call(user_id)
    logger.info(f"Charged user {user_id} API call cost")
    except Exception as e:
    logger.error(f"Failed to charge API call cost for user {user_id}: {str(e)}")
    # Continue with backtest - billing failure shouldn't block the operation

    # Dispatch to Celery with error handling
    from app.workers.celery_tasks import execute_backtest_task

    try:
    task = execute_backtest_task.delay(queued_backtest.id)
    logger.info(f"✅ Queued backtest {queued_backtest.id} with Celery task {task.id}")
    except Exception as e:
    logger.error(f"❌ Failed to queue backtest {queued_backtest.id} to Celery: {str(e)}")
    # Mark backtest as failed immediately
    crud_backtests.fail_backtest(db, queued_backtest.id, f"Queue failed: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail={"error": "queue_failed", "message": "Backtest could not be queued - please try again"}
    )

    # Return immediate response with queued status and hierarchical structure
    return {
        "backtest_id": queued_backtest.id,
        "backtest_status": "queued",
        "backtest_config": {
            "target_id": target_id,
            "target_type": target_type,
            "target_subtype": target_subtype,
            "target_symbol": target_symbol,
            "target_name": target_name,
            "start_date": backtest_request.start_date.isoformat() if backtest_request.start_date else None,
            "end_date": backtest_request.end_date.isoformat() if backtest_request.end_date else None,
            "initial_capital": backtest_request.initial_capital
        }
    }

    except APIError as e:
        # Re-raise APIError - it will be handled by global exception handler
    raise e
    except HTTPException as e:
        # Re-raise HTTPException (like our projected usage error)
    raise e
    except Exception as e:
    import traceback
    error_msg = f"{type(e).__name__}: {str(e)}"
    logger.error(f"Failed to queue backtest: {error_msg}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise handle_backtest_failed_error(error_msg)


@router.get(
    "",
    operation_id="listBacktests",
    summary="List Backtests",
    response_model=List[dict],
    responses={
        200: {
            "description": "Backtests retrieved successfully",
            "content": {
                "application/json": {
                 "example": [
                     {
                         "backtest_id": "bt-12345678-1234-5678-9abc-123456789012",
                         "backtest_status": "completed",
                         "backtest_config": {
                             "target_id": "VTI",
                             "target_type": "asset",
                             "target_subtype": "stock",
                             "target_symbol": "VTI",
                             "target_name": "VTI",
                             "start_date": "2020-01-01T00:00:00",
                             "end_date": None,
                             "initial_capital": 100000.0
                         },
                         "backtest_metrics": {
                             "final_value": 125000.0,
                             "total_return": 0.25,
                             "annualized_return": 0.12,
                             "volatility": 0.18,
                             "sharpe_ratio": 0.67,
                             "max_drawdown": -0.15
                         },
                         "backtest_info": {
                             "created_at": "2024-01-15T10:30:00Z",
                             "started_at": "2024-01-15T10:30:05Z",
                             "finished_at": "2024-01-15T10:30:15Z",
                             "queued_seconds": 5.0,
                             "execution_seconds": 10.0,
                             "completion_seconds": 15.0,
                             "warnings": [],
                             "errors": []
                         }
                     }
                 ]
                }
            }
        }
    }
)
async def list_backtests(
    target_id: str = Query(
        default=None,
        description="Filter by specific asset symbol or strategy ID (e.g., 'VTI' or 'sb-12345')"
    ),
    status: str = Query(
        default=None,
        description="Filter by execution status",
        enum=["queued", "executing", "completed", "failed"]
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of backtests to return (newest first)"
    ),
    current_user: Tuple[uuid.UUID, APIKey] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all backtests with optional filtering.

    Returns array ordered by creation date (newest first) with summary metrics and configuration.
    Filter by specific target or execution status, with configurable result limit.
    """
    try:
        # Extract user_id from current_user tuple
    user_id, api_key = current_user

    # Initialize logger for this function
    logger = get_domain_logger('api', __name__)

    # NO BILLING CHARGE: Listing backtests is free
    # Users poll this endpoint to check backtest status, so we don't charge for reads.
    # The value is in creating backtests (POST), not reading results (GET).

    # Build query with filters - only show user's own backtests
    query = db.query(Backtest).filter(Backtest.user_id == user_id)

    # Apply target_id filter (matches asset symbols or strategy IDs)
    if target_id:
    query = query.filter(Backtest.target_id == target_id)

    # Apply status filter
    if status:
    query = query.filter(Backtest.backtest_status == status)

    # Apply ordering and limit (always newest first)
    backtests = query.order_by(Backtest.created_at.desc()).limit(limit).all()

    # Convert to dict format for response
    backtest_list = []
    for bt in backtests:
        # Extract metrics from JSONB field
    metrics = bt.backtest_metrics or {}
    config = bt.backtest_config or {}

    backtest_dict = {
        "backtest_id": bt.id,
        "backtest_status": bt.backtest_status,
        "backtest_config": {
            "target_id": bt.target_id,
            "target_type": bt.target_type,
            "target_subtype": bt.target_subtype,
            "target_symbol": bt.target_symbol,
            "target_name": bt.target_name,
            "start_date": config.get("start_date"),
            "end_date": config.get("end_date"),
            "initial_capital": config.get("initial_capital")
        },
        "backtest_metrics": {
            "final_value": metrics.get("final_value"),
            "total_return": metrics.get("total_return"),
            "annualized_return": metrics.get("annualized_return"),
            "volatility": metrics.get("volatility"),
            "sharpe_ratio": metrics.get("sharpe_ratio"),
            "max_drawdown": metrics.get("max_drawdown")
        },
        "backtest_info": {
            "created_at": bt.created_at.isoformat() if bt.created_at else None,
            "started_at": bt.started_at.isoformat() if bt.started_at else None,
            "finished_at": bt.finished_at.isoformat() if bt.finished_at else None,
            "queued_seconds": bt.queued_seconds,
            "execution_seconds": bt.execution_seconds,
            "completion_seconds": bt.completion_seconds,
            "warnings": bt.backtest_info.get("warnings", []) if bt.backtest_info else [],
            "errors": bt.backtest_info.get("errors", []) if bt.backtest_info else []
        }
    }
    backtest_list.append(backtest_dict)

    return backtest_list

    except Exception as e:
    raise handle_retrieval_failed_error("backtests", str(e))


@router.get(
    "/{backtest_id}",
    operation_id="getBacktest",
    summary="Get Backtest",
    responses={
        200: {
            "description": "Backtest retrieved successfully",
            "content": {
                "application/json": {
                 "example": {
                     "backtest_id": "bt-12345678-1234-5678-9abc-123456789012",
                     "backtest_status": "completed",
                     "celery_status": "SUCCESS",
                     "task_id": "abc123-task-id",
                     "backtest_config": {
                         "target_id": "VTI",
                         "target_type": "asset",
                         "target_subtype": "stock",
                         "target_symbol": "VTI",
                         "target_name": "VTI",
                         "start_date": "2020-01-01T00:00:00",
                         "end_date": None,
                         "initial_capital": 100000.0
                     },
                     "backtest_metrics": {
                         "final_value": 125000.0,
                         "total_return": 0.25,
                         "annualized_return": 0.12,
                         "volatility": 0.18,
                         "sharpe_ratio": 0.67,
                         "max_drawdown": -0.15
                     },
                     "backtest_history": {
                         "equity": [
                             {"date": "2020-01-01T00:00:00", "value": 100000.0}
                         ],
                         "allocations": [
                             {"date": "2020-01-01T00:00:00", "positions": {"VTI": 1.0}}
                         ]
                     },
                     "backtest_info": {
                         "created_at": "2024-01-15T10:30:00Z",
                         "started_at": "2024-01-15T10:30:05Z",
                         "finished_at": "2024-01-15T10:30:15Z",
                         "queued_seconds": 5.0,
                         "execution_seconds": 10.0,
                         "completion_seconds": 15.0
                     }
                 }
                }
            }
        },
        404: {
            "description": "Backtest not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "not_found",
                            "message": "Backtest not found: bt-invalid-id"
                        }
                    }
                }
            }
        }
    }
)
async def get_backtest(
    backtest_id: str,
    current_user: Tuple[uuid.UUID, APIKey] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve complete backtest results including config, metrics, and history.

    Poll this endpoint for status updates. History is available when status='completed'.
    """
    # Extract user_id from current_user tuple
    user_id, api_key = current_user

    # Initialize logger for this function
    logger = get_domain_logger('api', __name__)

    # NO BILLING CHARGE: Getting backtest results is free
    # Users poll this endpoint repeatedly to check backtest status, so we don't charge for reads.
    # The value is in creating backtests (POST), not reading results (GET).

    backtest = crud_backtests.get_backtest(db=db, backtest_id=backtest_id)
    if not backtest:
    raise handle_not_found_error("backtest", backtest_id)

    # Ensure user can only access their own backtests
    if backtest.user_id != user_id:
    raise handle_not_found_error("backtest", backtest_id)  # Return 404 instead of 403 for security

    # Get Celery task status if available
    celery_status = None
    if backtest.celery_task_id:
    try:
    from app.workers.celery_app import celery_app
    task = celery_app.AsyncResult(backtest.celery_task_id)
    celery_status = task.status
    except Exception:
    celery_status = "UNKNOWN"

    # Convert to dict format for response
    config = backtest.backtest_config or {}
    metrics = backtest.backtest_metrics or {}
    history = backtest.backtest_history or {}

    return {
        "backtest_id": backtest.id,
        "backtest_status": backtest.backtest_status,
        "celery_status": celery_status,
        "task_id": backtest.celery_task_id,
        "backtest_config": {
            "target_id": backtest.target_id,
            "target_type": backtest.target_type,
            "target_subtype": backtest.target_subtype,
            "target_symbol": backtest.target_symbol,
            "target_name": backtest.target_name,
            "start_date": config.get("start_date"),
            "end_date": config.get("end_date"),
            "initial_capital": config.get("initial_capital")
        },
        "backtest_metrics": metrics,
        "backtest_history": history,
        "backtest_info": {
            "created_at": backtest.created_at.isoformat() if backtest.created_at else None,
            "started_at": backtest.started_at.isoformat() if backtest.started_at else None,
            "finished_at": backtest.finished_at.isoformat() if backtest.finished_at else None,

            "queued_seconds": backtest.queued_seconds,
            "execution_seconds": backtest.execution_seconds,
            "completion_seconds": backtest.completion_seconds,
            **(backtest.backtest_info or {})
        }
    }


def _transform_to_new_schema(
    raw_results: Dict[str, Any],
    request: BacktestRequest,
    target_type: str,
    target_subtype: str,
    target_identifier: str
) -> Dict[str, Any]:
    """Transform raw backtest results into the new organized schema structure"""

    # Generate unique backtest ID
    backtest_id = f"bt-{str(uuid.uuid4())}"
    created_at = datetime.utcnow()

    # Extract basic info from raw results
    target_name = raw_results.get("target_name", f"Unknown {target_subtype}")
    final_value = raw_results.get("final_value", request.initial_capital)

    # Create backtest config
    # Prefer actual computed dates from raw_results when available to reflect
    # effective backtest bounds (handles omitted or truncated request dates)
    actual_start = raw_results.get("actual_start_date", request.start_date)
    actual_end = raw_results.get("actual_end_date", request.end_date)

    # Determine stream_symbol and proper stream_id
    stream_symbol = request.stream_symbol or stream_identifier

    # NEEDS FIXING. THIS IS FUCKING SILLY. WE HAVE DETERMINISTIC STREAM IDS FOR ASSETS IN ALPACA_CLIENT.
    # For assets, generate proper asset ID; for other streams, use identifier as-is
    if stream_type == StreamType.ASSET:
        # Generate proper asset ID for database storage
    proper_stream_id = f"a-{str(uuid.uuid4())}"
    else:
    proper_stream_id = stream_identifier

    backtest_config = BacktestConfig(
        stream_id=proper_stream_id,
        stream_symbol=stream_symbol,
        stream_type=stream_type,
        stream_name=stream_name,
        start_date=actual_start,
        end_date=actual_end,
        initial_capital=request.initial_capital
    )

    # Create backtest metrics
    total_return = (final_value - request.initial_capital) / request.initial_capital

    backtest_metrics = BacktestMetrics(
        final_value=final_value,
        total_return=total_return,
        annualized_return=raw_results.get("annualized_return"),
        volatility=raw_results.get("volatility"),
        sharpe_ratio=raw_results.get("sharpe_ratio"),
        max_drawdown=raw_results.get("max_drawdown")
    )

    # Create backtest history
    equity_data = raw_results.get("equity_curve", [])
    allocation_data = raw_results.get("allocations", [])

    # Transform equity data to simple dictionaries
    equity_points = []
    for point in equity_data:
    equity_points.append({
        "date": point.get("date").isoformat() if hasattr(point.get("date"), 'isoformat') else str(point.get("date")),
        "value": point.get("value", request.initial_capital)
    })

    # Transform allocation data to simple dictionaries
    allocation_points = []
    for point in allocation_data:
        # Both basket and strategy services now return 'positions' field consistently
    allocations_dict = point.get("positions", point.get("allocations", {}))
    allocation_points.append({
        "date": point.get("date").isoformat() if hasattr(point.get("date"), 'isoformat') else str(point.get("date")),
        "positions": allocations_dict
    })

    backtest_history = BacktestHistory(
        equity=equity_points,
        allocations=allocation_points
    )

    return BacktestResults(
        backtest_id=backtest_id,
        created_at=created_at,
        backtest_config=backtest_config,
        backtest_metrics=backtest_metrics,
        backtest_history=backtest_history,
        backtest_info=raw_results.get("backtest_info")
    )
