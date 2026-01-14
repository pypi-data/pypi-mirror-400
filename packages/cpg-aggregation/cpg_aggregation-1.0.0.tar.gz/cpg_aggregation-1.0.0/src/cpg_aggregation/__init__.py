"""
Cholayil Gold Layer Aggregations Package
A collection of data transformation functions for CPG analytics in Snowflake.
"""

__version__ = "1.0.0"
__author__ = "Akash"
__email__ = "akashlimkar1999.com"

from .aggregations import (
    # Helper functions
    list_available_functions,
    list_domains,
    get_functions_by_domain,
    
    # Execution functions
    run_aggregation,
    run_multiple_aggregations,
    run_domain_aggregations,
    run_all_aggregations,
    format_results,
    
    # Individual aggregation functions - DIM
    gold_dim_date,
    
    # Individual aggregation functions - RMS
    gold_rms_fact_sustainability,
    gold_rms_delivery_delay,
    gold_rms_procurement_lead_time,
    gold_rms_4,
    
    # Individual aggregation functions - PM
    gold_pm_4,
    gold_pm_plan_adherence,
    gold_pm_downtime_per_shift_aggregated,
    gold_pm_downtime_per_shift_oeee,
    
    # Individual aggregation functions - DSC
    gold_dsc_3,
    gold_dsc_3_inventory_days,
    gold_dsc_damaged_return,
    gold_dsc_transport_cost_per_unit,
    gold_dsc_on_time_shipment_rate,
    gold_dsc_inbound_delivery_accuracy,
    
    # Individual aggregation functions - REUS
    gold_reus_customer_retention_monthly_totals,
    gold_reus_customer_retention_monthly_retained,
    gold_reus_customer_retention_monthly_new,
    gold_reus_product_return_analysis,
    gold_reus_average_order_value_analysis,
    gold_reus_sales_per_outlet_analysis,
    
    # Individual aggregation functions - CFM
    gold_cfm_conversion_rate,
    gold_cfm_cost_per_conversion_spend,
    gold_cfm_cost_per_conversion_engagement,
    gold_cfm_survey_response_rate,
    gold_cfm_customer_satisfaction_score,
    gold_cfm_trade_promotion_effectiveness,
    
    # Individual aggregation functions - FC
    gold_fc_invoice_accuracy_analysis,
    gold_fc_budget,
    gold_fc_payment_timeliness_analysis,
    
    # Individual aggregation functions - SESG
    gold_sesg_emission_production_analysis,
    
    # Constants
    FUNCTION_REGISTRY,
    DOMAIN_FUNCTIONS,
    FUNCTION_MAP
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Helper functions
    "list_available_functions",
    "list_domains",
    "get_functions_by_domain",
    
    # Execution functions
    "run_aggregation",
    "run_multiple_aggregations",
    "run_domain_aggregations",
    "run_all_aggregations",
    "format_results",
    
    # All individual functions
    "gold_dim_date",
    "gold_rms_fact_sustainability",
    "gold_rms_delivery_delay",
    "gold_rms_procurement_lead_time",
    "gold_rms_4",
    "gold_pm_4",
    "gold_pm_plan_adherence",
    "gold_pm_downtime_per_shift_aggregated",
    "gold_pm_downtime_per_shift_oeee",
    "gold_dsc_3",
    "gold_dsc_3_inventory_days",
    "gold_dsc_damaged_return",
    "gold_dsc_transport_cost_per_unit",
    "gold_dsc_on_time_shipment_rate",
    "gold_dsc_inbound_delivery_accuracy",
    "gold_reus_customer_retention_monthly_totals",
    "gold_reus_customer_retention_monthly_retained",
    "gold_reus_customer_retention_monthly_new",
    "gold_reus_product_return_analysis",
    "gold_reus_average_order_value_analysis",
    "gold_reus_sales_per_outlet_analysis",
    "gold_cfm_conversion_rate",
    "gold_cfm_cost_per_conversion_spend",
    "gold_cfm_cost_per_conversion_engagement",
    "gold_cfm_survey_response_rate",
    "gold_cfm_customer_satisfaction_score",
    "gold_cfm_trade_promotion_effectiveness",
    "gold_fc_invoice_accuracy_analysis",
    "gold_fc_budget",
    "gold_fc_payment_timeliness_analysis",
    "gold_sesg_emission_production_analysis",
    
    # Constants
    "FUNCTION_REGISTRY",
    "DOMAIN_FUNCTIONS",
    "FUNCTION_MAP"
]
