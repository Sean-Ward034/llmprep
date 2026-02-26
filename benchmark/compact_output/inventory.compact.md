# inventory.csv
Rows: 300 | Columns: 13

## Schema
- **SKU** (text): 300 unique values
- **Product_Name** (text): 229 unique values
- **Category** (categorical): Electronics, Hardware, Services, Software
- **Subcategory** (text): 17 unique values
- **Unit_Cost** (numeric): range [38.3, 1995], mean 1036
- **Retail_Price** (numeric): range [86.81, 5815], mean 2163
- **Stock_Qty** (numeric): range [12, 4998], mean 2511
- **Reorder_Point** (numeric): range [13, 500], mean 267.8
- **Supplier** (categorical): AsiaComponents, Atlas Manufacturing, EuroTech GmbH, GlobalParts Ltd, NorthAm Distributing, Pacific Electronics, TechSupply Co
- **Warehouse** (categorical): WH-AUS, WH-LON, WH-NYC, WH-SFO, WH-SIN, WH-TKY
- **Last_Restock** (text): 144 unique values
- **Weight_kg** (numeric): range [0.15, 24.87], mean 12.94
- **Dimensions_cm** (text): 298 unique values

## Sample (15 of 300 rows, plus last 5)
| SKU | Product_Name | Category | Subcategory | Unit_Cost | Retail_Price | Stock_Qty | Reorder_Point | Supplier | Warehouse | Last_Restock | Weight_kg | Dimensions_cm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SKU-010000 | Implementation Basic XL | Services | Implementation | 1433.38 | 2182.56 | 3057 | 210 | EuroTech GmbH | WH-SFO | 2025-04-26 | 0.29 | 40x35x8 |
| SKU-010001 | Training Pro S | Services | Training | 426.49 | 575.07 | 3733 | 69 | EuroTech GmbH | WH-AUS | 2025-04-06 | 15.11 | 48x29x18 |
| SKU-010002 | Plugins Pro M | Software | Plugins | 465.42 | 738.85 | 4618 | 97 | EuroTech GmbH | WH-SIN | 2025-03-24 | 17.19 | 23x30x28 |
| SKU-010003 | Accessories Max XL | Electronics | Accessories | 1994.75 | 4380.6 | 2718 | 321 | Atlas Manufacturing | WH-NYC | 2025-02-03 | 15.62 | 47x19x8 |
| SKU-010004 | Tablets Basic S | Electronics | Tablets | 601.71 | 879.35 | 4956 | 163 | Pacific Electronics | WH-SIN | 2025-03-14 | 6.37 | 27x5x11 |
| SKU-010005 | Peripherals Ultra M | Hardware | Peripherals | 345.04 | 463.1 | 2533 | 470 | TechSupply Co | WH-TKY | 2025-02-03 | 10.68 | 47x29x26 |
| SKU-010006 | Servers Elite L | Hardware | Servers | 978.95 | 1361.07 | 1808 | 310 | TechSupply Co | WH-LON | 2025-04-09 | 19.97 | 12x13x25 |
| SKU-010007 | Accessories Basic XL | Electronics | Accessories | 1609.11 | 3932.92 | 175 | 23 | Pacific Electronics | WH-SIN | 2025-03-14 | 14.88 | 5x13x25 |
| SKU-010008 | Accessories Pro L | Electronics | Accessories | 113.74 | 318.06 | 4112 | 424 | GlobalParts Ltd | WH-LON | 2025-02-02 | 11.99 | 20x6x26 |
| SKU-010009 | Implementation Plus L | Services | Implementation | 300.31 | 584.01 | 4903 | 486 | EuroTech GmbH | WH-NYC | 2025-03-20 | 7.95 | 60x38x24 |
| SKU-010010 | Consulting Pro XL | Services | Consulting | 187.76 | 347.74 | 293 | 200 | Atlas Manufacturing | WH-SIN | 2025-03-25 | 6.85 | 9x23x24 |
| SKU-010011 | Support Elite X | Services | Support | 144.38 | 407.74 | 4788 | 83 | EuroTech GmbH | WH-SFO | 2025-06-20 | 23.88 | 25x14x14 |
| SKU-010012 | Accessories Ultra XL | Electronics | Accessories | 253.95 | 511.0 | 492 | 230 | NorthAm Distributing | WH-NYC | 2025-06-23 | 18.69 | 35x13x30 |
| SKU-010013 | Smartphones Basic L | Electronics | Smartphones | 1545.84 | 2680.43 | 2580 | 50 | GlobalParts Ltd | WH-NYC | 2025-02-22 | 8.22 | 10x31x8 |
| SKU-010014 | Servers Ultra S | Hardware | Servers | 463.96 | 1268.13 | 2487 | 462 | EuroTech GmbH | WH-NYC | 2025-03-21 | 23.01 | 41x12x23 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| SKU-010295 | Peripherals Elite X | Hardware | Peripherals | 1684.08 | 3570.61 | 2232 | 412 | AsiaComponents | WH-SFO | 2025-03-05 | 5.97 | 33x33x27 |
| SKU-010296 | Consulting Basic M | Services | Consulting | 1536.71 | 2014.02 | 4339 | 477 | AsiaComponents | WH-SFO | 2025-04-21 | 14.97 | 56x26x22 |
| SKU-010297 | Implementation Elite S | Services | Implementation | 487.99 | 806.07 | 959 | 464 | AsiaComponents | WH-LON | 2025-06-07 | 24.24 | 46x18x15 |
| SKU-010298 | Accessories Pro S | Electronics | Accessories | 317.6 | 524.4 | 3382 | 336 | Atlas Manufacturing | WH-SFO | 2025-06-16 | 0.9 | 20x35x9 |
| SKU-010299 | Implementation Plus XL | Services | Implementation | 1656.32 | 2275.28 | 741 | 339 | EuroTech GmbH | WH-TKY | 2025-01-15 | 17.89 | 5x22x30 |