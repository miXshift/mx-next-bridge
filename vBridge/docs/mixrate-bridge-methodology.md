# MixRate Bridge Methodology

## Overview

The MixRate Bridge methodology handles rate metric contributions (like ACoS) using inverse calculations to prevent infinity errors and provide mathematically consistent attribution.

## Problem Statement

Traditional Mix Bridge methodology faces challenges with rate metrics:

1. **Infinity Errors**: When denominators are zero (e.g., no sales), rate calculations become undefined
2. **Missing Contributions**: Rate metrics traditionally don't have contributions in standard Mix Bridge
3. **Attribution Gaps**: Changes in rate metrics lack granular campaign-level attribution

## MixRate Bridge Solution

### Core Concept

Instead of calculating contributions directly for rate metrics, MixRate Bridge:

1. **Uses Inverse Methodology**: Calculates through the inverse metric (ROAS for ACoS)
2. **Prevents Infinity Errors**: ROAS uses Ad Spend as denominator (always positive)
3. **Transforms Back**: Converts ROAS contributions to ACoS contributions using relative impact

## Implementation: ACoS via ROAS

### Step 1: ROAS Mix and Rate Impact Calculation

**Formula Components:**
- **Mix Determinant**: Ad Spend (not Sales as in traditional Mix Bridge)
- **Mix Impact**: `(P2 Mix – P1 Mix) × (P2 ROAS – P2 Total ROAS)`
- **Rate Impact**: `(P2 ROAS – P1 ROAS) × P1 Mix`

**Where:**
- `P1 Mix = Campaign P1 Spend / Total P1 Spend`
- `P2 Mix = Campaign P2 Spend / Total P2 Spend`
- `ROAS = Ad Sales / Ad Spend`

### Step 2: Transform ROAS to ACoS Contributions

**Transformation Formula:**
```
ACoS Contribution (bps) = (Campaign ROAS Contribution / Total ROAS Change) × Total ACoS Change (pts) × 100
```

**Example:**
- Campaign X contributed -$0.05 to -$0.17 total ROAS decrease
- Relative Impact: -$0.05 / -$0.17 = +29.17%
- Total ACoS increased by +1.11 pts
- Campaign X ACoS Contribution: +29.17% × +1.11 pts × 100 = +32.38 bps

## Mathematical Properties

### Consistency Guarantees

1. **Sum Property**: Individual campaign contributions sum exactly to total contribution
2. **Direction Consistency**: ROAS decreases correspond to ACoS increases
3. **Proportional Attribution**: Larger ROAS impacts create larger ACoS contributions

### Validation Checks

- **Mathematical Consistency**: `Σ(Campaign Contributions) = Total Contribution`
- **Sign Consistency**: Negative ROAS changes → Positive ACoS contributions
- **Magnitude Reasonableness**: Contributions proportional to underlying changes

## Example Results

From Hydrapak campaign analysis:

### Total Level Changes
- **ROAS**: 4.821 → 4.575 (-0.246 change)
- **ACoS**: 20.74% → 21.86% (+1.11 pts change)
- **Total ACoS Contribution**: +111.43 bps

### Campaign Attribution
- **82 out of 156 campaigns** received non-zero ACoS contributions
- **Top Contributors**: BottleBright campaigns (+79.89 bps, +63.50 bps)
- **Top Detractors**: Water Storage campaigns (-23.39 bps, -22.56 bps)

## Benefits

### 1. Infinity Error Prevention
- Uses Ad Spend as denominator (always positive in active campaigns)
- Eliminates undefined calculations from zero sales scenarios

### 2. Complete Attribution
- Every campaign receives appropriate ACoS contribution
- Total contributions sum to exact total change

### 3. Business Insight
- Identifies which campaigns drive ACoS performance
- Enables granular optimization decisions
- Maintains mathematical rigor

## Integration with Existing Framework

### Backward Compatibility
- Absolute metrics continue using traditional Mix Bridge
- Rate metrics automatically use MixRate Bridge
- No changes required to existing workflows

### Performance Impact
- Minimal computational overhead
- Integrated validation and error handling
- Comprehensive logging and diagnostics

## Technical Implementation

### Core Classes
- **`MixRateBridgeCalculator`**: Main calculation engine
- **`BridgeCalculator.calculate_rate_metric_contributions()`**: Integration point

### Error Handling
- Graceful fallback to zero contributions if calculation fails
- Input validation and mathematical consistency checks
- Comprehensive logging for troubleshooting

### Configuration
- Precision controls for decimal calculations
- Tolerance settings for consistency validation
- Debug modes for detailed analysis

## Future Extensions

### Additional Rate Metrics
- **Total ACoS (TACOS)**: Using Total ROAS (TROAS) methodology
- **CTR, Conversion Rate**: Similar inverse approaches
- **Custom Rate Metrics**: Framework extensible to new metrics

### Enhanced Analytics
- Mix vs Rate impact decomposition
- Time-series contribution analysis
- Advanced attribution models

---

## Mathematical Proof of Consistency

**Theorem**: The sum of individual campaign ACoS contributions equals the total ACoS contribution.

**Proof**:
1. Let `R_total = Σ R_i` where `R_i` is campaign i's ROAS contribution
2. Each ACoS contribution: `A_i = (R_i / R_total) × A_total × 100`
3. Sum of ACoS contributions: `Σ A_i = Σ [(R_i / R_total) × A_total × 100]`
4. Factor out constants: `= (A_total × 100 / R_total) × Σ R_i`
5. Substitute: `= (A_total × 100 / R_total) × R_total`
6. Simplify: `= A_total × 100` ✓

This mathematical foundation ensures the MixRate Bridge methodology provides consistent, reliable attribution for rate metrics while preventing computational errors.

---

## Understanding Percent Change Aggregation

### The Mathematical Principle

A common question when reviewing MixBridge output is: "Why don't the individual campaign percent changes sum to the total percent change?" This is due to a fundamental mathematical principle: **percent changes cannot be directly summed when they have different denominators (base values)**.

### Why Direct Summation Fails

Percent change is calculated as: `((New Value - Old Value) / Old Value) × 100`

Each campaign has its own base value (Old Value) as the denominator. You cannot sum percentages with different denominators.

**Example:**
- Campaign A: $100 → $110 (10% increase)
- Campaign B: $10 → $15 (50% increase)
- Total: $110 → $125 (13.64% increase)

If we incorrectly sum the percentages: 10% + 50% = 60% ❌

This is wrong because Campaign A's 10% is based on $100 while Campaign B's 50% is based on $10.

### Real Data Example

From actual MixBridge output:
- **Total Spend % Change**: 7.41%
- **Sum of Individual Campaign % Changes**: 3,381.11% (meaningless!)

### Correct Methods for Aggregating Percent Changes

#### Method 1: Calculate from Totals (Used by MixBridge)
```
total_january = sum(all_campaign_january_values)
total_february = sum(all_campaign_february_values)
total_percent_change = ((total_february - total_january) / total_january) × 100
```

#### Method 2: Weighted Average
Weight each campaign's percent change by its share of the total:
```
weights = campaign_january_values / total_january_value
weighted_percent_change = sum(campaign_percent_changes × weights)
```

#### Method 3: Sum Absolute Changes
```
total_absolute_change = sum(all_campaign_absolute_changes)
total_january = sum(all_campaign_january_values)
percent_change = (total_absolute_change / total_january) × 100
```

### Key Takeaway

Individual percent changes should never be directly summed. The Total row percent change is calculated correctly from the aggregated total values. This is expected mathematical behavior, not a bug in the calculations.

### Verification

The analysis script at `scripts/analysis/analyze_percent_change_issue.py` demonstrates these principles with real data.