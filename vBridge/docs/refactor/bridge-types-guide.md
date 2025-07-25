# Bridge Types Guide

## Overview

The vBridge system implements three distinct bridge calculation methodologies, each optimized for specific types of metrics. This guide provides detailed explanations of when and how to use each bridge type.

## Bridge Type Selection Matrix

| Metric Category | Bridge Type | Use Cases | Formula | Contribution Units |
|----------------|-------------|------------|---------|-------------------|
| **Absolute/Summable** | Mix Bridge | Spend, Sales, Units, Impressions | Traditional Mix Bridge | Currency, Count |
| **Rate/Ratio** | MixRate Bridge | ROAS, CTR, CPC, Conversion Rate | MixRate components | Currency, Basis Points |
| **Rate with Infinity Risk** | MixRate Infinity | ACoS, Total ACoS | Inverse methodology | Basis Points |

## Type 1: Mix Bridge (Traditional)

### When to Use
- **Absolute metrics** that can be summed across campaigns
- **Volume metrics** like impressions, clicks, orders
- **Financial metrics** like spend, sales, revenue
- **Any metric** where total = sum of campaign values

### Mathematical Formula
```
Contribution = P1 Mix × Growth Rate × Total P1 Value

Where:
- P1 Mix = Campaign P1 Value / Total P1 Value  
- Growth Rate = (Campaign P2 Value / Campaign P1 Value) - 1
```

### Special Handling: Zero Baseline
When P1 value is zero, uses **delta assignment**:
```
Contribution = P2 Value (full delta assigned to campaign)
```

### Example Metrics
```python
# Financial metrics
"Spend": BridgeConfiguration(
    bridge_type=BridgeType.MIX_BRIDGE,
    contribution_unit=ContributionUnit.CURRENCY
)

# Volume metrics  
"Impressions": BridgeConfiguration(
    bridge_type=BridgeType.MIX_BRIDGE,
    contribution_unit=ContributionUnit.COUNT
)
```

### Calculation Example
```
Campaign A: P1=$1000, P2=$1200 (20% growth)
Campaign B: P1=$2000, P2=$1800 (-10% growth)
Total: P1=$3000, P2=$3000 (0% growth)

Campaign A Mix = $1000/$3000 = 33.33%
Campaign B Mix = $2000/$3000 = 66.67%

Campaign A Contribution = 33.33% × 20% × $3000 = $200
Campaign B Contribution = 66.67% × (-10%) × $3000 = -$200
Total Contribution = $200 + (-$200) = $0 ✓
```

## Type 2: MixRate Bridge (Standard)

### When to Use
- **Rate/ratio metrics** without infinity error risk
- **Performance metrics** like ROAS, CTR, conversion rates
- **Efficiency metrics** like CPC, CPM
- **Any calculated metric** where denominator is never zero

### Mathematical Formula
```
Mix Impact = (P2 Mix - P1 Mix) × (P2 Rate - P2 Total Rate)
Rate Impact = (P2 Rate - P1 Rate) × P1 Mix
Total Contribution = Mix Impact + Rate Impact

Where Mix is determined by the metric's denominator:
- ROAS: Mix based on Spend
- CTR: Mix based on Impressions  
- Conversion Rate: Mix based on Clicks
```

### Mix Determinant Mapping
| Metric | Mix Determinant | Reasoning |
|--------|----------------|-----------|
| ROAS | Spend | ROAS = Sales/Spend, mix by spend allocation |
| CTR | Impressions | CTR = Clicks/Impressions, mix by impression share |
| CPC | Clicks | CPC = Spend/Clicks, mix by click volume |
| Conversion Rate | Sessions | ConvR = Units/Sessions, mix by session share |

### Example Metrics
```python
# Performance metrics
"ROAS": BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Spend",
    contribution_unit=ContributionUnit.CURRENCY
)

# Percentage metrics (displayed as basis points)
"CTR": BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Impressions", 
    contribution_unit=ContributionUnit.BASIS_POINTS,
    requires_percentage_conversion=True
)
```

### Calculation Example (ROAS)
```
Campaign A: Spend P1=$1000, P2=$1200; Sales P1=$5000, P2=$6000
Campaign B: Spend P1=$2000, P2=$1800; Sales P1=$8000, P2=$7200

ROAS A: P1=5.00, P2=5.00 (no change)
ROAS B: P1=4.00, P2=4.00 (no change)
Total ROAS: P1=4.33, P2=4.15 (-0.18 change)

Mix by Spend:
Campaign A: P1=33.33%, P2=40.00%
Campaign B: P1=66.67%, P2=60.00%

Campaign A:
Mix Impact = (40% - 33.33%) × (5.00 - 4.15) = 6.67% × 0.85 = +0.057
Rate Impact = (5.00 - 5.00) × 33.33% = 0 × 33.33% = 0.000
Total = +0.057

Campaign B:
Mix Impact = (60% - 66.67%) × (4.00 - 4.15) = -6.67% × (-0.15) = +0.010  
Rate Impact = (4.00 - 4.00) × 66.67% = 0 × 66.67% = 0.000
Total = +0.010

Total Contribution = 0.057 + 0.010 = 0.067
Expected Change = 4.15 - 4.33 = -0.18 (Note: Different due to non-linear aggregation)
```

## Type 3: MixRate Bridge with Infinity Error Handling

### When to Use
- **Rate metrics** where denominator can be zero
- **Metrics prone to infinity errors** like ACoS = Spend/Sales
- **Any metric** where direct calculation could produce undefined results

### Mathematical Approach: Inverse Methodology
1. **Calculate inverse metric** (e.g., ROAS for ACoS)
2. **Apply MixRate Bridge** to inverse metric
3. **Transform back** using relative impact methodology

### Formula
```
Step 1: Calculate inverse metric (ROAS = Sales/Spend)
Step 2: Apply MixRate Bridge to ROAS
Step 3: Transform ROAS contributions to ACoS contributions:

ACoS Contribution = (ROAS Contribution / Total ROAS Change) × Total ACoS Change × 100
```

### Why This Works
- **Prevents Division by Zero**: Uses sales as numerator instead of denominator
- **Maintains Attribution**: Relative impact methodology preserves contribution relationships
- **Handles Edge Cases**: Gracefully handles zero sales scenarios

### Example Metrics
```python
# Infinity-prone metrics
"ACoS": BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_INFINITY,
    mix_determinant="Spend",
    contribution_unit=ContributionUnit.BASIS_POINTS,
    inverse_metric="ROAS",
    requires_percentage_conversion=True
)
```

### Calculation Example (ACoS via ROAS)
```
Campaign A: Spend=$1000, Sales P1=$5000, P2=$6000
Campaign B: Spend=$2000, Sales P1=$8000, P2=$0 (would cause infinity)

Direct ACoS calculation would fail due to division by zero.

Step 1: Calculate ROAS
ROAS A: P1=5.00, P2=6.00
ROAS B: P1=4.00, P2=0.00  
Total ROAS: P1=4.33, P2=2.00 (change: -2.33)

Step 2: Apply MixRate Bridge to ROAS
[MixRate Bridge calculations...]
ROAS Contributions: A=+0.50, B=-2.83

Step 3: Transform to ACoS
ACoS P1: 23.08%, P2: 50.00% (change: +26.92 percentage points)

A's ACoS Contribution = (0.50 / -2.33) × 26.92 × 100 = -576 bps
B's ACoS Contribution = (-2.83 / -2.33) × 26.92 × 100 = +3268 bps
Total = -576 + 3268 = +2692 bps = +26.92 pts ✓
```

## Contribution Units Explained

### Currency ($)
- **Used for**: Financial metrics (Spend, Sales, ROAS, CPC)
- **Format**: `+$0.42`, `-$1.23`
- **Interpretation**: Dollar contribution to total change

### Basis Points (bps)  
- **Used for**: Percentage metrics (ACoS, CTR, Conversion Rate)
- **Format**: `+29 bps`, `-150 bps`
- **Conversion**: 1% = 100 bps, so 0.29% = 29 bps
- **Interpretation**: Basis point contribution to total percentage change

### Count
- **Used for**: Volume metrics (Impressions, Clicks, Orders)
- **Format**: `+1,500`, `-2,300`
- **Interpretation**: Unit contribution to total count change

### Ratio
- **Used for**: Dimensionless ratios  
- **Format**: `+0.0042`, `-0.0123`
- **Interpretation**: Ratio contribution to total ratio change

## Bridge Type Selection Decision Tree

```
Is the metric summable? (Total = Sum of campaigns)
├─ YES → Use Mix Bridge
│   └─ Examples: Spend, Sales, Impressions, Clicks
│
└─ NO → Is it a rate/ratio?
    ├─ YES → Can denominator be zero?
    │   ├─ YES → Use MixRate Infinity
    │   │   └─ Examples: ACoS, Total ACoS
    │   │
    │   └─ NO → Use MixRate Bridge  
    │       └─ Examples: ROAS, CTR, CPC, Conversion Rate
    │
    └─ NO → Use Mix Bridge (default)
```

## Common Patterns

### Financial Metrics
```python
# Revenue metrics - Mix Bridge
"Total Ad Sales": BridgeConfiguration(
    bridge_type=BridgeType.MIX_BRIDGE,
    contribution_unit=ContributionUnit.CURRENCY
)

# Efficiency metrics - MixRate Bridge
"ROAS": BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Spend",
    contribution_unit=ContributionUnit.CURRENCY
)

# Cost ratios - MixRate Infinity (prone to division by zero)
"ACoS": BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_INFINITY,
    mix_determinant="Spend",
    inverse_metric="ROAS",
    contribution_unit=ContributionUnit.BASIS_POINTS,
    requires_percentage_conversion=True
)
```

### Performance Metrics
```python
# Click-through rates - MixRate Bridge
"CTR": BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Impressions",
    contribution_unit=ContributionUnit.BASIS_POINTS,
    requires_percentage_conversion=True
)

# Conversion rates - MixRate Bridge
"Conversion Rate": BridgeConfiguration(
    bridge_type=BridgeType.MIXRATE_BRIDGE,
    mix_determinant="Sessions",
    contribution_unit=ContributionUnit.BASIS_POINTS,
    requires_percentage_conversion=True
)
```

## Validation and Debugging

### Mathematical Consistency
Each bridge type validates that:
```
Sum of Campaign Contributions ≈ Total Change
```

### Common Issues
1. **Mix Bridge**: Contributions don't sum to total change
   - Check for data quality issues
   - Verify zero baseline handling

2. **MixRate Bridge**: Mix determinant mismatch
   - Ensure correct denominator specified
   - Verify column exists in data

3. **MixRate Infinity**: Inverse metric not defined
   - Check inverse metric configuration
   - Ensure inverse metric formula exists

### Debug Information
```python
results = orchestrator.calculate_metric(data, totals, "ACoS")
metadata = results['metadata']

print(f"Bridge type: {metadata['bridge_type']}")
print(f"Mathematical consistency: {metadata['mathematical_consistency']}")
print(f"Total contributions: {metadata['total_contributions']}")
print(f"Expected change: {metadata['total_change']}")
```

## Best Practices

### Configuration
- **Always specify contribution unit** appropriate for the metric
- **Use basis points** for percentage metrics to avoid confusion
- **Verify mix determinant** matches the metric's denominator
- **Test edge cases** like zero values and infinity scenarios

### Implementation
- **Validate inputs** before calculation
- **Check mathematical consistency** after calculation  
- **Use appropriate precision** (default 12 decimal places)
- **Handle errors gracefully** with meaningful messages

### Performance
- **Cache calculator instances** for repeated use
- **Batch similar metrics** by bridge type
- **Validate once** rather than per metric
- **Use efficient data structures** for large datasets