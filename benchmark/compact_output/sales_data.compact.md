# sales_data.csv
Rows: 500 | Columns: 10

## Schema
- **Date** (text): 266 unique values
- **Product** (categorical): APIBridge, AuthShield, CloudGuard, DataSync Enterprise, LogVault, MetricsDash, PipelineBuilder, QueryEngine, StreamKit, Widget Pro
- **Region** (categorical): ANZ, APAC-East, APAC-South, Canada, EU-Central, EU-West, LATAM, MEA, US-East, US-West
- **Channel** (categorical): Direct, OEM, Online, Partner, Reseller
- **Units** (numeric): range [1, 200], mean 99
- **Revenue_USD** (numeric): range [242.8, 8.691e+05], mean 2.251e+05
- **Discount_Pct** (numeric): range [0, 25], mean 13.5
- **Customer_Segment** (categorical): Enterprise, Mid-Market, SMB, Strategic
- **Deal_Size** (categorical): Large, Medium, Mega, Small
- **Rep_ID** (text): 388 unique values

## Sample (15 of 500 rows, plus last 5)
| Date | Product | Region | Channel | Units | Revenue_USD | Discount_Pct | Customer_Segment | Deal_Size | Rep_ID |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-11-04 | DataSync Enterprise | Canada | Direct | 7 | 24742.49 | 5 | Mid-Market | Medium | REP-704 |
| 2025-07-02 | QueryEngine | LATAM | Partner | 8 | 3904.81 | 5 | SMB | Medium | REP-559 |
| 2025-10-09 | StreamKit | EU-West | Partner | 2 | 7231.58 | 5 | Strategic | Large | REP-881 |
| 2025-06-04 | Widget Pro | MEA | OEM | 24 | 41701.83 | 10 | Enterprise | Large | REP-227 |
| 2025-07-03 | DataSync Enterprise | US-East | Partner | 142 | 159881.26 | 25 | Enterprise | Medium | REP-891 |
| 2025-05-03 | MetricsDash | EU-West | Online | 60 | 221293.8 | 15 | Enterprise | Mega | REP-463 |
| 2025-04-22 | QueryEngine | EU-Central | Partner | 69 | 182367.55 | 25 | SMB | Medium | REP-573 |
| 2025-07-09 | APIBridge | US-East | Online | 164 | 538507.38 | 5 | Enterprise | Small | REP-510 |
| 2025-05-03 | AuthShield | LATAM | Reseller | 55 | 201081.05 | 20 | Enterprise | Medium | REP-246 |
| 2025-05-05 | PipelineBuilder | LATAM | Online | 64 | 191370.01 | 20 | Enterprise | Mega | REP-324 |
| 2025-03-17 | CloudGuard | LATAM | OEM | 127 | 63500.2 | 0 | SMB | Medium | REP-165 |
| 2025-07-13 | DataSync Enterprise | Canada | Online | 153 | 609650.02 | 20 | Enterprise | Small | REP-887 |
| 2025-11-11 | StreamKit | Canada | Partner | 29 | 41402.85 | 5 | Strategic | Small | REP-619 |
| 2025-02-28 | MetricsDash | EU-West | OEM | 161 | 184421.68 | 25 | Mid-Market | Medium | REP-897 |
| 2025-09-01 | StreamKit | EU-Central | Direct | 154 | 254804.16 | 0 | SMB | Large | REP-346 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 2025-10-05 | QueryEngine | LATAM | Reseller | 148 | 509972.33 | 0 | Enterprise | Medium | REP-300 |
| 2025-03-26 | AuthShield | EU-West | OEM | 190 | 150149.95 | 0 | Mid-Market | Mega | REP-646 |
| 2025-12-11 | DataSync Enterprise | EU-West | Direct | 125 | 153516.92 | 20 | SMB | Mega | REP-320 |
| 2025-05-16 | MetricsDash | APAC-South | OEM | 162 | 63993.36 | 25 | Enterprise | Large | REP-670 |
| 2025-05-12 | StreamKit | APAC-South | Online | 6 | 11276.37 | 10 | Mid-Market | Medium | REP-789 |