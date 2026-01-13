"""
GSA visualization functions for Global Sensitivity Analysis.

This module contains GSA visualization functions including heatmaps,
LaTeX table export, and partial dependence plots.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, List, Tuple, Any

# Graceful handling of optional matplotlib dependency
try:
    from matplotlib import pyplot as plt
    from matplotlib.colors import Normalize
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    plt = None
    Normalize = None

# Graceful handling of optional sklearn dependency for PDP
try:
    from sklearn.inspection import PartialDependenceDisplay
    HAS_SKLEARN_INSPECTION = True
except ImportError:
    HAS_SKLEARN_INSPECTION = False
    PartialDependenceDisplay = None

try:
    from IPython.display import Latex, Markdown, display
    HAS_IPYTHON = True
except ImportError:
    HAS_IPYTHON = False


def _check_matplotlib_available():
    """Check if matplotlib is available and raise informative error if not."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "Matplotlib is required for plotting functionality. "
            "Install it with: pip install mcpost[viz] or pip install matplotlib"
        )


def _check_sklearn_inspection_available():
    """Check if sklearn inspection is available and raise informative error if not."""
    if not HAS_SKLEARN_INSPECTION:
        raise ImportError(
            "scikit-learn with inspection module is required for partial dependence plots. "
            "Install it with: pip install scikit-learn>=1.0.0"
        )


def plot_sensitivity_metrics(
    table, 
    metrics: Optional[List[str]] = None, 
    title: str = "Global sensitivity summary", 
    cmap: str = "viridis"
) -> Tuple[Any, Any]:
    """
    Plot selected sensitivity metrics as a heatmap using matplotlib.
    
    Parameters
    ----------
    table : pd.DataFrame or dict
        Sensitivity metrics table
    metrics : List[str], optional
        Specific metrics to plot. If None, plots all numeric columns
    title : str, default="Global sensitivity summary"
        Plot title
    cmap : str, default="viridis"
        Colormap name
        
    Returns
    -------
    tuple
        (figure, axes) matplotlib objects
        
    Raises
    ------
    ImportError
        If matplotlib is not installed
    """
    _check_matplotlib_available()
    
    df = pd.DataFrame(table)
    
    # Remove ARD_LS column but keep 1/ARD_LS
    for col in ('ARD_LS',):
        if col in df.columns and col != '1/ARD_LS':
            df = df.drop(columns=[col])
            
    if metrics is not None:
        missing = [m for m in metrics if m not in df.columns]
        if missing:
            raise ValueError(f"Metrics not found in table: {missing}")
        df_plot = df.loc[:, metrics]
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if numeric_cols.empty:
            raise ValueError("No numeric columns available for plotting.")
        df_plot = df.loc[:, numeric_cols]

    df_plot = df_plot.astype(float)
    order = df_plot.sort_values(df_plot.columns[0], ascending=False).index
    df_plot = df_plot.loc[order]

    data = df_plot.values
    norm = Normalize(vmin=np.nanmin(data), vmax=np.nanmax(data))

    try:
        cmap_obj = plt.get_cmap(cmap)
    except ValueError as exc:
        raise ValueError(f"Invalid colormap '{cmap}'. Try one of: {plt.colormaps()}") from exc

    fig_width = 1.8 * df_plot.shape[1] + 2
    fig_height = 0.6 * df_plot.shape[0] + 2
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    im = ax.imshow(data, aspect='auto', cmap=cmap_obj, norm=norm)
    cbar = fig.colorbar(im, ax=ax, pad=0.015)
    cbar.set_label("Relative importance")

    ax.set_xticks(range(df_plot.shape[1]))
    ax.set_xticklabels(df_plot.columns, rotation=45, ha='right')
    ax.set_yticks(range(df_plot.shape[0]))
    ax.set_yticklabels(df_plot.index)

    threshold = (norm.vmax + norm.vmin) / 2 if np.isfinite(norm.vmax) and np.isfinite(norm.vmin) else np.nanmean(data)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            value = data[i, j]
            text = f"{value:.3f}"
            text_color = 'white' if value > threshold else 'black'
            ax.text(j, i, text, ha='center', va='center', color=text_color)

    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel("Metric")
    ax.set_ylabel("Parameter")
    fig.tight_layout()
    return fig, ax


def sensitivity_table_to_latex(
    table, 
    caption: Optional[str] = None, 
    label: Optional[str] = None,
    float_format: str = "{:.3f}", 
    column_format: Optional[str] = None,
    display_result: bool = False, 
    fallback_markdown: bool = True,
    feature_label: Optional[str] = None
) -> str:
    """
    Return a LaTeX table string from a sensitivity summary table.
    
    Parameters
    ----------
    table : pd.DataFrame or dict
        Sensitivity metrics table
    caption : str, optional
        Table caption
    label : str, optional
        LaTeX label
    float_format : str, default="{:.3f}"
        Format string for floating point numbers
    column_format : str, optional
        LaTeX column format specification
    display_result : bool, default=False
        Whether to display the result in Jupyter
    fallback_markdown : bool, default=True
        Whether to fallback to markdown if LaTeX display fails
    feature_label : str, optional
        Feature label for multirow
        
    Returns
    -------
    str
        LaTeX table string
    """
    df = pd.DataFrame(table)
    
    # Remove ARD_LS column but keep 1/ARD_LS
    for col in ('ARD_LS',):
        if col in df.columns and col != '1/ARD_LS':
            df = df.drop(columns=[col])

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df.loc[:, numeric_cols] = df.loc[:, numeric_cols].astype(float)

    df.index = [str(idx).replace('_', r'\_') for idx in df.index]
    df = df.rename_axis("Parameter").reset_index()

    if feature_label:
        label_tex = str(feature_label).replace('_', r'\_')
        multirow = f"\\multirow{{{len(df)}}}{{*}}{{{label_tex}}}"
        feature_col = [''] * len(df)
        feature_col[0] = multirow
        df.insert(0, 'Feature', feature_col)

    formatter = None if float_format is None else (lambda x: float_format.format(x))

    latex_str = df.to_latex(index=False, escape=False, caption=caption, label=label,
                            column_format=column_format, float_format=formatter)
    
    if display_result and HAS_IPYTHON:
        try:
            display(Latex(latex_str))
        except Exception:
            if fallback_markdown:
                display(Markdown(f"```latex\n{latex_str}\n```"))
            else:
                raise
    elif display_result and not HAS_IPYTHON:
        print("IPython not available for display. Returning LaTeX string.")
        
    return latex_str


def create_pdp_plots(
    rf_model,
    X: np.ndarray,
    param_names: List[str],
    top_params: List[str],
    pdp_fig_prefix: Optional[str] = None
) -> List[str]:
    """
    Create partial dependence plots for top parameters.
    
    Parameters
    ----------
    rf_model
        Fitted RandomForest model
    X : np.ndarray
        Input data
    param_names : List[str]
        All parameter names
    top_params : List[str]
        Top parameters to plot
    pdp_fig_prefix : str, optional
        Prefix for saved figure files
        
    Returns
    -------
    List[str]
        List of saved figure paths
        
    Raises
    ------
    ImportError
        If matplotlib or sklearn inspection module is not installed
    """
    _check_matplotlib_available()
    _check_sklearn_inspection_available()
    
    pdp_paths = []
    name_to_idx = {nm: i for i, nm in enumerate(param_names)}
    feats_idx = [name_to_idx[nm] for nm in top_params]
    
    for nm, fi in zip(top_params, feats_idx):
        fig, ax = plt.subplots(figsize=(6, 4))
        PartialDependenceDisplay.from_estimator(
            rf_model, X, features=[fi], ax=ax, kind="average"
        )
        ax.set_title(f"PDP – {nm}")
        fig.tight_layout()
        
        if pdp_fig_prefix:
            path = f"{pdp_fig_prefix}_{nm}.png"
            fig.savefig(path, dpi=150)
            pdp_paths.append(path)
        plt.close(fig)
        
    return pdp_paths