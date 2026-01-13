"""
Enhanced LatencyZero Gateway with Advanced Features
Includes: Semantic Prediction, Error Bounds, Resilience Layer
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import time
from datetime import datetime
import traceback

# Basic components
try:
    from prediction_engine import PredictionEngine
    from approximation_store import ApproximationStore
    from confidence_evaluator import ConfidenceEvaluator
    from refinement_worker import RefinementWorker
except ImportError:
    from gateway.prediction_engine import PredictionEngine
    from gateway.approximation_store import ApproximationStore
    from gateway.confidence_evaluator import ConfidenceEvaluator
    from gateway.refinement_worker import RefinementWorker

# Advanced features (optional)
try:
    from advanced import (
        AdvancedPredictionEngine,
        FormalErrorBounds,
        StaleOnErrorLayer,
        ResilienceConfig
    )
    ADVANCED_FEATURES = True
    print("✅ Advanced features loaded")
except ImportError:
    ADVANCED_FEATURES = False
    print("⚠️  Advanced features not available (install: pip install sentence-transformers scikit-learn scipy)")


app = FastAPI(
    title="LatencyZero Gateway",
    description="A³ Gateway with Advanced Features",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
USE_SEMANTIC_PREDICTION = True  # Enable semantic features
USE_ERROR_BOUNDS = True          # Enable error tracking
USE_RESILIENCE = True            # Enable stale-on-error

# Initialize components
approximation_store = ApproximationStore()
confidence_evaluator = ConfidenceEvaluator()
refinement_worker = RefinementWorker()

# Basic prediction engine (fallback)
prediction_engine = PredictionEngine()

# Advanced features (if available)
advanced_prediction_engine = None
error_bounds_tracker = None
resilience_layer = None

if ADVANCED_FEATURES:
    if USE_SEMANTIC_PREDICTION:
        try:
            advanced_prediction_engine = AdvancedPredictionEngine(
                use_embeddings=True,
                similarity_threshold=0.75
            )
            print("✅ Semantic prediction enabled")
        except Exception as e:
            print(f"⚠️  Semantic prediction failed to initialize: {e}")
    
    if USE_ERROR_BOUNDS:
        try:
            error_bounds_tracker = FormalErrorBounds()
            print("✅ Error bounds tracking enabled")
        except Exception as e:
            print(f"⚠️  Error bounds failed to initialize: {e}")
    
    if USE_RESILIENCE:
        try:
            resilience_layer = StaleOnErrorLayer(ResilienceConfig(
                max_stale_age=3600,
                min_confidence_for_stale=0.80,
                circuit_breaker_threshold=5
            ))
            print("✅ Resilience layer enabled")
        except Exception as e:
            print(f"⚠️  Resilience layer failed to initialize: {e}")


class StoreRequest(BaseModel):
    function: str
    hash: str
    result: str
    execution_time: float
    timestamp: float
    query_input: Optional[str] = None  # For semantic analysis
    input_data: Optional[str] = None  # For numeric interpolation


class ApproximateResponse(BaseModel):
    available: bool
    result: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = {}
    semantic_match: Optional[bool] = False
    stale: Optional[bool] = False


@app.get("/")
async def root():
    return {
        "service": "LatencyZero Gateway (Enhanced)",
        "status": "operational",
        "version": "0.2.0",
        "features": {
            "semantic_prediction": advanced_prediction_engine is not None,
            "error_bounds": error_bounds_tracker is not None,
            "resilience": resilience_layer is not None
        }
    }


@app.get("/api/v1/approximate", response_model=ApproximateResponse)
async def get_approximation(
    function: str,
    hash: str,
    tolerance: float = 0.02,
    query_input: Optional[str] = None,
    input_data: Optional[str] = None,  # NEW
    authorization: Optional[str] = Header(None)
):
    """
    Get approximation with advanced features:
    - Semantic similarity matching
    - Interpolation from similar queries
    - Stale-on-error resilience
    """
    try:
        # Try exact match first
        stored = approximation_store.get(function, hash)
        
        # If no exact match but semantic enabled, try semantic match
        if not stored and advanced_prediction_engine and query_input:
            # Check if we can interpolate
            similar = advanced_prediction_engine.can_interpolate(
                function,
                query_input,
                hash
            )
            
            if similar and len(similar) > 0:
                # Use the most similar cached result
                best_match_hash, similarity = similar[0]
                stored = approximation_store.get(function, best_match_hash)
                
                if stored:
                    print(f"🔍 Semantic match: {similarity*100:.1f}% similar")
                    stored['semantic_match'] = True
                    stored['similarity'] = similarity
        
        if not stored:
            return ApproximateResponse(available=False)
        
        # Evaluate confidence
        confidence = confidence_evaluator.evaluate(
            function=function,
            hash=hash,
            stored_data=stored,
            tolerance=tolerance
        )
        
        if confidence >= (1 - tolerance):
            # Record hit
            if advanced_prediction_engine and query_input:
                advanced_prediction_engine.record_query(function, query_input, hash)
            else:
                prediction_engine.record_hit(function, hash)
            
            return ApproximateResponse(
                available=True,
                result=stored['result'],
                confidence=confidence,
                semantic_match=stored.get('semantic_match', False),
                metadata={
                    'age_seconds': time.time() - stored['timestamp'],
                    'original_execution_time': stored['execution_time'],
                    'hit_count': stored.get('hit_count', 1),
                    'similarity': stored.get('similarity', 1.0)
                }
            )
        else:
            return ApproximateResponse(available=False)
    
    except Exception as e:
        print(f"❌ Error in get_approximation: {e}")
        traceback.print_exc()
        return ApproximateResponse(available=False)


@app.post("/api/v1/store")
async def store_result(
    request: StoreRequest,
    authorization: Optional[str] = Header(None)
):
    """Store result with advanced tracking"""
    try:
        # Store in approximation store
        approximation_store.put(
            function=request.function,
            query_hash=request.hash,
            result=request.result,
            execution_time=request.execution_time,
            timestamp=request.timestamp
        )
        
        # Record for prediction (basic or advanced)
        if advanced_prediction_engine and request.query_input:
            advanced_prediction_engine.record_query(
                request.function,
                request.query_input,
                request.hash
            )
        else:
            prediction_engine.record_query(request.function, request.hash)
        
        # Schedule refinement
        refinement_worker.schedule_refinement(request.function, request.hash)
        
        return {
            "status": "stored",
            "function": request.function,
            "hash": request.hash[:8] + "...",
            "semantic_enabled": advanced_prediction_engine is not None
        }
    
    except Exception as e:
        print(f"❌ Storage error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/error/record")
async def record_error(
    function: str,
    approximation: str,
    exact: str,
    authorization: Optional[str] = Header(None)
):
    """Record error between approximation and exact result"""
    if not error_bounds_tracker:
        return {"status": "error_tracking_disabled"}
    
    try:
        # Parse results (assuming JSON strings)
        import json
        approx_val = json.loads(approximation)
        exact_val = json.loads(exact)
        
        # Record error
        error_bounds_tracker.record_error(
            function,
            approx_val,
            exact_val
        )
        
        return {"status": "recorded"}
    
    except Exception as e:
        print(f"❌ Error recording: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/error/bound")
async def get_error_bound(
    function: str,
    confidence_level: float = 0.95,
    authorization: Optional[str] = Header(None)
):
    """Get formal error bound for function"""
    if not error_bounds_tracker:
        return {"error": "error_tracking_disabled"}
    
    from advanced.formal_error_bounds import ErrorBoundType
    
    bound = error_bounds_tracker.get_error_bound(
        function,
        ErrorBoundType.PERCENTILE,
        confidence_level
    )
    
    if not bound:
        return {"error": "insufficient_data"}
    
    return {
        "bound_type": bound.bound_type.value,
        "max_error": bound.max_error,
        "confidence_level": bound.confidence_level,
        "sample_size": bound.sample_size,
        "historical_accuracy": bound.historical_accuracy,
        "worst_case_error": bound.worst_case_error,
        "description": str(bound)
    }


@app.get("/api/v1/error/sla")
async def check_sla_compliance(
    function: str,
    sla_max_error: float = 0.05,
    sla_confidence: float = 0.95,
    authorization: Optional[str] = Header(None)
):
    """Check SLA compliance for function"""
    if not error_bounds_tracker:
        return {"error": "error_tracking_disabled"}
    
    compliance = error_bounds_tracker.get_sla_compliance(
        function,
        sla_max_error,
        sla_confidence
    )
    
    return compliance


@app.get("/api/v1/stats")
async def get_stats(authorization: Optional[str] = Header(None)):
    """Get comprehensive statistics"""
    stats = {
        "approximation_store": approximation_store.get_stats(),
        "confidence_evaluator": confidence_evaluator.get_stats(),
        "refinement_worker": refinement_worker.get_stats()
    }
    
    # Add advanced stats if available
    if advanced_prediction_engine:
        stats["semantic_prediction"] = advanced_prediction_engine.get_stats()
    else:
        stats["prediction_engine"] = prediction_engine.get_stats()
    
    if error_bounds_tracker:
        stats["error_bounds"] = error_bounds_tracker.get_sla_report()
    
    if resilience_layer:
        stats["resilience"] = resilience_layer.get_resilience_metrics()
    
    return stats


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "basic": True,
            "semantic": advanced_prediction_engine is not None,
            "error_bounds": error_bounds_tracker is not None,
            "resilience": resilience_layer is not None
        }
    }


@app.on_event("startup")
async def startup_event():
    print("\n" + "="*70)
    print("🚀 LatencyZero Gateway Starting (Enhanced)")
    print("="*70)
    
    refinement_worker.start()
    
    print("\n📊 Features:")
    print(f"   Basic caching: ✅")
    print(f"   Semantic prediction: {'✅' if advanced_prediction_engine else '❌'}")
    print(f"   Error bounds: {'✅' if error_bounds_tracker else '❌'}")
    print(f"   Resilience layer: {'✅' if resilience_layer else '❌'}")
    
    print("\n✅ Gateway operational")
    print("="*70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 LatencyZero Gateway shutting down...")
    refinement_worker.stop()
    approximation_store.close()
    print("✅ Gateway shutdown complete")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )