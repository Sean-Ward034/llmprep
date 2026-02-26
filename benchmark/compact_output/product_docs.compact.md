# StreamKit API Documentation v3.2

StreamKit API Documentation v3.2
StreamKit API Documentation
Version 3.2 | Last Updated: 2025-06-01
Authentication
All API requests require authentication via Bearer token in the
Authorization
header.
Authorization: Bearer sk_live_abc123def456...
Tokens can be generated from the
Dashboard → Settings → API Keys
page.
Rate Limits
Endpoints
POST
/v3/streams
Create a new data stream.
Request Body
{
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
}
Response (201 Created)
{
  "id": "strm_abc123",
  "name": "user-events",
  "status": "provisioning",
  "created_at": "2025-06-01T10:00:00Z",
  "endpoint": "wss://streams.example.com/v3/strm_abc123"
}
GET
/v3/streams
List all streams for the authenticated account.
Query Parameters
GET
/v3/streams/{stream_id}
Get details for a specific stream.
PUT
/v3/streams/{stream_id}
Update stream configuration. Only
retention_days
,
partitions
(increase only), and
compression
can be modified.
DELETE
/v3/streams/{stream_id}
Delete a stream. This action is irreversible. All data will be permanently deleted after a 24-hour grace period.
POST
/v3/streams/{stream_id}/publish
Publish events to a stream. Supports batch publishing up to 1,000 events per request.
{
  "events": [
    {
      "key": "user_123",
      "data": {"user_id": "user_123", "event": "page_view", "timestamp": "2025-06-01T10:05:00Z"},
      "headers": {"source": "web-app", "version": "2.1"}
    }
  ]
}
POST
/v3/streams/{stream_id}/query
Query stream data with SQL-like syntax.
{
  "query": "SELECT user_id, COUNT(*) as event_count FROM stream WHERE timestamp > NOW() - INTERVAL '1 hour' GROUP BY user_id ORDER BY event_count DESC LIMIT 10",
  "format": "json"
}
Webhooks
Configure webhooks to receive real-time notifications for stream events.
Error Codes
SDKs
Python
:
pip install streamkit
Node.js
:
npm install @streamkit/sdk
Go
:
go get github.com/streamkit/sdk-go
Java
: Maven artifact
com.streamkit:sdk:3.2.0
Rust
:
cargo add streamkit

### Table 1
| Plan | Requests/min | Burst | Concurrent Streams |
| --- | --- | --- | --- |
| Free | 60 | 10 | 2 |
| Pro | 600 | 100 | 10 |
| Enterprise | 6,000 | 1,000 | 100 |
| Custom | Unlimited | Custom | Custom |

### Table 2
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| limit | integer | 20 | Max results per page (1-100) |
| offset | integer | 0 | Pagination offset |
| status | string | all | Filter: active, paused, error |
| sort | string | created_at | Sort field |
| order | string | desc | Sort order: asc, desc |

### Table 3
| Event Type | Description | Payload |
| --- | --- | --- |
| stream.created | New stream provisioned | Stream object |
| stream.error | Stream processing error | Error details + stream ID |
| stream.threshold | Volume threshold crossed | Metric + threshold value |
| stream.deleted | Stream deletion completed | Stream ID + deletion time |
| consumer.lag | Consumer group lag alert | Group + lag metrics |

### Table 4
| Code | HTTP Status | Description | Resolution |
| --- | --- | --- | --- |
| STREAM_NOT_FOUND | 404 | Stream does not exist | Check stream ID |
| RATE_LIMITED | 429 | Too many requests | Implement backoff |
| SCHEMA_VIOLATION | 400 | Event doesn't match schema | Validate event data |
| QUOTA_EXCEEDED | 402 | Plan quota exceeded | Upgrade plan |
| INTERNAL_ERROR | 500 | Server error | Retry with backoff |
| STREAM_PAUSED | 409 | Stream is paused | Resume stream first |
| BATCH_TOO_LARGE | 413 | Batch exceeds 1000 events | Split into smaller batches |
| INVALID_QUERY | 400 | SQL syntax error | Check query syntax |
