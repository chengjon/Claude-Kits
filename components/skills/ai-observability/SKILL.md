---
name: ai-observability
description: Master comprehensive AI observability including model performance monitoring, data drift detection, bias auditing, explainability tracking, and ML-specific alerting systems. Use when building production ML monitoring, ensuring AI system reliability, or implementing responsible AI practices.
---

# AI Observability

Master comprehensive observability for AI and ML systems including model performance monitoring, data drift detection, bias auditing, explainability tracking, and ML-specific alerting.

## When to Use This Skill

- Setting up production ML monitoring and observability
- Implementing data drift and concept drift detection
- Building bias auditing and fairness monitoring systems
- Creating explainability and interpretability tracking
- Developing ML-specific alerting and notification systems
- Monitoring model degradation and performance issues
- Ensuring responsible AI practices in production
- Building comprehensive AI system health dashboards

## Core Observability Patterns

### 1. Model Performance Monitoring

**Multi-Dimensional Performance Tracking:**
```python
# Comprehensive ML model performance monitoring
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import asyncio

@dataclass
class PerformanceMetrics:
    """Multi-dimensional performance metrics for ML models"""
    model_id: str
    version: str
    timestamp: float
    latency_ms: float
    throughput_rps: float
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "version": self.version,
            "timestamp": self.timestamp,
            "latency_ms": self.latency_ms,
            "throughput_rps": self.throughput_rps,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "auc_roc": self.auc_roc,
            **self.custom_metrics
        }

class ModelPerformanceMonitor:
    def __init__(self, model_id: str, retention_period_hours: int = 168):
        self.model_id = model_id
        self.retention_period = retention_period_hours * 3600  # Convert to seconds
        self.metrics_buffer = deque(maxlen=10000)  # Store last 10k metrics
        self.alert_thresholds = {}
        self.notification_service = NotificationService()
        
        # Performance baselines
        self.baselines = {
            "latency_p95": None,
            "accuracy": None,
            "throughput": None,
            "error_rate": 0.01  # 1% default error rate threshold
        }
    
    async def record_inference(self, prediction: Any, actual: Any = None,
                             features: Dict = None, metadata: Dict = None) -> PerformanceMetrics:
        """Record inference with comprehensive metrics"""
        
        # Calculate performance metrics
        metrics = await self._calculate_performance_metrics(prediction, actual)
        metrics.model_id = self.model_id
        metrics.timestamp = time.time()
        
        # Add custom metrics from metadata
        if metadata:
            metrics.custom_metrics.update(metadata)
        
        # Store metrics
        self.metrics_buffer.append(metrics)
        
        # Check for alerts
        await self._check_performance_alerts(metrics)
        
        # Update baselines periodically
        await self._update_baselines()
        
        return metrics
    
    async def _calculate_performance_metrics(self, prediction: Any, actual: Any) -> PerformanceMetrics:
        """Calculate performance metrics based on prediction type"""
        current_time = time.time()
        
        # Initialize with basic metrics
        metrics = PerformanceMetrics(
            model_id="",
            version="",
            timestamp=current_time,
            latency_ms=0.0,  # Would be calculated by caller
            throughput_rps=0.0  # Would be calculated by caller
        )
        
        # Calculate classification metrics if actual values available
        if actual is not None and prediction is not None:
            try:
                if isinstance(prediction, (int, float, bool)):
                    # Binary classification
                    metrics.accuracy = 1.0 if prediction == actual else 0.0
                    
                elif isinstance(prediction, (list, np.ndarray)) and len(prediction) > 0:
                    # Multi-class or probabilistic predictions
                    if isinstance(actual, (int, float)) and isinstance(prediction[0], float):
                        # Probabilistic predictions - use threshold
                        predicted_class = 1 if prediction[1] > 0.5 else 0
                        metrics.accuracy = 1.0 if predicted_class == actual else 0.0
                    
                    elif len(prediction) == len(actual):
                        # Multi-class predictions
                        metrics.accuracy = np.mean([p == a for p, a in zip(prediction, actual)])
                
                # Add more sophisticated metrics calculation here
                metrics.f1_score = await self._calculate_f1_score(prediction, actual)
                
            except Exception as e:
                print(f"Error calculating performance metrics: {e}")
        
        return metrics
    
    async def _calculate_f1_score(self, prediction: Any, actual: Any) -> float:
        """Calculate F1 score for binary classification"""
        try:
            # Simple F1 calculation for binary classification
            if isinstance(prediction, (int, float, bool)) and isinstance(actual, (int, float, bool)):
                tp = (prediction == 1 and actual == 1)
                fp = (prediction == 1 and actual == 0)
                fn = (prediction == 0 and actual == 1)
                
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                
                return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        except:
            pass
        return 0.0
    
    async def _check_performance_alerts(self, metrics: PerformanceMetrics):
        """Check metrics against thresholds and trigger alerts"""
        
        # Latency alerts
        if self.baselines["latency_p95"] and metrics.latency_ms > self.baselines["latency_p95"] * 1.5:
            await self._trigger_alert(
                "HIGH_LATENCY",
                f"Model latency {metrics.latency_ms}ms exceeds threshold {self.baselines['latency_p95'] * 1.5}ms",
                severity="warning",
                metrics=metrics.to_dict()
            )
        
        # Accuracy alerts
        if metrics.accuracy is not None and self.baselines["accuracy"]:
            accuracy_drop = (self.baselines["accuracy"] - metrics.accuracy) / self.baselines["accuracy"]
            if accuracy_drop > 0.05:  # 5% accuracy drop
                await self._trigger_alert(
                    "ACCURACY_DROP",
                    f"Model accuracy dropped by {accuracy_drop:.1%} from baseline {self.baselines['accuracy']:.3f}",
                    severity="critical",
                    metrics=metrics.to_dict()
                )
        
        # Error rate alerts (implement error tracking)
        # ...
    
    async def _update_baselines(self):
        """Update performance baselines periodically"""
        if len(self.metrics_buffer) < 100:  # Need minimum samples
            return
        
        # Calculate new baselines from recent data
        recent_metrics = list(self.metrics_buffer)[-1000:]  # Last 1000 samples
        
        # Latency P95
        latencies = [m.latency_ms for m in recent_metrics if m.latency_ms > 0]
        if latencies:
            self.baselines["latency_p95"] = np.percentile(latencies, 95)
        
        # Accuracy
        accuracies = [m.accuracy for m in recent_metrics if m.accuracy is not None]
        if accuracies:
            self.baselines["accuracy"] = np.mean(accuracies)
    
    async def _trigger_alert(self, alert_type: str, message: str, 
                           severity: str = "warning", metrics: Dict = None):
        """Trigger alert notification"""
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "model_id": self.model_id,
            "timestamp": time.time(),
            "metrics": metrics or {}
        }
        
        # Send notifications
        await self.notification_service.send_alert(alert)
        
        # Store alert for analysis
        await self._store_alert(alert)
    
    async def get_performance_summary(self, time_window_hours: int = 1) -> Dict[str, Any]:
        """Get performance summary for specified time window"""
        cutoff_time = time.time() - (time_window_hours * 3600)
        
        # Filter metrics by time window
        window_metrics = [m for m in self.metrics_buffer if m.timestamp >= cutoff_time]
        
        if not window_metrics:
            return {"error": "No metrics available for time window"}
        
        # Calculate summary statistics
        summary = {
            "model_id": self.model_id,
            "time_window_hours": time_window_hours,
            "sample_count": len(window_metrics),
            "avg_latency_ms": np.mean([m.latency_ms for m in window_metrics]),
            "p95_latency_ms": np.percentile([m.latency_ms for m in window_metrics], 95),
            "avg_throughput_rps": np.mean([m.throughput_rps for m in window_metrics]),
        }
        
        # Add accuracy metrics if available
        accuracies = [m.accuracy for m in window_metrics if m.accuracy is not None]
        if accuracies:
            summary["avg_accuracy"] = np.mean(accuracies)
            summary["min_accuracy"] = np.min(accuracies)
        
        return summary

class NotificationService:
    """Multi-channel notification service for alerts"""
    
    def __init__(self):
        self.channels = {
            "email": EmailNotifier(),
            "slack": SlackNotifier(),
            "pagerduty": PagerDutyNotifier()
        }
    
    async def send_alert(self, alert: Dict[str, Any]):
        """Send alert through configured channels"""
        # Determine notification channels based on severity
        channels = ["slack"]  # Default channel
        
        if alert["severity"] == "critical":
            channels.extend(["email", "pagerduty"])
        
        # Send through each channel
        for channel_name in channels:
            if channel_name in self.channels:
                try:
                    await self.channels[channel_name].send(alert)
                except Exception as e:
                    print(f"Failed to send alert via {channel_name}: {e}")
```

### 2. Data Drift Detection

**Statistical Drift Detection:**
```python
# Advanced data drift detection with multiple statistical tests
import scipy.stats as stats
from typing import Dict, List, Any, Tuple
import numpy as np
from sklearn.metrics import mutual_info_score
from collections import defaultdict

class DataDriftDetector:
    """Multi-method data drift detection system"""
    
    def __init__(self, reference_data: np.ndarray, significance_level: float = 0.05):
        self.reference_data = reference_data
        self.significance_level = significance_level
        self.reference_stats = self._compute_reference_statistics()
        self.drift_history = []
        
    def _compute_reference_statistics(self) -> Dict[str, Any]:
        """Compute comprehensive reference statistics"""
        stats_dict = {
            "mean": np.mean(self.reference_data, axis=0),
            "std": np.std(self.reference_data, axis=0),
            "min": np.min(self.reference_data, axis=0),
            "max": np.max(self.reference_data, axis=0),
            "quantiles": np.percentile(self.reference_data, [25, 50, 75], axis=0)
        }
        
        # Compute correlation matrix for multivariate data
        if len(self.reference_data.shape) > 1:
            stats_dict["correlation_matrix"] = np.corrcoef(self.reference_data.T)
        
        return stats_dict
    
    async def detect_drift(self, new_data: np.ndarray) -> Dict[str, Any]:
        """Comprehensive drift detection using multiple methods"""
        
        drift_results = {
            "timestamp": time.time(),
            "sample_size": len(new_data),
            "drift_detected": False,
            "drift_score": 0.0,
            "tests": {}
        }
        
        # 1. Kolmogorov-Smirnov test for distribution drift
        ks_results = await self._ks_test(new_data)
        drift_results["tests"]["kolmogorov_smirnov"] = ks_results
        
        # 2. Population Stability Index (PSI) for categorical features
        psi_results = await self._psi_test(new_data)
        drift_results["tests"]["population_stability_index"] = psi_results
        
        # 3. Jensen-Shannon divergence for probability distributions
        js_results = await self._js_divergence_test(new_data)
        drift_results["tests"]["jensen_shannon_divergence"] = js_results
        
        # 4. Statistical tests for mean and variance changes
        mean_var_results = await self._mean_variance_test(new_data)
        drift_results["tests"]["mean_variance"] = mean_var_results
        
        # Calculate overall drift score
        drift_results["drift_score"] = self._calculate_overall_drift_score(drift_results["tests"])
        drift_results["drift_detected"] = drift_results["drift_score"] > 0.1  # Threshold
        
        # Store drift history
        self.drift_history.append(drift_results)
        
        return drift_results
    
    async def _ks_test(self, new_data: np.ndarray) -> Dict[str, Any]:
        """Kolmogorov-Smirnov test for distribution drift"""
        if len(self.reference_data.shape) > 1:
            # For multivariate data, test each feature separately
            ks_scores = []
            p_values = []
            
            for feature_idx in range(self.reference_data.shape[1]):
                ks_stat, p_value = stats.ks_2samp(
                    self.reference_data[:, feature_idx], 
                    new_data[:, feature_idx]
                )
                ks_scores.append(ks_stat)
                p_values.append(p_value)
            
            # Use maximum statistic across features
            max_ks_stat = max(ks_scores)
            min_p_value = min(p_values)
        else:
            # Univariate data
            max_ks_stat, min_p_value = stats.ks_2samp(
                self.reference_data.flatten(), 
                new_data.flatten()
            )
        
        return {
            "statistic": max_ks_stat,
            "p_value": min_p_value,
            "drift_detected": min_p_value < self.significance_level,
            "interpretation": "Distribution shift detected" if min_p_value < self.significance_level else "No significant distribution shift"
        }
    
    async def _psi_test(self, new_data: np.ndarray) -> Dict[str, Any]:
        """Population Stability Index test for categorical data"""
        # Convert continuous data to categorical bins for PSI calculation
        n_bins = min(10, int(np.sqrt(len(self.reference_data))))  # Use square root rule
        
        ref_hist, bin_edges = np.histogram(self.reference_data.flatten(), bins=n_bins)
        new_hist, _ = np.histogram(new_data.flatten(), bins=bin_edges)
        
        # Calculate PSI
        ref_probs = ref_hist / np.sum(ref_hist)
        new_probs = new_hist / np.sum(new_hist)
        
        # Add small constant to avoid division by zero
        ref_probs = ref_probs + 1e-8
        new_probs = new_probs + 1e-8
        
        psi = np.sum((new_probs - ref_probs) * np.log(new_probs / ref_probs))
        
        # PSI interpretation
        interpretation = "No drift"
        if psi > 0.2:
            interpretation = "Significant drift"
        elif psi > 0.1:
            interpretation = "Moderate drift"
        
        return {
            "psi_value": psi,
            "drift_detected": psi > 0.1,
            "interpretation": interpretation,
            "bin_count": n_bins
        }
    
    async def _js_divergence_test(self, new_data: np.ndarray) -> Dict[str, Any]:
        """Jensen-Shannon divergence for probability distributions"""
        # Convert to probability distributions
        ref_hist, _ = np.histogram(self.reference_data.flatten(), bins=50, density=True)
        new_hist, _ = np.histogram(new_data.flatten(), bins=50, density=True)
        
        # Normalize to probabilities
        ref_probs = ref_hist / np.sum(ref_hist)
        new_probs = new_hist / np.sum(new_hist)
        
        # Add smoothing
        ref_probs = ref_probs + 1e-8
        new_probs = new_probs + 1e-8
        
        # Calculate JS divergence
        m = 0.5 * (ref_probs + new_probs)
        js_div = 0.5 * (stats.entropy(ref_probs, m) + stats.entropy(new_probs, m))
        
        return {
            "js_divergence": js_div,
            "drift_detected": js_div > 0.1,
            "interpretation": "High divergence detected" if js_div > 0.1 else "Low divergence"
        }
    
    async def _mean_variance_test(self, new_data: np.ndarray) -> Dict[str, Any]:
        """Test for changes in mean and variance"""
        ref_mean = np.mean(self.reference_data, axis=0)
        ref_var = np.var(self.reference_data, axis=0)
        
        new_mean = np.mean(new_data, axis=0)
        new_var = np.var(new_data, axis=0)
        
        # T-test for mean differences (if reference data is available)
        mean_changes = []
        var_ratios = []
        
        if len(self.reference_data.shape) > 1:
            for feature_idx in range(self.reference_data.shape[1]):
                # T-test for means
                t_stat, p_value = stats.ttest_ind(
                    self.reference_data[:, feature_idx],
                    new_data[:, feature_idx]
                )
                mean_changes.append(p_value)
                
                # F-test for variances
                f_stat = ref_var[feature_idx] / new_var[feature_idx]
                var_ratios.append(f_stat)
        else:
            # Univariate case
            t_stat, p_value = stats.ttest_ind(
                self.reference_data.flatten(),
                new_data.flatten()
            )
            mean_changes.append(p_value)
        
        return {
            "mean_p_values": mean_changes,
            "variance_ratios": var_ratios,
            "significant_mean_drift": any(p < self.significance_level for p in mean_changes),
            "interpretation": "Mean/variance changes detected" if any(p < self.significance_level for p in mean_changes) else "No significant mean/variance changes"
        }
    
    def _calculate_overall_drift_score(self, tests: Dict[str, Any]) -> float:
        """Calculate weighted overall drift score"""
        weights = {
            "kolmogorov_smirnov": 0.3,
            "population_stability_index": 0.25,
            "jensen_shannon_divergence": 0.25,
            "mean_variance": 0.2
        }
        
        drift_score = 0.0
        
        # KS test contribution
        ks_stat = tests["kolmogorov_smirnov"]["statistic"]
        drift_score += weights["kolmogorov_smirnov"] * ks_stat
        
        # PSI contribution
        psi_value = tests["population_stability_index"]["psi_value"]
        drift_score += weights["population_stability_index"] * psi_value
        
        # JS divergence contribution
        js_div = tests["jensen_shannon_divergence"]["js_divergence"]
        drift_score += weights["jensen_shannon_divergence"] * js_div
        
        # Mean/variance contribution
        mean_drift = 1.0 if tests["mean_variance"]["significant_mean_drift"] else 0.0
        drift_score += weights["mean_variance"] * mean_drift
        
        return drift_score
    
    async def get_drift_trend(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analyze drift trends over time"""
        cutoff_time = time.time() - (time_window_hours * 3600)
        
        recent_drifts = [
            drift for drift in self.drift_history 
            if drift["timestamp"] >= cutoff_time
        ]
        
        if not recent_drifts:
            return {"error": "No drift data available for time window"}
        
        # Calculate trend statistics
        drift_scores = [d["drift_score"] for d in recent_drifts]
        
        trend_analysis = {
            "time_window_hours": time_window_hours,
            "total_measurements": len(recent_drifts),
            "avg_drift_score": np.mean(drift_scores),
            "max_drift_score": np.max(drift_scores),
            "drift_detected_count": sum(1 for d in recent_drifts if d["drift_detected"]),
            "drift_frequency": len(recent_drifts) / time_window_hours,
            "trend_direction": "increasing" if drift_scores[-1] > drift_scores[0] else "decreasing",
            "recommendations": await self._generate_drift_recommendations(recent_drifts)
        }
        
        return trend_analysis
    
    async def _generate_drift_recommendations(self, drift_history: List[Dict]) -> List[str]:
        """Generate recommendations based on drift patterns"""
        recommendations = []
        
        # High frequency drift
        drift_frequency = len(drift_history)
        if drift_frequency > 10:  # More than 10 drift detections
            recommendations.append("High drift frequency detected. Consider updating model retraining schedule.")
        
        # Increasing drift trend
        if len(drift_history) >= 2:
            recent_scores = [d["drift_score"] for d in drift_history[-5:]]
            if recent_scores[-1] > recent_scores[0]:
                recommendations.append("Drift trend is increasing. Monitor closely and prepare for model retraining.")
        
        # Severe drift
        max_drift = max(d["drift_score"] for d in drift_history)
        if max_drift > 0.5:
            recommendations.append("Severe data drift detected. Immediate model retraining recommended.")
        
        return recommendations

# Usage example
async def drift_detection_example():
    # Reference data (training data)
    reference_data = np.random.normal(0, 1, (1000, 5))
    
    # Current data (might have drift)
    current_data = np.random.normal(0.1, 1.2, (500, 5))  # Slight mean and variance shift
    
    detector = DataDriftDetector(reference_data)
    drift_result = await detector.detect_drift(current_data)
    
    print(f"Drift detected: {drift_result['drift_detected']}")
    print(f"Drift score: {drift_result['drift_score']:.3f}")
    
    # Get drift trend analysis
    trend = await detector.get_drift_trend(time_window_hours=24)
    print(f"Recommendations: {trend['recommendations']}")
```

### 3. Bias and Fairness Monitoring

**Comprehensive Bias Detection:**
```python
# AI bias and fairness monitoring system
from typing import Dict, List, Any, Tuple
import pandas as pd
from collections import defaultdict
import math

class BiasMonitor:
    """Comprehensive bias and fairness monitoring for AI models"""
    
    def __init__(self, protected_attributes: List[str]):
        self.protected_attributes = protected_attributes
        self.bias_metrics_history = []
        self.fairness_thresholds = {
            "demographic_parity": 0.1,  # Max 10% difference between groups
            "equalized_odds": 0.1,
            "equalized_opportunity": 0.1,
            "calibration": 0.05  # 5% calibration difference threshold
        }
    
    async def assess_bias(self, predictions: np.ndarray, 
                         actuals: np.ndarray, 
                         protected_attrs: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Comprehensive bias assessment across multiple fairness metrics"""
        
        bias_assessment = {
            "timestamp": time.time(),
            "sample_size": len(predictions),
            "protected_attributes": list(protected_attrs.keys()),
            "metrics": {},
            "overall_bias_score": 0.0,
            "bias_detected": False,
            "recommendations": []
        }
        
        # Calculate various fairness metrics
        bias_assessment["metrics"]["demographic_parity"] = await self._demographic_parity(
            predictions, protected_attrs
        )
        
        bias_assessment["metrics"]["equalized_odds"] = await self._equalized_odds(
            predictions, actuals, protected_attrs
        )
        
        bias_assessment["metrics"]["equalized_opportunity"] = await self._equalized_opportunity(
            predictions, actuals, protected_attrs
        )
        
        bias_assessment["metrics"]["calibration"] = await self._calibration_fairness(
            predictions, actuals, protected_attrs
        )
        
        # Calculate overall bias score
        bias_assessment["overall_bias_score"] = self._calculate_overall_bias_score(
            bias_assessment["metrics"]
        )
        
        bias_assessment["bias_detected"] = bias_assessment["overall_bias_score"] > 0.1
        
        # Generate recommendations
        bias_assessment["recommendations"] = await self._generate_bias_recommendations(
            bias_assessment["metrics"]
        )
        
        # Store assessment
        self.bias_metrics_history.append(bias_assessment)
        
        return bias_assessment
    
    async def _demographic_parity(self, predictions: np.ndarray, 
                                 protected_attrs: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Demographic parity: equal positive prediction rates across groups"""
        
        metric_results = {}
        
        for attr_name, attr_values in protected_attrs.items():
            if attr_name not in np.unique(attr_values):
                continue
            
            groups = np.unique(attr_values)
            positive_rates = {}
            
            for group in groups:
                group_mask = (attr_values == group)
                group_predictions = predictions[group_mask]
                positive_rate = np.mean(group_predictions)
                positive_rates[group] = positive_rate
            
            # Calculate demographic parity difference
            rates = list(positive_rates.values())
            max_difference = max(rates) - min(rates)
            
            # Statistical significance test
            group_sizes = {group: np.sum(attr_values == group) for group in groups}
            
            metric_results[attr_name] = {
                "positive_rates": positive_rates,
                "group_sizes": group_sizes,
                "max_difference": max_difference,
                "fairness_violated": max_difference > self.fairness_thresholds["demographic_parity"],
                "interpretation": self._interpret_demographic_parity(max_difference)
            }
        
        return metric_results
    
    async def _equalized_odds(self, predictions: np.ndarray, actuals: np.ndarray,
                            protected_attrs: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Equalized odds: equal true positive and false positive rates across groups"""
        
        metric_results = {}
        
        for attr_name, attr_values in protected_attrs.items():
            if attr_name not in np.unique(attr_values):
                continue
            
            groups = np.unique(attr_values)
            group_metrics = {}
            
            for group in groups:
                group_mask = (attr_values == group)
                group_predictions = predictions[group_mask]
                group_actuals = actuals[group_mask]
                
                # Calculate confusion matrix metrics
                tp = np.sum((group_predictions == 1) & (group_actuals == 1))
                fp = np.sum((group_predictions == 1) & (group_actuals == 0))
                tn = np.sum((group_predictions == 0) & (group_actuals == 0))
                fn = np.sum((group_predictions == 0) & (group_actuals == 1))
                
                # Calculate rates
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0  # True Positive Rate
                fpr = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Positive Rate
                
                group_metrics[group] = {
                    "tpr": tpr,
                    "fpr": fpr,
                    "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn}
                }
            
            # Check equalized odds violation
            tpr_values = [metrics["tpr"] for metrics in group_metrics.values()]
            fpr_values = [metrics["fpr"] for metrics in group_metrics.values()]
            
            tpr_difference = max(tpr_values) - min(tpr_values)
            fpr_difference = max(fpr_values) - min(fpr_values)
            
            metric_results[attr_name] = {
                "group_metrics": group_metrics,
                "tpr_difference": tpr_difference,
                "fpr_difference": fpr_difference,
                "fairness_violated": max(tpr_difference, fpr_difference) > self.fairness_thresholds["equalized_odds"],
                "interpretation": self._interpret_equalized_odds(tpr_difference, fpr_difference)
            }
        
        return metric_results
    
    async def _equalized_opportunity(self, predictions: np.ndarray, actuals: np.ndarray,
                                   protected_attrs: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Equalized opportunity: equal true positive rates across groups"""
        
        metric_results = {}
        
        for attr_name, attr_values in protected_attrs.items():
            if attr_name not in np.unique(attr_values):
                continue
            
            groups = np.unique(attr_values)
            tpr_values = {}
            
            for group in groups:
                group_mask = (attr_values == group)
                group_predictions = predictions[group_mask]
                group_actuals = actuals[group_mask]
                
                # Calculate True Positive Rate for positive instances
                positive_actuals = group_actuals == 1
                if np.sum(positive_actuals) > 0:
                    tpr = np.mean(group_predictions[positive_actuals])
                else:
                    tpr = 0
                
                tpr_values[group] = tpr
            
            # Calculate difference
            tpr_differences = list(tpr_values.values())
            max_tpr_difference = max(tpr_differences) - min(tpr_differences)
            
            metric_results[attr_name] = {
                "tpr_by_group": tpr_values,
                "max_difference": max_tpr_difference,
                "fairness_violated": max_tpr_difference > self.fairness_thresholds["equalized_opportunity"],
                "interpretation": self._interpret_equalized_opportunity(max_tpr_difference)
            }
        
        return metric_results
    
    async def _calibration_fairness(self, predictions: np.ndarray, actuals: np.ndarray,
                                  protected_attrs: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Calibration fairness: predictions have same meaning across groups"""
        
        metric_results = {}
        
        for attr_name, attr_values in protected_attrs.items():
            if attr_name not in np.unique(attr_values):
                continue
            
            groups = np.unique(attr_values)
            calibration_metrics = {}
            
            for group in groups:
                group_mask = (attr_values == group)
                group_predictions = predictions[group_mask]
                group_actuals = actuals[group_mask]
                
                # Calculate calibration by prediction score bins
                score_bins = np.linspace(0, 1, 11)  # 10 bins
                bin_calibrations = []
                
                for i in range(len(score_bins) - 1):
                    bin_mask = (
                        (group_predictions >= score_bins[i]) & 
                        (group_predictions < score_bins[i + 1])
                    )
                    
                    if np.sum(bin_mask) > 0:
                        bin_actual_rate = np.mean(group_actuals[bin_mask])
                        bin_predicted_rate = np.mean(group_predictions[bin_mask])
                        bin_calibrations.append(abs(bin_actual_rate - bin_predicted_rate))
                
                avg_calibration_error = np.mean(bin_calibrations) if bin_calibrations else 0
                calibration_metrics[group] = {
                    "average_calibration_error": avg_calibration_error,
                    "bin_count": len(bin_calibrations)
                }
            
            # Compare calibration across groups
            calibration_errors = [m["average_calibration_error"] for m in calibration_metrics.values()]
            max_calibration_difference = max(calibration_errors) - min(calibration_errors)
            
            metric_results[attr_name] = {
                "calibration_metrics": calibration_metrics,
                "max_calibration_difference": max_calibration_difference,
                "fairness_violated": max_calibration_difference > self.fairness_thresholds["calibration"],
                "interpretation": self._interpret_calibration_fairness(max_calibration_difference)
            }
        
        return metric_results
    
    def _calculate_overall_bias_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall bias score from all metrics"""
        bias_components = []
        
        # Demographic parity contribution
        for attr_name, metric in metrics["demographic_parity"].items():
            if metric["fairness_violated"]:
                bias_components.append(metric["max_difference"])
        
        # Equalized odds contribution
        for attr_name, metric in metrics["equalized_odds"].items():
            if metric["fairness_violated"]:
                max_diff = max(metric["tpr_difference"], metric["fpr_difference"])
                bias_components.append(max_diff)
        
        # Equalized opportunity contribution
        for attr_name, metric in metrics["equalized_opportunity"].items():
            if metric["fairness_violated"]:
                bias_components.append(metric["max_difference"])
        
        # Average bias score
        return np.mean(bias_components) if bias_components else 0.0
    
    async def _generate_bias_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on bias assessment"""
        recommendations = []
        
        # Demographic parity recommendations
        for attr_name, metric in metrics["demographic_parity"].items():
            if metric["fairness_violated"]:
                recommendations.append(
                    f"Demographic parity violation for {attr_name}: "
                    f"Consider rebalancing training data or applying fairness constraints"
                )
        
        # Equalized odds recommendations
        for attr_name, metric in metrics["equalized_odds"].items():
            if metric["fairness_violated"]:
                recommendations.append(
                    f"Equalized odds violation for {attr_name}: "
                    f"Focus on reducing differences in TPR and FPR across groups"
                )
        
        # Overall recommendations
        if len(recommendations) > 2:
            recommendations.append(
                "Multiple fairness violations detected. Consider comprehensive model retraining "
                "with fairness-aware algorithms or data augmentation strategies"
            )
        
        return recommendations
    
    def _interpret_demographic_parity(self, max_difference: float) -> str:
        """Interpret demographic parity results"""
        if max_difference < 0.05:
            return "Good demographic parity"
        elif max_difference < 0.1:
            return "Moderate demographic parity violation"
        else:
            return "Significant demographic parity violation"
    
    def _interpret_equalized_odds(self, tpr_diff: float, fpr_diff: float) -> str:
        """Interpret equalized odds results"""
        max_diff = max(tpr_diff, fpr_diff)
        if max_diff < 0.05:
            return "Good equalized odds"
        elif max_diff < 0.1:
            return "Moderate equalized odds violation"
        else:
            return "Significant equalized odds violation"
    
    def _interpret_equalized_opportunity(self, max_difference: float) -> str:
        """Interpret equalized opportunity results"""
        if max_difference < 0.05:
            return "Good equalized opportunity"
        elif max_difference < 0.1:
            return "Moderate equalized opportunity violation"
        else:
            return "Significant equalized opportunity violation"
    
    def _interpret_calibration_fairness(self, max_difference: float) -> str:
        """Interpret calibration fairness results"""
        if max_difference < 0.02:
            return "Good calibration fairness"
        elif max_difference < 0.05:
            return "Moderate calibration fairness violation"
        else:
            return "Significant calibration fairness violation"

# Usage example
async def bias_monitoring_example():
    # Sample data
    predictions = np.random.binomial(1, 0.3, 1000)  # 30% positive predictions
    actuals = np.random.binomial(1, 0.25, 1000)     # 25% actual positives
    protected_attrs = {
        "gender": np.random.choice([0, 1], 1000),     # 0=female, 1=male
        "race": np.random.choice([0, 1, 2], 1000)    # 3 racial groups
    }
    
    bias_monitor = BiasMonitor(protected_attributes=["gender", "race"])
    bias_assessment = await bias_monitor.assess_bias(predictions, actuals, protected_attrs)
    
    print(f"Bias detected: {bias_assessment['bias_detected']}")
    print(f"Overall bias score: {bias_assessment['overall_bias_score']:.3f}")
    print(f"Recommendations: {bias_assessment['recommendations']}")
```

### 4. Explainability and Interpretability Tracking

**Model Explainability Monitoring:**
```python
# Comprehensive model explainability tracking system
import shap
import lime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import json

class ExplainabilityTracker:
    """Track and monitor model explainability across different methods"""
    
    def __init__(self, model, explainability_methods: List[str] = None):
        self.model = model
        self.methods = explainability_methods or ["shap", "lime", "feature_importance"]
        self.explanation_history = []
        self.feature_importance_trends = defaultdict(list)
        
    async def generate_explanation(self, instance: np.ndarray, 
                                 method: str = "shap") -> Dict[str, Any]:
        """Generate explanation for a single instance using specified method"""
        
        explanation_result = {
            "timestamp": time.time(),
            "method": method,
            "instance_id": hash(str(instance.tobytes()))[:8],
            "explanation": {},
            "feature_names": None,
            "interpretation": {}
        }
        
        try:
            if method == "shap":
                explanation_result["explanation"] = await self._shap_explanation(instance)
            elif method == "lime":
                explanation_result["explanation"] = await self._lime_explanation(instance)
            elif method == "feature_importance":
                explanation_result["explanation"] = await self._feature_importance_explanation()
            else:
                raise ValueError(f"Unknown explainability method: {method}")
            
            # Add interpretation
            explanation_result["interpretation"] = self._interpret_explanation(
                explanation_result["explanation"], method
            )
            
        except Exception as e:
            explanation_result["error"] = str(e)
        
        # Store explanation
        self.explanation_history.append(explanation_result)
        
        return explanation_result
    
    async def _shap_explanation(self, instance: np.ndarray) -> Dict[str, Any]:
        """Generate SHAP explanation for the instance"""
        try:
            # Use SHAP explainer (adjust based on model type)
            explainer = shap.Explainer(self.model)
            shap_values = explainer(instance.reshape(1, -1))
            
            return {
                "shap_values": shap_values.values[0].tolist(),
                "base_value": shap_values.base_values[0],
                "feature_names": shap_values.feature_names
            }
        except Exception as e:
            # Fallback for models not directly supported by SHAP
            return {"error": f"SHAP explanation failed: {e}"}
    
    async def _lime_explanation(self, instance: np.ndarray) -> Dict[str, Any]:
        """Generate LIME explanation for the instance"""
        try:
            # LIME explanation for tabular data
            explainer = lime.lime_tabular.LimeTabularExplainer(
                training_data=np.array([]),  # Would need actual training data
                feature_names=[f"feature_{i}" for i in range(instance.shape[0])],
                class_names=['negative', 'positive'],
                mode='classification'
            )
            
            explanation = explainer.explain_instance(
                instance, 
                self.model.predict
            )
            
            return {
                "lime_weights": dict(explanation.as_list()),
                "lime_score": explanation.score,
                "lime_label": explanation.local_exp
            }
        except Exception as e:
            return {"error": f"LIME explanation failed: {e}"}
    
    async def _feature_importance_explanation(self) -> Dict[str, Any]:
        """Generate global feature importance explanation"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                # Tree-based models
                importances = self.model.feature_importances_
                feature_names = [f"feature_{i}" for i in range(len(importances))]
                
                # Sort by importance
                importance_pairs = list(zip(feature_names, importances))
                importance_pairs.sort(key=lambda x: x[1], reverse=True)
                
                return {
                    "feature_importances": dict(importance_pairs),
                    "top_features": importance_pairs[:10]
                }
            elif hasattr(self.model, 'coef_'):
                # Linear models
                coefs = self.model.coef_[0] if len(self.model.coef_.shape) > 1 else self.model.coef_
                feature_names = [f"feature_{i}" for i in range(len(coefs))]
                
                # Sort by absolute coefficient value
                coef_pairs = list(zip(feature_names, np.abs(coefs)))
                coef_pairs.sort(key=lambda x: x[1], reverse=True)
                
                return {
                    "feature_coefficients": dict(coef_pairs),
                    "top_features": coef_pairs[:10]
                }
            else:
                return {"error": "Model does not support feature importance extraction"}
        except Exception as e:
            return {"error": f"Feature importance extraction failed: {e}"}
    
    def _interpret_explanation(self, explanation: Dict[str, Any], method: str) -> Dict[str, Any]:
        """Generate human-readable interpretation of the explanation"""
        interpretation = {
            "method": method,
            "summary": "",
            "key_insights": [],
            "confidence": "medium"
        }
        
        try:
            if method == "shap" and "shap_values" in explanation:
                shap_values = explanation["shap_values"]
                base_value = explanation["base_value"]
                
                # Find most influential features
                abs_shap = [(i, abs(val)) for i, val in enumerate(shap_values)]
                abs_shap.sort(key=lambda x: x[1], reverse=True)
                top_features = abs_shap[:3]
                
                interpretation["summary"] = (
                    f"SHAP explanation: Model prediction is {abs(shap_values[abs_shap[0][0]]):.3f} "
                    f"away from the expected value due to feature {top_features[0][0]}"
                )
                
                interpretation["key_insights"] = [
                    f"Feature {idx} contributes {val:.3f} to the prediction"
                    for idx, val in abs_shap[:3]
                ]
                
                interpretation["confidence"] = "high"
            
            elif method == "feature_importance" and "top_features" in explanation:
                top_features = explanation["top_features"]
                
                interpretation["summary"] = (
                    f"Top 3 most important features: "
                    f"{', '.join([f[0] for f in top_features])}"
                )
                
                interpretation["key_insights"] = [
                    f"{feature}: {importance:.3f}"
                    for feature, importance in top_features
                ]
                
                interpretation["confidence"] = "medium"
            
        except Exception as e:
            interpretation["summary"] = f"Explanation interpretation failed: {e}"
        
        return interpretation
    
    async def analyze_explanation_consistency(self, instances: List[np.ndarray],
                                            method: str = "shap") -> Dict[str, Any]:
        """Analyze consistency of explanations across multiple instances"""
        
        explanations = []
        for instance in instances:
            explanation = await self.generate_explanation(instance, method)
            explanations.append(explanation)
        
        # Calculate explanation stability metrics
        consistency_analysis = {
            "timestamp": time.time(),
            "method": method,
            "instance_count": len(instances),
            "consistency_metrics": {},
            "stability_score": 0.0,
            "recommendations": []
        }
        
        try:
            if method == "shap":
                consistency_analysis["consistency_metrics"] = await self._analyze_shap_consistency(explanations)
            elif method == "feature_importance":
                consistency_analysis["consistency_metrics"] = await self._analyze_importance_consistency(explanations)
            
            # Calculate overall stability score
            consistency_analysis["stability_score"] = self._calculate_stability_score(
                consistency_analysis["consistency_metrics"]
            )
            
            # Generate recommendations
            consistency_analysis["recommendations"] = self._generate_consistency_recommendations(
                consistency_analysis["stability_score"]
            )
            
        except Exception as e:
            consistency_analysis["error"] = str(e)
        
        return consistency_analysis
    
    async def _analyze_shap_consistency(self, explanations: List[Dict]) -> Dict[str, Any]:
        """Analyze SHAP explanation consistency across instances"""
        # Extract SHAP values from all explanations
        shap_values_list = []
        for exp in explanations:
            if "shap_values" in exp["explanation"]:
                shap_values_list.append(exp["explanation"]["shap_values"])
        
        if len(shap_values_list) < 2:
            return {"error": "Insufficient explanations for consistency analysis"}
        
        # Calculate variance across explanations
        shap_matrix = np.array(shap_values_list)
        feature_variances = np.var(shap_matrix, axis=0)
        
        # Calculate consistency metrics
        consistency_metrics = {
            "average_feature_variance": np.mean(feature_variances),
            "max_feature_variance": np.max(feature_variances),
            "stable_features": np.sum(feature_variances < np.percentile(feature_variances, 25)),
            "unstable_features": np.sum(feature_variances > np.percentile(feature_variances, 75))
        }
        
        return consistency_metrics
    
    async def _analyze_importance_consistency(self, explanations: List[Dict]) -> Dict[str, Any]:
        """Analyze feature importance consistency across explanations"""
        # Extract top features from each explanation
        top_features_list = []
        for exp in explanations:
            if "top_features" in exp["explanation"]:
                top_features_list.append([f[0] for f in exp["explanation"]["top_features"]])
        
        if not top_features_list:
            return {"error": "No top features found in explanations"}
        
        # Calculate feature ranking consistency
        from collections import Counter
        
        # Flatten all top features
        all_top_features = [feature for sublist in top_features_list for feature in sublist]
        feature_counts = Counter(all_top_features)
        
        # Calculate consistency metrics
        total_appearances = len(top_features_list) * len(top_features_list[0])
        unique_features = len(set(all_top_features))
        
        consistency_metrics = {
            "feature_diversity": unique_features,
            "top_feature_consistency": feature_counts.most_common(1)[0][1] / len(top_features_list),
            "average_feature_overlap": total_appearances / unique_features,
            "most_consistent_features": feature_counts.most_common(10)
        }
        
        return consistency_metrics
    
    def _calculate_stability_score(self, consistency_metrics: Dict[str, Any]) -> float:
        """Calculate overall stability score from consistency metrics"""
        if "error" in consistency_metrics:
            return 0.0
        
        # Different calculation based on available metrics
        if "average_feature_variance" in consistency_metrics:
            # For SHAP: lower variance = higher stability
            avg_variance = consistency_metrics["average_feature_variance"]
            return max(0, 1.0 - (avg_variance / 2.0))  # Normalize variance
        
        elif "top_feature_consistency" in consistency_metrics:
            # For feature importance: higher consistency = higher stability
            return consistency_metrics["top_feature_consistency"]
        
        return 0.5  # Default neutral score
    
    def _generate_consistency_recommendations(self, stability_score: float) -> List[str]:
        """Generate recommendations based on explanation consistency"""
        recommendations = []
        
        if stability_score < 0.3:
            recommendations.append(
                "Low explanation consistency detected. Model may be overfitting or data distribution is shifting."
            )
            recommendations.append(
                "Consider model regularization or data augmentation to improve stability."
            )
        elif stability_score < 0.7:
            recommendations.append(
                "Moderate explanation consistency. Monitor for data drift and model performance."
            )
        
        recommendations.append(
            "Implement regular explainability monitoring to track model interpretability over time."
        )
        
        return recommendations

class ComprehensiveAIObservability:
    """Complete AI observability system integrating all monitoring aspects"""
    
    def __init__(self, model_id: str, model, config: Dict[str, Any]):
        self.model_id = model_id
        self.model = model
        self.config = config
        
        # Initialize monitoring components
        self.performance_monitor = ModelPerformanceMonitor(model_id)
        self.bias_monitor = BiasMonitor(config.get("protected_attributes", []))
        self.explainability_tracker = ExplainabilityTracker(model)
        self.alert_manager = AlertManager()
        
        # Data for drift detection
        self.reference_data = config.get("reference_data")
        if self.reference_data is not None:
            self.drift_detector = DataDriftDetector(self.reference_data)
        else:
            self.drift_detector = None
    
    async def comprehensive_monitoring_cycle(self, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete monitoring cycle for a prediction"""
        
        monitoring_result = {
            "timestamp": time.time(),
            "model_id": self.model_id,
            "prediction_id": prediction_data.get("prediction_id"),
            "monitoring_results": {}
        }
        
        try:
            # 1. Performance Monitoring
            perf_metrics = await self.performance_monitor.record_inference(
                prediction=prediction_data["prediction"],
                actual=prediction_data.get("actual"),
                features=prediction_data.get("features"),
                metadata=prediction_data.get("metadata")
            )
            monitoring_result["monitoring_results"]["performance"] = perf_metrics.to_dict()
            
            # 2. Bias Assessment (if actual values available)
            if "actual" in prediction_data and "protected_attributes" in prediction_data:
                bias_assessment = await self.bias_monitor.assess_bias(
                    predictions=np.array([prediction_data["prediction"]]),
                    actuals=np.array([prediction_data["actual"]]),
                    protected_attrs=prediction_data["protected_attributes"]
                )
                monitoring_result["monitoring_results"]["bias"] = bias_assessment
            
            # 3. Data Drift Detection
            if self.drift_detector and "features" in prediction_data:
                drift_result = await self.drift_detector.detect_drift(
                    np.array([prediction_data["features"]])
                )
                monitoring_result["monitoring_results"]["drift"] = drift_result
            
            # 4. Explainability (sample-based)
            if "features" in prediction_data and np.random.random() < 0.01:  # 1% sampling
                explanation = await self.explainability_tracker.generate_explanation(
                    np.array([prediction_data["features"]])
                )
                monitoring_result["monitoring_results"]["explainability"] = explanation
            
            # 5. Overall Health Assessment
            monitoring_result["overall_health"] = await self._assess_overall_health(
                monitoring_result["monitoring_results"]
            )
            
            # 6. Trigger alerts if necessary
            await self._check_and_trigger_alerts(monitoring_result)
            
        except Exception as e:
            monitoring_result["error"] = str(e)
        
        return monitoring_result
    
    async def _assess_overall_health(self, monitoring_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall AI system health based on all monitoring signals"""
        
        health_assessment = {
            "overall_score": 1.0,  # Start with perfect health
            "health_indicators": {},
            "alerts_generated": [],
            "status": "healthy"
        }
        
        # Performance health
        if "performance" in monitoring_results:
            perf_health = self._assess_performance_health(monitoring_results["performance"])
            health_assessment["health_indicators"]["performance"] = perf_health
            health_assessment["overall_score"] *= perf_health["score"]
        
        # Bias health
        if "bias" in monitoring_results:
            bias_health = self._assess_bias_health(monitoring_results["bias"])
            health_assessment["health_indicators"]["bias"] = bias_health
            health_assessment["overall_score"] *= bias_health["score"]
        
        # Drift health
        if "drift" in monitoring_results:
            drift_health = self._assess_drift_health(monitoring_results["drift"])
            health_assessment["health_indicators"]["drift"] = drift_health
            health_assessment["overall_score"] *= drift_health["score"]
        
        # Determine overall status
        if health_assessment["overall_score"] >= 0.9:
            health_assessment["status"] = "healthy"
        elif health_assessment["overall_score"] >= 0.7:
            health_assessment["status"] = "degraded"
        else:
            health_assessment["status"] = "unhealthy"
        
        return health_assessment
    
    def _assess_performance_health(self, performance_data: Dict) -> Dict[str, Any]:
        """Assess performance-related health"""
        score = 1.0
        issues = []
        
        # Check latency
        if performance_data.get("latency_ms", 0) > 1000:  # 1 second threshold
            score *= 0.8
            issues.append("High latency detected")
        
        # Check accuracy (if available)
        if performance_data.get("accuracy") is not None:
            accuracy = performance_data["accuracy"]
            if accuracy < 0.8:
                score *= accuracy
                issues.append(f"Low accuracy: {accuracy:.3f}")
        
        return {
            "score": score,
            "issues": issues,
            "status": "healthy" if score >= 0.8 else "degraded" if score >= 0.6 else "unhealthy"
        }
    
    def _assess_bias_health(self, bias_data: Dict) -> Dict[str, Any]:
        """Assess bias-related health"""
        score = 1.0
        issues = []
        
        # Check for bias violations
        if bias_data.get("bias_detected"):
            score *= 0.7
            issues.append("Bias detected in model predictions")
        
        # Check overall bias score
        bias_score = bias_data.get("overall_bias_score", 0)
        if bias_score > 0.1:
            score *= (1.0 - bias_score)
            issues.append(f"High bias score: {bias_score:.3f}")
        
        return {
            "score": score,
            "issues": issues,
            "status": "healthy" if score >= 0.9 else "degraded" if score >= 0.7 else "unhealthy"
        }
    
    def _assess_drift_health(self, drift_data: Dict) -> Dict[str, Any]:
        """Assess drift-related health"""
        score = 1.0
        issues = []
        
        # Check drift detection
        if drift_data.get("drift_detected"):
            drift_score = drift_data.get("drift_score", 0)
            if drift_score > 0.5:
                score *= 0.5
                issues.append("Severe data drift detected")
            elif drift_score > 0.2:
                score *= 0.7
                issues.append("Moderate data drift detected")
        
        return {
            "score": score,
            "issues": issues,
            "status": "healthy" if score >= 0.9 else "degraded" if score >= 0.7 else "unhealthy"
        }
    
    async def _check_and_trigger_alerts(self, monitoring_result: Dict[str, Any]):
        """Check monitoring results and trigger appropriate alerts"""
        
        health = monitoring_result.get("overall_health", {})
        overall_score = health.get("overall_score", 1.0)
        
        # Health-based alerts
        if overall_score < 0.7:
            await self.alert_manager.trigger_alert(
                level="critical" if overall_score < 0.5 else "warning",
                message=f"AI model {self.model_id} health degraded. Score: {overall_score:.3f}",
                data=monitoring_result
            )
        
        # Specific alerts for different monitoring aspects
        monitoring_results = monitoring_result.get("monitoring_results", {})
        
        # Performance alerts
        if "performance" in monitoring_results:
            perf_data = monitoring_results["performance"]
            if perf_data.get("accuracy", 1.0) < 0.8:
                await self.alert_manager.trigger_alert(
                    level="warning",
                    message=f"Model accuracy dropped to {perf_data['accuracy']:.3f}",
                    data=perf_data
                )
        
        # Bias alerts
        if "bias" in monitoring_results:
            bias_data = monitoring_results["bias"]
            if bias_data.get("bias_detected"):
                await self.alert_manager.trigger_alert(
                    level="warning",
                    message=f"Bias detected in model predictions for {self.model_id}",
                    data=bias_data
                )
        
        # Drift alerts
        if "drift" in monitoring_results:
            drift_data = monitoring_results["drift"]
            if drift_data.get("drift_detected"):
                await self.alert_manager.trigger_alert(
                    level="info",
                    message=f"Data drift detected for model {self.model_id}",
                    data=drift_data
                )

class AlertManager:
    """Centralized alert management for AI observability"""
    
    def __init__(self):
        self.alert_channels = {
            "webhook": WebhookNotifier(),
            "email": EmailNotifier(),
            "slack": SlackNotifier()
        }
        self.alert_history = []
    
    async def trigger_alert(self, level: str, message: str, data: Dict = None):
        """Trigger alert through configured channels"""
        
        alert = {
            "timestamp": time.time(),
            "level": level,  # critical, warning, info
            "message": message,
            "data": data or {},
            "alert_id": f"alert_{int(time.time() * 1000)}"
        }
        
        # Store alert
        self.alert_history.append(alert)
        
        # Determine channels based on level
        channels = ["webhook"]  # Always send to webhook
        
        if level == "critical":
            channels.extend(["email", "slack"])
        elif level == "warning":
            channels.append("slack")
        
        # Send to channels
        for channel_name in channels:
            if channel_name in self.alert_channels:
                try:
                    await self.alert_channels[channel_name].send(alert)
                except Exception as e:
                    print(f"Failed to send alert via {channel_name}: {e}")
        
        return alert["alert_id"]

# Concrete notifier implementations (simplified)
class WebhookNotifier:
    async def send(self, alert: Dict):
        # Implementation would send to webhook URL
        print(f"Webhook alert: {alert['message']}")

class EmailNotifier:
    async def send(self, alert: Dict):
        # Implementation would send email
        print(f"Email alert: {alert['message']}")

class SlackNotifier:
    async def send(self, alert: Dict):
        # Implementation would send Slack message
        print(f"Slack alert: {alert['message']}")

# Usage example
async def complete_observability_example():
    """Example of comprehensive AI observability setup"""
    
    # Initialize observability system
    observability = ComprehensiveAIObservability(
        model_id="fraud_detection_model",
        model=my_ml_model,
        config={
            "protected_attributes": ["gender", "age_group", "location"],
            "reference_data": training_data,
            "alert_thresholds": {
                "accuracy": 0.85,
                "latency": 500  # milliseconds
            }
        }
    )
    
    # Simulate prediction with monitoring
    prediction_data = {
        "prediction_id": "pred_123",
        "prediction": 0.85,  # Fraud probability
        "actual": 1,  # Actual fraud (for bias assessment)
        "features": {
            "transaction_amount": 1500.0,
            "user_age": 35,
            "account_age_days": 180
        },
        "protected_attributes": {
            "gender": 1,
            "age_group": 1,
            "location": 0
        },
        "metadata": {
            "inference_time_ms": 45,
            "model_version": "2.1.0"
        }
    }
    
    # Run comprehensive monitoring
    monitoring_result = await observability.comprehensive_monitoring_cycle(prediction_data)
    
    print(f"Overall health status: {monitoring_result['overall_health']['status']}")
    print(f"Health score: {monitoring_result['overall_health']['overall_score']:.3f}")
    
    # Generate monitoring dashboard data
    dashboard_data = await observability.generate_dashboard_data(time_window_hours=24)
    print(f"Dashboard data generated: {len(dashboard_data)} metrics")
```

## Best Practices

### 1. Monitoring Strategy

- **Multi-dimensional monitoring**: Track performance, bias, drift, and explainability
- **Real-time alerting**: Immediate notification for critical issues
- **Historical trend analysis**: Track metrics over time to detect patterns
- **Contextual thresholds**: Adaptive thresholds based on business context
- **False positive reduction**: Minimize alert fatigue with intelligent filtering

### 2. Data Quality Monitoring

- **Input validation**: Monitor input data quality and distribution
- **Missing value detection**: Track and alert on missing data patterns
- **Outlier detection**: Identify anomalous input patterns
- **Data drift detection**: Monitor for changes in input data distribution
- **Feature correlation monitoring**: Track relationships between features

### 3. Model Performance Monitoring

- **Accuracy degradation**: Track model performance over time
- **Prediction confidence**: Monitor model uncertainty and calibration
- **Latency monitoring**: Track inference time and throughput
- **Error rate monitoring**: Track prediction failures and edge cases
- **Feature importance drift**: Monitor changes in feature importance over time

### 4. Bias and Fairness Monitoring

- **Protected attribute monitoring**: Track performance across protected groups
- **Fairness metric calculation**: Implement multiple fairness metrics
- **Bias detection alerts**: Automated detection of unfair model behavior
- **Remediation tracking**: Monitor effectiveness of bias mitigation strategies
- **Regulatory compliance**: Ensure adherence to fairness regulations

## Common Pitfalls

1. **Over-monitoring**: Tracking too many metrics leading to alert fatigue
2. **Insufficient baseline data**: Not having adequate reference data for comparisons
3. **False alarms**: Poor threshold tuning causing excessive alerts
4. **Missing context**: Monitoring metrics without business context
5. **Reactive monitoring**: Only monitoring after problems occur
6. **Single metric focus**: Relying on one metric to assess model health
7. **Ignoring data drift**: Not monitoring for changes in input data distribution

## Resources

- **references/ml-monitoring.md**: Comprehensive ML monitoring strategies
- **references/fairness-monitoring.md**: Bias detection and mitigation
- **references/data-quality.md**: Data quality monitoring patterns
- **assets/observability-dashboard.yaml**: Complete observability stack
- **assets/alert-config.yaml**: Alert configuration templates
- **assets/monitoring-prometheus.yml**: Prometheus monitoring configuration

## Production Checklist

- [ ] Performance monitoring implemented with appropriate thresholds
- [ ] Data drift detection configured with baseline data
- [ ] Bias and fairness monitoring operational for all protected attributes
- [ ] Explainability tracking implemented for key predictions
- [ ] Alert system configured with proper escalation paths
- [ ] Dashboard created for real-time monitoring visibility
- [ ] Historical trend analysis implemented
- [ ] Incident response procedures documented and tested
- [ ] Monitoring data retention and archival policies defined
- [ ] Team trained on monitoring tools and alert interpretation
- [ ] Regular monitoring review process established
- [ ] Regulatory compliance requirements mapped to monitoring
- [ ] Model retraining triggers based on monitoring signals
- [ ] Monitoring system tested under various failure scenarios