---
name: model-serving-patterns
description: Master production-ready model serving patterns including batch vs real-time inference, A/B testing, canary deployments, model versioning, and performance optimization strategies. Use when deploying ML models to production or optimizing inference infrastructure.
---

# Model Serving Patterns

Master production-ready machine learning model serving architectures, deployment strategies, and performance optimization for scalable AI applications.

## When to Use This Skill

- Deploying ML models to production environments
- Optimizing model inference performance and latency
- Implementing A/B testing and canary deployments for ML models
- Designing batch and real-time inference systems
- Managing model versioning and rollback strategies
- Scaling ML inference infrastructure
- Implementing model monitoring and observability
- Optimizing inference costs and resource utilization

## Core Serving Patterns

### 1. Real-Time Inference Patterns

**Synchronous Inference:**
```python
# High-throughput synchronous model serving
import asyncio
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
import time
from concurrent.futures import ThreadPoolExecutor

class RealTimeModelServer:
    def __init__(self, model, max_workers: int = 10):
        self.model = model
        self.app = FastAPI()
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.metrics = ModelMetrics()
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.post("/predict")
        async def predict(request: Dict[str, Any]):
            start_time = time.time()
            
            try:
                # Validate input
                input_data = self.validate_input(request["data"])
                
                # Run inference in thread pool for CPU-intensive models
                loop = asyncio.get_event_loop()
                prediction = await loop.run_in_executor(
                    self.thread_pool, 
                    self.model.predict, 
                    input_data
                )
                
                # Record metrics
                latency = time.time() - start_time
                await self.metrics.record_inference(latency, "success")
                
                return {
                    "prediction": prediction,
                    "latency_ms": round(latency * 1000, 2),
                    "model_version": self.model.version
                }
                
            except Exception as e:
                latency = time.time() - start_time
                await self.metrics.record_inference(latency, "error")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "model_loaded": self.model is not None}
    
    def validate_input(self, data: Any) -> Any:
        # Input validation logic
        if isinstance(data, list) and len(data) > 1000:
            raise ValueError("Batch size too large")
        return data
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8080):
        import uvicorn
        await self.app.run_server(host=host, port=port)

# Usage
# server = RealTimeModelServer(my_model)
# await server.start_server()
```

**Asynchronous Inference:**
```python
# Asynchronous inference with queue-based processing
import asyncio
from asyncio import Queue
from dataclasses import dataclass
from typing import Optional

@dataclass
class InferenceRequest:
    request_id: str
    data: Any
    response_queue: Queue
    created_at: float

class AsyncModelServer:
    def __init__(self, model, max_queue_size: int = 10000):
        self.model = model
        self.request_queue = asyncio.Queue(maxsize=max_queue_size)
        self.results_cache = {}
        self.processing = False
        self.metrics = AsyncMetrics()
    
    async def submit_request(self, request: InferenceRequest):
        try:
            await self.request_queue.put(request)
            await self.metrics.record_queue_size(self.request_queue.qsize())
        except asyncio.QueueFull:
            raise HTTPException(status_code=503, detail="Server overloaded")
    
    async def process_requests(self):
        while True:
            try:
                # Process request from queue
                request = await self.request_queue.get()
                start_time = time.time()
                
                # Run inference
                prediction = await self.model.predict(request.data)
                latency = time.time() - start_time
                
                # Send result back
                await request.response_queue.put({
                    "request_id": request.request_id,
                    "prediction": prediction,
                    "latency_ms": round(latency * 1000, 2)
                })
                
                await self.metrics.record_inference(latency)
                
            except Exception as e:
                await request.response_queue.put({
                    "request_id": request.request_id,
                    "error": str(e)
                })
    
    async def start_server(self):
        self.processing = True
        # Start request processing task
        asyncio.create_task(self.process_requests())
        
        # Start API server
        await self.start_api_server()

# Async API endpoint
@server.app.post("/predict/async")
async def predict_async(request: Dict[str, Any]):
    response_queue = asyncio.Queue()
    inference_request = InferenceRequest(
        request_id=str(uuid.uuid4()),
        data=request["data"],
        response_queue=response_queue,
        created_at=time.time()
    )
    
    await server.submit_request(inference_request)
    
    # Wait for result with timeout
    try:
        result = await asyncio.wait_for(response_queue.get(), timeout=30.0)
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")
```

### 2. Batch Inference Patterns

**Micro-Batch Processing:**
```python
# Efficient micro-batch inference processing
import numpy as np
from collections import defaultdict
import asyncio

class BatchInferenceServer:
    def __init__(self, model, batch_size: int = 32, max_wait_time: float = 1.0):
        self.model = model
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_requests = []
        self.processing_lock = asyncio.Lock()
        self.metrics = BatchMetrics()
    
    async def add_to_batch(self, request_id: str, data: Any) -> Dict[str, Any]:
        async with self.processing_lock:
            # Add request to pending batch
            self.pending_requests.append({
                "id": request_id,
                "data": data,
                "timestamp": time.time()
            })
            
            # Check if we should process batch
            should_process = (
                len(self.pending_requests) >= self.batch_size or
                (self.pending_requests and 
                 time.time() - self.pending_requests[0]["timestamp"] > self.max_wait_time)
            )
            
            if should_process and len(self.pending_requests) > 0:
                return await self.process_batch()
            else:
                # Return pending status
                return {
                    "status": "pending",
                    "position": len(self.pending_requests),
                    "estimated_wait_ms": self.estimate_wait_time()
                }
    
    async def process_batch(self) -> Dict[str, Any]:
        if not self.pending_requests:
            return {"status": "no_pending_requests"}
        
        # Extract batch data
        batch_data = [req["data"] for req in self.pending_requests]
        request_ids = [req["id"] for req in self.pending_requests]
        
        # Clear pending requests
        self.pending_requests.clear()
        
        start_time = time.time()
        
        try:
            # Run batch inference
            batch_predictions = await self.model.predict_batch(batch_data)
            
            # Calculate per-request latency
            processing_time = time.time() - start_time
            per_request_latency = processing_time / len(batch_data)
            
            # Record metrics
            await self.metrics.record_batch(
                batch_size=len(batch_data),
                processing_time=processing_time,
                per_request_latency=per_request_latency
            )
            
            # Return results
            results = {}
            for i, request_id in enumerate(request_ids):
                results[request_id] = {
                    "prediction": batch_predictions[i],
                    "batch_processed": True,
                    "processing_time_ms": round(per_request_latency * 1000, 2)
                }
            
            return {"status": "completed", "results": results}
            
        except Exception as e:
            # Handle batch processing errors
            error_results = {}
            for request_id in request_ids:
                error_results[request_id] = {
                    "error": str(e),
                    "batch_processed": False
                }
            return {"status": "error", "results": error_results}
    
    def estimate_wait_time(self) -> float:
        """Estimate wait time for next batch processing"""
        if not self.pending_requests:
            return 0.0
        
        oldest_request = self.pending_requests[0]
        time_waited = time.time() - oldest_request["timestamp"]
        
        if len(self.pending_requests) >= self.batch_size:
            return 0.0  # Batch is full, will process immediately
        
        remaining_wait = max(0, self.max_wait_time - time_waited)
        return remaining_wait * 1000  # Convert to milliseconds

# Usage with streaming
async def streaming_inference_example():
    server = BatchInferenceServer(my_model, batch_size=16, max_wait_time=0.5)
    
    # Simulate multiple concurrent requests
    tasks = []
    for i in range(100):
        task = asyncio.create_task(
            server.add_to_batch(f"req_{i}", get_test_data(i))
        )
        tasks.append(task)
    
    # Process all requests
    results = await asyncio.gather(*tasks)
    return results
```

### 3. Model Versioning Patterns

**Version Management System:**
```python
# Advanced model versioning and deployment
import semantic_version
from typing import Dict, List, Optional
import asyncio

class ModelVersion:
    def __init__(self, model_id: str, version: str, model_instance, metadata: Dict):
        self.model_id = model_id
        self.version = version
        self.model_instance = model_instance
        self.metadata = metadata
        self.deployment_time = time.time()
        self.metrics = VersionMetrics()
    
    async def predict(self, data: Any) -> Any:
        return await self.model_instance.predict(data)
    
    async def health_check(self) -> Dict:
        try:
            # Run quick health check
            test_prediction = await self.predict(self.metadata.get("health_check_data"))
            return {"status": "healthy", "test_prediction": test_prediction}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

class ModelRegistry:
    def __init__(self):
        self.models = {}
        self.deployments = {}
        self.load_balancer = LoadBalancer()
    
    async def register_model(self, model_id: str, version: str, 
                           model_instance, metadata: Dict) -> ModelVersion:
        model_version = ModelVersion(model_id, version, model_instance, metadata)
        
        if model_id not in self.models:
            self.models[model_id] = {}
        
        self.models[model_id][version] = model_version
        
        # Update load balancer
        await self.load_balancer.add_model_version(model_id, version, model_version)
        
        return model_version
    
    async def deploy_model(self, model_id: str, version: str, 
                          deployment_config: Dict) -> str:
        """Deploy model version with specified configuration"""
        if model_id not in self.models or version not in self.models[model_id]:
            raise ValueError(f"Model {model_id} version {version} not found")
        
        model_version = self.models[model_id][version]
        deployment_id = f"{model_id}:{version}:{int(time.time())}"
        
        # Create deployment configuration
        deployment = {
            "id": deployment_id,
            "model_id": model_id,
            "version": version,
            "status": "deploying",
            "config": deployment_config,
            "created_at": time.time(),
            "endpoints": {}
        }
        
        self.deployments[deployment_id] = deployment
        
        # Perform deployment
        await self._perform_deployment(deployment, model_version)
        
        return deployment_id
    
    async def _perform_deployment(self, deployment: Dict, model_version: ModelVersion):
        """Execute the actual deployment"""
        try:
            # Health check before deployment
            health_check = await model_version.health_check()
            if health_check["status"] != "healthy":
                deployment["status"] = "failed"
                deployment["error"] = "Health check failed"
                return
            
            # Deploy to serving infrastructure
            serving_config = await self._setup_serving_infrastructure(deployment)
            deployment["endpoints"] = serving_config
            
            # Start serving
            serving_endpoint = await self._start_model_serving(model_version, serving_config)
            
            deployment["status"] = "deployed"
            deployment["serving_endpoint"] = serving_endpoint
            deployment["deployed_at"] = time.time()
            
        except Exception as e:
            deployment["status"] = "failed"
            deployment["error"] = str(e)
            deployment["failed_at"] = time.time()
    
    async def route_inference(self, model_id: str, data: Any, 
                            routing_config: Dict = None) -> Dict[str, Any]:
        """Route inference to appropriate model version(s)"""
        if routing_config and routing_config.get("strategy") == "canary":
            # Canary deployment routing
            canary_percentage = routing_config.get("canary_percentage", 10)
            if random.randint(1, 100) <= canary_percentage:
                # Route to canary version
                canary_version = routing_config.get("canary_version")
                if canary_version:
                    model_version = self.models[model_id][canary_version]
                    prediction = await model_version.predict(data)
                    return {
                        "prediction": prediction,
                        "version": canary_version,
                        "deployment_type": "canary"
                    }
        
        # Route to stable version
        stable_version = routing_config.get("stable_version") or \
                        await self.get_latest_stable_version(model_id)
        
        model_version = self.models[model_id][stable_version]
        prediction = await model_version.predict(data)
        
        return {
            "prediction": prediction,
            "version": stable_version,
            "deployment_type": "stable"
        }

# Model registry usage
registry = ModelRegistry()

# Register new model version
await registry.register_model(
    model_id="recommendation_model",
    version="2.1.0",
    model_instance=my_model,
    metadata={"accuracy": 0.95, "training_date": "2025-11-12"}
)

# Deploy with canary strategy
await registry.deploy_model(
    model_id="recommendation_model",
    version="2.1.0",
    deployment_config={
        "replicas": 3,
        "canary_percentage": 10,
        "canary_version": "2.1.0",
        "stable_version": "2.0.5"
    }
)
```

### 4. A/B Testing and Experimentation

**Model Experimentation Framework:**
```python
# A/B testing framework for model comparison
import hashlib
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    name: str
    model_a: str
    model_b: str
    traffic_split: float  # 0.5 = 50/50 split
    success_metrics: List[str]
    duration_days: int
    min_sample_size: int

class ModelExperimentManager:
    def __init__(self, model_registry: ModelRegistry):
        self.model_registry = model_registry
        self.active_experiments = {}
        self.experiment_results = {}
        self.metrics_collector = MetricsCollector()
    
    async def start_experiment(self, config: ExperimentConfig) -> str:
        experiment_id = f"exp_{config.name}_{int(time.time())}"
        
        experiment = {
            "id": experiment_id,
            "config": config,
            "status": "running",
            "started_at": time.time(),
            "current_split": {},
            "metrics": {}
        }
        
        self.active_experiments[experiment_id] = experiment
        return experiment_id
    
    async def route_to_experiment(self, experiment_id: str, user_id: str) -> Tuple[str, Dict]:
        """Route user to experiment with consistent hashing"""
        if experiment_id not in self.active_experiments:
            raise ValueError("Experiment not found")
        
        experiment = self.active_experiments[experiment_id]
        config = experiment["config"]
        
        # Consistent hashing for stable routing
        hash_value = int(hashlib.md5(f"{experiment_id}:{user_id}".encode()).hexdigest(), 16)
        percentage = (hash_value % 10000) / 100  # 0.0 to 99.99
        
        if percentage < config.traffic_split * 100:
            model_version = config.model_a
            variant = "A"
        else:
            model_version = config.model_b
            variant = "B"
        
        # Update experiment statistics
        if variant not in experiment["current_split"]:
            experiment["current_split"][variant] = {"count": 0, "models": set()}
        
        experiment["current_split"][variant]["count"] += 1
        experiment["current_split"][variant]["models"].add(model_version)
        
        return model_version, {"variant": variant, "experiment_id": experiment_id}
    
    async def record_prediction(self, experiment_id: str, variant: str, 
                              prediction: Any, actual: Any = None, 
                              metadata: Dict = None):
        """Record prediction and outcome for experiment analysis"""
        if experiment_id not in self.active_experiments:
            return
        
        experiment = self.active_experiments[experiment_id]
        
        # Collect metrics
        metrics_data = {
            "timestamp": time.time(),
            "variant": variant,
            "prediction": prediction,
            "actual": actual,
            "metadata": metadata or {}
        }
        
        await self.metrics_collector.record_experiment_metric(
            experiment_id, variant, metrics_data
        )
    
    async def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze experiment results and determine winner"""
        experiment = self.active_experiments[experiment_id]
        config = experiment["config"]
        
        # Get metrics for both variants
        metrics_a = await self.metrics_collector.get_variant_metrics(
            experiment_id, "A"
        )
        metrics_b = await self.metrics_collector.get_variant_metrics(
            experiment_id, "B"
        )
        
        # Statistical analysis
        analysis = {
            "experiment_id": experiment_id,
            "duration_days": (time.time() - experiment["started_at"]) / (24 * 3600),
            "sample_size": {
                "variant_a": len(metrics_a),
                "variant_b": len(metrics_b)
            },
            "performance": {}
        }
        
        # Calculate performance for each metric
        for metric in config.success_metrics:
            if metric in ["accuracy", "precision", "recall", "f1_score"]:
                analysis["performance"][metric] = {
                    "variant_a": self._calculate_classification_metric(metric, metrics_a),
                    "variant_b": self._calculate_classification_metric(metric, metrics_b)
                }
            elif metric in ["latency", "throughput"]:
                analysis["performance"][metric] = {
                    "variant_a": self._calculate_latency_metric(metric, metrics_a),
                    "variant_b": self._calculate_latency_metric(metric, metrics_b)
                }
        
        # Determine winner using statistical significance
        winner = await self._determine_winner(analysis, config)
        analysis["winner"] = winner
        
        # Update experiment status
        if winner:
            experiment["status"] = "completed"
            experiment["winner"] = winner
            self.experiment_results[experiment_id] = analysis
        
        return analysis
    
    def _calculate_classification_metric(self, metric: str, metrics_data: List[Dict]) -> float:
        """Calculate classification performance metrics"""
        if metric == "accuracy":
            correct = sum(1 for m in metrics_data if m["prediction"] == m["actual"])
            return correct / len(metrics_data) if metrics_data else 0.0
        
        # Add other metric calculations...
        return 0.0
    
    async def _determine_winner(self, analysis: Dict, config: ExperimentConfig) -> Optional[str]:
        """Determine experiment winner with statistical significance"""
        # Simple winner determination - in practice, use proper statistical tests
        for metric in config.success_metrics:
            if metric in analysis["performance"]:
                perf = analysis["performance"][metric]
                if perf["variant_a"] > perf["variant_b"]:
                    return "A"
                elif perf["variant_b"] > perf["variant_a"]:
                    return "B"
        
        return None

# Experiment usage
experiment_manager = ModelExperimentManager(registry)

# Start A/B test
config = ExperimentConfig(
    name="model_v2_improvement",
    model_a="recommendation_model:2.0.5",
    model_b="recommendation_model:2.1.0",
    traffic_split=0.5,
    success_metrics=["accuracy", "latency"],
    duration_days=7,
    min_sample_size=1000
)

experiment_id = await experiment_manager.start_experiment(config)

# Route user to experiment
user_id = "user_12345"
model_version, routing_info = await experiment_manager.route_to_experiment(experiment_id, user_id)

# Make prediction
prediction = await registry.route_inference(
    "recommendation_model", user_data, 
    routing_config={"stable_version": model_version}
)

# Record outcome
await experiment_manager.record_prediction(
    experiment_id, routing_info["variant"], 
    prediction, actual_user_action
)
```

## Performance Optimization Patterns

### 1. Model Optimization

**Quantization and Pruning:**
```python
# Model optimization for inference performance
import torch
import torch.quantization as quantization
from torch import nn

class OptimizedModelServer:
    def __init__(self, model_path: str, optimization_config: Dict):
        self.model = self.load_and_optimize_model(model_path, optimization_config)
        self.optimization_config = optimization_config
        self.performance_metrics = PerformanceMetrics()
    
    def load_and_optimize_model(self, model_path: str, config: Dict) -> nn.Module:
        # Load base model
        model = torch.load(model_path)
        model.eval()
        
        # Apply optimizations
        if config.get("quantization") == "dynamic":
            model = quantization.quantize_dynamic(
                model, {nn.Linear}, dtype=torch.qint8
            )
        elif config.get("quantization") == "static":
            # Calibration required for static quantization
            model = quantization.quantize_dynamic(
                model, {nn.Linear}, dtype=torch.qint8
            )
        
        if config.get("pruning"):
            # Apply structured pruning
            import torch.nn.utils.prune as prune
            parameters_to_prune = [
                (module, "weight") for module in model.modules()
                if isinstance(module, nn.Linear)
            ]
            prune.global_unstructured(
                parameters_to_prune,
                pruning_method=prune.L1Unstructured,
                amount=config.get("pruning_amount", 0.2),
            )
        
        return model
    
    async def optimized_inference(self, input_data: torch.Tensor) -> Dict[str, Any]:
        start_time = time.time()
        
        # Run optimized inference
        with torch.no_grad():
            if self.optimization_config.get("use_gpu") and torch.cuda.is_available():
                input_data = input_data.cuda()
                prediction = self.model(input_data).cpu()
            else:
                prediction = self.model(input_data)
        
        latency = time.time() - start_time
        
        # Record performance metrics
        await self.performance_metrics.record_inference(
            latency=latency,
            model_size_mb=self._get_model_size_mb(),
            memory_usage_mb=self._get_memory_usage()
        )
        
        return {
            "prediction": prediction.numpy(),
            "latency_ms": round(latency * 1000, 2),
            "optimization": self.optimization_config
        }
    
    def _get_model_size_mb(self) -> float:
        """Calculate model size in megabytes"""
        param_size = sum(p.numel() * p.element_size() for p in self.model.parameters())
        buffer_size = sum(b.numel() * b.element_size() for b in self.model.buffers())
        return (param_size + buffer_size) / (1024 * 1024)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / (1024 * 1024)
        return 0.0

# Optimization configuration
optimization_config = {
    "quantization": "dynamic",  # or "static" or None
    "pruning": True,
    "pruning_amount": 0.3,
    "use_gpu": True,
    "batch_size": 32
}

optimized_server = OptimizedModelServer("model.pth", optimization_config)
```

### 2. Caching Strategies

**Prediction and Feature Caching:**
```python
# Intelligent caching for model predictions and features
import redis
import pickle
from typing import Any, Optional, Dict
from functools import wraps

class ModelCachingLayer:
    def __init__(self, redis_config: Dict, cache_ttl: int = 3600):
        self.redis_client = redis.Redis(**redis_config)
        self.cache_ttl = cache_ttl
        self.cache_stats = CacheStatistics()
    
    def cache_prediction(self, model_id: str, expiration: int = None):
        """Decorator for caching model predictions"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from inputs
                cache_key = self._generate_cache_key(model_id, args, kwargs)
                
                # Try to get from cache
                cached_result = await self._get_cached_prediction(cache_key)
                if cached_result is not None:
                    await self.cache_stats.record_cache_hit(cache_key)
                    return cached_result
                
                # Cache miss - run inference
                result = await func(*args, **kwargs)
                
                # Cache the result
                await self._cache_prediction(cache_key, result, expiration)
                await self.cache_stats.record_cache_miss(cache_key)
                
                return result
            return wrapper
        return decorator
    
    def _generate_cache_key(self, model_id: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from model ID and inputs"""
        # Create hash from inputs
        inputs = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        inputs_str = str(inputs)
        inputs_hash = hashlib.md5(inputs_str.encode()).hexdigest()
        
        return f"prediction:{model_id}:{inputs_hash}"
    
    async def _get_cached_prediction(self, cache_key: str) -> Optional[Any]:
        """Retrieve cached prediction"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return pickle.loads(cached_data)
        except Exception as e:
            print(f"Cache retrieval error: {e}")
        return None
    
    async def _cache_prediction(self, cache_key: str, result: Any, expiration: int = None):
        """Cache prediction result"""
        try:
            serialized_result = pickle.dumps(result)
            self.redis_client.setex(
                cache_key, 
                expiration or self.cache_ttl, 
                serialized_result
            )
        except Exception as e:
            print(f"Caching error: {e}")
    
    async def invalidate_cache(self, model_id: str = None, pattern: str = None):
        """Invalidate cache entries"""
        if model_id:
            # Invalidate all predictions for specific model
            keys = self.redis_client.keys(f"prediction:{model_id}:*")
            if keys:
                self.redis_client.delete(*keys)
        
        if pattern:
            # Invalidate by pattern
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)

# Usage with caching
caching_layer = ModelCachingLayer({"host": "localhost", "port": 6379})

class CachedModelServer:
    def __init__(self, model):
        self.model = model
        self.caching_layer = caching_layer
    
    @caching_layer.cache_prediction("recommendation_model", expiration=1800)
    async def predict(self, user_id: str, items: List[str]) -> Dict[str, Any]:
        # Expensive inference logic
        prediction = await self.model.predict(user_id, items)
        return prediction

# Usage
server = CachedModelServer(my_model)
result = await server.predict("user123", ["item1", "item2"])  # Will be cached
```

## Deployment Strategies

### 1. Blue-Green Deployment

```python
# Blue-green deployment for ML models
class BlueGreenDeployment:
    def __init__(self, model_registry: ModelRegistry):
        self.model_registry = model_registry
        self.deployment_history = []
    
    async def blue_green_deploy(self, model_id: str, new_version: str, 
                              deployment_config: Dict) -> str:
        """Execute blue-green deployment strategy"""
        
        # Get current stable version (Blue)
        current_version = await self.model_registry.get_current_version(model_id)
        
        # Deploy new version to Green environment
        green_deployment_id = await self.model_registry.deploy_model(
            model_id, new_version, {
                **deployment_config,
                "environment": "green",
                "traffic_percentage": 0
            }
        )
        
        # Wait for Green environment to be ready
        await self._wait_for_green_health(green_deployment_id)
        
        # Perform smoke tests
        await self._run_smoke_tests(model_id, new_version)
        
        # Gradual traffic shift
        await self._gradual_traffic_shift(
            model_id, current_version, new_version, deployment_config
        )
        
        # If successful, make Green the new production
        await self._promote_green_to_production(model_id, new_version)
        
        return green_deployment_id
    
    async def _gradual_traffic_shift(self, model_id: str, blue_version: str, 
                                   green_version: str, config: Dict):
        """Gradually shift traffic from Blue to Green"""
        steps = config.get("traffic_shift_steps", [10, 25, 50, 100])
        
        for step in steps:
            print(f"Shifting {step}% traffic to Green version...")
            
            # Update routing configuration
            await self.model_registry.update_routing_config(
                model_id, {
                    f"{blue_version}_percentage": 100 - step,
                    f"{green_version}_percentage": step
                }
            )
            
            # Monitor for issues
            await self._monitor_deployment(model_id, green_version, duration_minutes=5)
            
            if await self._detect_deployment_issues(green_version):
                print(f"Issues detected at {step}% traffic. Rolling back...")
                await self._rollback_deployment(model_id, blue_version)
                return
        
        print("Blue-green deployment successful!")
    
    async def _rollback_deployment(self, model_id: str, stable_version: str):
        """Rollback to stable version"""
        print(f"Rolling back to stable version {stable_version}")
        
        # Update routing to send all traffic to stable version
        await self.model_registry.update_routing_config(
            model_id, {
                f"{stable_version}_percentage": 100
            }
        )
        
        # Mark failed deployment
        await self._mark_deployment_failed(model_id)
```

### 2. Canary Deployment

```python
# Canary deployment with automated rollback
class CanaryDeployment:
    def __init__(self, model_registry: ModelRegistry, metrics_monitor: MetricsMonitor):
        self.model_registry = model_registry
        self.metrics_monitor = metrics_monitor
        self.canary_configs = {}
    
    async def start_canary_deployment(self, model_id: str, canary_version: str,
                                    canary_config: Dict) -> str:
        """Start canary deployment with progressive rollout"""
        
        canary_id = f"canary_{model_id}_{canary_version}_{int(time.time())}"
        
        # Initial canary configuration
        canary_setup = {
            "id": canary_id,
            "model_id": model_id,
            "canary_version": canary_version,
            "current_traffic": 0,
            "target_traffic": canary_config.get("max_traffic", 10),
            "step_size": canary_config.get("step_size", 1),
            "monitoring_duration": canary_config.get("monitoring_duration", 300),  # 5 minutes
            "success_threshold": canary_config.get("success_threshold", 0.95),
            "latency_threshold": canary_config.get("latency_threshold", 1.2),  # 20% worse than baseline
            "status": "starting"
        }
        
        self.canary_configs[canary_id] = canary_setup
        
        # Deploy canary version with minimal traffic
        await self.model_registry.deploy_model(
            model_id, canary_version, {
                "environment": "canary",
                "traffic_percentage": 0,  # Start with 0%
                "replicas": canary_config.get("canary_replicas", 1)
            }
        )
        
        # Start canary monitoring loop
        asyncio.create_task(self._canary_monitor_loop(canary_id))
        
        return canary_id
    
    async def _canary_monitor_loop(self, canary_id: str):
        """Monitor canary deployment and adjust traffic"""
        canary_config = self.canary_configs[canary_id]
        model_id = canary_config["model_id"]
        
        try:
            while canary_config["current_traffic"] < canary_config["target_traffic"]:
                current_traffic = canary_config["current_traffic"]
                next_traffic = min(
                    current_traffic + canary_config["step_size"],
                    canary_config["target_traffic"]
                )
                
                print(f"Canary {canary_id}: Increasing traffic to {next_traffic}%")
                
                # Update traffic allocation
                await self._update_canary_traffic(canary_id, next_traffic)
                
                # Monitor metrics for the duration
                monitoring_start = time.time()
                while time.time() - monitoring_start < canary_config["monitoring_duration"]:
                    # Collect metrics
                    metrics = await self.metrics_monitor.get_canary_metrics(
                        model_id, canary_config["canary_version"]
                    )
                    
                    # Check for issues
                    if await self._evaluate_canary_health(metrics, canary_config):
                        await asyncio.sleep(30)  # Wait 30 seconds between checks
                        continue
                    else:
                        # Rollback due to issues
                        await self._rollback_canary(canary_id)
                        return
                
                canary_config["current_traffic"] = next_traffic
            
            # Canary deployment successful
            await self._promote_canary_to_production(canary_id)
            
        except Exception as e:
            print(f"Canary monitoring error: {e}")
            await self._rollback_canary(canary_id)
    
    async def _evaluate_canary_health(self, metrics: Dict, config: Dict) -> bool:
        """Evaluate if canary is healthy enough to continue"""
        
        # Check success rate
        success_rate = metrics.get("success_rate", 1.0)
        if success_rate < config["success_threshold"]:
            print(f"Canary health check failed: success rate {success_rate} < {config['success_threshold']}")
            return False
        
        # Check latency
        avg_latency = metrics.get("avg_latency_ms", 0)
        baseline_latency = metrics.get("baseline_latency_ms", 100)
        if avg_latency > baseline_latency * config["latency_threshold"]:
            print(f"Canary health check failed: latency {avg_latency}ms > threshold {baseline_latency * config['latency_threshold']}ms")
            return False
        
        # Check error rate
        error_rate = metrics.get("error_rate", 0)
        if error_rate > 0.01:  # 1% error rate threshold
            print(f"Canary health check failed: error rate {error_rate} > 1%")
            return False
        
        return True
    
    async def _rollback_canary(self, canary_id: str):
        """Rollback canary deployment"""
        config = self.canary_configs[canary_id]
        model_id = config["model_id"]
        
        print(f"Rolling back canary {canary_id}")
        
        # Reduce canary traffic to 0
        await self._update_canary_traffic(canary_id, 0)
        
        # Update status
        config["status"] = "rolled_back"
        config["rolled_back_at"] = time.time()
        
        # Log rollback event
        await self._log_deployment_event("canary_rollback", canary_id, config)
```

## Best Practices

### 1. Performance Optimization

- **Batch Processing**: Group small requests for efficiency
- **Model Optimization**: Use quantization, pruning, and distillation
- **Caching**: Cache frequent predictions and features
- **Async Processing**: Use async/await for I/O-bound operations
- **Resource Management**: Monitor and optimize CPU/memory usage
- **GPU Utilization**: Efficient GPU memory management and kernel optimization

### 2. Reliability Patterns

- **Circuit Breakers**: Prevent cascade failures
- **Retry Logic**: Handle transient failures gracefully
- **Health Checks**: Continuous health monitoring
- **Graceful Degradation**: Reduce quality under load
- **Load Balancing**: Distribute traffic across instances
- **Error Handling**: Comprehensive error handling and logging

### 3. Monitoring and Observability

- **Metrics Collection**: Latency, throughput, accuracy, error rates
- **Distributed Tracing**: Track requests across services
- **Log Aggregation**: Centralized logging and analysis
- **Alerting**: Automated alerts for performance degradation
- **Performance Dashboards**: Real-time monitoring dashboards
- **Anomaly Detection**: Detect unusual patterns automatically

## Common Pitfalls

1. **Synchronous Blocking**: Using synchronous calls in async contexts
2. **Memory Leaks**: Not properly managing model instances and data
3. **Cold Start Issues**: Slow model loading causing latency spikes
4. **Over-Batching**: Waiting too long for batches causing timeouts
5. **Insufficient Monitoring**: Lack of proper observability
6. **Hard-coded Configurations**: Not parameterizing deployment configs
7. **Security Gaps**: Unsecured model endpoints and data access

## Resources

- **references/performance-optimization.md**: Advanced optimization techniques
- **references/deployment-strategies.md**: Production deployment patterns
- **references/monitoring-ml.md**: ML-specific monitoring strategies
- **assets/model-serving-config.yaml**: Kubernetes model serving templates
- **assets/canary-deployment.yaml**: Canary deployment configuration
- **assets/monitoring-dashboard.json**: Grafana monitoring dashboard

## Production Checklist

- [ ] Model serving architecture designed and implemented
- [ ] Batch processing optimized for your use case
- [ ] Real-time inference latency meets requirements
- [ ] A/B testing framework operational
- [ ] Canary deployment process tested
- [ ] Model versioning system in place
- [ ] Performance monitoring and alerting configured
- [ ] Security measures implemented
- [ ] Cost optimization strategies applied
- [ ] Disaster recovery plans tested
- [ ] Load testing completed
- [ ] Documentation and runbooks created
