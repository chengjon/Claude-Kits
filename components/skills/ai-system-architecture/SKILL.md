---
name: ai-system-architecture
description: Design and implement enterprise-grade AI system architectures including model serving, data pipelines, inference services, and ML operations infrastructure. Use when building scalable AI platforms, production ML systems, or architecting AI-powered applications.
---

# AI System Architecture

Master enterprise-grade AI system design for production-ready machine learning platforms, model serving infrastructure, and scalable AI applications.

## When to Use This Skill

- Architecting production ML platforms
- Designing scalable model serving systems
- Building AI infrastructure for high-traffic applications
- Creating multi-model orchestration systems
- Implementing enterprise AI observability
- Designing AI security and governance frameworks
- Planning ML lifecycle management systems
- Creating cost-optimized AI architectures

## Core Architecture Patterns

### 1. Model Serving Architecture

**Microservices Model Serving:**
```python
# Model serving gateway with multiple models
from fastapi import FastAPI, BackgroundTasks
from typing import Dict, Any
import asyncio

app = FastAPI()

class ModelServingCluster:
    def __init__(self):
        self.models = {}
        self.load_balancers = {}
        self.health_checks = {}
    
    async def register_model(self, model_id: str, model_instance):
        self.models[model_id] = model_instance
        self.health_checks[model_id] = {"status": "healthy", "last_check": datetime.now()}

# Gateway API for model serving
model_cluster = ModelServingCluster()

@app.post("/predict/{model_id}")
async def predict(model_id: str, request: Dict[str, Any]):
    if model_id not in model_cluster.models:
        raise HTTPException(404, "Model not found")
    
    try:
        model = model_cluster.models[model_id]
        prediction = await model.predict(request["data"])
        return {"prediction": prediction, "model_id": model_id}
    except Exception as e:
        return {"error": str(e), "model_id": model_id}
```

### 2. Data Pipeline Architecture

**Streaming Data Pipeline:**
```python
# Real-time ML data pipeline with Kafka
from kafka import KafkaProducer, KafkaConsumer
import asyncio
from typing import Generator

class StreamingMLPipeline:
    def __init__(self, kafka_config: Dict):
        self.producer = KafkaProducer(**kafka_config)
        self.consumer = KafkaConsumer(
            'raw-data', 'processed-data', 'predictions',
            bootstrap_servers=kafka_config['bootstrap_servers']
        )
    
    async def process_stream(self) -> Generator[Dict, None, None]:
        for message in self.consumer:
            data = json.loads(message.value)
            # Apply ML processing
            processed_data = await self.transform_data(data)
            # Generate prediction
            prediction = await self.predict(processed_data)
            # Publish results
            self.producer.send('predictions', json.dumps(prediction).encode())
            yield prediction

# Data transformation with feature engineering
async def transform_data(self, raw_data: Dict) -> Dict:
    # Feature extraction
    features = {
        "timestamp": raw_data["timestamp"],
        "user_id": raw_data["user_id"],
        "feature_1": raw_data["value_1"] / 100.0,
        "feature_2": raw_data["value_2"] ** 2,
        "feature_3": hash(raw_data["category"]) % 1000
    }
    return features
```

### 3. Multi-Model Orchestration

**Model Router Pattern:**
```python
# Intelligent model routing based on input characteristics
class ModelRouter:
    def __init__(self):
        self.model_routes = {
            "fast": "lightweight_model_v2",
            "accurate": "heavyweight_model_v3",
            "balanced": "mediumweight_model_v1"
        }
        self.performance_metrics = {}
    
    async def route_request(self, request: Dict) -> str:
        # Analyze request characteristics
        complexity_score = self.calculate_complexity(request)
        latency_requirement = request.get("latency_requirement", "balanced")
        
        # Route to appropriate model
        if latency_requirement == "fast":
            return self.model_routes["fast"]
        elif latency_requirement == "accurate":
            return self.model_routes["accurate"]
        else:
            return self.model_routes["balanced"]
    
    def calculate_complexity(self, request: Dict) -> float:
        # Complexity scoring logic
        features_count = len(request.get("features", []))
        data_size = request.get("data_size", 0)
        return (features_count * 0.7) + (data_size * 0.3)
```

### 4. A/B Testing Framework

**Model Experimentation:**
```python
# A/B testing for model comparisons
class ModelExperimentManager:
    def __init__(self):
        self.experiments = {}
        self.metrics_collector = MetricsCollector()
    
    async def create_experiment(self, experiment_id: str, models: List[str]):
        self.experiments[experiment_id] = {
            "models": models,
            "traffic_split": {"model_a": 0.5, "model_b": 0.5},
            "metrics": ["accuracy", "latency", "throughput"],
            "status": "running"
        }
    
    async def route_to_experiment(self, experiment_id: str, user_id: str) -> str:
        if experiment_id not in self.experiments:
            raise ValueError("Experiment not found")
        
        # Use consistent hashing for stable routing
        hash_value = hash(f"{experiment_id}:{user_id}") % 100
        if hash_value < 50:
            return "model_a"
        else:
            return "model_b"
    
    async def collect_metrics(self, experiment_id: str, model_id: str, metrics: Dict):
        # Collect and aggregate experiment metrics
        await self.metrics_collector.record(
            experiment_id, model_id, metrics
        )
```

## Infrastructure Components

### 1. Container Orchestration

**Kubernetes ML Workloads:**
```yaml
# Kubernetes deployment for ML model serving
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-serving
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model-serving
  template:
    metadata:
      labels:
        app: ml-model-serving
    spec:
      containers:
      - name: model-server
        image: ml/model-serving:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        env:
        - name: MODEL_PATH
          value: "/models/production_model"
        - name: BATCH_SIZE
          value: "32"
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
```

### 2. Auto-Scaling Configuration

**HPA for ML Services:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-model-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-model-serving
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 3. Service Mesh Integration

**Istio for ML Traffic Management:**
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: ml-model-routing
spec:
  hosts:
  - ml-model-service
  http:
  - match:
    - headers:
        latency-priority:
          exact: "high"
    route:
    - destination:
        host: ml-model-service
        subset: fast-model
  - route:
    - destination:
        host: ml-model-service
        subset: standard-model
```

## Data Management Architecture

### 1. Feature Store Design

**Centralized Feature Management:**
```python
# Feature store implementation
from typing import Dict, Any, List, Optional
import pandas as pd
import redis
from datetime import datetime, timedelta

class FeatureStore:
    def __init__(self, redis_config: Dict):
        self.redis_client = redis.Redis(**redis_config)
        self.feature_catalog = {}
    
    async def register_feature(self, feature_name: str, feature_config: Dict):
        self.feature_catalog[feature_name] = feature_config
    
    async def get_feature(self, entity_id: str, feature_names: List[str]) -> Dict:
        # Retrieve features from cache/database
        features = {}
        for feature_name in feature_names:
            cache_key = f"feature:{entity_id}:{feature_name}"
            cached_value = self.redis_client.get(cache_key)
            
            if cached_value:
                features[feature_name] = json.loads(cached_value)
            else:
                # Compute or fetch from database
                feature_value = await self.compute_feature(feature_name, entity_id)
                features[feature_name] = feature_value
                
                # Cache the feature
                await self.cache_feature(entity_id, feature_name, feature_value)
        
        return features
    
    async def compute_offline_features(self, entity_ids: List[str]) -> pd.DataFrame:
        # Batch compute features for training
        feature_data = []
        for entity_id in entity_ids:
            features = await self.get_features_for_training(entity_id)
            features["entity_id"] = entity_id
            feature_data.append(features)
        
        return pd.DataFrame(feature_data)
```

### 2. Data Versioning

**Dataset Version Control:**
```python
# Dataset versioning for ML experiments
class DatasetVersionManager:
    def __init__(self):
        self.versions = {}
        self.lineage = {}
    
    async def create_dataset_version(self, dataset_id: str, data: pd.DataFrame, metadata: Dict):
        version_id = f"{dataset_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store dataset with versioning
        self.versions[version_id] = {
            "dataset_id": dataset_id,
            "created_at": datetime.now(),
            "data_shape": data.shape,
            "schema": list(data.columns),
            "metadata": metadata
        }
        
        # Track lineage
        if dataset_id not in self.lineage:
            self.lineage[dataset_id] = []
        self.lineage[dataset_id].append(version_id)
        
        return version_id
    
    async def get_dataset(self, version_id: str) -> Optional[pd.DataFrame]:
        # Retrieve specific dataset version
        if version_id not in self.versions:
            return None
        
        # Load data from storage
        version_info = self.versions[version_id]
        return await self.load_data_from_storage(version_id, version_info)
```

## Monitoring and Observability

### 1. ML-Specific Metrics

**Model Performance Monitoring:**
```python
# ML model monitoring and drift detection
import numpy as np
from typing import List, Dict, Any

class MLModelMonitor:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.performance_history = []
        self.drift_detectors = {}
    
    async def log_prediction(self, features: Dict, prediction: Any, actual: Any = None):
        # Log prediction with features and optionally actual value
        log_entry = {
            "timestamp": datetime.now(),
            "features": features,
            "prediction": prediction,
            "actual": actual,
            "model_id": self.model_id
        }
        
        # Store in monitoring system
        await self.store_monitoring_log(log_entry)
        
        # Update performance metrics if actual is available
        if actual is not None:
            await self.update_performance_metrics(prediction, actual)
    
    async def detect_data_drift(self, new_features: Dict):
        # Implement drift detection algorithms
        drift_score = 0.0
        
        for feature_name, feature_value in new_features.items():
            if feature_name in self.drift_detectors:
                # Use statistical drift detection
                historical_mean = self.drift_detectors[feature_name]["mean"]
                historical_std = self.drift_detectors[feature_name]["std"]
                
                # Z-score based drift detection
                z_score = abs(feature_value - historical_mean) / historical_std
                drift_score += z_score
        
        return drift_score / len(new_features) if new_features else 0.0
    
    async def update_performance_metrics(self, prediction: Any, actual: Any):
        # Calculate and update performance metrics
        accuracy = self.calculate_accuracy(prediction, actual)
        
        self.performance_history.append({
            "timestamp": datetime.now(),
            "accuracy": accuracy
        })
        
        # Alert if performance drops
        if len(self.performance_history) > 10:
            recent_accuracy = np.mean([h["accuracy"] for h in self.performance_history[-10:]])
            if recent_accuracy < 0.8:  # Threshold for alerting
                await self.send_performance_alert(recent_accuracy)
```

## Security and Compliance

### 1. Model Security

**Inference Security Framework:**
```python
# Secure model inference with input validation
from marshmallow import Schema, fields, ValidationError
import jwt

class InferenceRequest:
    def __init__(self, model_auth_token: str):
        self.auth_token = model_auth_token
    
    async def validate_request(self, request_data: Dict) -> bool:
        # Validate authentication
        if not self.validate_auth_token():
            return False
        
        # Validate input data schema
        schema = InferenceRequestSchema()
        try:
            schema.load(request_data)
            return True
        except ValidationError:
            return False
    
    def validate_auth_token(self) -> bool:
        try:
            payload = jwt.decode(self.auth_token, "secret_key", algorithms=["HS256"])
            return payload.get("model_access") == self.model_id
        except jwt.InvalidTokenError:
            return False

class SecureInferenceEngine:
    def __init__(self, model: Any, security_config: Dict):
        self.model = model
        self.security_config = security_config
        self.rate_limiter = RateLimiter()
        self.anomaly_detector = AnomalyDetector()
    
    async def secure_predict(self, request_data: Dict, auth_context: Dict) -> Dict:
        # Check rate limits
        if not await self.rate_limiter.check_limit(auth_context["user_id"]):
            raise RateLimitExceeded("Too many requests")
        
        # Detect anomalous requests
        anomaly_score = await self.anomaly_detector.detect(request_data)
        if anomaly_score > self.security_config["anomaly_threshold"]:
            await self.log_security_event("anomalous_request", request_data)
        
        # Validate and process
        await self.validate_inputs(request_data)
        prediction = await self.model.predict(request_data)
        
        # Log secure inference
        await self.log_inference(request_data, prediction, auth_context)
        
        return {"prediction": prediction, "confidence": 0.95}
```

## Cost Optimization

### 1. Resource Optimization

**Dynamic Resource Allocation:**
```python
# Cost-optimized resource allocation for ML workloads
class MLResourceOptimizer:
    def __init__(self, cost_budget: float):
        self.cost_budget = cost_budget
        self.resource_usage = {}
        self.cost_tracking = CostTracker()
    
    async def optimize_deployment(self, model_config: Dict) -> Dict:
        # Analyze workload patterns
        traffic_pattern = await self.analyze_traffic_patterns(model_config["model_id"])
        
        # Calculate optimal resources
        cpu_cores = self.calculate_cpu_requirement(traffic_pattern)
        memory_gb = self.calculate_memory_requirement(traffic_pattern)
        
        # Cost-aware scaling
        cost_per_hour = (cpu_cores * 0.05) + (memory_gb * 0.01)  # AWS pricing example
        
        if cost_per_hour > self.cost_budget:
            # Reduce resources with graceful degradation
            cpu_cores = min(cpu_cores, self.cost_budget / 0.05)
        
        return {
            "cpu_cores": cpu_cores,
            "memory_gb": memory_gb,
            "estimated_cost_per_hour": cost_per_hour,
            "scaling_recommendations": self.generate_scaling_advice(traffic_pattern)
        }
    
    def calculate_cpu_requirement(self, traffic_pattern: Dict) -> float:
        # CPU calculation based on inference complexity and QPS
        base_cpu = 0.5
        complexity_factor = traffic_pattern.get("avg_complexity", 1.0)
        qps = traffic_pattern.get("qps", 10)
        
        return base_cpu * complexity_factor * (qps / 10)
```

## Implementation Examples

### 1. Complete ML Platform Architecture

```python
# Enterprise ML platform implementation
class EnterpriseMLPlatform:
    def __init__(self, config: Dict):
        self.config = config
        self.model_registry = ModelRegistry()
        self.feature_store = FeatureStore(config["redis"])
        self.monitoring = MLModelMonitor()
        self.security = SecurityManager()
    
    async def deploy_model(self, model_id: str, model_binary: bytes, metadata: Dict):
        # Model lifecycle management
        model_version = await self.model_registry.register_model(model_id, model_binary, metadata)
        
        # Deploy to serving infrastructure
        deployment_info = await self.deploy_to_serving(model_id, model_version)
        
        # Configure monitoring
        await self.monitoring.setup_model_monitoring(model_id)
        
        # Setup alerting
        await self.setup_alerting(model_id, deployment_info)
        
        return deployment_info
    
    async def serve_inference(self, model_id: str, request: Dict, auth_context: Dict):
        # Security validation
        await self.security.validate_request(request, auth_context)
        
        # Feature retrieval
        features = await self.feature_store.get_features(
            request["entity_id"], 
            request["feature_names"]
        )
        
        # Model routing and inference
        model_version = await self.model_registry.get_current_version(model_id)
        prediction = await model_version.predict(features)
        
        # Monitoring and logging
        await self.monitoring.log_prediction(features, prediction)
        
        return {"prediction": prediction, "model_version": model_version.version_id}
```

## Best Practices

### 1. Architecture Design Principles

- **Modularity**: Design loosely coupled ML services
- **Scalability**: Plan for horizontal and vertical scaling
- **Reliability**: Implement fault tolerance and graceful degradation
- **Security**: Secure model serving and data access
- **Observability**: Comprehensive monitoring and alerting
- **Cost Optimization**: Resource efficiency and budget management
- **Compliance**: Data governance and regulatory compliance

### 2. Deployment Patterns

- **Blue-Green Deployments**: Zero-downtime model updates
- **Canary Releases**: Gradual rollout with performance monitoring
- **A/B Testing**: Model comparison and optimization
- **Feature Flags**: Dynamic model routing and experimentation
- **Rollback Strategies**: Quick recovery from model failures

### 3. Performance Optimization

- **Model Optimization**: Quantization, pruning, and distillation
- **Caching Strategies**: Feature caching and prediction caching
- **Batch Processing**: Efficient batch inference
- **Edge Deployment**: Reduce latency with edge computing
- **Resource Tuning**: CPU/memory optimization

## Common Pitfalls

1. **Over-engineering**: Don't overcomplicate for simple use cases
2. **Poor Monitoring**: Lack of ML-specific observability
3. **Security Blind Spots**: Unsecured model endpoints and data access
4. **Cost Spikes**: Unoptimized resource allocation
5. **Data Drift**: Inadequate monitoring for model degradation
6. **Vendor Lock-in**: Over-dependence on specific cloud providers
7. **Insufficient Testing**: Lack of comprehensive model testing

## Resources

- **references/mlops-platforms.md**: MLOps platform comparisons
- **references/model-serving.md**: Model serving architectures
- **references/data-pipelines.md**: ML data pipeline design
- **references/security-ml.md**: ML security best practices
- **assets/ml-platform-template.yaml**: Kubernetes ML platform template
- **assets/monitoring-config.yaml**: ML monitoring configuration examples
- **assets/security-policies.yaml**: ML security policy templates

## Production Checklist

- [ ] Model serving architecture designed
- [ ] Data pipeline infrastructure implemented
- [ ] Monitoring and alerting configured
- [ ] Security controls implemented
- [ ] Performance optimization applied
- [ ] Cost monitoring and optimization
- [ ] Disaster recovery plans in place
- [ ] Compliance requirements met
- [ ] Documentation and runbooks created
- [ ] Team training and knowledge transfer completed
