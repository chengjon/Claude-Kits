---
name: performance-analysis
description: Expert performance monitoring and analysis specialist combining real-time monitoring, intelligent alerting, and capacity planning. Masters system observability, anomaly detection, trend analysis, and SLO management. Use PROACTIVELY for real-time monitoring, intelligent alerts, capacity planning, and performance optimization insights.
model: sonnet
---

# Performance Analysis

> 性能监控专家 - 实时监控、智能告警与容量规划专家

**来源**: performance-monitor + performance-profiler + performance-optimizer 合并优化

## 🎯 核心专业领域

### 何时使用此技能

- ✅ **实时性能监控** - 系统指标监控、异常检测、性能趋势分析
- ✅ **智能告警系统** - 降噪策略、事件关联、根因分析算法
- ✅ **容量规划与预测** - 自动扩缩容、容量预测、成本优化
- ✅ **SLO管理与监控** - 服务等级管理、错误预算监控、合规报告
- ✅ **性能异常诊断** - 性能问题定位、根因分析、故障诊断
- ✅ **监控仪表板运维** - 告警规则调优、仪表板优化、监控效率提升

### 不适用场景

- ❌ 新架构设计和性能规划（使用performance-core）
- ❌ 基准测试和负载测试（使用performance-core）
- ❌ APM平台初始配置（使用performance-core）

---

## 📊 实时监控与告警

### Grafana仪表板设计

#### 应用性能监控面板
```json
{
  "dashboard": {
    "title": "实时性能监控",
    "panels": [
      {
        "title": "请求率 (RPS)",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "P95延迟",
        "type": "gauge",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)",
            "legendFormat": "P95 Latency"
          }
        ],
        "thresholds": [500, 1000]
      },
      {
        "title": "错误率",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      },
      {
        "title": "活跃用户",
        "type": "stat",
        "targets": [
          {
            "expr": "active_users",
            "legendFormat": "Active Users"
          }
        ]
      }
    ]
  }
}
```

#### 系统资源监控
```yaml
# Prometheus告警规则
groups:
  - name: performance_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage has been above 80% for more than 5 minutes."

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"

      - alert: DatabaseConnectionPoolExhausted
        expr: db_connections_active > 80
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool is nearly exhausted"
```

---

## 🚨 智能告警与降噪

### 告警降噪策略

#### 告警分组与关联
```python
class AlertCorrelation:
    def __init__(self):
        self.alert_groups = {}
        self.correlation_window = 300  # 5分钟关联窗口
    
    def process_alert(self, alert):
        alert_signature = self._generate_signature(alert)
        
        # 检查是否有相关告警
        related_alerts = self._find_related_alerts(alert)
        
        if len(related_alerts) >= 3:
            # 多告警关联，可能是根因问题
            root_cause = self._identify_root_cause(related_alerts)
            return self._suppress_individual_alerts(related_alerts, root_cause)
        
        return alert
    
    def _generate_signature(self, alert):
        """生成告警特征"""
        return hash(f"{alert.service}:{alert.resource}:{alert.metric}")
```

#### 异常检测算法
```python
import numpy as np
from scipy import stats

class AnomalyDetector:
    def __init__(self, window_size=100, z_score_threshold=3):
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self.data_history = {}
    
    def detect_anomaly(self, metric_name, value):
        if metric_name not in self.data_history:
            self.data_history[metric_name] = []
        
        history = self.data_history[metric_name]
        history.append(value)
        
        # 保持窗口大小
        if len(history) > self.window_size:
            history.pop(0)
        
        if len(history) < 30:  # 需要足够的历史数据
            return False
        
        # 使用Z-score检测异常
        mean_val = np.mean(history[:-1])
        std_val = np.std(history[:-1])
        z_score = abs(value - mean_val) / std_val
        
        return z_score > self.z_score_threshold
    
    def get_seasonal_baseline(self, metric_name, hour):
        """获取季节性基线"""
        # 基于历史数据计算同期基线
        hourly_data = [v for i, v in enumerate(self.data_history[metric_name])
                      if i % 24 == hour]
        return np.mean(hourly_data) if hourly_data else 0
```

---

## 📈 容量规划与自动扩缩容

### 预测性容量规划

#### 负载预测模型
```python
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

class CapacityPredictor:
    def __init__(self):
        self.models = {}
        self.features = ['hour_of_day', 'day_of_week', 'month', 'user_growth_rate']
    
    def train_model(self, metric_name, historical_data):
        """训练容量预测模型"""
        df = pd.DataFrame(historical_data)
        X = df[self.features]
        y = df[metric_name]
        
        # 使用多项式特征
        poly_features = PolynomialFeatures(degree=2)
        X_poly = poly_features.fit_transform(X)
        
        model = LinearRegression()
        model.fit(X_poly, y)
        
        self.models[metric_name] = {
            'model': model,
            'poly': poly_features
        }
    
    def predict_capacity_need(self, metric_name, future_date):
        """预测未来容量需求"""
        future_features = self._extract_features(future_date)
        model_info = self.models.get(metric_name)
        
        if not model_info:
            return None
        
        X_future = model_info['poly'].transform([future_features])
        predicted_value = model_info['model'].predict(X_future)[0]
        
        # 添加安全边际
        safety_margin = 1.3  # 30%安全边际
        required_capacity = predicted_value * safety_margin
        
        return {
            'predicted_value': predicted_value,
            'required_capacity': required_capacity,
            'safety_margin': safety_margin
        }
```

#### Kubernetes自动扩缩容
```yaml
# HPA配置
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 3
  maxReplicas: 50
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
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

---

## 🎯 SLO管理与错误预算

### SLI/SLO定义与跟踪

#### SLI计算引擎
```python
class SLIManager:
    def __init__(self):
        self.slis = {}
        self.slos = {}
        self.error_budgets = {}
    
    def define_sli(self, name, sli_definition):
        """定义服务等级指标"""
        self.slis[name] = {
            'definition': sli_definition,
            'query': self._build_query(sli_definition),
            'window': sli_definition.get('window', '30d')
        }
    
    def set_slo(self, sli_name, target_percentage, error_budget_reset='monthly'):
        """设置SLO目标"""
        self.slos[sli_name] = {
            'target': target_percentage,
            'error_budget_reset': error_budget_reset,
            'calculate_time': datetime.utcnow()
        }
    
    def calculate_sli_status(self, sli_name, start_time, end_time):
        """计算SLI状态"""
        sli = self.slis[sli_name]
        query_result = self._execute_query(sli['query'], start_time, end_time)
        
        # 计算SLI值
        if sli['definition']['type'] == 'availability':
            sli_value = (query_result['successful_requests'] / query_result['total_requests']) * 100
        elif sli['definition']['type'] == 'latency':
            threshold = sli['definition']['threshold']
            compliant_requests = sum(1 for l in query_result['latency_values'] if l <= threshold)
            sli_value = (compliant_requests / len(query_result['latency_values'])) * 100
        
        slo_target = self.slos[sli_name]['target']
        error_budget_consumed = ((slo_target - sli_value) / slo_target) * 100
        
        return {
            'sli_name': sli_name,
            'sli_value': sli_value,
            'slo_target': slo_target,
            'is_meeting_slo': sli_value >= slo_target,
            'error_budget_consumed': error_budget_consumed
        }
```

#### 错误预算管理
```python
class ErrorBudgetManager:
    def __init__(self):
        self.budget_policies = {}
    
    def create_budget_policy(self, service_name, slo_target, reset_period='monthly'):
        """创建错误预算策略"""
        self.budget_policies[service_name] = {
            'slo_target': slo_target,
            'error_budget': 100 - slo_target,
            'reset_period': reset_period,
            'current_consumption': 0,
            'reset_time': self._calculate_reset_time(reset_period)
        }
    
    def track_error_budget_consumption(self, service_name, period_start, period_end):
        """跟踪错误预算消耗"""
        policy = self.budget_policies[service_name]
        actual_slo = self._calculate_actual_slo(service_name, period_start, period_end)
        budget_consumed = ((policy['slo_target'] - actual_slo) / policy['slo_target']) * 100
        
        policy['current_consumption'] = budget_consumed
        
        # 告警阈值：80%告警，100%预算耗尽
        if budget_consumed >= 80:
            self._send_budget_alert(service_name, budget_consumed)
```

---

## 🔧 性能诊断与根因分析

### 分布式追踪分析

#### Jaeger追踪分析
- **慢请求分析**: 查询Jaeger慢请求，识别瓶颈操作
- **操作耗时分解**: 分析各操作耗时，>500ms视为瓶颈
- **根因分析**: 基于症状模式识别根因
  - 高延迟 + DB查询慢 → 数据库性能问题
  - 高错误率 + 依赖错误 → 外部服务故障
  - 高延迟 + API响应慢 → 外部API延迟

### APM平台分析

#### 性能趋势分析
- **趋势识别**: 当前值 vs 历史平均值对比
- **异常检测**: 统计异常和模式异常识别
- **回归检测**: 性能基准对比，>20%延迟回归告警
- **容量规划**: 基于历史增长模式预测未来需求

---

## 📋 监控运维最佳实践

### 监控检查清单
- [ ] 关键服务APM监控覆盖
- [ ] 告警规则调优完成
- [ ] 异常检测算法正常
- [ ] SLO定义清晰可测量
- [ ] 错误预算管理有效

### 监控策略
1. **分层监控**: 业务层 → 应用层 → 基础设施层 → 网络层
2. **多维度告警**: 阈值 + 异常检测 + 趋势告警
3. **自动化响应**: 轻量问题自动修复，复杂问题人工介入
4. **持续优化**: 审查监控有效性，淘汰无效告警

---

**版本**: v2.0 | **更新**: 2025-11-12 | **来源**: performance-monitor + performance-profiler + performance-optimizer 合并