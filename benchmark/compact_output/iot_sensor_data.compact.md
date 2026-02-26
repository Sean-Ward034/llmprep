# iot_sensor_data.csv
Rows: 1440 | Columns: 11

## Schema
- **Timestamp** (text): 144 unique values
- **Sensor_ID** (categorical): SENS-001, SENS-002, SENS-003, SENS-004, SENS-005, SENS-006, SENS-007, SENS-008, SENS-009, SENS-010
- **Location** (categorical): Building A - Floor 1 - Lobby, Building A - Floor 2 - Open Office, Building A - Floor 3 - Server Room, Building B - Floor 1 - Conference Room, Building B - Floor 2 - Lab, Building C - Floor 1 - Warehouse, Building C - Floor 2 - Break Room, Outdoor - Parking Lot A, Outdoor - Rooftop, Underground - Data Center
- **Temperature_C** (numeric): range [14.3, 31.8], mean 23.06
- **Humidity_Pct** (numeric): range [13.8, 74.9], mean 45.15
- **Pressure_hPa** (numeric): range [992.2, 1030], mean 1013
- **CO2_ppm** (numeric): range [300, 699], mean 451.8
- **Light_lux** (numeric): range [0, 596], mean 143.2
- **Motion** (numeric): range [0, 1], mean 0.4014
- **Battery_Pct** (numeric): range [19.8, 100], mean 74.84
- **Signal_dBm** (numeric): range [-99.6, -30], mean -65.33

## Sample (15 of 1440 rows, plus last 5)
| Timestamp | Sensor_ID | Location | Temperature_C | Humidity_Pct | Pressure_hPa | CO2_ppm | Light_lux | Motion | Battery_Pct | Signal_dBm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-06-15T00:00:00Z | SENS-001 | Building A - Floor 1 - Lobby | 20.4 | 52.1 | 1017.3 | 470 | 29 | 1 | 50.4 | -76.5 |
| 2025-06-15T00:00:00Z | SENS-002 | Building A - Floor 2 - Open Office | 20.8 | 48.0 | 1016.7 | 367 | 0 | 1 | 92.9 | -57.9 |
| 2025-06-15T00:00:00Z | SENS-003 | Building A - Floor 3 - Server Room | 23.0 | 56.8 | 1008.0 | 385 | 104 | 0 | 92.9 | -56.5 |
| 2025-06-15T00:00:00Z | SENS-004 | Building B - Floor 1 - Conference Room | 21.4 | 34.6 | 1022.1 | 478 | 0 | 0 | 65.1 | -98.7 |
| 2025-06-15T00:00:00Z | SENS-005 | Building B - Floor 2 - Lab | 22.6 | 44.2 | 1008.4 | 368 | 0 | 1 | 76.4 | -64.8 |
| 2025-06-15T00:00:00Z | SENS-006 | Building C - Floor 1 - Warehouse | 22.3 | 35.4 | 1006.8 | 300 | 206 | 1 | 68.0 | -67.1 |
| 2025-06-15T00:00:00Z | SENS-007 | Building C - Floor 2 - Break Room | 25.6 | 36.3 | 1013.0 | 504 | 0 | 1 | 99.0 | -50.5 |
| 2025-06-15T00:00:00Z | SENS-008 | Outdoor - Parking Lot A | 22.6 | 51.2 | 1020.6 | 401 | 73 | 0 | 76.4 | -69.4 |
| 2025-06-15T00:00:00Z | SENS-009 | Outdoor - Rooftop | 20.3 | 70.5 | 1011.1 | 468 | 0 | 1 | 82.8 | -69.1 |
| 2025-06-15T00:00:00Z | SENS-010 | Underground - Data Center | 22.5 | 58.6 | 1012.0 | 392 | 106 | 0 | 59.3 | -76.2 |
| 2025-06-15T00:10:00Z | SENS-001 | Building A - Floor 1 - Lobby | 19.8 | 38.2 | 1005.9 | 496 | 0 | 1 | 60.3 | -48.8 |
| 2025-06-15T00:10:00Z | SENS-002 | Building A - Floor 2 - Open Office | 22.3 | 18.0 | 1009.3 | 505 | 103 | 0 | 68.2 | -61.4 |
| 2025-06-15T00:10:00Z | SENS-003 | Building A - Floor 3 - Server Room | 19.6 | 34.3 | 1016.7 | 431 | 0 | 1 | 65.2 | -54.6 |
| 2025-06-15T00:10:00Z | SENS-004 | Building B - Floor 1 - Conference Room | 22.9 | 56.6 | 1012.7 | 336 | 0 | 0 | 100 | -67.3 |
| 2025-06-15T00:10:00Z | SENS-005 | Building B - Floor 2 - Lab | 22.5 | 30.5 | 1014.0 | 486 | 0 | 1 | 68.1 | -50.4 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 2025-06-15T23:50:00Z | SENS-006 | Building C - Floor 1 - Warehouse | 20.4 | 47.4 | 1014.4 | 523 | 67 | 0 | 59.0 | -74.4 |
| 2025-06-15T23:50:00Z | SENS-007 | Building C - Floor 2 - Break Room | 23.3 | 42.9 | 1015.4 | 406 | 0 | 0 | 91.9 | -62.1 |
| 2025-06-15T23:50:00Z | SENS-008 | Outdoor - Parking Lot A | 21.3 | 55.7 | 1011.5 | 466 | 24 | 0 | 72.3 | -54.6 |
| 2025-06-15T23:50:00Z | SENS-009 | Outdoor - Rooftop | 22.3 | 17.3 | 1014.2 | 396 | 0 | 0 | 65.8 | -67.8 |
| 2025-06-15T23:50:00Z | SENS-010 | Underground - Data Center | 21.9 | 52.9 | 1014.7 | 445 | 161 | 1 | 54.1 | -71.7 |