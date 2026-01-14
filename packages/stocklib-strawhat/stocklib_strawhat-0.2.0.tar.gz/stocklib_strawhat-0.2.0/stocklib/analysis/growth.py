from stocklib.models.growth import GrowthMetrics


def calculate_growth(growth: GrowthMetrics) -> GrowthMetrics:
    """
    Return growth metrics from provider data.
    Since growth metrics require historical data comparison (YoY), 
    we use the provider's pre-calculated growth values.
    
    Args:
        growth: Provider-calculated growth metrics (revenue, net income, FCF, EPS growth)
        
    Returns:
        GrowthMetrics object with all growth attributes
    """
    # Simply return the provider's growth metrics as-is
    # Growth calculations require historical data (comparing current vs previous year),
    # which is best handled by the data provider who has access to historical records
    return GrowthMetrics(
        revenue_growth_yoy=growth.revenue_growth_yoy,
        net_income_growth_yoy=growth.net_income_growth_yoy,
        free_cash_flow_growth_yoy=growth.free_cash_flow_growth_yoy,
        eps_growth_yoy=growth.eps_growth_yoy
    )