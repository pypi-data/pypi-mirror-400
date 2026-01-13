# Comprehensive Global Sensitivity Analysis Tutorial

This tutorial provides an in-depth exploration of GSA capabilities in MCPost, covering advanced techniques and interpretation strategies.

## Table of Contents

1. [Understanding GSA Metrics](#understanding-gsa-metrics)
2. [The Ishigami Function](#the-ishigami-function)
3. [Advanced GSA Configuration](#advanced-gsa-configuration)
4. [Interpreting Results](#interpreting-results)
5. [Handling Real-World Challenges](#handling-real-world-challenges)

## Understanding GSA Metrics

MCPost provides multiple sensitivity metrics, each capturing different aspects of parameter influence:

### Mutual Information (MI)
- Measures statistical dependence between parameters and outputs
- Captures both linear and nonlinear relationships
- Range: [0, ∞), higher values indicate stronger influence
- Model-agnostic and distribution-free

### Distance Correlation (dCor)
- Measures dependence between random vectors
- Range: [0, 1], where 0 = independent, 1 = perfectly dependent
- Captures nonlinear and non-monotonic relationships
- Particularly useful for complex, multimodal relationships

### Permutation Importance
- Model-agnostic importance measure
- Computed by shuffling parameter values and measuring performance decrease
- Directly interpretable: how much does randomizing this parameter hurt predictions?
- Robust to model assumptions

### Sobol' Indices
- **Si (First-order)**: Main effect of parameter i
- **STi (Total)**: Total effect including all interactions involving parameter i
- **Interaction effects**: STi - Si measures interaction contributions
- Variance-based decomposition: Si + interactions = 1

### Gaussian Process ARD
- Automatic Relevance Determination from GP surrogate
- 1/ARD_LS indicates relative parameter importance
- Based on learned length scales in GP kernel
- Reflects how "relevant" each parameter is for GP predictions

## The Ishigami Function

The Ishigami function is a standard benchmark for GSA methods:

```python
f(x1, x2, x3) = sin(x1) + 7*sin(x2)^2 + 0.1*x3^4*sin(x1)
```

**Theoretical Sobol' indices:**
- S1 = 0.314, S2 = 0.442, S3 = 0.000
- ST1 = 0.558, ST2 = 0.442, ST3 = 0.244

**Key insights:**
- x2 has the largest main effect (S2 = 0.442)
- x1 has moderate main effect but strong interactions (ST1 - S1 = 0.244)
- x3 has no main effect but contributes through interactions with x1

## Advanced GSA Configuration

### Scaling Options

```python
# MinMax scaling (default) - good for bounded parameters
results = gsa_pipeline(X, Y, scaler="minmax")

# Standard scaling - good for unbounded parameters
results = gsa_pipeline(X, Y, scaler="standard")

# No scaling - when parameters are already on similar scales
results = gsa_pipeline(X, Y, scaler=None)
```

### Kernel Selection

```python
# RBF kernel (default) - smooth, general-purpose
results = gsa_pipeline(X, Y, kernel_kind="rbf")

# Matérn kernels - different smoothness assumptions
results = gsa_pipeline(X, Y, kernel_kind="matern32")  # Less smooth
results = gsa_pipeline(X, Y, kernel_kind="matern52")  # More smooth

# Rational Quadratic - mixture of length scales
results = gsa_pipeline(X, Y, kernel_kind="rq")
```

### Computational Trade-offs

```python
# Fast analysis - skip expensive methods
results = gsa_pipeline(
    X, Y,
    enable_perm=False,    # Skip permutation importance
    enable_sobol=False,   # Skip Sobol indices
    make_pdp=False        # Skip partial dependence plots
)

# High-accuracy analysis - increase Sobol budget
results = gsa_pipeline(
    X, Y,
    N_sobol=8192,         # More Sobol samples
    enable_gp=True,       # Ensure GP is enabled
    ard=True              # Use ARD kernel
)
```

## Interpreting Results

### Ranking Parameters

Different metrics may give different rankings. Consider:

1. **Consistency across metrics**: Parameters ranking high in multiple metrics are robustly important
2. **Metric-specific insights**: 
   - High MI + low dCor → linear relationship
   - High dCor + moderate MI → strong nonlinear relationship
   - High STi - Si → strong interaction effects

### Interaction Detection

```python
# Identify parameters with strong interactions
table = results["results"]["target"]["table"]
interaction_strength = table["STi"] - table["Si"]
high_interaction_params = interaction_strength.nlargest(3)
```

### Model Quality Assessment

```python
# Check GP surrogate quality
gp_model = results["results"]["target"]["models"]["gp_model"]
if gp_model is not None:
    # R² score on training data indicates surrogate quality
    train_score = gp_model.score(X_scaled, y)
    print(f"GP R² score: {train_score:.3f}")
```

## Handling Real-World Challenges

### Correlated Parameters

When parameters are correlated:
- Sobol' indices may be misleading (assume independence)
- Rely more on MI, dCor, and permutation importance
- Consider parameter transformations to reduce correlation

### High-Dimensional Problems

For many parameters (>20):
- Use screening methods first to identify important parameters
- Consider grouped sensitivity analysis
- Use regularized GP methods or dimension reduction

### Noisy Outputs

For noisy model outputs:
- Increase sample size
- Use robust metrics (MI, dCor less sensitive to outliers)
- Consider denoising techniques

### Computational Constraints

For expensive models:
- Start with smaller sample sizes (500-1000)
- Use fast screening methods first
- Disable expensive methods (Sobol', permutation importance)
- Use surrogate models for initial exploration

## Example: Multi-Output GSA

```python
# Analyze multiple outputs simultaneously
Y_multi = np.column_stack([output1, output2, output3])
feature_names = ["pressure", "temperature", "flow_rate"]

results = gsa_pipeline(
    X, Y_multi,
    param_names=param_names,
    feature_names=feature_names,
    scaler="minmax"
)

# Compare sensitivities across outputs
for feature in feature_names:
    print(f"\n{feature} sensitivity:")
    print(results["results"][feature]["table"].head())
```

## Best Practices

1. **Start simple**: Begin with default settings and basic metrics
2. **Validate with known functions**: Test on Ishigami or other benchmarks
3. **Check convergence**: Ensure results are stable with sample size
4. **Use multiple metrics**: Don't rely on a single sensitivity measure
5. **Visualize results**: Use heatmaps and PDPs for interpretation
6. **Document assumptions**: Note parameter ranges, distributions, and model assumptions

## Troubleshooting

### Common Issues

**"All parameters are constant"**
- Check parameter ranges and sampling
- Verify data loading and preprocessing

**Poor GP surrogate quality**
- Try different kernels or scaling methods
- Increase sample size
- Check for outliers in data

**Inconsistent sensitivity rankings**
- Normal for complex models
- Focus on parameters consistently ranking high
- Consider model-specific factors

**High computational cost**
- Reduce N_sobol parameter
- Disable expensive methods temporarily
- Use parallel processing if available

## Further Reading

- Saltelli, A. et al. "Global Sensitivity Analysis: The Primer" (2008)
- Sobol', I.M. "Sensitivity Estimates for Nonlinear Mathematical Models" (1993)
- Borgonovo, E. "A new uncertainty importance measure" (2007)