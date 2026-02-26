# Q2 2025 Operations Dashboard

Q2 2025 Operations Dashboard
Operations Dashboard - Q2 2025
Infrastructure Summary
Incident Log

### Table 1
| Service | Instances | CPU Avg | Memory Avg | Uptime | Incidents | MTTR |
| --- | --- | --- | --- | --- | --- | --- |
| API Gateway | 12 | 34.2% | 67.8% | 99.99% | 1 | 4m |
| Auth Service | 6 | 22.1% | 45.3% | 99.98% | 2 | 8m |
| User Service | 8 | 41.7% | 72.1% | 99.97% | 3 | 12m |
| Payment Engine | 4 | 28.9% | 58.4% | 99.999% | 0 | 0m |
| Notification Hub | 6 | 38.4% | 61.2% | 99.95% | 4 | 15m |
| Search Cluster | 10 | 56.3% | 81.7% | 99.96% | 2 | 6m |
| ML Inference | 8 | 78.2% | 89.3% | 99.9% | 5 | 22m |
| CDN Edge | 24 | 15.8% | 32.1% | 99.999% | 0 | 0m |
| Message Queue | 6 | 42.1% | 55.8% | 99.98% | 1 | 3m |
| Analytics Pipeline | 4 | 67.4% | 76.9% | 99.94% | 3 | 18m |

### Table 2
| ID | Date | Severity | Service | Description | Duration | Root Cause |
| --- | --- | --- | --- | --- | --- | --- |
| INC-2401 | 2025-04-03 | P1 | ML Inference | Model serving latency spike >5s p99 | 47m | GPU memory leak in TensorRT engine |
| INC-2402 | 2025-04-08 | P2 | Auth Service | Token validation failures for SSO users | 23m | Certificate rotation script missed edge case |
| INC-2403 | 2025-04-15 | P3 | Notification Hub | Email delivery delays >30min | 2h 15m | Upstream SMTP provider throttling |
| INC-2404 | 2025-04-22 | P2 | Search Cluster | Index corruption after rebalance | 1h 4m | Race condition in shard allocation |
| INC-2405 | 2025-05-01 | P1 | API Gateway | 502 errors on /v3/streams endpoints | 4m | Misconfigured upstream timeout after deploy |
| INC-2406 | 2025-05-10 | P3 | Analytics Pipeline | Stale data in real-time dashboard | 3h | Checkpoint lag due to GC pressure |
| INC-2407 | 2025-05-18 | P2 | User Service | Profile updates returning 500 | 12m | Database connection pool exhaustion |
| INC-2408 | 2025-05-25 | P3 | Notification Hub | Push notification duplicates | 45m | Idempotency key collision in queue consumer |
| INC-2409 | 2025-06-02 | P2 | ML Inference | Incorrect model version served | 35m | Blue-green deployment rollback incomplete |
| INC-2410 | 2025-06-10 | P1 | Message Queue | Consumer group rebalance storm | 3m | Session timeout too aggressive after scaling event |
