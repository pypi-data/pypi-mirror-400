import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import matplotlib.animation
from sympy import latex, Matrix

def animate(exprs, var, labels=None, line_styles=None, colors=None,
            title="Animation", xlabel="x", ylabel="y",
            xlim=None, ylim=None, thickness=2, 
            animation_time=5000, frames=100, resolution=400, show=True):
    """
    Animates 2D curves from symbolic expressions or numeric datasets using Matplotlib.

    Parameters:
        exprs          : Expression, tuple, or list of expressions to animate (symbolic, parametric, or numeric data)
        var            : Symbol or tuple defining the variable and range, or array mode ('array', x_values)
        labels         : Curve labels (strings or SymPy expressions, LaTeX supported) (default=None)
        line_styles    : Line styles for each curve (default=None → solid)
        colors         : Colors for each curve (default=None → Matplotlib cycle)
        title          : Plot title (string or SymPy expression, LaTeX supported) (default="Animation")
        xlabel         : X-axis label (string or SymPy expression, LaTeX supported) (default="x")
        ylabel         : Y-axis label (string or SymPy expression, LaTeX supported) (default="y")
        xlim           : X-axis limits as (min, max) (default=None → auto)
        ylim           : Y-axis limits as (min, max) (default=None → auto)
        thickness      : Line width(s) as int or list (default=2)
        animation_time : Total animation duration in milliseconds (default=5000)
        frames         : Number of animation frames (default=100)
        resolution     : Number of evaluation points for symbolic expressions (default=400)
        show           : Whether to display the animation (default=True)

    Returns:
        matplotlib.animation.FuncAnimation
            The animation object
    """

    
    # Configure matplotlib for Jupyter notebook compatibility
    plt.rcParams["animation.html"] = "jshtml"
    plt.rcParams['figure.dpi'] = 150
    plt.ioff()
    
    # Helper function to convert labels to LaTeX
    def smart_label(lbl):
        if isinstance(lbl, str):
            # Check for LaTeX characters
            if any(c in lbl for c in ['_', '^', '\\']):
                return f"${lbl}$"
            else:
                return lbl
        else:
            # Convert SymPy expression to LaTeX
            return f"${latex(lbl)}$"
    
    # Normalize inputs to lists
    if not isinstance(exprs, list):
        exprs = [exprs]
    
    # Determine symbol and range
    is_sympy = True
    if isinstance(var, tuple):
        if var[0] == 'array':
            is_sympy = False
            x_vals_sample = var[1]
            frames = len(x_vals_sample)
        else:
            x_sym = var[0]
            x_range = var[1]
            x_vals_sample = np.linspace(float(x_range[0]), float(x_range[1]), frames)
    else:
        x_sym = var
        x_range = (-1, 1)
        x_vals_sample = np.linspace(float(x_range[0]), float(x_range[1]), frames)
    
    # Setup thickness
    if isinstance(thickness, (int, float)):
        thickness = [thickness] * len(exprs)
    
    # Prepare data for all expressions
    plot_data = []
    for i, expr in enumerate(exprs):
        # Convert SymPy Matrix to NumPy array
        if isinstance(expr, Matrix):
            expr = np.array(expr).astype(np.float64).flatten()
        
        # Tuple/list of two items (x, y) - parametric or data
        if isinstance(expr, (tuple, list)) and len(expr) == 2:
            x_data, y_data = expr
            
            # If symbolic expressions, lambdify automatically
            if isinstance(x_data, sp.Basic) or isinstance(y_data, sp.Basic):
                if is_sympy:
                    f_x = sp.lambdify(x_sym, x_data, modules='numpy')
                    f_y = sp.lambdify(x_sym, y_data, modules='numpy')
                    x_data = f_x(x_vals_sample)
                    y_data = f_y(x_vals_sample)
            
            # Handle constant parametric plots
            is_x_array = hasattr(x_data, '__len__')
            is_y_array = hasattr(y_data, '__len__')
            
            if is_x_array and not is_y_array:
                y_data = np.full_like(x_data, y_data)
            elif not is_x_array and is_y_array:
                x_data = np.full_like(y_data, x_data)
            
            plot_data.append((np.array(x_data), np.array(y_data)))
        
        else:
            # Single symbolic or numeric expression
            expr = sp.sympify(expr)
            if not expr.has(x_sym) if is_sympy else False:
                y_vals = np.full_like(x_vals_sample, float(expr))
            else:
                if is_sympy:
                    f = sp.lambdify(x_sym, expr, modules='numpy')
                    y_vals = np.array(f(x_vals_sample)).flatten()
                else:
                    y_vals = np.array(expr).flatten()
            
            plot_data.append((x_vals_sample, y_vals))
    
    # Auto-calculate axis limits if not provided
    if xlim is None:
        all_x = np.concatenate([data[0] for data in plot_data])
        x_min, x_max = np.min(all_x), np.max(all_x)
        x_range = x_max - x_min
        xlim = (x_min - 0.05 * x_range, x_max + 0.05 * x_range)
    
    if ylim is None:
        all_y = np.concatenate([data[1] for data in plot_data])
        y_min, y_max = np.min(all_y), np.max(all_y)
        y_range = y_max - y_min
        ylim = (y_min - 0.1 * y_range, y_max + 0.1 * y_range)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    def animate_frame(frame):
        ax.clear()
        
        # Show data up to current frame
        idx = frame + 1
        
        for i, (x_data, y_data) in enumerate(plot_data):
            style = line_styles[i] if line_styles and i < len(line_styles) else 'solid'
            color = colors[i] if colors and i < len(colors) else None
            raw_label = labels[i] if labels and i < len(labels) else None
            label = smart_label(raw_label) if raw_label is not None else None
            
            ax.plot(x_data[:idx], y_data[:idx], 
                   label=label, 
                   linestyle=style, 
                   color=color, 
                   linewidth=thickness[i])
        
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_title(smart_label(title))
        ax.set_xlabel(smart_label(xlabel))
        ax.set_ylabel(smart_label(ylabel))
        
        if labels:
            ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Calculate interval from animation_time and frames
    interval = animation_time / frames
    
    anim = matplotlib.animation.FuncAnimation(
        fig, animate_frame, frames=frames, interval=interval, repeat=True
    )
    
    if not show:
        plt.close()
    
    return anim