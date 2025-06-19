# vBridge Output Directory Structure

This directory contains the organized output files from the vBridge 4-step KPI analysis process. Files are now organized into subdirectories based on the step that generates them.

## Directory Structure

### 📁 step1_kpi_calculation/
**Purpose**: KPI Calculation step
- This step calculates all KPIs for both periods but doesn't generate direct output files
- KPIs are calculated in memory and passed to subsequent steps

### 📁 step2_absolute_contributions/
**Purpose**: Absolute Metric Contributions (Mix Analysis)
- Contains contribution analysis for all 9 absolute metrics (bridge_type = "M")
- **Individual files**:
  - `spend_absolute_contribution.csv`
  - `total_ad_sales_absolute_contribution.csv`
  - `impressions_absolute_contribution.csv`
  - `clicks_absolute_contribution.csv`
  - `same_sku_ad_sales_absolute_contribution.csv`
  - `other_sku_sales_absolute_contribution.csv`
  - `same_sku_ad_orders_absolute_contribution.csv`
  - `other_sku_ad_orders_absolute_contribution.csv`
  - `total_ad_orders_absolute_contribution.csv`
- **Combined file**:
  - `all_absolute_metric_contributions.csv` - All absolute contributions in one file

### 📁 step3_mix_rate_contributions/
**Purpose**: Mix/Rate Contributions for Calculated KPIs
- Contains mix and rate contribution analysis for calculated KPIs (bridge_type = "MR")
- **Files**:
  - `acos_mix_rate_contributions.csv`
  - `roas_mix_rate_contributions.csv`
  - `conversion_rate_mix_rate_contributions.csv`
  - `clickthrough_rate_mix_rate_contributions.csv`
  - `cost_per_click_mix_rate_contributions.csv`

### 📁 step4_acos_roas_final/
**Purpose**: ACoS/ROAS Infinity Handling
- Contains final contributions with special infinity handling for ACoS/ROAS metrics
- **Files**:
  - `acos_roas_final_contributions.csv` - Final ACoS/ROAS contributions with infinity cases handled

### 📁 summary_reports/
**Purpose**: Summary Reports and Formatted Outputs
- Contains formatted summary reports and period comparisons
- **Files**:
  - `campaign_kpis_mom_change.csv` - Month-over-month changes with formatting
  - `p1_campaign_kpis.csv` - Period 1 campaign-level KPIs with formatting
  - `p2_campaign_kpis.csv` - Period 2 campaign-level KPIs with formatting
  - `p1_totals_kpis.csv` - Period 1 total KPIs
  - `p2_totals_kpis.csv` - Period 2 total KPIs

## Analysis Flow

1. **Step 1**: Calculate all KPIs for both periods
2. **Step 2**: Calculate absolute metric contributions (mix analysis)
3. **Step 3**: Calculate mix/rate contributions for calculated KPIs
4. **Step 4**: Apply special handling for ACoS/ROAS infinity cases
5. **Summary**: Generate formatted reports and period comparisons

## File Naming Convention

- `*_absolute_contribution.csv` - Absolute metric contributions from Step 2
- `*_mix_rate_contributions.csv` - Mix/rate contributions from Step 3
- `*_final_contributions.csv` - Final contributions with special handling from Step 4
- `p1_*` / `p2_*` - Period 1 and Period 2 specific files
- `*_mom_change.csv` - Month-over-month change analysis

This organization makes it easier to:
- Understand which step generated each file
- Debug specific analysis steps
- Locate relevant outputs for different types of analysis
- Maintain and extend the analysis pipeline 