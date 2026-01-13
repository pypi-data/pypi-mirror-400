# fastloess

[![PyPI](https://img.shields.io/pypi/v/fastloess.svg?style=flat-square)](https://pypi.org/project/fastloess/)
[![License](https://img.shields.io/badge/license-MIT%2FApache--2.0-blue.svg)](LICENSE-MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/fastloess.svg?style=flat-square)](https://pypi.org/project/fastloess/)
[![Documentation Status](https://readthedocs.org/projects/fastloess-py/badge/?version=latest)](https://fastloess-py.readthedocs.io/en/latest/?badge=latest)
[![Conda](https://anaconda.org/conda-forge/fastloess/badges/version.svg)](https://anaconda.org/conda-forge/fastloess)

**High-performance parallel LOESS (Locally Estimated Scatterplot Smoothing) for Python** — A high-level wrapper around the [`fastLoess`](https://github.com/thisisamirv/fastLoess) Rust crate that adds rayon-based parallelism and seamless NumPy integration.

> [!IMPORTANT]
> **Full Documentation & API Reference:**
>
> ## 📖 [fastloess-py.readthedocs.io](https://fastloess-py.readthedocs.io/)

## How LOESS Works

LOESS creates smooth curves through scattered data using local weighted neighborhoods:

![LOESS Smoothing Concept](https://raw.githubusercontent.com/thisisamirv/fastLoess/main/docs/source/_static/images/loess_concept.svg)

## LOESS vs. LOWESS

| Feature               | LOESS (This Package)              | LOWESS                         |
|-----------------------|-----------------------------------|--------------------------------|
| **Polynomial Degree** | Linear, Quadratic, Cubic, Quartic | Linear (Degree 1)              |
| **Dimensions**        | Multivariate (n-D support)        | Univariate (1-D only)          |
| **Flexibility**       | High (Distance metrics)           | Standard                       |
| **Complexity**        | Higher (Matrix inversion)         | Lower (Weighted average/slope) |

LOESS can fit higher-degree polynomials for more complex data:

![Degree Comparison](https://raw.githubusercontent.com/thisisamirv/fastLoess/main/docs/source/_static/images/degree_comparison.svg)

LOESS can also handle multivariate data (n-D), while LOWESS is limited to univariate data (1-D):

![Multivariate LOESS](https://raw.githubusercontent.com/thisisamirv/fastLoess/main/docs/source/_static/images/multivariate_loess.svg)

> [!TIP]
> **Note:** For a simple, lightweight, and fast **LOWESS** implementation, use [`fastlowess`](https://github.com/thisisamirv/fastLowess-py) package.

## Features

- **Robust Statistics**: IRLS with Bisquare, Huber, or Talwar weighting for outlier handling.
- **Multidimensional Smoothing**: Support for n-D data with customizable distance metrics (Euclidean, Manhattan, etc.).
- **Flexible Fitting**: Linear, Quadratic, Cubic, and Quartic local polynomials.
- **Uncertainty Quantification**: Point-wise standard errors, confidence intervals, and prediction intervals.
- **Optimized Performance**: Interpolation surface with Tensor Product Hermite interpolation and streaming/online modes for large or real-time datasets.
- **Parameter Selection**: Built-in cross-validation for automatic smoothing fraction selection.
- **Flexibility**: Multiple weight kernels (Tricube, Epanechnikov, etc.).
- **Validated**: Numerical twin of R's `stats::loess` with exact match (< 1e-12 diff).

## Performance

Benchmarked against R's `stats::loess`. The latest benchmarks comparing **Serial** vs **Parallel** execution modes show that the parallel implementation correctly leverages multiple cores to provide additional speedups, particularly for computationally heavier tasks (high dimensions, larger datasets).

Overall, fastloess implementations achieve **3x to 54x** speedups over R.

### Comparison: R vs fastloess (Serial) vs fastloess (Parallel)

The table below shows the execution time and speedup relative to R.

| Name                           |      R       | fastloess (Serial) | fastloess (Parallel) |
|--------------------------------|--------------|--------------------|----------------------|
| **Dimensions**                 |              |                    |                      |
| 1d_linear                      |    4.18ms    |     7.2x           |      8.1x            |
| 2d_linear                      |   13.24ms    |     6.5x           |      10.1x           |
| 3d_linear                      |   28.37ms    |     7.9x           |      13.6x           |
| **Pathological**               |              |                    |                      |
| clustered                      |   19.70ms    |     15.7x          |      21.5x           |
| constant_y                     |   13.61ms    |     13.6x          |      17.5x           |
| extreme_outliers               |   23.55ms    |     10.3x          |      11.7x           |
| high_noise                     |   34.96ms    |     19.9x          |      28.0x           |
| **Polynomial Degree**          |              |                    |                      |
| degree_constant                |    8.50ms    |     10.0x          |      13.5x           |
| degree_linear                  |   13.47ms    |     16.2x          |      21.4x           |
| degree_quadratic               |   19.07ms    |     23.3x          |      29.7x           |
| **Scalability**                |              |                    |                      |
| scale_1000                     |    1.09ms    |     4.3x           |      3.7x            |
| scale_5000                     |    8.63ms    |     7.2x           |      8.2x            |
| scale_10000                    |   28.68ms    |     10.4x          |      14.5x           |
| **Real-world Scenarios**       |              |                    |                      |
| financial_1000                 |    1.11ms    |     4.8x           |      4.7x            |
| financial_5000                 |    8.28ms    |     7.6x           |      9.2x            |
| genomic_5000                   |    8.27ms    |     6.7x           |      7.5x            |
| scientific_5000                |   11.23ms    |     6.8x           |      10.1x           |
| **Parameter Sensitivity**      |              |                    |                      |
| fraction_0.67                  |   44.96ms    |     54.0x          |      54.1x           |
| iterations_10                  |   23.31ms    |     10.9x          |      11.8x           |

*Note: "fastloess (Parallel)" corresponds to the optimized CPU backend using Rayon.*

### Key Takeaways

1. **Parallel Wins on Load**: For computationally intensive tasks (e.g., `3d_linear`, `high_noise`, `scientific_5000`, `scale_10000`), the parallel backend provides significant additional speedup over the serial implementation (e.g., **13.6x vs 7.9x** for 3D data).
2. **Overhead on Small Data**: For very small or fast tasks (e.g., `scale_1000`, `financial_1000`), the serial implementation is comparable or slightly faster, indicating that thread management overhead is visible but minimal (often < 0.05ms difference).
3. **Consistent Superiority**: Both Rust implementations consistently outperform R, usually by an order of magnitude.

### Recommendation

- **Default to Parallel**: The overhead for small datasets is negligible (microseconds), while the gains for larger or more complex datasets are substantial (doubling the speedup factor in some cases).
- **Use Serial for Tiny Batches**: If processing millions of independent tiny datasets (< 1000 points) where calling `smooth` repeatedly, the serial backend might save thread pool overhead.

Check [Benchmarks](https://github.com/thisisamirv/fastloess-py/tree/bench/benchmarks) for detailed results and reproducible benchmarking code.

## Robustness Advantages

This implementation includes several robustness features beyond R's `loess`:

### MAD-Based Scale Estimation

Uses **MAD-based scale estimation** for robustness weight calculations:

```text
s = median(|r_i - median(r)|)
```

MAD is a **breakdown-point-optimal** estimator—it remains valid even when up to 50% of data are outliers, compared to the median of absolute residuals used by some other implementations.

Median Absolute Residual (MAR), which is the default Cleveland's choice, is also available through the `scaling_method` parameter.

### Configurable Boundary Policies

R's `loess` uses asymmetric windows at data boundaries, which can introduce edge bias. This implementation offers configurable **boundary policies** to mitigate this:

- **Extend** (default): Pad with constant values for symmetric windows
- **Reflect**: Mirror data at boundaries (best for periodic data)
- **Zero**: Pad with zeros (signal processing applications)
- **NoBoundary**: Original R behavior (no padding)

### Boundary Degree Fallback

When using `Interpolation` mode with higher polynomial degrees (Quadratic, Cubic), vertices outside the tight data bounds can produce unstable extrapolation. This implementation offers a configurable **boundary degree fallback**:

- **`true`** (default): Reduce to Linear fits at boundary vertices (more stable)
- **`false`**: Use full requested degree everywhere (matches R exactly)

## Validation

The Python `fastloess` package is a **numerical twin** of R's `loess` implementation:

| Aspect          | Status         | Details                                    |
|-----------------|----------------|--------------------------------------------|
| **Accuracy**    | ✅ EXACT MATCH | Max diff < 1e-12 across all scenarios      |
| **Consistency** | ✅ PERFECT     | 20/20 scenarios pass with strict tolerance |
| **Robustness**  | ✅ VERIFIED    | Robust smoothing matches R exactly         |

Check [Validation](https://github.com/thisisamirv/fastLoess-py/tree/bench/validation) for detailed scenario results.

## Installation

Install via PyPI:

```bash
pip install fastloess
```

Or install from conda-forge:

```bash
conda install -c conda-forge fastloess
```

## Quick Start

```python
import numpy as np
import fastloess

x = np.linspace(0, 10, 100)
y = np.sin(x) + np.random.normal(0, 0.2, 100)

# Basic smoothing (parallel CPU by default)
result = fastloess.smooth(x, y, fraction=0.3)

print(f"Smoothed values: {result.y}")
```

## Smoothing Parameters

```python
import fastloess

fastloess.smooth(
    x, y,
    # Smoothing span (0, 1]
    fraction=0.5,

    # Polynomial degree
    polynomial_degree="linear",  # "constant", "linear", "quadratic", "cubic", "quartic"

    # Number of dimensions
    dimensions=1,

    # Distance metric
    distance_metric="normalized",  # "euclidean", "normalized", "manhattan", "chebyshev"

    # Robustness iterations
    iterations=3,

    # Interpolation threshold
    delta=0.01,

    # Kernel function
    weight_function="tricube",

    # Robustness method
    robustness_method="bisquare",

    # Scaling method
    scaling_method="mad",  # "mad" or "mar"

    # Zero-weight fallback
    zero_weight_fallback="use_local_mean",

    # Boundary handling
    boundary_policy="extend",

    # Boundary degree fallback
    boundary_degree_fallback=True,

    # Surface evaluation mode
    surface_mode="interpolation",  # "interpolation" or "direct"

    # Interpolation settings
    cell=0.2,
    interpolation_vertices=None,

    # Standard errors
    return_se=False,

    # Intervals
    confidence_intervals=0.95,
    prediction_intervals=0.95,

    # Diagnostics
    return_diagnostics=True,
    return_residuals=True,
    return_robustness_weights=True,

    # Cross-validation
    cv_fractions=[0.3, 0.5, 0.7],
    cv_method="kfold",
    cv_k=5,

    # Convergence
    auto_converge=1e-4,

    # Parallelism
    parallel=True
)
```

## Result Structure

The `smooth()` function returns a `LoessResult` object:

```python
result.x                    # Sorted independent variable values
result.y                    # Smoothed dependent variable values
result.dimensions           # Number of predictor dimensions
result.distance_metric      # Distance metric used
result.polynomial_degree    # Polynomial degree used
result.standard_errors      # Point-wise standard errors
result.confidence_lower     # Lower bound of confidence interval
result.confidence_upper     # Upper bound of confidence interval
result.prediction_lower     # Lower bound of prediction interval
result.prediction_upper     # Upper bound of prediction interval
result.residuals            # Residuals (y - fit)
result.robustness_weights   # Final robustness weights
result.diagnostics          # Diagnostics (RMSE, R^2, etc.)
result.iterations_used      # Number of iterations performed
result.fraction_used        # Smoothing fraction used
result.cv_scores            # CV scores for each candidate
```

## Streaming Processing

For datasets that don't fit in memory:

```python
result = fastloess.smooth_streaming(
    x, y,
    fraction=0.3,
    chunk_size=5000,
    overlap=500,
    parallel=True
)
```

## Online Processing

For real-time data streams:

```python
result = fastloess.smooth_online(
    x, y,
    fraction=0.2,
    window_capacity=100,
    update_mode="incremental" # or "full"
)
```

## Parameter Selection Guide

### Fraction (Smoothing Span)

- **0.1-0.3**: Fine detail, may be noisy
- **0.3-0.5**: Moderate smoothing (good for most cases)
- **0.5-0.7**: Heavy smoothing, emphasizes trends
- **0.7-1.0**: Very smooth, may over-smooth
- **Default: 0.67** (Cleveland's choice)

### Robustness Iterations

- **0**: No robustness (fastest, sensitive to outliers)
- **1-3**: Light to moderate robustness (recommended)
- **4-6**: Strong robustness (for contaminated data)
- **7+**: Diminishing returns

### Polynomial Degree

- **Constant**: Local weighted mean (smoothing only)
- **Linear** (default): Standard LOESS, good bias-variance balance
- **Quadratic**: Better for peaks/valleys, higher variance
- **Cubic/Quartic**: Specialized high-order fitting

### Kernel Function

- **Tricube** (default): Best all-around, Cleveland's original choice
- **Epanechnikov**: Theoretically optimal MSE
- **Gaussian**: Maximum smoothness, no compact support
- **Uniform**: Fastest, least smooth (moving average)

### Distance Metric

- **Normalized** (default): Scales by range, good for mixed-scale data
- **Euclidean**: Standard distance
- **Manhattan**: L1 distance, robust to outliers
- **Chebyshev**: L∞ distance, maximum absolute difference

### Boundary Policy

- **Extend** (default): Pad with constant values
- **Reflect**: Mirror data at boundaries (for periodic/symmetric data)
- **Zero**: Pad with zeros (signal processing)
- **NoBoundary**: Original Cleveland behavior

> **Note:** For nD data, `Extend` defaults to `NoBoundary` to preserve regression accuracy.

## Examples

Check the `examples` directory:

```bash
python examples/batch_smoothing.py
python examples/online_smoothing.py
python examples/streaming_smoothing.py
```

## Related Work

- [fastLoess (Rust core)](https://github.com/thisisamirv/fastLoess)
- [fastLoess-R (R wrapper)](https://github.com/thisisamirv/rfastloess)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Licensed under either of

- Apache License, Version 2.0
   ([LICENSE-APACHE](LICENSE-APACHE) or <http://www.apache.org/licenses/LICENSE-2.0>)
- MIT license
   ([LICENSE-MIT](LICENSE-MIT) or <http://opensource.org/licenses/MIT>)

at your option.

## References

- Cleveland, W.S. (1979). "Robust Locally Weighted Regression and Smoothing Scatterplots". *JASA*.
- Cleveland, W.S. (1981). "LOWESS: A Program for Smoothing Scatterplots". *The American Statistician*.
