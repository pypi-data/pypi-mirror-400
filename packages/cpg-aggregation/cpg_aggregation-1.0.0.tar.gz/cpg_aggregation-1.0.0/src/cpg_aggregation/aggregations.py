"""
Gold Layer Aggregation Functions for Cholayil CPG Data Warehouse.

This module contains all 31 aggregation functions organized by business domain.
Functions are designed to be database-agnostic - you pass the session and table
references, and the functions handle the transformations.
"""

from snowflake.snowpark.functions import (
    col, datediff, avg, sum as sum_, count, max as max_, min as min_,
    to_date, to_timestamp, when, lit, coalesce, concat, substr,
    to_char, countDistinct
)


# ============================================
# FUNCTION REGISTRY & DOMAIN MAPPINGS
# ============================================

FUNCTION_REGISTRY = {
    "GOLD_DIM_DATE": {
        "tables": ["dim_date"],
        "function": "gold_dim_date"
    },
    "GOLD_RMS_FACT_SUSTAINABILITY": {
        "tables": ["dim_supplier_master"],
        "function": "gold_rms_fact_sustainability"
    },
    "GOLD_RMS_DELIVERY_DELAY": {
        "tables": ["fact_goods_receipt", "fact_purchase_order_line", "fact_purchase_order_header", 
                   "dim_supplier_master", "dim_material_master", "dim_product_master"],
        "function": "gold_rms_delivery_delay"
    },
    "GOLD_RMS_PROCUREMENT_LEAD_TIME": {
        "tables": ["fact_goods_receipt", "fact_purchase_order_line", "fact_purchase_order_header",
                   "dim_supplier_master", "dim_material_master", "dim_product_master"],
        "function": "gold_rms_procurement_lead_time"
    },
    "GOLD_RMS_4": {
        "tables": ["fact_goods_receipt", "fact_purchase_order_line", "fact_purchase_order_header",
                   "dim_supplier_master", "dim_product_master", "dim_material_master"],
        "function": "gold_rms_4"
    },
    "GOLD_PM_4": {
        "tables": ["fact_production_batch", "fact_shift_log", "dim_production_line", "dim_facility_master"],
        "function": "gold_pm_4"
    },
    "GOLD_PM_PLAN_ADHERENCE": {
        "tables": ["fact_production_schedule_line", "fact_production_schedule_header", 
                   "dim_production_line", "dim_facility_master"],
        "function": "gold_pm_plan_adherence"
    },
    "GOLD_PM_DOWNTIME_PER_SHIFT_AGGREGATED": {
        "tables": ["fact_line_efficiency_log", "fact_shift_log", "fact_equipment_downtime_log",
                   "dim_production_line", "dim_facility_master"],
        "function": "gold_pm_downtime_per_shift_aggregated"
    },
    "GOLD_PM_DOWNTIME_PER_SHIFT_OEEE": {
        "tables": ["fact_line_efficiency_log", "fact_shift_log", "dim_production_line", "dim_facility_master"],
        "function": "gold_pm_downtime_per_shift_oeee"
    },
    "GOLD_DSC_3": {
        "tables": ["fact_product_inventory", "dim_warehouse_master", "dim_product_master", "fact_sales_order_line"],
        "function": "gold_dsc_3"
    },
    "GOLD_DSC_3_INVENTORY_DAYS": {
        "tables": ["fact_product_inventory", "dim_warehouse_master", "dim_product_master", "fact_sales_order_line"],
        "function": "gold_dsc_3_inventory_days"
    },
    "GOLD_DSC_DAMAGED_RETURN": {
        "tables": ["fact_outbound_shipment", "dim_carrier_master", "fact_shipment_line", "fact_return_order",
                   "fact_purchase_order_line", "fact_purchase_order_header", "dim_supplier_master"],
        "function": "gold_dsc_damaged_return"
    },
    "GOLD_DSC_TRANSPORT_COST_PER_UNIT": {
        "tables": ["fact_transportation_cost", "dim_carrier_master", "dim_truck_route", "fact_outbound_shipment"],
        "function": "gold_dsc_transport_cost_per_unit"
    },
    "GOLD_DSC_ON_TIME_SHIPMENT_RATE": {
        "tables": ["fact_outbound_shipment", "dim_carrier_master", "dim_distribution_center"],
        "function": "gold_dsc_on_time_shipment_rate"
    },
    "GOLD_DSC_INBOUND_DELIVERY_ACCURACY": {
        "tables": ["fact_inbound_shipment", "dim_supplier_master", "dim_warehouse_master"],
        "function": "gold_dsc_inbound_delivery_accuracy"
    },
    "GOLD_REUS_CUSTOMER_RETENTION_MONTHLY_TOTALS": {
        "tables": ["fact_sales_order", "fact_customer_visit"],
        "function": "gold_reus_customer_retention_monthly_totals"
    },
    "GOLD_REUS_CUSTOMER_RETENTION_MONTHLY_RETAINED": {
        "tables": ["fact_sales_order", "fact_customer_visit"],
        "function": "gold_reus_customer_retention_monthly_retained"
    },
    "GOLD_REUS_CUSTOMER_RETENTION_MONTHLY_NEW": {
        "tables": ["fact_sales_order", "fact_customer_visit"],
        "function": "gold_reus_customer_retention_monthly_new"
    },
    "GOLD_REUS_PRODUCT_RETURN_ANALYSIS": {
        "tables": ["fact_return_order", "fact_sales_order", "dim_channel", "dim_product_master", "dim_material_category"],
        "function": "gold_reus_product_return_analysis"
    },
    "GOLD_REUS_AVERAGE_ORDER_VALUE_ANALYSIS": {
        "tables": ["fact_sales_order", "dim_retail_outlet", "dim_customer_master", "dim_region_hierarchy"],
        "function": "gold_reus_average_order_value_analysis"
    },
    "GOLD_REUS_SALES_PER_OUTLET_ANALYSIS": {
        "tables": ["fact_sales_order", "dim_retail_outlet", "dim_region_hierarchy"],
        "function": "gold_reus_sales_per_outlet_analysis"
    },
    "GOLD_CFM_CONVERSION_RATE": {
        "tables": ["fact_ad_impression"],
        "function": "gold_cfm_conversion_rate"
    },
    "GOLD_CFM_COST_PER_CONVERSION_SPEND": {
        "tables": ["fact_marketing_spend", "fact_ad_impression", "dim_campaign_master"],
        "function": "gold_cfm_cost_per_conversion_spend"
    },
    "GOLD_CFM_COST_PER_CONVERSION_ENGAGEMENT": {
        "tables": ["fact_ad_impression", "dim_campaign_master"],
        "function": "gold_cfm_cost_per_conversion_engagement"
    },
    "GOLD_CFM_SURVEY_RESPONSE_RATE": {
        "tables": ["fact_consumer_survey"],
        "function": "gold_cfm_survey_response_rate"
    },
    "GOLD_CFM_CUSTOMER_SATISFACTION_SCORE": {
        "tables": ["fact_consumer_survey", "dim_product_master", "dim_material_category"],
        "function": "gold_cfm_customer_satisfaction_score"
    },
    "GOLD_CFM_TRADE_PROMOTION_EFFECTIVENESS": {
        "tables": ["fact_promotion_plan", "dim_promotion_master", "dim_channel", "fact_trade_promotion"],
        "function": "gold_cfm_trade_promotion_effectiveness"
    },
    "GOLD_FC_INVOICE_ACCURACY_ANALYSIS": {
        "tables": ["fact_invoice", "fact_payment"],
        "function": "gold_fc_invoice_accuracy_analysis"
    },
    "GOLD_FC_BUDGET": {
        "tables": ["dim_account_master", "fact_budget", "fact_general_ledger"],
        "function": "gold_fc_budget"
    },
    "GOLD_FC_PAYMENT_TIMELINESS_ANALYSIS": {
        "tables": ["fact_payment", "fact_invoice"],
        "function": "gold_fc_payment_timeliness_analysis"
    },
    "GOLD_SESG_EMISSION_PRODUCTION_ANALYSIS": {
        "tables": ["fact_emission_record", "fact_production_batch"],
        "function": "gold_sesg_emission_production_analysis"
    }
}

DOMAIN_FUNCTIONS = {
    "RMS": ["GOLD_RMS_FACT_SUSTAINABILITY", "GOLD_RMS_DELIVERY_DELAY", 
            "GOLD_RMS_PROCUREMENT_LEAD_TIME", "GOLD_RMS_4"],
    "PM": ["GOLD_PM_4", "GOLD_PM_PLAN_ADHERENCE", 
           "GOLD_PM_DOWNTIME_PER_SHIFT_AGGREGATED", "GOLD_PM_DOWNTIME_PER_SHIFT_OEEE"],
    "DSC": ["GOLD_DSC_3", "GOLD_DSC_3_INVENTORY_DAYS", "GOLD_DSC_DAMAGED_RETURN",
            "GOLD_DSC_TRANSPORT_COST_PER_UNIT", "GOLD_DSC_ON_TIME_SHIPMENT_RATE", 
            "GOLD_DSC_INBOUND_DELIVERY_ACCURACY"],
    "REUS": ["GOLD_REUS_CUSTOMER_RETENTION_MONTHLY_TOTALS", "GOLD_REUS_CUSTOMER_RETENTION_MONTHLY_RETAINED",
             "GOLD_REUS_CUSTOMER_RETENTION_MONTHLY_NEW", "GOLD_REUS_PRODUCT_RETURN_ANALYSIS",
             "GOLD_REUS_AVERAGE_ORDER_VALUE_ANALYSIS", "GOLD_REUS_SALES_PER_OUTLET_ANALYSIS"],
    "CFM": ["GOLD_CFM_CONVERSION_RATE", "GOLD_CFM_COST_PER_CONVERSION_SPEND",
            "GOLD_CFM_COST_PER_CONVERSION_ENGAGEMENT", "GOLD_CFM_SURVEY_RESPONSE_RATE",
            "GOLD_CFM_CUSTOMER_SATISFACTION_SCORE", "GOLD_CFM_TRADE_PROMOTION_EFFECTIVENESS"],
    "FC": ["GOLD_FC_INVOICE_ACCURACY_ANALYSIS", "GOLD_FC_BUDGET", "GOLD_FC_PAYMENT_TIMELINESS_ANALYSIS"],
    "SESG": ["GOLD_SESG_EMISSION_PRODUCTION_ANALYSIS"],
    "DIM": ["GOLD_DIM_DATE"]
}


# ============================================
# HELPER FUNCTIONS
# ============================================

def list_available_functions():
    """List all available aggregation functions."""
    return list(FUNCTION_REGISTRY.keys())


def list_domains():
    """List all available domains."""
    return list(DOMAIN_FUNCTIONS.keys())


def get_functions_by_domain(domain):
    """Get all functions for a specific domain."""
    domain_upper = domain.upper()
    if domain_upper in DOMAIN_FUNCTIONS:
        return DOMAIN_FUNCTIONS[domain_upper]
    return []


def get_required_tables(function_name):
    """Get the list of required tables for a function."""
    function_name_upper = function_name.upper()
    if function_name_upper in FUNCTION_REGISTRY:
        return FUNCTION_REGISTRY[function_name_upper]["tables"]
    return []


# ============================================
# 1. DIMENSION TABLE FUNCTIONS
# ============================================

def gold_dim_date(session, source_db, source_schema):
    """
    Gold dimension date table.
    
    Args:
        session: Snowpark session
        source_db: Source database name
        source_schema: Source schema name
    
    Returns:
        Snowpark DataFrame with date dimension
    """
    dim_date = session.table(f"{source_db}.{source_schema}.dim_date")
    return dim_date.select(
        col('"date_id"'),
        col('"full_date"'),
        col('"year"'),
        col('"quarter"'),
        col('"month"'),
        col('"month_name"'),
        col('"week"'),
        col('"day"'),
        col('"day_of_week"'),
        col('"day_name"'),
        col('"fiscal_year"'),
        col('"fiscal_quarter"'),
        col('"is_weekend"'),
        col('"is_holiday"'),
        col('"is_month_end"'),
        col('"is_year_end"')
    )


# ============================================
# 2-5. RMS (Raw Material Sourcing) FUNCTIONS
# ============================================

def gold_rms_fact_sustainability(session, source_db, source_schema):
    """RMS Sustainability facts - raw columns for scoring."""
    d = session.table(f"{source_db}.{source_schema}.dim_supplier_master")
    
    return d.select(
        d['"supplier_name"'],
        d['"country"'],
        d['"region"'],
        d['"vendor_category"'],
        d['"sustainability_rating"'],
        d['"compliance_score"']
    )


def gold_rms_delivery_delay(session, source_db, source_schema):
    """RMS Delivery delay analysis - raw columns."""
    g = session.table(f"{source_db}.{source_schema}.fact_goods_receipt")
    pol = session.table(f"{source_db}.{source_schema}.fact_purchase_order_line")
    poh = session.table(f"{source_db}.{source_schema}.fact_purchase_order_header")
    sup = session.table(f"{source_db}.{source_schema}.dim_supplier_master")
    mat = session.table(f"{source_db}.{source_schema}.dim_material_master")
    prod = session.table(f"{source_db}.{source_schema}.dim_product_master")
    
    result = g.join(pol, 
                   (g['"po_id"'] == pol['"po_id"']) & 
                   (g['"line_item_no"'] == pol['"line_item_no"']), 
                   "inner") \
        .join(poh, pol['"po_id"'] == poh['"po_id"'], "inner") \
        .join(sup, poh['"supplier_id"'] == sup['"supplier_id"'], "inner") \
        .join(mat, pol['"material_id"'] == mat['"material_id"'], "inner") \
        .join(prod, pol['"product_id"'] == prod['"product_id"'], "inner")
    
    return result.select(
        sup['"supplier_name"'],
        sup['"country"'],
        sup['"region"'],
        mat['"material_name"'],
        prod['"product_name"'],
        g['"receipt_date"'],
        pol['"expected_delivery_date"'],
        datediff("day", pol['"expected_delivery_date"'], g['"receipt_date"']).alias("delivery_delay_days")
    )


def gold_rms_procurement_lead_time(session, source_db, source_schema):
    """RMS Procurement lead time analysis - raw columns."""
    g = session.table(f"{source_db}.{source_schema}.fact_goods_receipt")
    pol = session.table(f"{source_db}.{source_schema}.fact_purchase_order_line")
    poh = session.table(f"{source_db}.{source_schema}.fact_purchase_order_header")
    sup = session.table(f"{source_db}.{source_schema}.dim_supplier_master")
    mat = session.table(f"{source_db}.{source_schema}.dim_material_master")
    prod = session.table(f"{source_db}.{source_schema}.dim_product_master")
    
    result = g.join(pol, 
                   (g['"po_id"'] == pol['"po_id"']) & 
                   (g['"line_item_no"'] == pol['"line_item_no"']), 
                   "inner") \
        .join(poh, pol['"po_id"'] == poh['"po_id"'], "inner") \
        .join(sup, poh['"supplier_id"'] == sup['"supplier_id"'], "inner") \
        .join(mat, pol['"material_id"'] == mat['"material_id"'], "inner") \
        .join(prod, pol['"product_id"'] == prod['"product_id"'], "inner")
    
    return result.select(
        sup['"supplier_name"'],
        sup['"country"'],
        sup['"region"'],
        mat['"material_name"'],
        prod['"product_name"'],
        g['"receipt_date"'],
        poh['"order_date"'],
        datediff("day", poh['"order_date"'], g['"receipt_date"']).alias("procurement_lead_time_days")
    )


def gold_rms_4(session, source_db, source_schema):
    """RMS aggregated metrics (raw aggregates only)."""
    g = session.table(f"{source_db}.{source_schema}.fact_goods_receipt")
    pol = session.table(f"{source_db}.{source_schema}.fact_purchase_order_line")
    poh = session.table(f"{source_db}.{source_schema}.fact_purchase_order_header")
    sup = session.table(f"{source_db}.{source_schema}.dim_supplier_master")
    prod = session.table(f"{source_db}.{source_schema}.dim_product_master")
    mat = session.table(f"{source_db}.{source_schema}.dim_material_master")
    
    result = g.join(pol, 
                   (g['"po_id"'] == pol['"po_id"']) & 
                   (g['"line_item_no"'] == pol['"line_item_no"']), 
                   "inner") \
        .join(poh, pol['"po_id"'] == poh['"po_id"'], "inner") \
        .join(sup, poh['"supplier_id"'] == sup['"supplier_id"'], "inner") \
        .join(prod, pol['"product_id"'] == prod['"product_id"'], "inner") \
        .join(mat, pol['"material_id"'] == mat['"material_id"'], "inner")

    grouped = result.group_by(
        sup['"supplier_name"'],
        sup['"country"'],
        sup['"region"'],
        mat['"material_name"'],
        prod['"product_name"'],
        g['"receipt_date"']
    )

    return grouped.agg(
        sum_(g['"received_qty"']).alias("total_received_qty"),
        sum_(pol['"quantity"']).alias("total_ordered_qty"),
        sum_(g['"rejected_qty"']).alias("total_rejected_qty"),
        countDistinct(g['"grn_id"']).alias("grn_count"),
        countDistinct(poh['"po_id"']).alias("po_count")
    )


# ============================================
# 6-9. PM (Production Management) FUNCTIONS
# ============================================

def gold_pm_4(session, source_db, source_schema):
    """Production metrics - raw columns for KPI calculation."""
    fpb = session.table(f"{source_db}.{source_schema}.fact_production_batch")
    fsl = session.table(f"{source_db}.{source_schema}.fact_shift_log")
    dpl = session.table(f"{source_db}.{source_schema}.dim_production_line")
    dfm = session.table(f"{source_db}.{source_schema}.dim_facility_master")
    
    result = fpb.join(fsl, fpb['"batch_id"'] == fsl['"batch_id"'], "inner") \
        .join(dpl, fsl['"line_id"'] == dpl['"line_id"'], "inner") \
        .join(dfm, dpl['"facility_id"'] == dfm['"facility_id"'], "inner")
    
    return result.select(
        dfm['"country"'],
        dfm['"state"'],
        dfm['"city"'],
        dfm['"location"'],
        dfm['"name"'].alias("facility_name"),
        fpb['"good_qty"'],
        fpb['"produced_qty"'],
        fpb['"scrap_qty"'],
        fpb['"raw_material_used_qty"'],
        fpb['"start_time"'],
        fpb['"end_time"']
    )


def gold_pm_plan_adherence(session, source_db, source_schema):
    """Production plan adherence - raw columns."""
    psl = session.table(f"{source_db}.{source_schema}.fact_production_schedule_line")
    psh = session.table(f"{source_db}.{source_schema}.fact_production_schedule_header")
    dpl = session.table(f"{source_db}.{source_schema}.dim_production_line")
    dfm = session.table(f"{source_db}.{source_schema}.dim_facility_master")
    
    result = psl.join(psh, psl['"schedule_id"'] == psh['"schedule_id"'], "inner") \
        .join(dpl, psh['"line_id"'] == dpl['"line_id"'], "inner") \
        .join(dfm, dpl['"facility_id"'] == dfm['"facility_id"'], "inner")
    
    return result.select(
        dfm['"country"'],
        dfm['"state"'],
        dfm['"city"'],
        dfm['"location"'],
        dfm['"name"'].alias("facility_name"),
        psl['"planned_qty"'],
        psl['"actual_qty"']
    )


def gold_pm_downtime_per_shift_aggregated(session, source_db, source_schema):
    """Production downtime per shift - aggregated metrics."""
    fle = session.table(f"{source_db}.{source_schema}.fact_line_efficiency_log")
    fsl = session.table(f"{source_db}.{source_schema}.fact_shift_log")
    fedl = session.table(f"{source_db}.{source_schema}.fact_equipment_downtime_log")
    dpl = session.table(f"{source_db}.{source_schema}.dim_production_line")
    dfm = session.table(f"{source_db}.{source_schema}.dim_facility_master")
    
    result = fle.join(fsl, fle['"shift_id"'] == fsl['"shift_id"'], "inner") \
        .join(fedl, fsl['"shift_id"'] == fedl['"log_id"'], "inner") \
        .join(dpl, fle['"line_id"'] == dpl['"line_id"'], "inner") \
        .join(dfm, dpl['"facility_id"'] == dfm['"facility_id"'], "inner")
    
    result = result.with_column("facility_name", dfm['"name"'])
    
    grouped = result.group_by(
        dfm['"country"'],
        dfm['"state"'],
        dfm['"city"'],
        dfm['"location"'],
        col("facility_name")
    )
    
    return grouped.agg(
        sum_(datediff("second", fedl['"start_time"'], fedl['"end_time"']) / 60).alias("total_downtime_minutes"),
        count(fle['"shift_id"']).alias("total_shifts")
    )


def gold_pm_downtime_per_shift_oeee(session, source_db, source_schema):
    """Production OEEE percentage - separate function for non-aggregated column."""
    fle = session.table(f"{source_db}.{source_schema}.fact_line_efficiency_log")
    fsl = session.table(f"{source_db}.{source_schema}.fact_shift_log")
    dpl = session.table(f"{source_db}.{source_schema}.dim_production_line")
    dfm = session.table(f"{source_db}.{source_schema}.dim_facility_master")
    
    result = fle.join(fsl, fle['"shift_id"'] == fsl['"shift_id"'], "inner") \
        .join(dpl, fle['"line_id"'] == dpl['"line_id"'], "inner") \
        .join(dfm, dpl['"facility_id"'] == dfm['"facility_id"'], "inner")
    
    return result.select(
        dfm['"country"'],
        dfm['"state"'],
        dfm['"city"'],
        dfm['"location"'],
        dfm['"name"'].alias("facility_name"),
        fle['"oeee_pct"']
    )


# ============================================
# 10-15. DSC (Distribution & Supply Chain) FUNCTIONS
# ============================================

def gold_dsc_3(session, source_db, source_schema):
    """Distribution & Supply Chain metrics - raw columns for KPI calculation."""
    fpi = session.table(f"{source_db}.{source_schema}.fact_product_inventory")
    dwm = session.table(f"{source_db}.{source_schema}.dim_warehouse_master")
    dpm = session.table(f"{source_db}.{source_schema}.dim_product_master")
    fsol = session.table(f"{source_db}.{source_schema}.fact_sales_order_line")
    
    result = fpi.join(dwm, fpi['"warehouse_id"'] == dwm['"warehouse_id"'], "inner") \
        .join(dpm, fpi['"product_id"'] == dpm['"product_id"'], "inner") \
        .join(fsol, fpi['"product_id"'] == fsol['"product_id"'], "left")
    
    result = result.with_column("date", fpi['"updated_date"'])
    
    grouped = result.group_by(
        dwm['"warehouse_name"'],
        dpm['"product_name"'],
        col("date")
    )
    
    return grouped.agg(
        sum_(fpi['"quantity_on_hand"']).alias("total_quantity_on_hand"),
        sum_(dwm['"capacity_units"']).alias("total_capacity_units"),
        sum_(fsol['"cogs"']).alias("total_cogs")
    )


def gold_dsc_3_inventory_days(session, source_db, source_schema):
    """Distribution & Supply Chain - separate function for inventory days calculation."""
    fpi = session.table(f"{source_db}.{source_schema}.fact_product_inventory")
    dwm = session.table(f"{source_db}.{source_schema}.dim_warehouse_master")
    dpm = session.table(f"{source_db}.{source_schema}.dim_product_master")
    fsol = session.table(f"{source_db}.{source_schema}.fact_sales_order_line")
    
    result = fpi.join(dwm, fpi['"warehouse_id"'] == dwm['"warehouse_id"'], "inner") \
        .join(dpm, fpi['"product_id"'] == dpm['"product_id"'], "inner") \
        .join(fsol, fpi['"product_id"'] == fsol['"product_id"'], "left")
    
    return result.select(
        dwm['"warehouse_name"'],
        dpm['"product_name"'],
        fpi['"updated_date"'].alias("date"),
        fpi['"quantity_on_hand"'],
        fsol['"cogs"']
    )


def gold_dsc_damaged_return(session, source_db, source_schema):
    """DSC Damaged goods and returns analysis - raw columns."""
    fos = session.table(f"{source_db}.{source_schema}.fact_outbound_shipment")
    dcm = session.table(f"{source_db}.{source_schema}.dim_carrier_master")
    fsl = session.table(f"{source_db}.{source_schema}.fact_shipment_line")
    fro = session.table(f"{source_db}.{source_schema}.fact_return_order")
    fpol = session.table(f"{source_db}.{source_schema}.fact_purchase_order_line")
    fpoh = session.table(f"{source_db}.{source_schema}.fact_purchase_order_header")
    dsm = session.table(f"{source_db}.{source_schema}.dim_supplier_master")
    
    result = fos.join(dcm, fos['"carrier_id"'] == dcm['"carrier_id"'], "inner") \
        .join(fsl, fos['"shipment_id"'] == fsl['"shipment_id"'], "inner") \
        .join(fro, (fro['"product_id"'] == fsl['"product_id"']) & (fro['"warehouse_id"'] == fos['"origin_warehouse_id"']), "left") \
        .join(fpol, fpol['"product_id"'] == fsl['"product_id"'], "left") \
        .join(fpoh, fpoh['"po_id"'] == fpol['"po_id"'], "left") \
        .join(dsm, dsm['"supplier_id"'] == fpoh['"supplier_id"'], "left")
    
    grouped = result.group_by(
        dcm['"carrier_name"'],
        dsm['"supplier_name"']
    )
    
    return grouped.agg(
        sum_(fsl['"quantity"']).alias("total_shipped_quantity"),
        sum_(fro['"quantity"']).alias("total_returned_quantity"),
        sum_(when(fro['"condition_on_return"'] == lit("Damaged"), fro['"quantity"']).otherwise(lit(0))).alias("total_damaged_quantity")
    )


def gold_dsc_transport_cost_per_unit(session, source_db, source_schema):
    """DSC Transportation cost per unit - raw columns."""
    ftc = session.table(f"{source_db}.{source_schema}.fact_transportation_cost")
    dcm = session.table(f"{source_db}.{source_schema}.dim_carrier_master")
    dtr = session.table(f"{source_db}.{source_schema}.dim_truck_route")
    fos = session.table(f"{source_db}.{source_schema}.fact_outbound_shipment")
    
    result = ftc.join(dcm, ftc['"carrier_id"'] == dcm['"carrier_id"'], "inner") \
        .join(dtr, ftc['"route_id"'] == dtr['"route_id"'], "inner") \
        .join(fos, (ftc['"carrier_id"'] == fos['"carrier_id"']) & (ftc['"shipment_date"'] <= fos['"planned_ship_date"']), "left")
    
    grouped = result.group_by(
        dcm['"carrier_name"'],
        dtr['"route_type"'],
        ftc['"shipment_date"']
    )
    
    return grouped.agg(
        sum_(ftc['"total_cost"']).alias("total_transportation_cost"),
        sum_(fos['"total_qty"']).alias("total_quantity")
    )


def gold_dsc_on_time_shipment_rate(session, source_db, source_schema):
    """DSC On-time shipment rate - raw columns."""
    fos = session.table(f"{source_db}.{source_schema}.fact_outbound_shipment")
    dcm = session.table(f"{source_db}.{source_schema}.dim_carrier_master")
    ddc = session.table(f"{source_db}.{source_schema}.dim_distribution_center")
    
    result = fos.join(dcm, fos['"carrier_id"'] == dcm['"carrier_id"'], "inner") \
        .join(ddc, fos['"origin_warehouse_id"'] == ddc['"dc_id"'], "inner")
    
    result = result.with_column("distribution_center", ddc['"dc_name"'])
    result = result.with_column("month", to_char(fos['"planned_ship_date"'], lit("YYYY-MM")))
    
    grouped = result.group_by(
        dcm['"carrier_name"'],
        col("distribution_center"),
        col("month")
    )
    
    return grouped.agg(
        count(when(fos['"ship_date"'] <= fos['"planned_ship_date"'], lit(1))).alias("on_time_shipments"),
        count(lit(1)).alias("total_shipments")
    )


def gold_dsc_inbound_delivery_accuracy(session, source_db, source_schema):
    """DSC Inbound delivery accuracy - raw columns."""
    fis = session.table(f"{source_db}.{source_schema}.fact_inbound_shipment")
    dsm = session.table(f"{source_db}.{source_schema}.dim_supplier_master")
    dwm = session.table(f"{source_db}.{source_schema}.dim_warehouse_master")
    
    result = fis.join(dsm, fis['"source_id"'] == dsm['"supplier_id"'], "inner") \
        .join(dwm, fis['"destination_warehouse_id"'] == dwm['"warehouse_id"'], "inner")
    
    result = result.with_column("date", fis['"actual_delivery_date"'])
    
    grouped = result.group_by(
        dsm['"supplier_name"'],
        dwm['"warehouse_name"'],
        col("date")
    )
    
    return grouped.agg(
        count(when(fis['"actual_delivery_date"'] <= fis['"expected_delivery_date"'], lit(1))).alias("on_time_deliveries"),
        count(lit(1)).alias("total_deliveries")
    )


# ============================================
# 16-21. REUS (Retail & End User Sales) FUNCTIONS
# ============================================

def gold_reus_customer_retention_monthly_totals(session, source_db, source_schema):
    """Customer retention monthly analysis - aggregated totals."""
    fso = session.table(f"{source_db}.{source_schema}.fact_sales_order")
    fcv = session.table(f"{source_db}.{source_schema}.fact_customer_visit")
    
    customer_orders = fso.select(
        col('"customer_id"').alias("co_customer_id"),
        col('"channel"').alias("co_channel"),
        to_char(col('"order_date"'), lit("YYYY-MM")).alias("co_month_year")
    )
    
    customer_visits_device = fcv.select(
        col('"customer_id"').alias("cvd_customer_id"),
        col('"channel"').alias("cvd_channel"),
        col('"device_type"').alias("cvd_device_type"),
        to_char(col('"visit_timestamp"'), lit("YYYY-MM")).alias("cvd_month_year")
    )
    
    customer_month_visits = customer_orders.join(
        customer_visits_device,
        (col("co_customer_id") == col("cvd_customer_id")) & 
        (col("co_channel") == col("cvd_channel")) & 
        (col("co_month_year") == col("cvd_month_year")),
        "left"
    ).select(
        col("co_customer_id").alias("customer_id"),
        col("co_channel").alias("channel"),
        coalesce(col("cvd_device_type"), lit("Unknown")).alias("device_type"),
        col("co_month_year").alias("month_year")
    )
    
    monthly_totals = customer_month_visits.group_by(
        col("channel"), 
        col("device_type"), 
        col("month_year")
    ).agg(
        countDistinct(col("customer_id")).alias("total_customers")
    )
    
    return monthly_totals


def gold_reus_customer_retention_monthly_retained(session, source_db, source_schema):
    """Customer retention monthly analysis - retained customers."""
    fso = session.table(f"{source_db}.{source_schema}.fact_sales_order")
    fcv = session.table(f"{source_db}.{source_schema}.fact_customer_visit")
    
    customer_orders = fso.select(
        col('"customer_id"').alias("co_customer_id"),
        col('"channel"').alias("co_channel"),
        to_char(col('"order_date"'), lit("YYYY-MM")).alias("co_month_year")
    )
    
    customer_visits_device = fcv.select(
        col('"customer_id"').alias("cvd_customer_id"),
        col('"channel"').alias("cvd_channel"),
        col('"device_type"').alias("cvd_device_type"),
        to_char(col('"visit_timestamp"'), lit("YYYY-MM")).alias("cvd_month_year")
    )
    
    customer_month_visits = customer_orders.join(
        customer_visits_device,
        (col("co_customer_id") == col("cvd_customer_id")) & 
        (col("co_channel") == col("cvd_channel")) & 
        (col("co_month_year") == col("cvd_month_year")),
        "left"
    ).select(
        col("co_customer_id").alias("customer_id"),
        col("co_channel").alias("channel"),
        coalesce(col("cvd_device_type"), lit("Unknown")).alias("device_type"),
        col("co_month_year").alias("month_year")
    )
    
    curr = customer_month_visits.select(
        col("customer_id").alias("curr_customer_id"),
        col("channel").alias("curr_channel"),
        col("device_type").alias("curr_device_type"),
        col("month_year").alias("curr_month_year"),
        to_date(concat(substr(col("month_year"), 1, 4), lit("-"), substr(col("month_year"), 6, 2), lit("-01"))).alias("curr_date")
    )
    
    prev = customer_month_visits.select(
        col("customer_id").alias("prev_customer_id"),
        col("channel").alias("prev_channel"),
        col("device_type").alias("prev_device_type"),
        col("month_year").alias("prev_month_year"),
        to_date(concat(substr(col("month_year"), 1, 4), lit("-"), substr(col("month_year"), 6, 2), lit("-01"))).alias("prev_date")
    )
    
    pairs = curr.join(
        prev,
        (col("curr_channel") == col("prev_channel")) &
        (col("curr_device_type") == col("prev_device_type")) &
        (col("curr_customer_id") == col("prev_customer_id")) &
        (datediff("day", col("prev_date"), col("curr_date")) >= 28) &
        (datediff("day", col("prev_date"), col("curr_date")) <= 31),
        "inner"
    )
    
    result = pairs.group_by(
        col("curr_channel").alias("channel"),
        col("curr_device_type").alias("device_type"),
        col("curr_month_year").alias("month")
    ).agg(
        countDistinct(col("curr_customer_id")).alias("retained_customers")
    )
    
    return result


def gold_reus_customer_retention_monthly_new(session, source_db, source_schema):
    """Customer retention monthly analysis - new customers."""
    fso = session.table(f"{source_db}.{source_schema}.fact_sales_order")
    fcv = session.table(f"{source_db}.{source_schema}.fact_customer_visit")
    
    customer_orders = fso.select(
        col('"customer_id"').alias("co_customer_id"),
        col('"channel"').alias("co_channel"),
        to_char(col('"order_date"'), lit("YYYY-MM")).alias("co_month_year")
    )
    
    customer_visits_device = fcv.select(
        col('"customer_id"').alias("cvd_customer_id"),
        col('"channel"').alias("cvd_channel"),
        col('"device_type"').alias("cvd_device_type"),
        to_char(col('"visit_timestamp"'), lit("YYYY-MM")).alias("cvd_month_year")
    )
    
    customer_month_visits = customer_orders.join(
        customer_visits_device,
        (col("co_customer_id") == col("cvd_customer_id")) & 
        (col("co_channel") == col("cvd_channel")) & 
        (col("co_month_year") == col("cvd_month_year")),
        "left"
    ).select(
        col("co_customer_id").alias("customer_id"),
        col("co_channel").alias("channel"),
        coalesce(col("cvd_device_type"), lit("Unknown")).alias("device_type"),
        col("co_month_year").alias("month_year")
    )
    
    curr = customer_month_visits.select(
        col("customer_id").alias("curr_customer_id"),
        col("channel").alias("curr_channel"),
        col("device_type").alias("curr_device_type"),
        col("month_year").alias("curr_month_year")
    )
    
    prev = customer_month_visits.select(
        col("customer_id").alias("prev_customer_id"),
        col("channel").alias("prev_channel"),
        col("device_type").alias("prev_device_type"),
        col("month_year").alias("prev_month_year")
    )
    
    new_customers = curr.join(
        prev,
        (col("curr_customer_id") == col("prev_customer_id")) &
        (col("curr_channel") == col("prev_channel")) &
        (col("curr_device_type") == col("prev_device_type")) &
        (col("prev_month_year") < col("curr_month_year")),
        "left"
    ).filter(
        col("prev_customer_id").isNull()
    )
    
    result = new_customers.group_by(
        col("curr_channel").alias("channel"),
        col("curr_device_type").alias("device_type"),
        col("curr_month_year").alias("month")
    ).agg(
        countDistinct(col("curr_customer_id")).alias("new_customers")
    )
    
    return result


def gold_reus_product_return_analysis(session, source_db, source_schema):
    """Product return analysis - raw columns."""
    fro = session.table(f"{source_db}.{source_schema}.fact_return_order")
    fso = session.table(f"{source_db}.{source_schema}.fact_sales_order")
    dc = session.table(f"{source_db}.{source_schema}.dim_channel")
    dpm = session.table(f"{source_db}.{source_schema}.dim_product_master")
    dmc = session.table(f"{source_db}.{source_schema}.dim_material_category")
    
    result = fro.join(fso, fro['"original_sales_order_id"'] == fso['"sales_order_id"'], "inner") \
        .join(dc, fro['"channel_id"'] == dc['"channel_id"'], "inner") \
        .join(dpm, fro['"product_id"'] == dpm['"product_id"'], "inner") \
        .join(dmc, dpm['"category_id"'] == dmc['"category_id"'], "inner")
    
    result = result.with_column("product_category", dmc['"category_name"'])
    result = result.with_column("date", fro['"return_date"'])
    
    grouped = result.group_by(
        dc['"channel_name"'],
        col("product_category"),
        dpm['"product_name"'],
        col("date")
    )
    
    return grouped.agg(
        sum_(fro['"refund_amount"']).alias("total_refund_amount"),
        sum_(fso['"total_amount"']).alias("total_sales_amount"),
        countDistinct(fro['"return_id"']).alias("total_returns"),
        countDistinct(fso['"sales_order_id"']).alias("total_orders")
    )


def gold_reus_average_order_value_analysis(session, source_db, source_schema):
    """Average order value analysis - raw columns."""
    fso = session.table(f"{source_db}.{source_schema}.fact_sales_order")
    dro = session.table(f"{source_db}.{source_schema}.dim_retail_outlet")
    dcm = session.table(f"{source_db}.{source_schema}.dim_customer_master")
    drh = session.table(f"{source_db}.{source_schema}.dim_region_hierarchy")
    
    result = fso.join(dro, fso['"outlet_id"'] == dro['"outlet_id"'], "inner") \
        .join(dcm, fso['"customer_id"'] == dcm['"customer_id"'], "inner") \
        .join(drh, dro['"region_id"'] == drh['"region_id"'], "inner")
    
    result = result.with_column("date", fso['"order_date"'])
    
    grouped = result.group_by(
        fso['"country"'],
        drh['"region"'],
        fso['"channel"'],
        dro['"outlet_name"'],
        dcm['"customer_name"'],
        col("date")
    )
    
    return grouped.agg(
        sum_(fso['"total_amount"']).alias("total_order_amount"),
        count(fso['"sales_order_id"']).alias("total_orders")
    )


def gold_reus_sales_per_outlet_analysis(session, source_db, source_schema):
    """Sales per outlet analysis - raw columns."""
    fso = session.table(f"{source_db}.{source_schema}.fact_sales_order")
    dro = session.table(f"{source_db}.{source_schema}.dim_retail_outlet")
    drh = session.table(f"{source_db}.{source_schema}.dim_region_hierarchy")
    
    result = fso.join(dro, fso['"outlet_id"'] == dro['"outlet_id"'], "inner") \
        .join(drh, dro['"region_id"'] == drh['"region_id"'], "inner")
    
    result = result.with_column("date", fso['"order_date"'])
    
    grouped = result.group_by(
        fso['"country"'],
        drh['"region"'],
        fso['"channel"'],
        col("date")
    )
    
    return grouped.agg(
        countDistinct(fso['"outlet_id"']).alias("total_outlets"),
        sum_(fso['"total_amount"']).alias("total_sales")
    )


# ============================================
# 22-27. CFM (Consumer & Field Marketing) FUNCTIONS
# ============================================

def gold_cfm_conversion_rate(session, source_db, source_schema):
    """CFM Conversion rate - raw columns."""
    fai = session.table(f"{source_db}.{source_schema}.fact_ad_impression")
    
    result = fai.with_column("channel", fai['"platform"'])
    result = result.with_column("date", fai['"impression_date"'])
    
    grouped = result.group_by(
        col("channel"),
        col("date")
    )
    
    return grouped.agg(
        sum_(fai['"conversions"']).alias("total_conversions"),
        sum_(fai['"impressions"']).alias("total_impressions")
    )


def gold_cfm_cost_per_conversion_spend(session, source_db, source_schema):
    """CFM Cost per conversion - campaign spend aggregated."""
    fms = session.table(f"{source_db}.{source_schema}.fact_marketing_spend")
    fai = session.table(f"{source_db}.{source_schema}.fact_ad_impression")
    dcm = session.table(f"{source_db}.{source_schema}.dim_campaign_master")
    
    campaign_spend = fms.group_by(col('"campaign_id"')).agg(
        sum_(col('"amount"')).alias("total_spend_amount")
    ).select(
        col('"campaign_id"').alias("cs_campaign_id"),
        col("total_spend_amount")
    )
    
    campaign_impressions = fai.group_by(col('"campaign_id"')).agg(
        sum_(col('"conversions"')).alias("total_conversions")
    ).select(
        col('"campaign_id"').alias("ci_campaign_id"),
        col("total_conversions")
    )
    
    campaign_details = dcm.select(
        col('"campaign_id"').alias("cd_campaign_id"),
        col('"campaign_name"'),
        col('"start_date"'),
        col('"end_date"')
    )
    
    result = campaign_details \
        .join(campaign_spend, col("cd_campaign_id") == col("cs_campaign_id"), "left") \
        .join(campaign_impressions, col("cd_campaign_id") == col("ci_campaign_id"), "left")
    
    return result.select(
        col('"campaign_name"').alias("campaign"),
        col('"start_date"'),
        col('"end_date"'),
        coalesce(col("total_spend_amount"), lit(0)).alias("total_spend_amount"),
        coalesce(col("total_conversions"), lit(0)).alias("total_conversions")
    )


def gold_cfm_cost_per_conversion_engagement(session, source_db, source_schema):
    """CFM Cost per conversion - engagement time calculation."""
    fai = session.table(f"{source_db}.{source_schema}.fact_ad_impression")
    dcm = session.table(f"{source_db}.{source_schema}.dim_campaign_master")
    
    campaign_impressions = fai.group_by(col('"campaign_id"')).agg(
        sum_(col('"impressions"')).alias("total_impressions")
    ).select(
        col('"campaign_id"').alias("ci_campaign_id"),
        col("total_impressions")
    )
    
    campaign_details = dcm.select(
        col('"campaign_id"').alias("cd_campaign_id"),
        col('"campaign_name"'),
        col('"start_date"'),
        col('"end_date"'),
        datediff("day", col('"start_date"'), col('"end_date"')).alias("time_engaged_days")
    )
    
    result = campaign_details \
        .join(campaign_impressions, col("cd_campaign_id") == col("ci_campaign_id"), "left")
    
    return result.select(
        col('"campaign_name"').alias("campaign"),
        col('"start_date"'),
        col('"end_date"'),
        col("time_engaged_days"),
        coalesce(col("total_impressions"), lit(0)).alias("total_impressions")
    )


def gold_cfm_survey_response_rate(session, source_db, source_schema):
    """CFM Survey response rate - raw columns."""
    fcs = session.table(f"{source_db}.{source_schema}.fact_consumer_survey")
    
    result = fcs.with_column("date", col('"survey_date"'))
    
    grouped = result.group_by(
        col('"channel"'),
        col('"region"'),
        col("date")
    )
    
    return grouped.agg(
        count(when(col('"feedback_text"').isNotNull(), lit(1))).alias("responses_with_feedback"),
        count(col('"survey_id"')).alias("total_surveys")
    )


def gold_cfm_customer_satisfaction_score(session, source_db, source_schema):
    """CFM Customer satisfaction score - raw data."""
    cs = session.table(f"{source_db}.{source_schema}.fact_consumer_survey")
    pm = session.table(f"{source_db}.{source_schema}.dim_product_master")
    mc = session.table(f"{source_db}.{source_schema}.dim_material_category")
    
    result = cs.join(pm, cs['"product_id"'] == pm['"product_id"'], "inner") \
        .join(mc, pm['"category_id"'] == mc['"category_id"'], "inner")
    
    return result.select(
        mc['"category_name"'].alias("product_category"),
        pm['"product_name"'],
        cs['"survey_date"'].alias("date"),
        cs['"satisfaction_score"']
    )


def gold_cfm_trade_promotion_effectiveness(session, source_db, source_schema):
    """CFM Trade promotion effectiveness - raw columns."""
    pp = session.table(f"{source_db}.{source_schema}.fact_promotion_plan")
    pm = session.table(f"{source_db}.{source_schema}.dim_promotion_master")
    dc = session.table(f"{source_db}.{source_schema}.dim_channel")
    tp = session.table(f"{source_db}.{source_schema}.fact_trade_promotion")
    
    result = pp.join(pm, pp['"promotion_id"'] == pm['"promotion_id"'], "inner") \
        .join(dc, pp['"channel_id"'] == dc['"channel_id"'], "inner") \
        .join(tp, pp['"product_id"'] == tp['"product_id"'], "left")
    
    result = result.with_column("date", pp['"period_start"'])
    
    grouped = result.group_by(
        pm['"promotion_name"'],
        dc['"channel_name"'],
        col("date")
    )
    
    return grouped.agg(
        sum_(coalesce(tp['"actual_lift_pct"'], lit(0))).alias("total_actual_lift_pct"),
        sum_(pp['"target_lift_pct"']).alias("total_target_lift_pct")
    )


# ============================================
# 28-30. FC (Finance & Controlling) FUNCTIONS
# ============================================

def gold_fc_invoice_accuracy_analysis(session, source_db, source_schema):
    """Calculate accurate and total invoices by snapshot_date and payment_method."""
    fact_invoice = session.table(f"{source_db}.{source_schema}.fact_invoice")
    fact_payment = session.table(f"{source_db}.{source_schema}.fact_payment")
    
    result = fact_invoice.join(
        fact_payment,
        (fact_invoice['"customer_id"'] == fact_payment['"customer_id"']) & 
        (fact_invoice['"amount_paid"'] == fact_payment['"amount"']),
        "left"
    )
    
    aggregated_result = result.group_by(
        fact_invoice['"snapshot_date"'],
        fact_payment['"payment_method"']
    ).agg(
        count(
            when(
                (fact_invoice['"payment_status"'] == lit("Paid")) & 
                (fact_invoice['"difference_days"'] <= lit(0)),
                lit(1)
            )
        ).alias("Accurate_Invoices"),
        count(fact_invoice['"invoice_id"']).alias("Total_Invoices")
    )
    
    return aggregated_result.select(
        col('"snapshot_date"'),
        col('"payment_method"'),
        col("Accurate_Invoices"),
        col("Total_Invoices")
    ).sort(col('"snapshot_date"'), col('"payment_method"'))


def gold_fc_budget(session, source_db, source_schema):
    """Calculate Actual Spend vs Budget by account."""
    dim_account_master = session.table(f"{source_db}.{source_schema}.dim_account_master")
    fact_budget = session.table(f"{source_db}.{source_schema}.fact_budget")
    fact_general_ledger = session.table(f"{source_db}.{source_schema}.fact_general_ledger")
    
    actual_spend = fact_general_ledger.group_by(col('"account_id"')).agg(
        (sum_(fact_general_ledger['"debit"']) - sum_(fact_general_ledger['"credit"'])).alias("actual_spend_raw")
    ).select(
        col('"account_id"').alias("as_account_id"),
        col("actual_spend_raw")
    )
    
    budget_data = fact_budget.filter(
        fact_budget['"approved_flag"'] == lit(True)
    ).group_by(col('"account_id"')).agg(
        sum_(fact_budget['"budget_amount"']).alias("Budget")
    ).select(
        col('"account_id"').alias("bd_account_id"),
        col("Budget")
    )
    
    result = dim_account_master.join(
        actual_spend, 
        dim_account_master['"account_id"'] == col("as_account_id"), 
        "left"
    ).join(
        budget_data,
        dim_account_master['"account_id"'] == col("bd_account_id"),
        "left"
    )
    
    final_result = result.select(
        dim_account_master['"account_name"'],
        when(
            dim_account_master['"account_type"'] == lit("Expense"),
            coalesce(col("actual_spend_raw"), lit(0))
        ).when(
            dim_account_master['"account_type"'] == lit("Revenue"),
            coalesce(-col("actual_spend_raw"), lit(0))
        ).otherwise(lit(0)).alias("Actual_Spend"),
        coalesce(col("Budget"), lit(0)).alias("Budget")
    ).filter(
        dim_account_master['"active_flag"'] == lit(True)
    )
    
    return final_result.sort(col('"account_name"'))


def gold_fc_payment_timeliness_analysis(session, source_db, source_schema):
    """Calculate On-Time Payments and Total Payments by source_type and date."""
    fact_payment = session.table(f"{source_db}.{source_schema}.fact_payment")
    fact_invoice = session.table(f"{source_db}.{source_schema}.fact_invoice")
    
    result = fact_payment.join(
        fact_invoice,
        (fact_payment['"source_type"'] == lit("Invoice")) & 
        (fact_payment['"source_id"'] == fact_invoice['"invoice_id"']) & 
        (fact_payment['"customer_id"'] == fact_invoice['"customer_id"']),
        "left"
    )
    
    aggregated_result = result.group_by(
        fact_payment['"source_type"'],
        fact_payment['"payment_date"']
    ).agg(
        count(
            when(
                (fact_payment['"source_type"'] != lit("Invoice")) |
                ((fact_payment['"source_type"'] == lit("Invoice")) & 
                 (fact_payment['"payment_date"'] <= fact_invoice['"due_date"'])),
                lit(1)
            )
        ).alias("On_Time_Payments"),
        count(fact_payment['"payment_id"']).alias("Total_Payments")
    )
    
    return aggregated_result.select(
        col('"source_type"'),
        col('"payment_date"'),
        col("On_Time_Payments"), 
        col("Total_Payments")
    ).sort(col('"payment_date"'), col('"source_type"'))


# ============================================
# 31. SESG (Sustainability & ESG) FUNCTIONS
# ============================================

def gold_sesg_emission_production_analysis(session, source_db, source_schema):
    """Calculate CO2e emissions by source type and correlate with production units."""
    fact_emission_record = session.table(f"{source_db}.{source_schema}.fact_emission_record")
    fact_production_batch = session.table(f"{source_db}.{source_schema}.fact_production_batch")
    
    production_by_date = fact_production_batch.with_column(
        "production_date", 
        to_date(fact_production_batch['"start_time"'])
    ).group_by(col("production_date")).agg(
        sum_(col('"produced_qty"')).alias("daily_units_produced")
    )
    
    emission_by_date_source = fact_emission_record.group_by(
        col('"record_date"'),
        col('"source_type"')
    ).agg(
        sum_(col('"co2e_amount"')).alias("daily_co2e_amount")
    ).select(
        col('"record_date"').alias("emission_date"),
        col('"source_type"').alias("emission_source_type"),
        col("daily_co2e_amount")
    )
    
    result = emission_by_date_source.join(
        production_by_date,
        col("emission_date") == col("production_date"),
        "left"
    )
    
    final_result = result.group_by(col("emission_source_type")).agg(
        sum_(col("daily_co2e_amount")).alias("CO2e_Amount"),
        sum_(col("daily_units_produced")).alias("Units_Produced")
    )
    
    return final_result.select(
        col("emission_source_type").alias("source_type"),
        coalesce(col("CO2e_Amount"), lit(0)).alias("CO2e_Amount"),
        coalesce(col("Units_Produced"), lit(0)).alias("Units_Produced")
    ).sort(col("source_type"))


# ============================================
# FUNCTION MAP
# ============================================

FUNCTION_MAP = {
    "GOLD_DIM_DATE": gold_dim_date,
    "GOLD_RMS_FACT_SUSTAINABILITY": gold_rms_fact_sustainability,
    "GOLD_RMS_DELIVERY_DELAY": gold_rms_delivery_delay,
    "GOLD_RMS_PROCUREMENT_LEAD_TIME": gold_rms_procurement_lead_time,
    "GOLD_RMS_4": gold_rms_4,
    "GOLD_PM_4": gold_pm_4,
    "GOLD_PM_PLAN_ADHERENCE": gold_pm_plan_adherence,
    "GOLD_PM_DOWNTIME_PER_SHIFT_AGGREGATED": gold_pm_downtime_per_shift_aggregated,
    "GOLD_PM_DOWNTIME_PER_SHIFT_OEEE": gold_pm_downtime_per_shift_oeee,
    "GOLD_DSC_3": gold_dsc_3,
    "GOLD_DSC_3_INVENTORY_DAYS": gold_dsc_3_inventory_days,
    "GOLD_DSC_DAMAGED_RETURN": gold_dsc_damaged_return,
    "GOLD_DSC_TRANSPORT_COST_PER_UNIT": gold_dsc_transport_cost_per_unit,
    "GOLD_DSC_ON_TIME_SHIPMENT_RATE": gold_dsc_on_time_shipment_rate,
    "GOLD_DSC_INBOUND_DELIVERY_ACCURACY": gold_dsc_inbound_delivery_accuracy,
    "GOLD_REUS_CUSTOMER_RETENTION_MONTHLY_TOTALS": gold_reus_customer_retention_monthly_totals,
    "GOLD_REUS_CUSTOMER_RETENTION_MONTHLY_RETAINED": gold_reus_customer_retention_monthly_retained,
    "GOLD_REUS_CUSTOMER_RETENTION_MONTHLY_NEW": gold_reus_customer_retention_monthly_new,
    "GOLD_REUS_PRODUCT_RETURN_ANALYSIS": gold_reus_product_return_analysis,
    "GOLD_REUS_AVERAGE_ORDER_VALUE_ANALYSIS": gold_reus_average_order_value_analysis,
    "GOLD_REUS_SALES_PER_OUTLET_ANALYSIS": gold_reus_sales_per_outlet_analysis,
    "GOLD_CFM_CONVERSION_RATE": gold_cfm_conversion_rate,
    "GOLD_CFM_COST_PER_CONVERSION_SPEND": gold_cfm_cost_per_conversion_spend,
    "GOLD_CFM_COST_PER_CONVERSION_ENGAGEMENT": gold_cfm_cost_per_conversion_engagement,
    "GOLD_CFM_SURVEY_RESPONSE_RATE": gold_cfm_survey_response_rate,
    "GOLD_CFM_CUSTOMER_SATISFACTION_SCORE": gold_cfm_customer_satisfaction_score,
    "GOLD_CFM_TRADE_PROMOTION_EFFECTIVENESS": gold_cfm_trade_promotion_effectiveness,
    "GOLD_FC_INVOICE_ACCURACY_ANALYSIS": gold_fc_invoice_accuracy_analysis,
    "GOLD_FC_BUDGET": gold_fc_budget,
    "GOLD_FC_PAYMENT_TIMELINESS_ANALYSIS": gold_fc_payment_timeliness_analysis,
    "GOLD_SESG_EMISSION_PRODUCTION_ANALYSIS": gold_sesg_emission_production_analysis
}


# ============================================
# EXECUTION ENGINE
# ============================================

def run_aggregation(session, function_name, source_db, source_schema, target_db, target_schema):
    """
    Run a single aggregation function and write to target location.
    
    Args:
        session: Snowpark session
        function_name: Name of the aggregation (e.g., 'GOLD_DIM_DATE')
        source_db: Source database name (Silver layer)
        source_schema: Source schema name
        target_db: Target database name (Gold layer)
        target_schema: Target schema name
    
    Returns:
        dict with status, rows, and any error message
    """
    function_name_upper = function_name.upper()
    
    if function_name_upper not in FUNCTION_MAP:
        return {
            "function": function_name_upper,
            "status": "ERROR",
            "rows": 0,
            "error": f"Unknown function: {function_name_upper}. Use list_available_functions() to see available options."
        }
    
    try:
        func = FUNCTION_MAP[function_name_upper]
        df = func(session, source_db, source_schema)
        
        # Write to target
        full_table_name = f"{target_db}.{target_schema}.{function_name_upper}"
        df.write.mode("overwrite").save_as_table(full_table_name)
        row_count = df.count()
        
        return {
            "function": function_name_upper,
            "status": "SUCCESS",
            "rows": row_count,
            "error": None
        }
    except Exception as e:
        return {
            "function": function_name_upper,
            "status": "ERROR",
            "rows": 0,
            "error": str(e)
        }


def run_multiple_aggregations(session, function_names, source_db, source_schema, target_db, target_schema):
    """
    Run multiple aggregation functions.
    
    Args:
        session: Snowpark session
        function_names: List of function names to run
        source_db: Source database name
        source_schema: Source schema name
        target_db: Target database name
        target_schema: Target schema name
    
    Returns:
        List of result dictionaries
    """
    results = []
    for func_name in function_names:
        result = run_aggregation(session, func_name, source_db, source_schema, target_db, target_schema)
        results.append(result)
    return results


def run_domain_aggregations(session, domain, source_db, source_schema, target_db, target_schema):
    """
    Run all aggregation functions for a specific domain.
    
    Args:
        session: Snowpark session
        domain: Domain name (RMS, PM, DSC, REUS, CFM, FC, SESG, DIM)
        source_db: Source database name
        source_schema: Source schema name
        target_db: Target database name
        target_schema: Target schema name
    
    Returns:
        List of result dictionaries
    """
    functions = get_functions_by_domain(domain)
    if not functions:
        return [{
            "function": domain,
            "status": "ERROR",
            "rows": 0,
            "error": f"Unknown domain: {domain}. Available domains: {list_domains()}"
        }]
    
    return run_multiple_aggregations(session, functions, source_db, source_schema, target_db, target_schema)


def run_all_aggregations(session, source_db, source_schema, target_db, target_schema):
    """
    Run all 31 aggregation functions.
    
    Args:
        session: Snowpark session
        source_db: Source database name
        source_schema: Source schema name
        target_db: Target database name
        target_schema: Target schema name
    
    Returns:
        List of result dictionaries
    """
    return run_multiple_aggregations(session, list_available_functions(), source_db, source_schema, target_db, target_schema)


def format_results(results):
    """Format results into a readable summary string."""
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    
    summary = "\n" + "=" * 70 + "\n"
    summary += "GOLD LAYER AGGREGATION RESULTS\n"
    summary += "=" * 70 + "\n"
    summary += f"Successful: {success_count} | Errors: {error_count}\n\n"
    
    if success_count > 0:
        summary += "SUCCESSFUL:\n" + "-" * 40 + "\n"
        for r in results:
            if r["status"] == "SUCCESS":
                summary += f"  ✓ {r['function']} ({r['rows']} rows)\n"
        summary += "\n"
    
    if error_count > 0:
        summary += "ERRORS:\n" + "-" * 40 + "\n"
        for r in results:
            if r["status"] == "ERROR":
                summary += f"  ✗ {r['function']}: {r['error']}\n"
    
    summary += "=" * 70
    return summary
