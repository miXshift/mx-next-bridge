# Mathematical Decomposition Patterns for Performance Metric Analysis

## Overview

This document provides an abstract mathematical framework for decomposing performance metric shifts into their underlying patterns: **Net Change**, **Percentage Change**, and **Contribution to Change**. These patterns form the foundation for variance decomposition analysis across hierarchical dimensions.

## Core Mathematical Constructs

### Notation System

Let:
- **P₁** = Period 1 (baseline period)  
- **P₂** = Period 2 (comparison period)
- **Mᵢ** = Metric value for entity i
- **Tₘ** = Total metric value across all entities
- **πᵢ** = Mix proportion for entity i = Mᵢ,P₁ / Tₘ,P₁

## Pattern Decomposition Framework

### 1. Net Change (Δ) - Absolute Difference Pattern

**Definition**: The absolute difference between P₂ and P₁ values, representing the raw magnitude of change.

**Formula**:
```
Δᵢ = Mᵢ,P₂ - Mᵢ,P₁
```

**Metric Type Considerations**:
- **Absolute Metrics**: Direct subtraction (Spend, Sales, Clicks, Impressions)
- **Rate Metrics**: Points difference for percentage-based metrics (ACoS, CTR, Conversion Rate)

**Mathematical Properties**:
- Additive: Σ Δᵢ = ΔTotal
- Preserves units of measurement
- Sign indicates direction of change

### 2. Percentage Change (γ) - Relative Growth Pattern

**Definition**: The relative change expressed as a proportion of the baseline value, normalized to percentage form.

**Formula**:
```
γᵢ = (Mᵢ,P₂ / Mᵢ,P₁) - 1
```

**Alternative Expression**:
```
γᵢ = Δᵢ / Mᵢ,P₁
```

**Mathematical Properties**:
- Non-additive: Σ γᵢ ≠ γTotal
- Dimensionless (unit-free)
- Bounded below by -1 (complete decline)
- Unbounded above (unlimited growth)

**Edge Case Handling**:
- Division by zero: Requires infinity error handling methodology
- Negative baseline values: Requires sign convention definition

### 3. Contribution to Change (Cᵢ) - Attribution Pattern

**Definition**: The basis point contribution of entity i to the total percentage change, enabling decomposition of aggregate shifts into constituent drivers.

#### 3.1 Mix Bridge - Absolute Metric Decomposition

**Applicable to**: Absolute metrics where summation is mathematically valid.

**Formula**:
```
Cᵢ = πᵢ × γᵢ × 10,000
```

**Expanded Form**:
```
Cᵢ = (Mᵢ,P₁ / Tₘ,P₁) × ((Mᵢ,P₂ / Mᵢ,P₁) - 1) × 10,000
```

**Mathematical Properties**:
- Additive: Σ Cᵢ = CTotal
- Units: Basis points (bps)
- Weighted by baseline mix proportion
- Scaling factor: 10,000 (percentage to bps conversion)

#### 3.2 Rate Metric Contribution Methodology

**Applicable to**: Calculated metrics where direct summation is not mathematically valid.

**Approach**: For rate metrics (ACoS, ROAS, CTR, Conversion Rate), the contribution pattern follows a different mathematical structure due to non-additive properties.

**Standard Implementation**:
```
Cᵢ,rate = 0  (for aggregate totals)
```

**Rationale**: Rate metrics are composite ratios where:
- Total Rate ≠ Σ Individual Rates
- Mix decomposition requires numerator/denominator analysis
- Contribution attribution requires MixRate Bridge methodology

## Implementation Considerations

### Precision Requirements

**Decimal Precision**: 12 decimal places minimum for intermediate calculations to prevent rounding error propagation.

**Precision Rationale**: 
- Standard business metrics require 2-4 decimal places for display
- Intermediate calculations with dummy values (0.0000001) require higher precision
- 12 decimal places provides adequate buffer for compound calculations
- Prevents cumulative rounding errors in contribution summation

**Basis Point Conversion**: The 10,000 scaling factor converts decimal percentages to basis points:
```
0.0523 → 523 basis points
```

**Precision Impact on Dummy Value Calculations**:
With 12-decimal precision, dummy value calculations maintain stability:
```
P₂ = 100.00, P₁ = 0.0000001
γ = (100.00 / 0.0000001) - 1 = 999999999.000000
Contribution = π × 999999999.000000 × 10000 (bounded by π ≈ 0)
```

### Metric Classification Framework

#### Absolute Metrics (Additive)
- Summation Property: Σ Mᵢ = Mtotal
- Net Change: Direct subtraction
- Contribution: Mix Bridge methodology
- Examples: Spend, Sales, Clicks, Impressions, Orders

#### Rate Metrics (Non-Additive)  
- Composite Property: Rate = Numerator / Denominator
- Net Change: Points difference
- Contribution: Special handling (typically 0 for totals)
- Examples: ACoS, ROAS, CTR, Conversion Rate, CPC

### Edge Case Handling

#### Zero Baseline Values
- Percentage Change: Undefined (∞)
- Contribution: Requires special attribution methodology
- Treatment: Apply dummy value substitution method for Spend and absolute metrics

**Dummy Value Substitution Method**:
For absolute metrics where P₁ = 0 and P₂ ≠ 0:
```
P₁ₐₐⱼᵤₛₜₑₐ = 0.0000001
```

This enables valid calculation while preserving mathematical relationships:
```
γᵢ = (P₂ / 0.0000001) - 1 ≈ P₂ × 10,000,000 - 1
```

**Implementation Details**:
- Applied to both campaign-level and total-level calculations
- Specific to absolute metrics: Spend, Sales, Clicks, Impressions, Orders
- Rate metrics maintain standard zero-division handling
- Preserves contribution additivity: Σ Cᵢ = CTotal

**Mathematical Justification**:
The dummy value 0.0000001 is chosen to:
1. Be negligible relative to typical metric values
2. Maintain numerical stability in floating-point operations
3. Preserve the directional relationship of growth (P₂ > 0 → positive growth)
4. Enable contribution calculation without distorting mix proportions significantly

**Contribution Calculation with Dummy Values**:
```
Cᵢ = πᵢ × ((P₂ / 0.0000001) - 1) × 10,000
```

Where πᵢ approaches 0 for entities with zero baseline, resulting in bounded contribution values despite large growth rates.

#### Negative Baseline Values
- Sign Convention: Requires business logic definition
- Mathematical Validity: Standard formulas may produce counterintuitive results
- Treatment: Apply absolute value methodology or custom handling

## Validation Properties

### Mathematical Consistency Checks

1. **Additive Property Validation**:
   ```
   Σ Cᵢ,absolute = CTotal,absolute
   ```

2. **Mix Proportion Constraint**:
   ```
   Σ πᵢ = 1.0
   ```

3. **Sign Consistency**:
   ```
   sign(Cᵢ) = sign(πᵢ × γᵢ)
   ```

### Decomposition Completeness

The framework ensures that:
- All variance is attributed (no unexplained residuals)
- Double-counting is eliminated
- Mathematical relationships are preserved across hierarchical levels

## Advanced Considerations

### Hierarchical Decomposition
- Nested attribution across multiple dimensional levels
- Preservation of mathematical relationships at each aggregation level
- Consistent treatment of cross-dimensional interactions

### Temporal Stability
- Period-over-period consistency in calculation methodology
- Handling of newly introduced entities
- Treatment of discontinued entities

### Dimensional Scaling
- Methodology extensibility across different business dimensions
- Consistent application regardless of entity count
- Performance optimization for large-scale decompositions

---

*This framework provides the mathematical foundation for systematic performance variance decomposition, enabling precise attribution of changes across any hierarchical business dimension while maintaining mathematical rigor and computational stability.*