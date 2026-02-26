# support_tickets.csv
Rows: 200 | Columns: 10

## Schema
- **Ticket_ID** (text): 200 unique values
- **Created** (text): 119 unique values
- **Priority** (categorical): P1, P2, P3, P4
- **Category** (categorical): Access, Billing, Bug, Data Issue, Documentation, Feature Request, Integration, Onboarding, Performance, Security
- **Subject** (text): 20 unique values
- **Customer_Tier** (categorical): Enterprise, Free, Pro, Strategic
- **Assigned_Team** (categorical): Billing, Security, Solutions Architect, Tier-1 Support, Tier-2 Engineering
- **Status** (categorical): Closed, In Progress, Open, Resolved, Waiting on Customer
- **Resolution_Hours** (numeric): range [0.7, 71.2], mean 37.44
- **CSAT** (numeric): range [1, 5], mean 3.014

## Sample (15 of 200 rows, plus last 5)
| Ticket_ID | Created | Priority | Category | Subject | Customer_Tier | Assigned_Team | Status | Resolution_Hours | CSAT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TKT-10000 | 2025-02-09 | P2 | Integration | Request: custom retention policies | Enterprise | Billing | Open |  |  |
| TKT-10001 | 2025-01-01 | P3 | Onboarding | Invoice discrepancy for May | Free | Solutions Architect | Closed | 43.9 | 1 |
| TKT-10002 | 2025-06-15 | P2 | Security | API key rotation not working | Strategic | Billing | Closed | 23.7 | 1 |
| TKT-10003 | 2025-06-27 | P3 | Data Issue | Query execution timeout on complex joins | Pro | Billing | Open |  |  |
| TKT-10004 | 2025-03-16 | P4 | Billing | Python SDK version compatibility | Free | Security | Resolved | 70.1 | 3 |
| TKT-10005 | 2025-04-18 | P2 | Billing | Dashboard loading slowly with large datasets | Enterprise | Security | Waiting on Customer |  |  |
| TKT-10006 | 2025-05-03 | P4 | Bug | Invoice discrepancy for May | Strategic | Tier-2 Engineering | Open |  |  |
| TKT-10007 | 2025-01-20 | P3 | Performance | Cannot add team member to workspace | Strategic | Solutions Architect | Closed | 62.7 | 4 |
| TKT-10008 | 2025-02-03 | P3 | Feature Request | Salesforce connector not syncing | Enterprise | Solutions Architect | Closed | 50.0 | 3 |
| TKT-10009 | 2025-01-23 | P3 | Onboarding | Need webhook retry configuration | Enterprise | Billing | Open |  |  |
| TKT-10010 | 2025-03-04 | P3 | Integration | Need help with initial setup | Free | Security | Resolved | 21.1 | 5 |
| TKT-10011 | 2025-06-14 | P1 | Performance | Python SDK version compatibility | Enterprise | Tier-2 Engineering | Closed | 1.5 | 4 |
| TKT-10012 | 2025-03-06 | P2 | Feature Request | API key rotation not working | Pro | Tier-1 Support | Resolved | 60.8 | 4 |
| TKT-10013 | 2025-04-23 | P3 | Onboarding | Outdated SDK examples in docs | Free | Solutions Architect | Waiting on Customer |  |  |
| TKT-10014 | 2025-04-12 | P2 | Data Issue | Data showing incorrect timezone | Pro | Tier-2 Engineering | Waiting on Customer |  |  |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| TKT-10195 | 2025-05-05 | P4 | Billing | Python SDK version compatibility | Pro | Solutions Architect | Closed | 1.2 | 1 |
| TKT-10196 | 2025-03-06 | P3 | Billing | Missing records in analytics export | Pro | Billing | Open |  |  |
| TKT-10197 | 2025-04-02 | P3 | Access | Dashboard loading slowly with large datasets | Pro | Tier-2 Engineering | Waiting on Customer |  |  |
| TKT-10198 | 2025-03-23 | P3 | Documentation | Cannot add team member to workspace | Free | Tier-1 Support | Open |  |  |
| TKT-10199 | 2025-03-28 | P3 | Performance | Invoice discrepancy for May | Enterprise | Tier-2 Engineering | Closed | 26.2 | 2 |