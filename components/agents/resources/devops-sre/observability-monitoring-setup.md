# Modern Monitoring & Observability Setup

Complete configuration for Prometheus, Grafana, and alerting infrastructure.


## 📑 Table of Contents

- [Prometheus & Grafana Configuration](#prometheus-grafana-configuration)
  - [Prometheus Configuration](#prometheus-configuration)
  - [Prometheus Alert Rules](#prometheus-alert-rules)
- [Best Practices](#best-practices)
  - [Alert Design](#alert-design)
  - [Dashboard Design](#dashboard-design)
  - [Observability Principles](#observability-principles)

---
## Prometheus & Grafana Configuration

### Prometheus Configuration
```yaml
# prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: 'production-cluster'
        region: 'us-east-1'

    # Alert rule files
    rule_files:
      - '/etc/prometheus/rules/*.yml'

    # Alertmanager configuration
    alerting:
      alertmanagers:
        - static_configs:
            - targets: ['alertmanager:9093']

    # Scrape configurations
    scrape_configs:
      # Kubernetes API server
      - job_name: 'kubernetes-apiservers'
        kubernetes_sd_configs:
          - role: endpoints
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
          - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
            action: keep
            regex: default;kubernetes;https

      # Kubernetes nodes
      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
          - role: node
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
          - action: labelmap
            regex: __meta_kubernetes_node_label_(.+)

      # Kubernetes pods
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: $1:$2
            target_label: __address__
          - action: labelmap
            regex: __meta_kubernetes_pod_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: kubernetes_pod_name
```

### Prometheus Alert Rules
```yaml
# prometheus-rules.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-rules
  namespace: monitoring
data:
  alerts.yml: |
    groups:
      - name: sre_alerts
        interval: 30s
        rules:
          # High error rate (SLI violation)
          - alert: HighErrorRate
            expr: |
              rate(http_requests_total{status=~"5.."}[5m]) /
              rate(http_requests_total[5m]) > 0.01
            for: 5m
            labels:
              severity: critical
              category: sli_violation
            annotations:
              summary: "High error rate detected (> 1%)"
              description: "Service {{ $labels.service }} error rate is {{ $value | humanizePercentage }}"
              runbook: "https://runbooks.company.com/high-error-rate"

          # Service down
          - alert: ServiceDown
            expr: up{job="kubernetes-pods"} == 0
            for: 1m
            labels:
              severity: critical
              category: availability
            annotations:
              summary: "Service {{ $labels.kubernetes_pod_name }} is down"
              runbook: "https://runbooks.company.com/service-down"

          # High latency (SLI violation)
          - alert: HighLatency
            expr: |
              histogram_quantile(0.95,
                rate(http_request_duration_seconds_bucket[5m])
              ) > 1
            for: 10m
            labels:
              severity: warning
              category: sli_violation
            annotations:
              summary: "High latency detected (p95 > 1s)"
              description: "Service {{ $labels.service }} p95 latency is {{ $value }}s"

          # Memory pressure
          - alert: HighMemoryUsage
            expr: |
              container_memory_usage_bytes /
              container_spec_memory_limit_bytes > 0.9
            for: 5m
            labels:
              severity: warning
              category: resource
            annotations:
              summary: "High memory usage on {{ $labels.pod }}"
              description: "Memory usage is {{ $value | humanizePercentage }}"

          # CPU throttling
          - alert: CPUThrottling
            expr: |
              rate(container_cpu_cfs_throttled_seconds_total[5m]) > 0.3
            for: 10m
            labels:
              severity: warning
              category: resource
            annotations:
              summary: "CPU throttling detected on {{ $labels.pod }}"
              description: "Container is being throttled {{ $value | humanizePercentage }} of the time"

          # Disk space critical
          - alert: DiskSpaceCritical
            expr: |
              (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
            for: 5m
            labels:
              severity: critical
              category: resource
            annotations:
              summary: "Disk space critical on {{ $labels.instance }}"
              description: "Only {{ $value | humanizePercentage }} disk space remaining"

          # Error budget burn rate (fast burn)
          - alert: ErrorBudgetFastBurn
            expr: |
              (
                (1 - (sum(rate(http_requests_total{status!~"5.."}[1h])) / sum(rate(http_requests_total[1h]))))
                /
                (1 - 0.999)  # 99.9% SLO
              ) > 14.4  # 2% of monthly budget in 1 hour
            for: 5m
            labels:
              severity: critical
              category: error_budget
            annotations:
              summary: "Error budget burning too fast"
              description: "Burning {{ $value }}x faster than budget allows"
```

## Best Practices

### Alert Design
- **Actionable alerts**: Every alert should have a clear runbook and action
- **Noise reduction**: Use proper thresholds and for durations to prevent flapping
- **Severity levels**: Critical (P0), Warning (P1-P2), Info (P3-P4)
- **Runbook links**: Include direct links to troubleshooting guides

### Dashboard Design
- **Business metrics first**: Start with user-facing metrics
- **Technical KPIs**: Follow with system health indicators
- **Real-time status**: Include current state and recent trends
- **Capacity indicators**: Show resource utilization and limits

### Observability Principles
- **Distributed tracing**: Track requests across service boundaries
- **Structured logging**: Use consistent log formats and correlation IDs
- **Metrics cardinality**: Balance detail with performance impact
- **SLI-based monitoring**: Focus on user experience, not just system metrics
