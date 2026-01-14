import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from sympy import latex, Matrix

def plot_2D(exprs,var,labels=None,line_styles=None,colors=None,title="2D Plot",
            xlabel="x",ylabel="y",xlim=None,ylim=None,resolution=400,show=True,_break_=None,
    fontsize=14,title_size=None,label_size=None,tick_size=None,legend_size=None):
    
    """
    Plots 2D curves from symbolic expressions or numeric datasets using Matplotlib.

    Parameters:
        exprs        : Expression, tuple, or list of expressions to plot
        var          : Symbol or tuple defining the variable and range
        labels       : Labels for each curve (default=None)
        line_styles  : Line styles or markers for each curve (default=None)
        colors       : Colors for each curve (default=None)
        title        : Plot title (default="2D Plot")
        xlabel       : X-axis label (default="x")
        ylabel       : Y-axis label (default="y")
        xlim         : X-axis limits as (min, max) (default=None)
        ylim         : Y-axis limits as (min, max) (default=None)
        resolution   : Number of points used to evaluate symbolic expressions (default=400)
        show         : Whether to display the plot (default=True)
        _break_      : List of expressions for which discontinuities should be visually broken (default=None)
        fontsize     : Base font size for plot text (default=14)
        title_size   : Font size for the title (default=None → fontsize+2)
        label_size   : Font size for axis labels (default=None → fontsize)
        tick_size    : Font size for tick labels (default=None → fontsize-2)
        legend_size  : Font size for legend text (default=None → tick_size)

    Returns:
        matplotlib Axes
            The generated 2D plot axes
    """


    # Font size defaults
    title_size = title_size or fontsize + 2
    label_size = label_size or fontsize
    tick_size = tick_size or fontsize - 2
    legend_size = legend_size or tick_size

    # Helper functions
    def _break_kinks(y_data):
        dy = np.abs(np.diff(y_data))
        max_dy = np.nanmax(dy)
        if max_dy == 0 or np.isnan(max_dy):
            return y_data

        threshold = max_dy * 0.5
        y_data = y_data.copy()
        break_indices = np.where(dy > threshold)[0]
        for idx in break_indices:
            y_data[idx] = np.nan
            y_data[idx + 1] = np.nan
        return y_data

    def smart_label(lbl):
        if isinstance(lbl, str):
            if any(c in lbl for c in ['_', '^', '\\']):
                return f"${lbl}$"
            return lbl
        return f"${latex(lbl)}$"

    # Input normalization
    if not isinstance(exprs, list):
        exprs = [exprs]

    if _break_ is None:
        _break_ = []

    if isinstance(var, tuple):
        x_sym, x_range = var
    else:
        x_sym = var
        x_range = (-1, 1)

    x_vals_sample = np.linspace(float(x_range[0]), float(x_range[1]), resolution)

    # Plot setup
    fig, ax = plt.subplots()

    marker_symbols = [
        'o', 's', '^', 'x', '*', 'D', 'p', '+',
        'v', '<', '>', '1', '2', '3', '4'
    ]

    # Plot expressions
    for i, expr in enumerate(exprs):
        style = line_styles[i] if line_styles and i < len(line_styles) else 'solid'
        color = colors[i] if colors and i < len(colors) else None

        raw_label = labels[i] if labels and i < len(labels) else None
        label = smart_label(raw_label) if raw_label is not None else None

        marker = None

        if isinstance(expr, Matrix):
            expr = np.array(expr).astype(np.float64).flatten()

        # Parametric or dataset plot
        if isinstance(expr, (tuple, list)) and len(expr) == 2:
            x_data, y_data = expr

            if isinstance(x_data, sp.Basic) or isinstance(y_data, sp.Basic):
                f_x = sp.lambdify(x_sym, x_data, modules='numpy')
                f_y = sp.lambdify(x_sym, y_data, modules='numpy')
                x_data = f_x(x_vals_sample)
                y_data = f_y(x_vals_sample)

                if hasattr(x_data, '__len__') and not hasattr(y_data, '__len__'):
                    y_data = np.full_like(x_data, y_data)
                elif not hasattr(x_data, '__len__') and hasattr(y_data, '__len__'):
                    x_data = np.full_like(y_data, x_data)

            if expr in _break_:
                y_data = _break_kinks(y_data)

            if style in marker_symbols:
                marker = style
                style = ''

            ax.plot(
                x_data,
                y_data,
                label=label,
                linestyle=style,
                color=color,
                marker=marker
            )

        # Standard y = f(x)
        else:
            original_expr = expr
            expr = sp.sympify(expr)

            if not expr.has(x_sym):
                y_vals = np.full_like(x_vals_sample, float(expr))
            else:
                f = sp.lambdify(x_sym, expr, modules='numpy')
                y_vals = np.array(f(x_vals_sample)).flatten()

            if original_expr in _break_:
                y_vals = _break_kinks(y_vals)

            ax.plot(
                x_vals_sample,
                y_vals,
                label=label,
                linestyle=style,
                color=color
            )

    # Styling & Labels
    ax.set_title(smart_label(title), fontsize=title_size)
    ax.set_xlabel(smart_label(xlabel), fontsize=label_size)
    ax.set_ylabel(smart_label(ylabel), fontsize=label_size)

    ax.tick_params(axis='both', labelsize=tick_size)

    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)

    if labels:
        ax.legend(fontsize=legend_size)

    ax.grid(True)

    if show:
        plt.show()
    else:
        plt.close()

    return ax
