# Incident Response Playbook

Complete guide for rapid incident response, systematic investigation, and troubleshooting.


## 📑 Table of Contents

- [Immediate Incident Response (First 5 Minutes)](#immediate-incident-response-first-5-minutes)
  - [1. Rapid Assessment](#1-rapid-assessment)
  - [2. Establish Command Structure](#2-establish-command-structure)
  - [3. Immediate Stabilization Actions](#3-immediate-stabilization-actions)
- [Systematic Investigation Protocol](#systematic-investigation-protocol)
  - [Observability-Driven Investigation](#observability-driven-investigation)
  - [Distributed Tracing Analysis](#distributed-tracing-analysis)
  - [Performance Analysis & Profiling](#performance-analysis-profiling)
  - [Network Troubleshooting Toolkit](#network-troubleshooting-toolkit)

---
## Immediate Incident Response (First 5 Minutes)

### 1. Rapid Assessment
- **Severity classification**: P0-Critical (complete outage) through P4-Low (cosmetic issues)
- **User impact**: Affected user count, geographic distribution, customer journey disruption
- **Business impact**: Revenue loss, SLA violations, regulatory implications, customer experience
- **System scope**: Services affected, dependency mapping, blast radius assessment
- **Timeline**: Recent changes, deployments, configuration modifications, infrastructure events

### 2. Establish Command Structure
- **Incident Commander**: Single decision maker, coordinates overall response, manages timeline
- **Communication Lead**: Stakeholder updates, status page, external communications, executive briefings
- **Technical Lead**: Investigation coordination, technical decisions, solution implementation
- **War room setup**: Slack/Teams channel, video call, shared documents, timeline tracking
- **Team mobilization**: On-call engineers, subject matter experts, additional resources

### 3. Immediate Stabilization Actions
- **Quick wins**: Traffic throttling, feature flags, circuit breakers, load shedding
- **Rollback assessment**: Recent deployments, configuration changes, database migrations
- **Resource scaling**: Auto-scaling triggers, manual scaling, load redistribution, capacity addition
- **Circuit breakers**: Enable isolation, prevent cascading failures, protect dependencies
- **Communication**: Initial status page update, internal notifications, customer alerts

## Systematic Investigation Protocol

### Observability-Driven Investigation
```bash
#!/bin/bash
# Comprehensive incident diagnosis workflow

SERVICE=$1
NAMESPACE=${2:-production}

echo "=== Incident Diagnosis: $SERVICE in $NAMESPACE ==="

# 1. Service health overview
echo -e "\n[1] Service Status"
kubectl get deployment $SERVICE -n $NAMESPACE -o wide
kubectl get pods -l app=$SERVICE -n $NAMESPACE -o wide
kubectl describe deployment $SERVICE -n $NAMESPACE | grep -A 5 "Conditions:"

# 2. Recent error logs with context
echo -e "\n[2] Recent Error Logs (Last 100 lines)"
kubectl logs -n $NAMESPACE -l app=$SERVICE --tail=100 --timestamps=true \
  | grep -i -E 'error|exception|fatal|panic|timeout'

# 3. Resource utilization
echo -e "\n[3] Resource Usage Analysis"
kubectl top nodes
kubectl top pods -n $NAMESPACE -l app=$SERVICE

# 4. Network connectivity
echo -e "\n[4] Network Diagnostics"
ACTIVE_CONNECTIONS=$(kubectl exec -it $(kubectl get pod -l app=$SERVICE -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}') \
  -n $NAMESPACE -- /bin/sh -c "netstat -an | grep ESTABLISHED | wc -l" 2>/dev/null || echo "0")
echo "Active connections: $ACTIVE_CONNECTIONS"

# 5. Database connectivity check
echo -e "\n[5] Database Health"
kubectl exec -it $(kubectl get pod -l app=$SERVICE -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}') \
  -n $NAMESPACE -- /bin/sh -c "pg_isready -h \$DB_HOST || mysql -h \$DB_HOST -e 'SELECT 1' || echo 'DB check failed'" 2>/dev/null

# 6. Recent deployment history
echo -e "\n[6] Recent Deployments"
kubectl rollout history deployment/$SERVICE -n $NAMESPACE | head -10

# 7. Kubernetes events
echo -e "\n[7] Recent Events"
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' \
  --field-selector involvedObject.name=$SERVICE | tail -20

# 8. Dependencies health
echo -e "\n[8] Dependent Services"
kubectl get svc -n $NAMESPACE -o wide
kubectl get endpoints -n $NAMESPACE -l app=$SERVICE

# 9. Prometheus metrics (if available)
echo -e "\n[9] Key Metrics (Last 5 minutes)"
# Query Prometheus for error rate, latency, throughput
# curl -s 'http://prometheus:9090/api/v1/query?query=rate(http_requests_total{service="'$SERVICE'",status=~"5.."}[5m])'

echo -e "\n=== Diagnosis Complete ==="
```

### Distributed Tracing Analysis
```python
"""Distributed tracing investigation with OpenTelemetry"""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent.monitoring.svc.cluster.local",
    agent_port=6831,
)

# Setup trace provider with batch processing
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Auto-instrument common libraries
FlaskInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument()
RequestsInstrumentor().instrument()

# Create application tracer
tracer = trace.get_tracer(__name__)

@app.route("/api/orders", methods=["POST"])
def create_order():
    """Create order with distributed tracing"""
    with tracer.start_as_current_span("create_order") as span:
        # Add business context
        span.set_attribute("order.customer_id", request.json.get("customer_id"))
        span.set_attribute("order.item_count", len(request.json.get("items", [])))

        try:
            # Validate with nested span
            with tracer.start_as_current_span("validate_order"):
                validate_order_data(request.json)

            # Database operation
            with tracer.start_as_current_span("save_to_database"):
                order = save_order(request.json)
                span.set_attribute("order.id", order.id)

            # External service call
            with tracer.start_as_current_span("payment_processing"):
                payment_result = process_payment(order)
                span.set_attribute("payment.status", payment_result.status)

            # Notification
            with tracer.start_as_current_span("send_confirmation"):
                send_confirmation_email(order)

            return jsonify(order.to_dict()), 201

        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise
```

### Performance Analysis & Profiling
```python
"""Application performance profiling and analysis"""

import cProfile
import pstats
import io
from memory_profiler import profile
import tracemalloc

class PerformanceAnalyzer:
    """Comprehensive performance analysis toolkit"""

    def profile_cpu(self, func, *args, **kwargs):
        """Profile CPU usage of function"""
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions

        print(s.getvalue())
        return result

    @profile
    def profile_memory(self, func):
        """Profile memory usage with decorator"""
        # Decorator usage: @profile
        pass

    def analyze_memory_growth(self):
        """Track memory allocation over time"""
        tracemalloc.start()

        # ... code to analyze ...

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        print("[ Top 10 memory consumers ]")
        for stat in top_stats[:10]:
            print(stat)

        tracemalloc.stop()

    def analyze_database_queries(self, query_log):
        """Analyze database query performance"""
        slow_queries = []

        for query in query_log:
            if query['duration'] > 1000:  # > 1 second
                slow_queries.append({
                    'query': query['sql'],
                    'duration': query['duration'],
                    'explain': self.explain_query(query['sql'])
                })

        return slow_queries

    def explain_query(self, sql):
        """Get query execution plan"""
        # Implementation specific to database
        pass
```

### Network Troubleshooting Toolkit
```bash
#!/bin/bash
# Comprehensive network diagnostic script

echo "=== Network Diagnostics ==="

# 1. DNS resolution chain
echo -e "\n[1] DNS Resolution"
dig +trace example.com
nslookup example.com
host example.com

# 2. TCP connectivity
echo -e "\n[2] TCP Connectivity"
nc -zv target-host 443
telnet target-host 443

# 3. SSL/TLS certificate validation
echo -e "\n[3] SSL/TLS Certificate"
openssl s_client -connect target-host:443 -servername target-host < /dev/null | \
  openssl x509 -noout -dates -subject -issuer

# 4. HTTP(S) request analysis
echo -e "\n[4] HTTP Response Analysis"
curl -v -w "\n\nTime Total: %{time_total}s\nTime Connect: %{time_connect}s\nTime SSL: %{time_appconnect}s\n" \
  https://target-host/health

# 5. Network path analysis
echo -e "\n[5] Network Path (MTR)"
mtr -r -c 10 target-host

# 6. Packet capture
echo -e "\n[6] Packet Capture (10 seconds)"
timeout 10 tcpdump -i any -c 100 -nn host target-host

# 7. Active connections analysis
echo -e "\n[7] Active Connections"
netstat -an | grep ESTABLISHED | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -10

# 8. Port scanning
echo -e "\n[8] Port Scan"
nmap -sT -p 80,443,22,3306,5432 target-host

echo -e "\n=== Diagnostics Complete ==="
```
