"""Generate diverse test documents for llmprep benchmarking."""
import csv
import json
import os
import random
import textwrap

OUT = "benchmark/test_documents"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Small plain-text memo
# ---------------------------------------------------------------------------
with open(f"{OUT}/memo_short.txt", "w") as f:
    f.write(textwrap.dedent("""\
    MEMORANDUM
    TO: Engineering Team
    FROM: VP of Engineering
    DATE: 2025-06-15
    RE: Q3 Platform Migration Plan

    Team,

    After careful evaluation, we have decided to proceed with the migration from
    our legacy monolith to a microservices architecture. The timeline is as follows:

    Phase 1 (July): Service decomposition and API contract definition.
    Phase 2 (August): Data migration and dual-write validation.
    Phase 3 (September): Traffic cutover with canary deployments.

    Key risks identified:
    - Database schema incompatibilities between v2 and v3 schemas
    - Latency budget exceeded for cross-service calls (target: p99 < 50ms)
    - Third-party vendor API rate limits during peak migration windows

    Each team lead should prepare a detailed migration runbook by June 30.

    Regards,
    Sarah Chen
    """))

# ---------------------------------------------------------------------------
# 2. Medium technical document
# ---------------------------------------------------------------------------
with open(f"{OUT}/technical_spec.txt", "w") as f:
    f.write(textwrap.dedent("""\
    ============================================================
    TECHNICAL SPECIFICATION: Real-Time Event Processing Pipeline
    Version: 2.4.1
    Last Updated: 2025-05-20
    ============================================================

    1. OVERVIEW
    -----------
    This document specifies the architecture and implementation details for the
    real-time event processing pipeline (RTEP) that handles ingestion, enrichment,
    and routing of business events across the platform.

    2. SYSTEM ARCHITECTURE
    ----------------------
    The pipeline consists of four primary components:

    2.1 Event Ingestion Layer
    - Protocol: gRPC with Protocol Buffers v3
    - Throughput target: 500,000 events/second sustained
    - Backpressure mechanism: Token bucket with adaptive rate limiting
    - Serialization: Protobuf for internal, JSON for external APIs
    - Compression: LZ4 for wire format, Zstandard for storage

    2.2 Stream Processing Engine
    - Framework: Apache Flink 1.18 with RocksDB state backend
    - Windowing: Tumbling windows (1min), Sliding windows (5min/1min)
    - Checkpointing: Incremental, every 30 seconds, to S3-compatible storage
    - Exactly-once semantics via two-phase commit with Kafka transactions

    2.3 Enrichment Service
    - Lookup tables: Redis Cluster (6 nodes, 192GB total)
    - Geo-IP resolution: MaxMind GeoIP2 database, refreshed daily
    - User profile cache: 50M entries, LRU eviction, 15-minute TTL
    - Feature flags: LaunchDarkly integration with local fallback cache

    2.4 Output Routing
    - Primary sink: Apache Kafka (3 brokers, replication factor 3)
    - Secondary sink: Amazon Kinesis Data Firehose to S3 (Parquet format)
    - Dead letter queue: Separate Kafka topic with 7-day retention
    - Real-time dashboards: WebSocket fan-out via NATS JetStream

    3. DATA MODEL
    -------------
    Each event conforms to the CloudEvents v1.0 specification with extensions:

    {
      "specversion": "1.0",
      "type": "com.platform.user.action",
      "source": "/services/web-app",
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "time": "2025-05-20T14:30:00.000Z",
      "datacontenttype": "application/json",
      "data": {
        "user_id": "usr_abc123",
        "action": "purchase",
        "amount_cents": 4999,
        "currency": "USD",
        "item_ids": ["item_001", "item_002"],
        "session_id": "sess_xyz789",
        "device": {
          "type": "mobile",
          "os": "iOS 17.4",
          "app_version": "3.2.1"
        }
      },
      "extensions": {
        "tenant_id": "tenant_acme",
        "region": "us-east-1",
        "priority": "high",
        "trace_id": "trace_123456"
      }
    }

    4. PERFORMANCE REQUIREMENTS
    --------------------------
    | Metric                    | Target           | SLA    |
    |--------------------------|------------------|--------|
    | End-to-end latency (p50) | < 100ms          | 99.9%  |
    | End-to-end latency (p99) | < 500ms          | 99.5%  |
    | Throughput                | 500K events/sec  | 99.9%  |
    | Data loss                | 0 events         | 99.99% |
    | Availability             | 99.95%           | -      |
    | Recovery time            | < 5 minutes      | 99%    |

    5. FAILURE MODES AND RECOVERY
    -----------------------------
    5.1 Kafka Broker Failure
    - Detection: Health check failure after 3 consecutive missed heartbeats
    - Response: Automatic partition reassignment via controller
    - Recovery: ISR catch-up, typically < 30 seconds

    5.2 Flink JobManager Failure
    - Detection: ZooKeeper session timeout (30s default)
    - Response: Standby JobManager promotion
    - Recovery: Checkpoint restore, < 2 minutes

    5.3 Network Partition
    - Detection: Cross-AZ health check failures
    - Response: Graceful degradation to single-AZ operation
    - Recovery: Automatic reconciliation on partition heal

    6. MONITORING AND ALERTING
    --------------------------
    Metrics exported via Prometheus with the following key dashboards:
    - Pipeline throughput and latency (Grafana dashboard ID: 1001)
    - Consumer lag per partition (Grafana dashboard ID: 1002)
    - Error rates by type and source (Grafana dashboard ID: 1003)
    - Resource utilization (CPU, memory, disk I/O) (Grafana dashboard ID: 1004)

    Alert thresholds:
    - CRITICAL: Consumer lag > 100,000 messages for > 5 minutes
    - WARNING: p99 latency > 400ms for > 2 minutes
    - CRITICAL: Error rate > 1% for > 1 minute
    - WARNING: Disk usage > 80% on any broker

    7. SECURITY CONSIDERATIONS
    --------------------------
    - All inter-service communication encrypted via mTLS (cert rotation: 90 days)
    - PII fields encrypted at rest using AES-256-GCM with per-tenant keys
    - Access control: RBAC with tenant isolation enforced at Kafka ACL level
    - Audit logging: All administrative actions logged to immutable audit trail
    - Data retention: Configurable per tenant, default 90 days, max 7 years

    8. DEPLOYMENT
    -------------
    - Infrastructure: Kubernetes 1.28 on AWS EKS
    - CI/CD: GitHub Actions with ArgoCD for GitOps deployment
    - Environments: dev → staging → canary (5%) → production
    - Rollback: Automatic on error rate spike, manual approval for > 25% traffic
    """))

# ---------------------------------------------------------------------------
# 3. Large report with financial data
# ---------------------------------------------------------------------------
with open(f"{OUT}/financial_report.txt", "w") as f:
    f.write("ANNUAL FINANCIAL REPORT - FY2025\n")
    f.write("=" * 60 + "\n\n")
    f.write("EXECUTIVE SUMMARY\n")
    f.write("-" * 40 + "\n")
    f.write(textwrap.dedent("""\
    Total Revenue: $847.3M (+12.4% YoY)
    Gross Profit: $612.8M (72.3% margin)
    Operating Income: $198.4M (23.4% margin)
    Net Income: $156.2M (18.4% margin)
    Free Cash Flow: $203.7M
    Employees: 4,847 (+18% YoY)

    The fiscal year 2025 represented a period of significant growth and strategic
    transformation for the company. Revenue grew 12.4% year-over-year, driven
    primarily by strong adoption of our enterprise platform and expansion into
    new geographic markets. Operating margins improved by 2.1 percentage points
    as we realized economies of scale in our cloud infrastructure.

    REVENUE BREAKDOWN BY SEGMENT
    """))

    segments = [
        ("Enterprise Platform", 412.5, 38.2, 15.3),
        ("Cloud Services", 198.7, 23.4, 22.1),
        ("Professional Services", 89.4, 10.5, 3.2),
        ("Data Analytics", 78.2, 9.2, 28.7),
        ("Security Solutions", 45.8, 5.4, 41.3),
        ("Developer Tools", 22.7, 2.7, 18.9),
    ]
    f.write(f"{'Segment':<25} {'Revenue ($M)':>12} {'Margin (%)':>12} {'Growth (%)':>12}\n")
    f.write("-" * 65 + "\n")
    for name, rev, margin, growth in segments:
        f.write(f"{name:<25} {rev:>12.1f} {margin:>12.1f} {growth:>12.1f}\n")
    f.write("\n")

    f.write("\nQUARTERLY PERFORMANCE\n")
    f.write("-" * 40 + "\n")
    quarters = [
        ("Q1 FY2025", 189.2, 43.8, 135.6, 31.4),
        ("Q2 FY2025", 205.4, 47.5, 148.2, 34.3),
        ("Q3 FY2025", 218.7, 50.6, 158.1, 36.6),
        ("Q4 FY2025", 234.0, 54.2, 170.9, 39.5),
    ]
    f.write(f"{'Quarter':<12} {'Revenue':>10} {'OpEx':>10} {'Gross':>10} {'EBITDA':>10}\n")
    f.write("-" * 55 + "\n")
    for q, rev, opex, gross, ebitda in quarters:
        f.write(f"{q:<12} {rev:>10.1f} {opex:>10.1f} {gross:>10.1f} {ebitda:>10.1f}\n")
    f.write("\n")

    f.write("\nGEOGRAPHIC DISTRIBUTION\n")
    f.write("-" * 40 + "\n")
    regions = [
        ("North America", 508.4, 60.0),
        ("Europe", 186.4, 22.0),
        ("Asia Pacific", 101.7, 12.0),
        ("Latin America", 33.9, 4.0),
        ("Middle East & Africa", 16.9, 2.0),
    ]
    for name, rev, pct in regions:
        f.write(f"  {name:<25} ${rev:>7.1f}M  ({pct:.0f}%)\n")
    f.write("\n")

    f.write("\nKEY METRICS AND KPIs\n")
    f.write("-" * 40 + "\n")
    metrics = [
        ("Annual Recurring Revenue (ARR)", "$782.1M"),
        ("Net Revenue Retention", "118%"),
        ("Customer Acquisition Cost (CAC)", "$12,400"),
        ("Lifetime Value (LTV)", "$187,000"),
        ("LTV:CAC Ratio", "15.1x"),
        ("Gross Dollar Retention", "95.2%"),
        ("Monthly Active Users", "2.3M"),
        ("Enterprise Customers (>$100K ARR)", "847"),
        ("Average Contract Value", "$148,000"),
        ("Sales Cycle (days, median)", "67"),
        ("Customer Satisfaction (NPS)", "72"),
        ("Employee NPS (eNPS)", "61"),
    ]
    for name, val in metrics:
        f.write(f"  {name:<40} {val}\n")

    f.write("\n\nRISK FACTORS\n")
    f.write("-" * 40 + "\n")
    risks = [
        "Increasing competition from well-funded startups and established tech companies",
        "Regulatory changes in data privacy (GDPR, CCPA, emerging AI regulations)",
        "Macroeconomic uncertainty affecting enterprise IT spending decisions",
        "Talent acquisition and retention in competitive labor markets",
        "Cybersecurity threats and potential data breach liabilities",
        "Foreign exchange fluctuations impacting international revenue",
        "Concentration risk: top 10 customers represent 23% of ARR",
        "Technology platform risk: dependency on major cloud providers",
        "Integration risks from recent acquisitions",
        "Potential supply chain disruptions affecting hardware procurement",
    ]
    for i, risk in enumerate(risks, 1):
        f.write(f"  {i}. {risk}\n")

# ---------------------------------------------------------------------------
# 4. CSV - Sales data (medium)
# ---------------------------------------------------------------------------
random.seed(42)
products = ["Widget Pro", "DataSync Enterprise", "CloudGuard", "APIBridge", "StreamKit",
            "MetricsDash", "LogVault", "AuthShield", "QueryEngine", "PipelineBuilder"]
regions_csv = ["US-East", "US-West", "EU-West", "EU-Central", "APAC-East",
               "APAC-South", "LATAM", "MEA", "Canada", "ANZ"]
channels = ["Direct", "Partner", "Online", "Reseller", "OEM"]

with open(f"{OUT}/sales_data.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Date", "Product", "Region", "Channel", "Units", "Revenue_USD",
                "Discount_Pct", "Customer_Segment", "Deal_Size", "Rep_ID"])
    for i in range(500):
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        units = random.randint(1, 200)
        price = random.uniform(50, 5000)
        discount = random.choice([0, 5, 10, 15, 20, 25])
        seg = random.choice(["SMB", "Mid-Market", "Enterprise", "Strategic"])
        size = random.choice(["Small", "Medium", "Large", "Mega"])
        w.writerow([
            f"2025-{month:02d}-{day:02d}",
            random.choice(products),
            random.choice(regions_csv),
            random.choice(channels),
            units,
            round(units * price * (1 - discount / 100), 2),
            discount,
            seg,
            size,
            f"REP-{random.randint(100, 999)}"
        ])

# ---------------------------------------------------------------------------
# 5. CSV - Large metrics dataset
# ---------------------------------------------------------------------------
with open(f"{OUT}/system_metrics.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Timestamp", "Host", "CPU_Pct", "Memory_MB", "Disk_IO_MBps",
                "Network_In_Mbps", "Network_Out_Mbps", "Request_Count",
                "Error_Count", "Latency_p50_ms", "Latency_p99_ms", "Status"])
    hosts = [f"prod-app-{i:02d}" for i in range(1, 21)]
    for hour in range(24):
        for minute in range(0, 60, 5):
            for host in hosts:
                cpu = random.gauss(45, 15)
                mem = random.gauss(8192, 2048)
                w.writerow([
                    f"2025-06-15T{hour:02d}:{minute:02d}:00Z",
                    host,
                    round(max(0, min(100, cpu)), 1),
                    round(max(512, mem)),
                    round(random.uniform(10, 500), 1),
                    round(random.uniform(50, 2000), 1),
                    round(random.uniform(20, 800), 1),
                    random.randint(100, 50000),
                    random.randint(0, 50),
                    round(random.uniform(5, 100), 1),
                    round(random.uniform(50, 2000), 1),
                    random.choice(["healthy", "healthy", "healthy", "degraded", "critical"]),
                ])

# ---------------------------------------------------------------------------
# 6. HTML - Product documentation page
# ---------------------------------------------------------------------------
with open(f"{OUT}/product_docs.html", "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>StreamKit API Documentation v3.2</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
        pre { background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 8px; overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; margin: 16px 0; }
        th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
        th { background: #f8f9fa; }
        .endpoint { background: #e8f5e9; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .method { display: inline-block; padding: 2px 8px; border-radius: 4px; color: white; font-size: 12px; }
        .get { background: #4caf50; } .post { background: #2196f3; } .put { background: #ff9800; } .delete { background: #f44336; }
    </style>
</head>
<body>
    <h1>StreamKit API Documentation</h1>
    <p>Version 3.2 | Last Updated: 2025-06-01</p>

    <h2>Authentication</h2>
    <p>All API requests require authentication via Bearer token in the <code>Authorization</code> header.</p>
    <pre>Authorization: Bearer sk_live_abc123def456...</pre>
    <p>Tokens can be generated from the <a href="#">Dashboard → Settings → API Keys</a> page.</p>

    <h3>Rate Limits</h3>
    <table>
        <tr><th>Plan</th><th>Requests/min</th><th>Burst</th><th>Concurrent Streams</th></tr>
        <tr><td>Free</td><td>60</td><td>10</td><td>2</td></tr>
        <tr><td>Pro</td><td>600</td><td>100</td><td>10</td></tr>
        <tr><td>Enterprise</td><td>6,000</td><td>1,000</td><td>100</td></tr>
        <tr><td>Custom</td><td>Unlimited</td><td>Custom</td><td>Custom</td></tr>
    </table>

    <h2>Endpoints</h2>

    <h3><span class="method post">POST</span> /v3/streams</h3>
    <p>Create a new data stream.</p>
    <h4>Request Body</h4>
    <pre>{
  "name": "user-events",
  "schema": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string"},
      "event": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "metadata": {"type": "object"}
    },
    "required": ["user_id", "event", "timestamp"]
  },
  "retention_days": 30,
  "partitions": 8,
  "replication_factor": 3,
  "compression": "zstd"
}</pre>
    <h4>Response (201 Created)</h4>
    <pre>{
  "id": "strm_abc123",
  "name": "user-events",
  "status": "provisioning",
  "created_at": "2025-06-01T10:00:00Z",
  "endpoint": "wss://streams.example.com/v3/strm_abc123"
}</pre>

    <h3><span class="method get">GET</span> /v3/streams</h3>
    <p>List all streams for the authenticated account.</p>
    <h4>Query Parameters</h4>
    <table>
        <tr><th>Parameter</th><th>Type</th><th>Default</th><th>Description</th></tr>
        <tr><td><code>limit</code></td><td>integer</td><td>20</td><td>Max results per page (1-100)</td></tr>
        <tr><td><code>offset</code></td><td>integer</td><td>0</td><td>Pagination offset</td></tr>
        <tr><td><code>status</code></td><td>string</td><td>all</td><td>Filter: active, paused, error</td></tr>
        <tr><td><code>sort</code></td><td>string</td><td>created_at</td><td>Sort field</td></tr>
        <tr><td><code>order</code></td><td>string</td><td>desc</td><td>Sort order: asc, desc</td></tr>
    </table>

    <h3><span class="method get">GET</span> /v3/streams/{stream_id}</h3>
    <p>Get details for a specific stream.</p>

    <h3><span class="method put">PUT</span> /v3/streams/{stream_id}</h3>
    <p>Update stream configuration. Only <code>retention_days</code>, <code>partitions</code> (increase only), and <code>compression</code> can be modified.</p>

    <h3><span class="method delete">DELETE</span> /v3/streams/{stream_id}</h3>
    <p>Delete a stream. This action is irreversible. All data will be permanently deleted after a 24-hour grace period.</p>

    <h3><span class="method post">POST</span> /v3/streams/{stream_id}/publish</h3>
    <p>Publish events to a stream. Supports batch publishing up to 1,000 events per request.</p>
    <pre>{
  "events": [
    {
      "key": "user_123",
      "data": {"user_id": "user_123", "event": "page_view", "timestamp": "2025-06-01T10:05:00Z"},
      "headers": {"source": "web-app", "version": "2.1"}
    }
  ]
}</pre>

    <h3><span class="method post">POST</span> /v3/streams/{stream_id}/query</h3>
    <p>Query stream data with SQL-like syntax.</p>
    <pre>{
  "query": "SELECT user_id, COUNT(*) as event_count FROM stream WHERE timestamp > NOW() - INTERVAL '1 hour' GROUP BY user_id ORDER BY event_count DESC LIMIT 10",
  "format": "json"
}</pre>

    <h2>Webhooks</h2>
    <p>Configure webhooks to receive real-time notifications for stream events.</p>
    <table>
        <tr><th>Event Type</th><th>Description</th><th>Payload</th></tr>
        <tr><td><code>stream.created</code></td><td>New stream provisioned</td><td>Stream object</td></tr>
        <tr><td><code>stream.error</code></td><td>Stream processing error</td><td>Error details + stream ID</td></tr>
        <tr><td><code>stream.threshold</code></td><td>Volume threshold crossed</td><td>Metric + threshold value</td></tr>
        <tr><td><code>stream.deleted</code></td><td>Stream deletion completed</td><td>Stream ID + deletion time</td></tr>
        <tr><td><code>consumer.lag</code></td><td>Consumer group lag alert</td><td>Group + lag metrics</td></tr>
    </table>

    <h2>Error Codes</h2>
    <table>
        <tr><th>Code</th><th>HTTP Status</th><th>Description</th><th>Resolution</th></tr>
        <tr><td>STREAM_NOT_FOUND</td><td>404</td><td>Stream does not exist</td><td>Check stream ID</td></tr>
        <tr><td>RATE_LIMITED</td><td>429</td><td>Too many requests</td><td>Implement backoff</td></tr>
        <tr><td>SCHEMA_VIOLATION</td><td>400</td><td>Event doesn't match schema</td><td>Validate event data</td></tr>
        <tr><td>QUOTA_EXCEEDED</td><td>402</td><td>Plan quota exceeded</td><td>Upgrade plan</td></tr>
        <tr><td>INTERNAL_ERROR</td><td>500</td><td>Server error</td><td>Retry with backoff</td></tr>
        <tr><td>STREAM_PAUSED</td><td>409</td><td>Stream is paused</td><td>Resume stream first</td></tr>
        <tr><td>BATCH_TOO_LARGE</td><td>413</td><td>Batch exceeds 1000 events</td><td>Split into smaller batches</td></tr>
        <tr><td>INVALID_QUERY</td><td>400</td><td>SQL syntax error</td><td>Check query syntax</td></tr>
    </table>

    <h2>SDKs</h2>
    <ul>
        <li><strong>Python</strong>: <code>pip install streamkit</code></li>
        <li><strong>Node.js</strong>: <code>npm install @streamkit/sdk</code></li>
        <li><strong>Go</strong>: <code>go get github.com/streamkit/sdk-go</code></li>
        <li><strong>Java</strong>: Maven artifact <code>com.streamkit:sdk:3.2.0</code></li>
        <li><strong>Rust</strong>: <code>cargo add streamkit</code></li>
    </ul>
</body>
</html>""")

# ---------------------------------------------------------------------------
# 7. HTML - Complex dashboard report
# ---------------------------------------------------------------------------
with open(f"{OUT}/dashboard_report.html", "w") as f:
    f.write("""<!DOCTYPE html>
<html><head><title>Q2 2025 Operations Dashboard</title></head><body>
<h1>Operations Dashboard - Q2 2025</h1>
<h2>Infrastructure Summary</h2>
<table border="1">
<tr><th>Service</th><th>Instances</th><th>CPU Avg</th><th>Memory Avg</th><th>Uptime</th><th>Incidents</th><th>MTTR</th></tr>
""")
    services = [
        ("API Gateway", 12, 34.2, 67.8, 99.99, 1, "4m"),
        ("Auth Service", 6, 22.1, 45.3, 99.98, 2, "8m"),
        ("User Service", 8, 41.7, 72.1, 99.97, 3, "12m"),
        ("Payment Engine", 4, 28.9, 58.4, 99.999, 0, "0m"),
        ("Notification Hub", 6, 38.4, 61.2, 99.95, 4, "15m"),
        ("Search Cluster", 10, 56.3, 81.7, 99.96, 2, "6m"),
        ("ML Inference", 8, 78.2, 89.3, 99.90, 5, "22m"),
        ("CDN Edge", 24, 15.8, 32.1, 99.999, 0, "0m"),
        ("Message Queue", 6, 42.1, 55.8, 99.98, 1, "3m"),
        ("Analytics Pipeline", 4, 67.4, 76.9, 99.94, 3, "18m"),
    ]
    for svc in services:
        f.write(f"<tr><td>{svc[0]}</td><td>{svc[1]}</td><td>{svc[2]}%</td><td>{svc[3]}%</td><td>{svc[4]}%</td><td>{svc[5]}</td><td>{svc[6]}</td></tr>\n")
    f.write("</table>\n")

    f.write("<h2>Incident Log</h2><table border='1'>\n")
    f.write("<tr><th>ID</th><th>Date</th><th>Severity</th><th>Service</th><th>Description</th><th>Duration</th><th>Root Cause</th></tr>\n")
    incidents = [
        ("INC-2401", "2025-04-03", "P1", "ML Inference", "Model serving latency spike >5s p99", "47m", "GPU memory leak in TensorRT engine"),
        ("INC-2402", "2025-04-08", "P2", "Auth Service", "Token validation failures for SSO users", "23m", "Certificate rotation script missed edge case"),
        ("INC-2403", "2025-04-15", "P3", "Notification Hub", "Email delivery delays >30min", "2h 15m", "Upstream SMTP provider throttling"),
        ("INC-2404", "2025-04-22", "P2", "Search Cluster", "Index corruption after rebalance", "1h 4m", "Race condition in shard allocation"),
        ("INC-2405", "2025-05-01", "P1", "API Gateway", "502 errors on /v3/streams endpoints", "4m", "Misconfigured upstream timeout after deploy"),
        ("INC-2406", "2025-05-10", "P3", "Analytics Pipeline", "Stale data in real-time dashboard", "3h", "Checkpoint lag due to GC pressure"),
        ("INC-2407", "2025-05-18", "P2", "User Service", "Profile updates returning 500", "12m", "Database connection pool exhaustion"),
        ("INC-2408", "2025-05-25", "P3", "Notification Hub", "Push notification duplicates", "45m", "Idempotency key collision in queue consumer"),
        ("INC-2409", "2025-06-02", "P2", "ML Inference", "Incorrect model version served", "35m", "Blue-green deployment rollback incomplete"),
        ("INC-2410", "2025-06-10", "P1", "Message Queue", "Consumer group rebalance storm", "3m", "Session timeout too aggressive after scaling event"),
    ]
    for inc in incidents:
        f.write(f"<tr><td>{inc[0]}</td><td>{inc[1]}</td><td>{inc[2]}</td><td>{inc[3]}</td><td>{inc[4]}</td><td>{inc[5]}</td><td>{inc[6]}</td></tr>\n")
    f.write("</table>\n")
    f.write("</body></html>")

# ---------------------------------------------------------------------------
# 8. Text - Legal contract
# ---------------------------------------------------------------------------
with open(f"{OUT}/legal_contract.txt", "w") as f:
    f.write(textwrap.dedent("""\
    MASTER SERVICES AGREEMENT

    This Master Services Agreement ("Agreement") is entered into as of January 15, 2025
    ("Effective Date") by and between:

    SERVICE PROVIDER: TechCorp Solutions, Inc., a Delaware corporation with principal
    offices at 500 Innovation Drive, Suite 300, San Francisco, CA 94105 ("Provider")

    CLIENT: GlobalRetail Holdings, LLC, a New York limited liability company with
    principal offices at 200 Commerce Street, New York, NY 10004 ("Client")

    RECITALS

    WHEREAS, Provider is in the business of providing cloud-based software solutions,
    data analytics, and professional services; and

    WHEREAS, Client desires to engage Provider to provide certain services as described
    in one or more Statements of Work to be executed hereunder;

    NOW, THEREFORE, in consideration of the mutual covenants and agreements set forth
    herein, and for other good and valuable consideration, the receipt and sufficiency
    of which are hereby acknowledged, the parties agree as follows:

    ARTICLE 1: DEFINITIONS

    1.1 "Confidential Information" means any information disclosed by either party to
    the other party, either directly or indirectly, in writing, orally, or by inspection
    of tangible objects, that is designated as "Confidential," "Proprietary," or some
    similar designation, or that reasonably should be understood to be confidential
    given the nature of the information and circumstances of disclosure.

    1.2 "Deliverables" means all documents, work product, and other materials that are
    delivered to Client under a Statement of Work or otherwise created by Provider in
    connection with the Services.

    1.3 "Intellectual Property Rights" means all patent rights, copyright rights, mask
    work rights, moral rights, rights of publicity, trademark, trade dress and service
    mark rights, goodwill, trade secret rights, and other intellectual property rights
    as may now exist or hereafter come into existence.

    1.4 "Services" means the professional services, consulting, development, and support
    services to be performed by Provider pursuant to one or more Statements of Work.

    1.5 "Statement of Work" or "SOW" means a document executed by both parties that
    describes the specific Services to be performed, the Deliverables, timeline,
    milestones, and fees associated with such Services.

    ARTICLE 2: SERVICES AND DELIVERABLES

    2.1 Scope of Services. Provider shall perform the Services described in each SOW
    in accordance with the terms and conditions of this Agreement. Each SOW shall be
    deemed incorporated into and made a part of this Agreement.

    2.2 Standard of Performance. Provider shall perform the Services in a professional
    and workmanlike manner, consistent with generally accepted industry standards and
    practices. Provider shall assign qualified personnel with appropriate skills and
    experience to perform the Services.

    2.3 Change Orders. Any changes to the scope of Services described in a SOW shall
    require a written change order signed by authorized representatives of both parties.
    Provider shall not be obligated to perform any Services outside the scope of an
    existing SOW without an executed change order.

    ARTICLE 3: FEES AND PAYMENT

    3.1 Fees. Client shall pay Provider the fees set forth in each SOW. Unless otherwise
    specified in the applicable SOW, all fees shall be quoted in United States Dollars.

    3.2 Invoicing. Provider shall invoice Client monthly in arrears for Services
    performed during the preceding month. Each invoice shall include reasonable detail
    of the Services performed and hours worked.

    3.3 Payment Terms. Client shall pay all undisputed invoices within thirty (30) days
    of receipt. Late payments shall bear interest at the rate of 1.5% per month or the
    maximum rate permitted by law, whichever is less.

    3.4 Expenses. Client shall reimburse Provider for reasonable, pre-approved
    out-of-pocket expenses incurred in connection with the performance of Services,
    including but not limited to travel, lodging, and meals, in accordance with
    Client's travel and expense policy.

    3.5 Taxes. All fees are exclusive of taxes. Client shall be responsible for all
    sales, use, and excise taxes, and any other similar taxes, duties, and charges of
    any kind imposed by any governmental entity on any amounts payable by Client
    hereunder, other than taxes imposed on Provider's income.

    ARTICLE 4: INTELLECTUAL PROPERTY

    4.1 Pre-Existing IP. Each party shall retain all rights in its pre-existing
    intellectual property. "Pre-Existing IP" means any intellectual property owned
    or controlled by a party prior to the Effective Date or developed by a party
    outside the scope of this Agreement.

    4.2 Work Product. Subject to Section 4.1, all Deliverables created by Provider
    specifically for Client under a SOW shall be considered "Work Product." Upon full
    payment of all applicable fees, Provider hereby assigns to Client all right, title,
    and interest in and to the Work Product, including all Intellectual Property Rights.

    4.3 License to Pre-Existing IP. To the extent any Deliverable incorporates
    Provider's Pre-Existing IP, Provider hereby grants Client a non-exclusive,
    worldwide, perpetual, irrevocable, fully paid-up license to use, reproduce, modify,
    and distribute such Pre-Existing IP solely as incorporated in the Deliverables.

    ARTICLE 5: CONFIDENTIALITY

    5.1 Obligations. Each party agrees to: (a) hold the other party's Confidential
    Information in strict confidence; (b) not disclose such Confidential Information to
    any third parties except as expressly permitted herein; and (c) use such Confidential
    Information only for the purposes of this Agreement.

    5.2 Exceptions. Confidential Information shall not include information that: (a) is
    or becomes publicly available through no fault of the receiving party; (b) was
    rightfully in the receiving party's possession prior to disclosure; (c) is rightfully
    obtained by the receiving party from a third party without restriction; or (d) is
    independently developed by the receiving party without use of the disclosing party's
    Confidential Information.

    5.3 Duration. The obligations of confidentiality shall survive the termination or
    expiration of this Agreement for a period of five (5) years.

    ARTICLE 6: TERM AND TERMINATION

    6.1 Term. This Agreement shall commence on the Effective Date and continue for an
    initial term of three (3) years, unless earlier terminated as provided herein. The
    Agreement shall automatically renew for successive one (1) year periods unless
    either party provides written notice of non-renewal at least ninety (90) days prior
    to the end of the then-current term.

    6.2 Termination for Convenience. Either party may terminate this Agreement or any
    SOW for convenience upon sixty (60) days' prior written notice to the other party.

    6.3 Termination for Cause. Either party may terminate this Agreement immediately
    upon written notice if the other party: (a) materially breaches this Agreement and
    fails to cure such breach within thirty (30) days of receiving written notice; or
    (b) becomes insolvent, files for bankruptcy, or ceases to conduct business.

    ARTICLE 7: LIMITATION OF LIABILITY

    7.1 NEITHER PARTY SHALL BE LIABLE TO THE OTHER PARTY FOR ANY INDIRECT, INCIDENTAL,
    SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF OR RELATED TO THIS
    AGREEMENT, REGARDLESS OF THE FORM OF ACTION OR THE THEORY OF LIABILITY, EVEN IF
    SUCH PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

    7.2 EXCEPT FOR BREACHES OF CONFIDENTIALITY OBLIGATIONS OR INDEMNIFICATION
    OBLIGATIONS, THE TOTAL CUMULATIVE LIABILITY OF EITHER PARTY UNDER THIS AGREEMENT
    SHALL NOT EXCEED THE TOTAL FEES PAID OR PAYABLE BY CLIENT UNDER THIS AGREEMENT
    DURING THE TWELVE (12) MONTH PERIOD PRECEDING THE EVENT GIVING RISE TO LIABILITY.

    IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.
    """))

# ---------------------------------------------------------------------------
# 9. CSV - Customer support tickets
# ---------------------------------------------------------------------------
with open(f"{OUT}/support_tickets.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Ticket_ID", "Created", "Priority", "Category", "Subject",
                "Customer_Tier", "Assigned_Team", "Status", "Resolution_Hours", "CSAT"])
    categories = ["Bug", "Feature Request", "Integration", "Billing", "Performance",
                  "Security", "Documentation", "Onboarding", "Data Issue", "Access"]
    subjects = [
        "API returning 500 on batch publish", "Need webhook retry configuration",
        "SSO integration with Okta failing", "Invoice discrepancy for May",
        "Dashboard loading slowly with large datasets", "Concerned about data encryption at rest",
        "Outdated SDK examples in docs", "Need help with initial setup",
        "Missing records in analytics export", "Cannot add team member to workspace",
        "gRPC client connection timeout", "Request: custom retention policies",
        "Salesforce connector not syncing", "Double charge on credit card",
        "Query execution timeout on complex joins", "Audit log access request",
        "Python SDK version compatibility", "Migration from v2 to v3 guidance",
        "Data showing incorrect timezone", "API key rotation not working",
    ]
    teams = ["Tier-1 Support", "Tier-2 Engineering", "Billing", "Security", "Solutions Architect"]
    statuses = ["Open", "In Progress", "Waiting on Customer", "Resolved", "Closed"]
    for i in range(200):
        month = random.randint(1, 6)
        day = random.randint(1, 28)
        priority = random.choice(["P1", "P2", "P2", "P3", "P3", "P3", "P4"])
        status = random.choice(statuses)
        res_hours = round(random.uniform(0.5, 72), 1) if status in ("Resolved", "Closed") else ""
        csat = random.randint(1, 5) if status in ("Resolved", "Closed") else ""
        w.writerow([
            f"TKT-{10000 + i}",
            f"2025-{month:02d}-{day:02d}",
            priority,
            random.choice(categories),
            random.choice(subjects),
            random.choice(["Free", "Pro", "Enterprise", "Strategic"]),
            random.choice(teams),
            status,
            res_hours,
            csat,
        ])

# ---------------------------------------------------------------------------
# 10. Text - Research paper abstract collection
# ---------------------------------------------------------------------------
with open(f"{OUT}/research_abstracts.txt", "w") as f:
    f.write("SELECTED ABSTRACTS: ADVANCES IN MACHINE LEARNING SYSTEMS (2025)\n")
    f.write("=" * 70 + "\n\n")
    abstracts = [
        ("Efficient Attention Mechanisms for Long-Context Language Models",
         "We present FlashAttention-3, a hardware-aware attention algorithm that achieves 2.3x speedup over FlashAttention-2 on H100 GPUs. By exploiting the asynchronous execution capabilities of the Hopper architecture, including warp-specialized pipelining and FP8 tensor cores, we demonstrate sustained throughput of 740 TFLOPS for sequence lengths up to 256K tokens. Our approach reduces memory usage by 40% compared to standard attention while maintaining numerical precision within 0.01% of exact attention. We validate on GPT-4 scale models across language modeling, code generation, and multi-document summarization tasks."),
        ("Scaling Laws for Mixture-of-Experts Models",
         "We investigate the scaling behavior of Sparse Mixture-of-Experts (MoE) language models across 3 orders of magnitude (1B to 1T total parameters). Our analysis reveals that MoE models follow modified Chinchilla scaling laws with an effective parameter count of approximately 0.3x total parameters for 8-expert top-2 routing. We identify critical load balancing thresholds below which training becomes unstable, and propose Adaptive Expert Allocation (AEA), a dynamic routing strategy that reduces expert collapse probability by 85%. Models trained with AEA achieve equivalent quality to dense models at 2.7x lower compute cost."),
        ("Constitutional AI: Aligning Language Models through Self-Improvement",
         "We introduce Constitutional AI v2 (CAI-v2), an alignment framework where language models iteratively refine their own behavior using a set of written principles. Unlike RLHF, CAI-v2 requires no human preference labels during the alignment phase. We demonstrate that CAI-v2-aligned models score 12% higher on harmlessness benchmarks while maintaining 98.5% of helpfulness compared to RLHF-aligned baselines. The method scales efficiently to multi-turn conversations and domain-specific applications. We release our constitutional principles and alignment methodology for reproducibility."),
        ("Speculative Decoding with Learned Draft Models",
         "We propose SpecDraft, a framework for training lightweight draft models specifically optimized for speculative decoding with large language models. Unlike prior work using smaller pre-trained models as drafts, SpecDraft models are trained with a novel acceptance-rate-aware objective that maximizes the expected tokens accepted per draft step. Our 150M parameter SpecDraft model achieves 3.8x speedup when paired with a 70B target model, compared to 2.1x for Medusa and 2.5x for standard speculative decoding. We further introduce multi-sequence speculative decoding for batch inference scenarios."),
        ("Retrieval-Augmented Generation at Scale: Lessons from Production",
         "We present architectural insights from deploying RAG systems serving 50M+ daily queries across enterprise search, customer support, and code assistance applications. We identify five critical failure modes: retrieval drift (23% of failures), chunk boundary artifacts (18%), embedding space gaps (15%), context window overflow (12%), and citation hallucination (8%). We introduce Adaptive RAG, a production framework incorporating query-aware chunking, hierarchical retrieval with re-ranking, and grounded generation with provenance tracking. Adaptive RAG reduces hallucination rates by 67% and improves answer accuracy by 34% compared to naive RAG implementations."),
        ("Efficient Fine-Tuning with Quantized Low-Rank Adaptation",
         "We introduce QLoRA-2, an improved parameter-efficient fine-tuning method that combines 4-bit NormalFloat quantization with rank-adaptive LoRA decomposition. QLoRA-2 automatically determines optimal rank allocation per layer using a gradient-based importance score, resulting in 15-30% fewer trainable parameters than fixed-rank LoRA with equivalent or superior task performance. We demonstrate fine-tuning of 70B parameter models on a single 24GB GPU with training throughput of 1,200 tokens/second. Extensive evaluation across 15 benchmarks shows QLoRA-2 closes the gap to full fine-tuning to within 0.3% on average."),
        ("Multimodal Foundation Models: Unifying Vision, Language, and Action",
         "We present Unified-3, a 120B parameter multimodal foundation model trained on 15T tokens spanning text, images, video, audio, and robotic action trajectories. Unified-3 achieves state-of-the-art results on 28 of 32 evaluated benchmarks, including MMLU (91.2%), VQA-v2 (84.7%), VideoQA (78.3%), and Language-Table (93.1% success rate). Key architectural innovations include cross-modal attention routing, temporal-aware position embeddings, and a unified tokenizer handling continuous and discrete modalities. We demonstrate emergent cross-modal reasoning capabilities not present in single-modality or dual-modality models."),
        ("Watermarking Language Model Outputs for AI-Generated Text Detection",
         "We propose Semstamp, a semantic watermarking scheme that embeds statistically detectable signals in LLM outputs without degrading text quality. Unlike token-level watermarks, Semstamp operates on semantic sentence embeddings, making it robust to paraphrasing attacks (92% detection rate after paraphrasing vs. 34% for prior methods). The watermark is imperceptible: human evaluators prefer watermarked text over unwatermarked text 49.8% of the time (statistically indistinguishable). We provide formal security guarantees and analyze the information-theoretic capacity of semantic watermarking channels."),
    ]
    for i, (title, abstract) in enumerate(abstracts, 1):
        f.write(f"[{i}] {title}\n")
        f.write("-" * len(title) + "\n")
        f.write(f"{abstract}\n\n")

# ---------------------------------------------------------------------------
# 11. HTML - Employee directory
# ---------------------------------------------------------------------------
with open(f"{OUT}/employee_directory.html", "w") as f:
    f.write("<html><head><title>Employee Directory</title></head><body>\n")
    f.write("<h1>Company Employee Directory - 2025</h1>\n")
    f.write("<table border='1'><tr><th>ID</th><th>Name</th><th>Department</th><th>Title</th><th>Location</th><th>Email</th><th>Start Date</th><th>Level</th></tr>\n")
    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
                   "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                   "Thomas", "Sarah", "Christopher", "Karen", "Wei", "Priya", "Ahmed", "Yuki",
                   "Carlos", "Fatima", "Dmitri", "Aisha", "Kenji", "Mei"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Chen", "Kumar", "Patel", "Kim", "Nguyen", "Tanaka",
                  "Mueller", "Johansson", "Santos", "Ali"]
    departments = ["Engineering", "Product", "Design", "Marketing", "Sales", "Finance",
                   "HR", "Legal", "Operations", "Data Science", "Security", "DevOps"]
    titles_map = {
        "Engineering": ["Software Engineer", "Senior Software Engineer", "Staff Engineer", "Principal Engineer", "Engineering Manager"],
        "Product": ["Product Manager", "Senior PM", "Group PM", "VP Product"],
        "Design": ["UX Designer", "Senior Designer", "Design Lead", "Head of Design"],
        "Marketing": ["Marketing Manager", "Content Strategist", "Growth Lead", "CMO"],
        "Sales": ["Account Executive", "Senior AE", "Sales Director", "VP Sales"],
        "Finance": ["Financial Analyst", "Controller", "FP&A Manager", "CFO"],
        "HR": ["HR Business Partner", "Recruiter", "Head of People", "VP HR"],
        "Legal": ["Legal Counsel", "Senior Counsel", "General Counsel"],
        "Operations": ["Operations Manager", "Program Manager", "VP Operations"],
        "Data Science": ["Data Scientist", "ML Engineer", "Research Scientist", "Head of AI"],
        "Security": ["Security Engineer", "AppSec Lead", "CISO"],
        "DevOps": ["SRE", "Senior SRE", "Platform Engineer", "VP Infrastructure"],
    }
    locations = ["San Francisco", "New York", "London", "Berlin", "Tokyo", "Singapore",
                 "Austin", "Seattle", "Toronto", "Sydney", "Bangalore", "Remote"]
    for i in range(150):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        dept = random.choice(departments)
        title = random.choice(titles_map[dept])
        loc = random.choice(locations)
        year = random.randint(2018, 2025)
        month = random.randint(1, 12)
        level = random.choice(["IC1", "IC2", "IC3", "IC4", "IC5", "IC6", "M1", "M2", "M3", "D1", "D2", "VP"])
        email = f"{fn.lower()}.{ln.lower()}@company.com"
        f.write(f"<tr><td>EMP-{1000+i}</td><td>{fn} {ln}</td><td>{dept}</td><td>{title}</td>"
                f"<td>{loc}</td><td>{email}</td><td>{year}-{month:02d}-01</td><td>{level}</td></tr>\n")
    f.write("</table></body></html>")

# ---------------------------------------------------------------------------
# 12. Text - Meeting notes
# ---------------------------------------------------------------------------
with open(f"{OUT}/meeting_notes.txt", "w") as f:
    f.write(textwrap.dedent("""\
    BOARD OF DIRECTORS MEETING MINUTES
    Date: June 12, 2025
    Location: Conference Room A, 500 Innovation Drive, San Francisco
    Time: 9:00 AM - 12:30 PM PST

    ATTENDEES:
    - Dr. Sarah Chen, CEO & Chair
    - Mark Thompson, CFO
    - Lisa Park, CTO
    - James Miller, COO
    - Rachel Adams, General Counsel
    - Dr. David Kim, Independent Director
    - Patricia Williams, Independent Director
    - Robert Garcia, Independent Director

    ABSENT: None

    AGENDA ITEM 1: Call to Order and Approval of Previous Minutes
    ---------------------------------------------------------------
    Dr. Chen called the meeting to order at 9:02 AM. The minutes from the
    April 15, 2025 meeting were reviewed. Motion to approve by Mr. Thompson,
    seconded by Ms. Park. Approved unanimously.

    AGENDA ITEM 2: CEO Report - Company Performance
    --------------------------------------------------
    Dr. Chen presented the Q2 performance update:
    - Revenue: $218.7M (6.5% above forecast)
    - ARR: $782.1M (growth accelerating from 28% to 31% YoY)
    - Net new logos: 127 (target: 100)
    - Enterprise wins: Acme Corp ($2.1M ACV), GlobalBank ($1.8M ACV),
      TechManufacturing ($1.4M ACV)
    - Churn: 1.2% gross, -18% net (expansion offsetting)
    - Headcount: 4,847 (+203 in Q2, on plan)

    Discussion: Mr. Garcia inquired about competitive pressure from CloudRival's
    recent funding announcement ($500M Series E). Dr. Chen noted that win rates
    against CloudRival improved from 45% to 52% in Q2, attributed to the v3
    platform launch and superior enterprise features.

    AGENDA ITEM 3: Financial Review
    --------------------------------
    Mr. Thompson presented the detailed financial review:

    Income Statement Highlights:
    - Gross margin: 73.8% (up from 71.2% in Q1)
    - R&D spend: $47.2M (21.6% of revenue)
    - S&M spend: $52.1M (23.8% of revenue, down from 25.1%)
    - G&A spend: $18.4M (8.4% of revenue)
    - Operating margin: 19.9% (target: 18%)
    - Free cash flow: $52.3M (FCF margin: 23.9%)

    Balance Sheet:
    - Cash and equivalents: $412.8M
    - Total debt: $150M (revolving credit facility, undrawn)
    - DSO: 45 days (improved from 52 days)

    Discussion: Ms. Williams asked about the path to Rule of 40. Mr. Thompson
    confirmed current performance at 51% (31% growth + 20% operating margin),
    well above the threshold.

    AGENDA ITEM 4: Product and Technology Update
    -----------------------------------------------
    Ms. Park presented the technology roadmap:

    Completed in Q2:
    - StreamKit v3.2 GA release (WebSocket support, 3x throughput improvement)
    - SOC 2 Type II certification renewal
    - FedRAMP Moderate authorization (in progress, expected Q3)
    - ML-powered anomaly detection (beta, 40 customers enrolled)

    Q3 Priorities:
    - Multi-region deployment (EU-West, APAC-East)
    - Real-time collaboration features
    - Advanced analytics with natural language queries
    - Mobile SDK (iOS and Android)

    Technical Debt:
    - Monolith decomposition: 60% complete (target: 80% by Q4)
    - Test coverage: improved from 72% to 81%
    - Infrastructure cost optimization: $2.3M annual savings identified

    Discussion: Dr. Kim asked about AI/ML strategy. Ms. Park outlined the plan
    to integrate LLM capabilities for automated insights and natural language
    querying, with a prototype expected in Q3.

    AGENDA ITEM 5: Legal and Compliance Update
    --------------------------------------------
    Ms. Adams reported:
    - No material litigation pending
    - GDPR compliance audit: passed with no findings
    - Data Processing Agreements updated for 340 enterprise customers
    - Patent portfolio: 12 patents granted, 8 applications pending
    - Open source license compliance review completed

    AGENDA ITEM 6: Executive Session
    ----------------------------------
    The Board entered executive session at 11:45 AM.
    Independent directors discussed CEO performance review and compensation.
    Executive session concluded at 12:15 PM.

    AGENDA ITEM 7: New Business and Adjournment
    ----------------------------------------------
    Resolution 2025-12: Approved the Q3 operating budget of $198.5M.
    Resolution 2025-13: Authorized management to explore strategic acquisition
    opportunities in the observability and APM space, with a budget envelope
    of up to $75M.
    Resolution 2025-14: Approved the employee stock option pool refresh of
    2,000,000 shares.

    Next meeting scheduled for September 18, 2025.
    Meeting adjourned at 12:28 PM.

    Respectfully submitted,
    Rachel Adams, Secretary
    """))

# ---------------------------------------------------------------------------
# 13. CSV - Product inventory
# ---------------------------------------------------------------------------
with open(f"{OUT}/inventory.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["SKU", "Product_Name", "Category", "Subcategory", "Unit_Cost",
                "Retail_Price", "Stock_Qty", "Reorder_Point", "Supplier",
                "Warehouse", "Last_Restock", "Weight_kg", "Dimensions_cm"])
    categories_inv = {
        "Electronics": ["Smartphones", "Laptops", "Tablets", "Accessories", "Audio"],
        "Software": ["SaaS", "On-Premise", "Mobile Apps", "Plugins"],
        "Hardware": ["Servers", "Networking", "Storage", "Peripherals"],
        "Services": ["Consulting", "Training", "Support", "Implementation"],
    }
    suppliers = ["TechSupply Co", "GlobalParts Ltd", "AsiaComponents", "EuroTech GmbH",
                 "NorthAm Distributing", "Pacific Electronics", "Atlas Manufacturing"]
    warehouses = ["WH-SFO", "WH-NYC", "WH-LON", "WH-TKY", "WH-SIN", "WH-AUS"]
    for i in range(300):
        cat = random.choice(list(categories_inv.keys()))
        subcat = random.choice(categories_inv[cat])
        cost = round(random.uniform(10, 2000), 2)
        markup = random.uniform(1.3, 3.0)
        stock = random.randint(0, 5000)
        w.writerow([
            f"SKU-{10000+i:06d}",
            f"{subcat} {random.choice(['Pro', 'Elite', 'Basic', 'Plus', 'Max', 'Ultra'])} {random.choice(['X', 'S', 'M', 'L', 'XL'])}",
            cat,
            subcat,
            cost,
            round(cost * markup, 2),
            stock,
            random.randint(10, 500),
            random.choice(suppliers),
            random.choice(warehouses),
            f"2025-{random.randint(1,6):02d}-{random.randint(1,28):02d}",
            round(random.uniform(0.1, 25.0), 2),
            f"{random.randint(5,60)}x{random.randint(5,40)}x{random.randint(2,30)}",
        ])

# ---------------------------------------------------------------------------
# 14. Text - Code review discussion
# ---------------------------------------------------------------------------
with open(f"{OUT}/code_review.txt", "w") as f:
    f.write(textwrap.dedent("""\
    CODE REVIEW: PR #4721 - Implement rate limiting middleware
    Repository: platform/api-gateway
    Author: @alex.chen
    Reviewers: @sarah.kim, @david.mueller
    Status: Changes Requested (Round 2)

    == FILES CHANGED ==
    src/middleware/rate_limiter.py (+245, -12)
    src/middleware/token_bucket.py (+89, -0)
    src/config/rate_limits.yaml (+34, -0)
    tests/test_rate_limiter.py (+312, -0)
    tests/test_token_bucket.py (+156, -0)
    docs/rate-limiting.md (+78, -0)

    == REVIEW COMMENTS ==

    @sarah.kim on src/middleware/rate_limiter.py:L42-L58:
    > The sliding window implementation looks correct, but I'm concerned about
    > the Redis MULTI/EXEC block here. If the Redis connection drops mid-transaction,
    > we'll silently allow the request through (fail-open). Should we make this
    > configurable? Some endpoints (payment, auth) should fail-closed on rate
    > limiter errors.
    >
    > Also, the window size is hardcoded to 60 seconds. Can we make this
    > configurable per-endpoint via the YAML config?

    @alex.chen:
    > Good catch on fail-open vs fail-closed. I'll add a `on_error` config option
    > with values "allow" (default) and "deny". For payment endpoints, we should
    > definitely default to "deny".
    >
    > Will make window size configurable. I was thinking of supporting both
    > fixed-window and sliding-window strategies per endpoint.

    @david.mueller on src/middleware/token_bucket.py:L15-L30:
    > The token bucket implementation is clean, but there's a subtle race condition
    > in the `consume()` method. Between the `get_tokens()` and `set_tokens()` calls,
    > another process could modify the bucket. You should use Redis WATCH or a Lua
    > script for atomicity.
    >
    > Here's a pattern I've used before:
    >
    > ```lua
    > local key = KEYS[1]
    > local capacity = tonumber(ARGV[1])
    > local rate = tonumber(ARGV[2])
    > local now = tonumber(ARGV[3])
    > local requested = tonumber(ARGV[4])
    >
    > local data = redis.call('HMGET', key, 'tokens', 'last_refill')
    > local tokens = tonumber(data[1]) or capacity
    > local last_refill = tonumber(data[2]) or now
    >
    > local elapsed = now - last_refill
    > tokens = math.min(capacity, tokens + elapsed * rate)
    >
    > if tokens >= requested then
    >     tokens = tokens - requested
    >     redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    >     redis.call('EXPIRE', key, math.ceil(capacity / rate) * 2)
    >     return 1
    > end
    > return 0
    > ```

    @alex.chen:
    > You're right about the race condition. I'll switch to the Lua script approach.
    > This also avoids the round-trip overhead of WATCH/MULTI/EXEC.

    @sarah.kim on tests/test_rate_limiter.py:L89:
    > Missing test case for concurrent requests. We should verify that the rate
    > limiter correctly handles burst traffic from multiple threads/processes.
    > Consider using pytest-asyncio with multiple concurrent clients.

    @sarah.kim on src/config/rate_limits.yaml:
    > Can we add a "bypass" list for internal service-to-service calls? Our
    > monitoring and health check endpoints shouldn't count against rate limits.
    > Also, we need different limits for authenticated vs unauthenticated requests.

    @david.mueller on docs/rate-limiting.md:
    > Documentation looks good. Please add:
    > 1. A section on how to monitor rate limiting metrics (Prometheus counters)
    > 2. Runbook for responding to rate limiting alerts
    > 3. Migration guide for existing clients

    == AUTOMATED CHECKS ==
    ✓ Unit tests: 47/47 passed
    ✓ Integration tests: 12/12 passed
    ✓ Linting: No issues
    ✓ Type checking: No issues
    ✗ Coverage: 87% (target: 90%) - missing coverage in error handling paths
    ✓ Security scan: No vulnerabilities detected
    ✓ Performance: No regression detected (p99 latency unchanged)
    """))

# ---------------------------------------------------------------------------
# 15. Large CSV - Time series IoT data
# ---------------------------------------------------------------------------
with open(f"{OUT}/iot_sensor_data.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Timestamp", "Sensor_ID", "Location", "Temperature_C", "Humidity_Pct",
                "Pressure_hPa", "CO2_ppm", "Light_lux", "Motion", "Battery_Pct", "Signal_dBm"])
    sensor_locations = {
        "SENS-001": "Building A - Floor 1 - Lobby",
        "SENS-002": "Building A - Floor 2 - Open Office",
        "SENS-003": "Building A - Floor 3 - Server Room",
        "SENS-004": "Building B - Floor 1 - Conference Room",
        "SENS-005": "Building B - Floor 2 - Lab",
        "SENS-006": "Building C - Floor 1 - Warehouse",
        "SENS-007": "Building C - Floor 2 - Break Room",
        "SENS-008": "Outdoor - Parking Lot A",
        "SENS-009": "Outdoor - Rooftop",
        "SENS-010": "Underground - Data Center",
    }
    for hour in range(24):
        for minute in range(0, 60, 10):
            for sid, loc in sensor_locations.items():
                temp = random.gauss(22 + 3 * (hour > 8 and hour < 18), 2)
                humidity = random.gauss(45, 10)
                w.writerow([
                    f"2025-06-15T{hour:02d}:{minute:02d}:00Z",
                    sid,
                    loc,
                    round(max(-10, min(50, temp)), 1),
                    round(max(10, min(95, humidity)), 1),
                    round(random.gauss(1013, 5), 1),
                    round(max(300, random.gauss(450, 80))),
                    round(max(0, random.gauss(300 if 8 < hour < 18 else 20, 100))),
                    random.choice([0, 0, 0, 1, 1]),
                    round(max(5, min(100, random.gauss(75, 15))), 1),
                    round(random.gauss(-65, 10), 1),
                ])

print(f"Created test documents in {OUT}/")
for fn in sorted(os.listdir(OUT)):
    size = os.path.getsize(f"{OUT}/{fn}")
    print(f"  {fn:<30s} {size:>10,d} bytes")
