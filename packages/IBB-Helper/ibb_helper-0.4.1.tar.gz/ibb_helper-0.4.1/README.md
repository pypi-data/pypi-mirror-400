## Helper functions for symbolic math, matrix visualization, and plotting

**Author:** University of Stuttgart, Institute for Structural Mechanics (IBB)    
**License:** BSD3  
**Version:** 0.4.1      
**Date:** Jan 07, 2025  

### Description

This helper module currently provides 11 specialized functions for symbolic mathematics, matrix visualization, and plotting operations. Designed for SymPy, NumPy, Matplotlib, and Plotly integration in Jupyter Notebooks and Python environments.

### Helper Functions

1. **animate**           - Animate 2D curves from symbolic expressions or datasets
2. **combine_plots**     - Stack multiple Matplotlib/Plotly plots into combined figures
3. **display**           - Format scalars, vectors, or matrices in LaTeX for display
4. **display_eigen**     - Compute and display eigenvalues/eigenvectors with LaTeX formatting
5. **display_matrix**    - Display truncated matrices with optional numerical evaluation
6. **extend_plot**       - Merge multiple plots side-by-side with horizontal offsets
7. **minimize**          - General optimization wrapper for symbolic expressions with constraints
8. **num_int**           - Numerically integrate symbolic expressions over 1D domains using composite Gauss quadrature
9. **plot_2d**           - Plot symbolic expressions or datasets in 2D using Matplotlib
10. **plot_3d**          - Plot symbolic 3D surfaces using Plotly for interactive visualization
11. **plot_param_grid**  - Plot 2D parametric surface grids with control points
12. **symbolic_BSpline** - Generate symbolic B-spline basis functions with plotting  

### Dependencies

- Python 3.8+
- numpy, sympy, matplotlib, plotly
- IPython (for LaTeX rendering)


### Quick Start

```python
import IBB_Helper as ibb

# Display matrix
ibb.display_matrix(np.array([[1, 2], [3, 4]]), name="A")

# Show symbolic expression  
ibb.display(sp.sin(x)**2 + sp.cos(x)**2, name="Identity")

# Plot 2D curves
ibb.plot_2d([sp.sin(x), sp.cos(x)], var=(x, (-np.pi, np.pi)))

# Plot 3D surface
ibb.plot_3d(sp.sin(x*y), var=(x, (-2, 2), y, (-2, 2)))
```


### Development Status

This is an **ongoing project** with regular enhancements. Updates might include:

- New helper functions
- Performance optimizations
- Extended compatibility
- Bug fixes and stability improvements


### Notes

- Optimized for education, research, and technical documentation
- Seamless SymPy/NumPy integration
- Enhanced LaTeX formatting for presentations