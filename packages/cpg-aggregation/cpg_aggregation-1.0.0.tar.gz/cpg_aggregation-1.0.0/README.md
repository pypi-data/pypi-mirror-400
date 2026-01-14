# Cholayil Gold Aggregations

A Python package containing Gold layer aggregation functions for Cholayil CPG Data Warehouse in Snowflake.

## Features

- **31 aggregation functions** across 8 business domains
- **Flexible execution** - run single functions, multiple functions, entire domains, or all at once
- **Database-agnostic** - pass your own database/schema names
- **Snowpark native** - designed specifically for Snowflake Snowpark

## Installation

```bash
pip install cholayil-gold-aggregations
```

## Quick Start

### In Snowflake Stored Procedure

```sql
CREATE OR REPLACE PROCEDURE run_gold_aggregation(
    function_name STRING,
    source_db STRING,
    source_schema STRING,
    target_db STRING,
    target_schema STRING
)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'cholayil-gold-aggregations')
HANDLER = 'main'
AS
$$
import cholayil_gold_aggregations as cga

def main(session, function_name, source_db, source_schema, target_db, target_schema):
    result = cga.run_aggregation(session, function_name, source_db, source_schema, target_db, target_schema)
    return cga.format_results([result])
$$;

-- Execute
CALL run_gold_aggregation('GOLD_DIM_DATE', 'SILVER_LAYER', 'MAPPED_DATA', 'GOLD_LAYER', 'AGGREGATED_DATA');
```

### In Python (Local Development)

```python
from snowflake.snowpark import Session
import cholayil_gold_aggregations as cga

# Create session
session = Session.builder.configs({...}).create()

# List available functions
print(cga.list_available_functions())
# ['GOLD_DIM_DATE', 'GOLD_RMS_FACT_SUSTAINABILITY', ...]

# List domains
print(cga.list_domains())
# ['RMS', 'PM', 'DSC', 'REUS', 'CFM', 'FC', 'SESG', 'DIM']

# Run a single function
result = cga.run_aggregation(
    session, 
    'GOLD_DIM_DATE',
    source_db='SILVER_LAYER',
    source_schema='MAPPED_DATA',
    target_db='GOLD_LAYER',
    target_schema='AGGREGATED_DATA'
)
print(cga.format_results([result]))

# Run multiple functions
results = cga.run_multiple_aggregations(
    session,
    ['GOLD_DIM_DATE', 'GOLD_FC_BUDGET', 'GOLD_PM_4'],
    source_db='SILVER_LAYER',
    source_schema='MAPPED_DATA',
    target_db='GOLD_LAYER',
    target_schema='AGGREGATED_DATA'
)
print(cga.format_results(results))

# Run all functions in a domain
results = cga.run_domain_aggregations(
    session,
    'FC',  # Finance & Controlling
    source_db='SILVER_LAYER',
    source_schema='MAPPED_DATA',
    target_db='GOLD_LAYER',
    target_schema='AGGREGATED_DATA'
)
print(cga.format_results(results))

# Run all 31 functions
results = cga.run_all_aggregations(
    session,
    source_db='SILVER_LAYER',
    source_schema='MAPPED_DATA',
    target_db='GOLD_LAYER',
    target_schema='AGGREGATED_DATA'
)
print(cga.format_results(results))
```

### Call Individual Functions Directly

```python
import cholayil_gold_aggregations as cga

# Get the DataFrame without writing to a table
df = cga.gold_dim_date(session, 'SILVER_LAYER', 'MAPPED_DATA')
df.show()

# Get delivery delay analysis
df = cga.gold_rms_delivery_delay(session, 'SILVER_LAYER', 'MAPPED_DATA')
df.show()

# Get budget analysis
df = cga.gold_fc_budget(session, 'SILVER_LAYER', 'MAPPED_DATA')
df.show()
```

## Available Functions

### DIM (Dimension Tables) - 1 function
- `gold_dim_date` - Date dimension table

### RMS (Raw Material Sourcing) - 4 functions
- `gold_rms_fact_sustainability` - Supplier sustainability metrics
- `gold_rms_delivery_delay` - Delivery delay analysis
- `gold_rms_procurement_lead_time` - Procurement lead time
- `gold_rms_4` - RMS aggregated metrics

### PM (Production Management) - 4 functions
- `gold_pm_4` - Production metrics
- `gold_pm_plan_adherence` - Plan adherence analysis
- `gold_pm_downtime_per_shift_aggregated` - Downtime metrics
- `gold_pm_downtime_per_shift_oeee` - OEEE percentage

### DSC (Distribution & Supply Chain) - 6 functions
- `gold_dsc_3` - Supply chain metrics
- `gold_dsc_3_inventory_days` - Inventory days calculation
- `gold_dsc_damaged_return` - Damaged goods analysis
- `gold_dsc_transport_cost_per_unit` - Transportation costs
- `gold_dsc_on_time_shipment_rate` - On-time shipment rate
- `gold_dsc_inbound_delivery_accuracy` - Inbound delivery accuracy

### REUS (Retail & End User Sales) - 6 functions
- `gold_reus_customer_retention_monthly_totals` - Customer retention totals
- `gold_reus_customer_retention_monthly_retained` - Retained customers
- `gold_reus_customer_retention_monthly_new` - New customers
- `gold_reus_product_return_analysis` - Product return analysis
- `gold_reus_average_order_value_analysis` - Average order value
- `gold_reus_sales_per_outlet_analysis` - Sales per outlet

### CFM (Consumer & Field Marketing) - 6 functions
- `gold_cfm_conversion_rate` - Conversion rate
- `gold_cfm_cost_per_conversion_spend` - Cost per conversion (spend)
- `gold_cfm_cost_per_conversion_engagement` - Cost per conversion (engagement)
- `gold_cfm_survey_response_rate` - Survey response rate
- `gold_cfm_customer_satisfaction_score` - Customer satisfaction
- `gold_cfm_trade_promotion_effectiveness` - Trade promotion effectiveness

### FC (Finance & Controlling) - 3 functions
- `gold_fc_invoice_accuracy_analysis` - Invoice accuracy
- `gold_fc_budget` - Budget vs actual
- `gold_fc_payment_timeliness_analysis` - Payment timeliness

### SESG (Sustainability & ESG) - 1 function
- `gold_sesg_emission_production_analysis` - Emission production analysis

## Helper Functions

```python
import cholayil_gold_aggregations as cga

# List all 31 functions
cga.list_available_functions()

# List all 8 domains
cga.list_domains()

# Get functions for a specific domain
cga.get_functions_by_domain('FC')
# ['GOLD_FC_INVOICE_ACCURACY_ANALYSIS', 'GOLD_FC_BUDGET', 'GOLD_FC_PAYMENT_TIMELINESS_ANALYSIS']

# Get required source tables for a function
cga.get_required_tables('GOLD_FC_BUDGET')
# ['dim_account_master', 'fact_budget', 'fact_general_ledger']
```

## License

MIT License

## Author

Akash - Cholayil Data Engineering Team
