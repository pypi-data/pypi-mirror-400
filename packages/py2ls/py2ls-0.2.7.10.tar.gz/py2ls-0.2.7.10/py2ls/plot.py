import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import warnings
import logging

from typing import Dict, List, Optional, Union, Any, Tuple, Literal,Callable,Pattern,Set,Iterable
from .ips import (
    isa,
    fsave,
    fload,
    mkdir,
    listdir,
    figsave,
    strcmp,
    unique,
    get_os,
    ssplit,is_nan,
    flatten,
    plt_font,
    run_once_within,
    get_df_format,
    df_corr,
    df_scaler,
    df2array,array2df,
    ls_param,
    color2rgb,color2hex,
    handle_kwargs, 
)
from .utils import decorators
import scipy.stats as scipy_stats
from .stats import *
import os

from matplotlib import patches

_default_settings = None
_sns_info = None

def get_default_settings():
    global _default_settings
    if _default_settings is None:
        from pathlib import Path
        current_directory = Path(__file__).resolve().parent
        _default_settings = fload(current_directory / "data" / "usages_sns.json")
    return _default_settings

def get_sns_info():
    global _sns_info
    if _sns_info is None:
        from pathlib import Path
        current_directory = Path(__file__).resolve().parent
        _sns_info = pd.DataFrame(fload(current_directory / "data" / "sns_info.json"))

    return _sns_info

# Suppress INFO messages from fontTools
logging.getLogger("fontTools").setLevel(logging.ERROR)
logging.getLogger("matplotlib").setLevel(logging.ERROR)

warnings.simplefilter("ignore", category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)


def add_text(ax=None, height_offset=0.5, fmt=".1f", **kwargs):
    """Adds text annotations for various types of Seaborn and Matplotlib plots.
    Args:
        ax: Axes object.
        height_offset: 0.5 (default) The vertical distance (offset) to place the text.
        fmt: Default is ".1f" for one decimal place.
        **kwargs: Additional keyword arguments for the text function
    Usage:
        ax = sns.barplot(x='Category', y='Values', data=data)
        add_text(ax=ax, height_offset=1.0, color='black', fontsize=12)

    The function will automatically detect the type of plot and add annotations accordingly.
    It supports annotations for:
    - **Bar Plots**: Displays the height of each bar.
    - **Box Plots**: Shows the height of the boxes.
    - **Scatter and Line Plots**: Displays the y-value for each point.
    - **Histograms and KDE Plots**: Shows the maximum height of the bars.
    - **Other Plots**: If the Axes contains containers, it handles those as well.
    """
    from matplotlib.collections import LineCollection

    ha = kwargs.pop("ha", "center")
    va = kwargs.pop("va", "bottom")
    if ax is None:
        ax = plt.gca()
    # Check if the Axes has patches (for bar, count, boxen, violin, and other plots with bars)
    # Check for artists (for box plots)
    if hasattr(ax, "artists") and ax.artists:
        print("artists")
        for box in ax.artists:
            if hasattr(box, "get_height") and hasattr(box, "get_y"):
                height = box.get_y() + box.get_height()  # For box plots

                ax.text(
                    box.get_x() + box.get_width() / 2.0,
                    height + height_offset,
                    format(height, fmt),
                    ha=ha,
                    va=va,
                    **kwargs,
                )

    # Scatter plot or line plot
    if hasattr(ax, "lines"):
        print("lines")
        for line in ax.lines:
            if hasattr(line, "get_xydata"):
                xdata, ydata = line.get_xydata().T  # Get x and y data points
                for x, y in zip(xdata, ydata):
                    ax.text(x, y + height_offset, format(y, fmt), **kwargs)

    if hasattr(ax, "patches") and ax.patches:
        print("patches")
        for p in ax.patches:
            if hasattr(p, "get_height"):
                height = p.get_height()  # For bar plots

                ax.text(
                    p.get_x() + p.get_width() / 2.0,
                    height + height_offset,
                    format(height, fmt),
                    ha=ha,
                    va=va,
                    **kwargs,
                )
    # For histplot, kdeplot, rugplot
    if hasattr(ax, "collections"):
        print("collections")
        for collection in ax.collections:
            # If it is a histogram or KDE plot
            if isinstance(collection, LineCollection):
                for path in collection.get_paths():
                    if hasattr(path, "vertices"):
                        vertices = path.vertices
                        # Get the heights (y values) for histogram or KDE plots
                        ax.text(
                            vertices[:, 0].mean(),
                            vertices[:, 1].max() + height_offset,
                            format(vertices[:, 1].max(), fmt),
                            **kwargs,
                        )
            # Handle point, strip, and swarm plots
            elif isinstance(collection, LineCollection):
                for path in collection.get_paths():
                    vertices = path.vertices
                    ax.text(
                        vertices[:, 0].mean(),
                        vertices[:, 1].max() + height_offset,
                        format(vertices[:, 1].max(), fmt),
                        **kwargs,
                    )
        # Handle bar charts (not from seaborn)
    if hasattr(ax, "containers"):
        print("containers")
        for container in ax.containers:
            for bar in container:
                if hasattr(bar, "get_height"):
                    height = bar.get_height()

                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        height + height_offset,
                        format(height, fmt),
                        ha=ha,
                        va=va,
                        **kwargs,
                    )


def pval2str(p):
    if p > 0.05:
        txt = ""
    elif 0.01 <= p <= 0.05:
        txt = "*"
    elif 0.001 <= p < 0.01:
        txt = "**"
    elif p < 0.001:
        txt = "***"
    return txt

def heatmap(
    data,
    data_y=None, 
    ax=None,
    kind="corr",  #'corr','direct','pivot'
    method="pearson",  # for correlation: ‘pearson’(default), ‘kendall’, ‘spearman’
    columns=None,  # pivot, default: coll numeric columns
    columns_x=None,  #  For dataset1 when data_y provided
    columns_y=None,  # For dataset2 when data_y provided
    style=1,  # for correlation
    index=None,  # pivot
    values=None,  # pivot
    fontsize=10,
    tri="u",
    k=0,
    mask=True,
    vmin=None,
    vmax=None,
    size_scale=500,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    show_indicator=True,  # only for style==1
    cluster=False,
    inplace=False,
    figsize=(10, 8),
    row_cluster=True,  # Perform clustering on rows
    col_cluster=True,  # Perform clustering on columns
    dendrogram_ratio=(0.2, 0.1),  # Adjust size of dendrograms
    cbar_pos=(0.02, 1, 0.02, 0.1),  # Adjust colorbar position
    xticklabels=True,  # Show column labels
    yticklabels=True,  # Show row labels
    set_aspect: bool = False,
    invert_yaxis: bool = False,
    kws_figsets:dict = {},
    **kwargs,
):
    """
    plot heatmap or clustermap for a given dataset (DataFrame).
    """
    from matplotlib import patches
    p_ = None
    kinds = ["corr", "direct", "pivot"]
    kind = strcmp(kind, kinds)[0]
    if ax is None and not cluster:
        ax = plt.gca()
    
    # Check if we have two datasets
    has_two_datasets = data_y is not None
    
    # Handle list input for backward compatibility
    if isinstance(data, list) and len(data) == 2 and not has_two_datasets:
        print("Warning: Using list syntax. Consider using data_y parameter instead.")
        data_y = data[1]
        data = data[0]
        has_two_datasets = True
    
    if has_two_datasets:
        if isinstance(data, list):
            raise ValueError("Cannot provide both data_y and data as list")
        
        # Select numeric columns from both datasets
        if columns_x is None:
            df_numeric1 = data.select_dtypes(include=[np.number])
        else:
            df_numeric1 = data[columns_x]
        
        if columns_y is None:
            df_numeric2 = data_y.select_dtypes(include=[np.number])
        else:
            df_numeric2 = data_y[columns_y]
        
        # For correlation with two datasets
        if "corr" in kind: 
            if method.lower() == "mantel":
                # Mantel test style comparison
                from scipy.spatial.distance import pdist, squareform
                
                # Compute distance matrices
                dist1 = squareform(pdist(df_numeric1, metric='euclidean'))
                dist2 = squareform(pdist(df_numeric2, metric='euclidean'))
                
                # Flatten upper triangles
                n = dist1.shape[0]
                triu_indices = np.triu_indices(n, k=1)
                flat1 = dist1[triu_indices]
                flat2 = dist2[triu_indices]
                
                # Compute correlation between distance matrices
                from scipy.stats import pearsonr
                corr_val, p_val = pearsonr(flat1, flat2)
                
                # Create a simple matrix showing the correlation
                data4heatmap = pd.DataFrame([[corr_val]], columns=['Mantel Correlation'], index=[''])
                p_ = pd.DataFrame([[p_val]], columns=['p-value'], index=[''])
                
                if annot:
                    print(f"Mantel Correlation: {corr_val:.3f}, p-value: {p_val:.4f}")
            
            else:  # Regular cross-correlation
                from scipy.stats import pearsonr, spearmanr, kendalltau
                
                # Choose correlation function based on method
                if method == "pearson":
                    corr_func = pearsonr
                elif method == "spearman":
                    corr_func = spearmanr
                elif method == "kendall":
                    corr_func = kendalltau
                else:
                    corr_func = pearsonr
                
                # Initialize correlation and p-value matrices
                corr_matrix = pd.DataFrame(
                    index=df_numeric1.columns,
                    columns=df_numeric2.columns,
                    dtype=float
                )
                
                p_matrix = pd.DataFrame(
                    index=df_numeric1.columns,
                    columns=df_numeric2.columns,
                    dtype=float
                )
                
                # Compute correlations for all column pairs
                for i, col1 in enumerate(df_numeric1.columns):
                    for j, col2 in enumerate(df_numeric2.columns):
                        x_vals = df_numeric1[col1].dropna()
                        y_vals = df_numeric2[col2].dropna()
                        
                        # Ensure consistent indices
                        common_idx = x_vals.index.intersection(y_vals.index)
                        if len(common_idx) > 1:
                            x_common = x_vals.loc[common_idx]
                            y_common = y_vals.loc[common_idx]
                            
                            try:
                                corr, pval = corr_func(x_common, y_common)
                                corr_matrix.iloc[i, j] = corr
                                p_matrix.iloc[i, j] = pval
                            except:
                                corr_matrix.iloc[i, j] = np.nan
                                p_matrix.iloc[i, j] = np.nan
                        else:
                            corr_matrix.iloc[i, j] = np.nan
                            p_matrix.iloc[i, j] = np.nan
                
                data4heatmap = corr_matrix
                p_ = p_matrix
                # Store original dimensions for plotting
                n_rows_cross = len(df_numeric1.columns)
                n_cols_cross = len(df_numeric2.columns)
        
        else:  # For direct or pivot with two datasets
            data4heatmap = df_numeric1
            p_ = pd.DataFrame()
            n_rows_cross = len(data4heatmap.index)
            n_cols_cross = len(data4heatmap.columns)
    
    else:  # Single dataset
        # Select numeric columns
        if columns_x is not None and columns is None:
            columns = columns_x
        if columns is None:
            df_numeric = data.select_dtypes(include=[np.number])
        else:
            df_numeric = data[columns]
        
        if "corr" in kind:  # correlation 
            from scipy.stats import pearsonr, spearmanr, kendalltau
            
            if method == "pearson":
                corr_func = pearsonr
            elif method == "spearman":
                corr_func = spearmanr
            elif method == "kendall":
                corr_func = kendalltau
            else:
                corr_func = pearsonr
            
            # Initialize correlation and p-value matrices
            corr_matrix = pd.DataFrame(
                index=df_numeric.columns,
                columns=df_numeric.columns,
                dtype=float
            )
            
            p_matrix = pd.DataFrame(
                index=df_numeric.columns,
                columns=df_numeric.columns,
                dtype=float
            )
            
            # Compute correlations
            for i, col1 in enumerate(df_numeric.columns):
                for j, col2 in enumerate(df_numeric.columns):
                    if i <= j:  # Only compute once for symmetric matrix
                        x_vals = df_numeric[col1].dropna()
                        y_vals = df_numeric[col2].dropna()
                        
                        common_idx = x_vals.index.intersection(y_vals.index)
                        if len(common_idx) > 1:
                            x_common = x_vals.loc[common_idx]
                            y_common = y_vals.loc[common_idx]
                            
                            try:
                                corr, pval = corr_func(x_common, y_common)
                                corr_matrix.iloc[i, j] = corr
                                corr_matrix.iloc[j, i] = corr
                                p_matrix.iloc[i, j] = pval
                                p_matrix.iloc[j, i] = pval
                            except:
                                corr_matrix.iloc[i, j] = np.nan
                                corr_matrix.iloc[j, i] = np.nan
                                p_matrix.iloc[i, j] = np.nan
                                p_matrix.iloc[j, i] = np.nan
                        else:
                            corr_matrix.iloc[i, j] = np.nan
                            corr_matrix.iloc[j, i] = np.nan
                            p_matrix.iloc[i, j] = np.nan
                            p_matrix.iloc[j, i] = np.nan
            
            data4heatmap = corr_matrix
            p_ = p_matrix
        
        elif "dir" in kind:  # direct
            data4heatmap = df_numeric
            p_ = pd.DataFrame()
        
        elif "pi" in kind:  # pivot
            try:
                print(f'pivot: \n\tneed at least 3 param: e.g., index="Task", columns="Model", values="Score"')
                data4heatmap = data.pivot(index=index, columns=columns, values=values)
                p_ = pd.DataFrame()
            except:
                print(f'pivot_table: \n\tneed at least 4 param: e.g., index="Task", columns="Model", values="Score",aggfunc="mean"')
                aggfunc = "mean"
                for k_, v_ in kwargs.items():
                    if "agg" in k_.lower():
                        aggfunc = v_
                    kwargs.pop(k_, None)
                data4heatmap = data.pivot_table(
                    index=index, columns=columns, values=values, aggfunc=aggfunc
                )
                p_ = pd.DataFrame()
        else:
            print(f'"{kind}" is not supported')
            return None

    ##################################### 
    #### shared setup for all kinds ##### 
    #####################################
    
    # Get dimensions
    n_rows = len(data4heatmap.index)
    n_cols = len(data4heatmap.columns)

    # preset for appearance 
    xlim=kws_figsets.pop('xlim',(-0.5, n_cols - 0.5))
    ylim=kws_figsets.pop('ylim',(-0.5, n_rows - 0.5))
    xticks=kws_figsets.pop('xticks',range(n_cols))
    yticks=kws_figsets.pop('yticks',range(n_rows))
    xticklabels=kws_figsets.pop('xticklabels',data4heatmap.column())
    yticklabels=kws_figsets.pop('yticklabels',data4heatmap.index)
    xangle=kws_figsets.pop('xangle',90)
    
    # Check if it's a square matrix (for triangular plots)
    is_square_matrix = n_rows == n_cols and all(data4heatmap.index == data4heatmap.columns)
    
    # Set default vmin/vmax for correlation matrices
    if "corr" in kind and vmin is None:
        vmin = -1 if method.lower() != "mantel" else np.min(data4heatmap.values)
    if "corr" in kind and vmax is None:
        vmax = 1 if method.lower() != "mantel" else np.max(data4heatmap.values)
    
    if isinstance(cmap, str):
        cmap = get_cmap(cmap)
    if vmin is None:
        vmin = np.min(data4heatmap.values)
    if vmax is None:
        vmax = np.max(data4heatmap.values)
    
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    
    # For correlation, check if p-values are available
    if "corr" in kind and p_ is not None and not p_.empty:
        has_p_values = True
    else:
        has_p_values = False

    # Create mask array only for square correlation matrices
    if (mask and "corr" in kind and is_square_matrix):
        if "u" in tri.lower():
            mask_array = np.tril(np.ones_like(data4heatmap, dtype=bool), k=k)
        else:
            mask_array = np.triu(np.ones_like(data4heatmap, dtype=bool), k=k)
    else:
        mask_array = None
    
    title = kwargs.get("title", None)
    # Remove conflicting kwargs
    conflicting_kwargs = ["mask", "annot", "cmap", "fmt", "clustermap", 
                        "row_cluster", "col_cluster", "dendrogram_ratio", 
                        "cbar_pos", "xticklabels", "col_cluster","title"]
    for key in conflicting_kwargs:
        kwargs.pop(key, None)
    
    ##################################### 
    #### cluster logic for all kinds##### 
    #####################################
    if cluster:
        # For Mantel test result (single value), clustering doesn't make sense
        if method.lower() == "mantel" and has_two_datasets:
            print("Clustering not applicable for Mantel test results")
            cluster = False
        else:
            cluster_obj = sns.clustermap(
                data4heatmap,
                mask=mask_array if "corr" in kind and is_square_matrix else None,
                annot=annot,
                cmap=cmap,
                fmt=fmt,
                figsize=figsize,
                row_cluster=row_cluster,
                col_cluster=col_cluster,
                dendrogram_ratio=dendrogram_ratio,
                cbar_pos=cbar_pos,
                xticklabels=xticklabels,
                yticklabels=yticklabels,
                **kwargs,
            )
            return cluster_obj.ax_heatmap

    ##################################### 
    #### non-cluster logic for all kinds##### 
    #####################################
    else:
        # Handle special case for Mantel test (single value)
        if method.lower() == "mantel" and has_two_datasets and data4heatmap.shape == (1, 1):
            # Create a simple display for Mantel test result
            ax.text(0.5, 0.5, 
                   f"Mantel r = {data4heatmap.iloc[0,0]:.3f}\np = {p_.iloc[0,0]:.4f}",
                   ha='center', va='center', fontsize=fontsize*1.5,
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])
            return ax
        
        # Now handle all styles with proper rectangular matrix support
        if style == 0: # default, normal 
            ax = sns.heatmap(
                data4heatmap,
                ax=ax,
                mask=mask_array,
                annot=annot,
                cmap=cmap, vmin=vmin, vmax=vmax,
                fmt=fmt,
                **kwargs,
            )
            # figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets)

            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(**kws_figsets)
            return ax
            
        elif style == 1: # Bubble plot style for correlation matrices 
            # Check if this style is appropriate
            if not is_square_matrix:
                # print("Style 1 is designed for square correlation matrices. Switching to style 0.")
                return heatmap(data, data_y=data_y, ax=ax, kind=kind, method=method, style=0, 
                                  fontsize=fontsize, tri=tri, mask=mask, k=k, vmin=vmin, vmax=vmax,
                                  size_scale=size_scale, annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs)

            scatter_handles = []
            for i in range(n_rows):
                for j in range(n_cols):
                    if (i < j) if "u" in tri.lower() else (j < i):  # upper/lower triangle
                        color = cmap(norm(data4heatmap.iloc[i, j]))
                        scatter = ax.scatter(
                            j, i,  # Note: swapped i,j for correct orientation
                            s=np.abs(data4heatmap.iloc[i, j]) * size_scale,
                            color=color,
                            **kwargs,
                        )
                        scatter_handles.append(scatter)
                        if show_indicator and has_p_values:
                            ax.text(
                                j, i,  # swapped
                                pval2str(p_.iloc[i, j]),
                                ha="center",
                                va="center",
                                color="k",
                                fontsize=fontsize * 1.2,
                            )
                    elif (i > j) if "u" in tri.lower() else (j > i):  # opposite triangle
                        color = cmap(norm(data4heatmap.iloc[i, j]))
                        ax.text(
                            j, i,  # swapped
                            f"{data4heatmap.iloc[i, j]:{fmt}}",
                            ha="center",
                            va="center",
                            color=color,
                            fontsize=fontsize,
                        )
                    else:  # diagonal
                        ax.scatter(j, i, s=1, color="white")
            
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets)
            
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax, label="Correlation Coefficient" if "corr" in kind else "")
            return ax
            
        elif style == 2: # Diverging bar style heatmap
            bar_width = 0.8
            bar_height = 0.8
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    rect = patches.Rectangle(
                        (j - bar_width/2, i - bar_height/2),
                        width=bar_width * (value - vmin) / (vmax - vmin) if value >= 0 else bar_width * abs(value - vmin) / (vmax - vmin),
                        height=bar_height,
                        color=color,
                        alpha=0.8,
                        linewidth=0.5,
                        edgecolor='white'
                    )
                    ax.add_patch(rect)
                    
                    if annot:
                        ax.text(j, i, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if abs(norm(value)) > 0.5 else 'black',
                            fontsize=fontsize)
            

            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets) 
            
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax)
            return ax
            
        elif style == 3: # Circular heatmap with size/color encoding
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    circle = patches.Circle(
                        (j, i),
                        radius=0.35 * abs(value) / (vmax - vmin) * 2 if "corr" in kind else 0.35,
                        color=color,
                        alpha=0.8,
                        linewidth=1,
                        edgecolor='white'
                    )
                    ax.add_patch(circle)
                    
                    if annot:
                        ax.text(j, i, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if abs(norm(value)) > 0.6 else 'black',
                            fontsize=fontsize,
                            fontweight='bold')
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            ax.grid(True, which='both', color='lightgray', linestyle='-', linewidth=0.5, alpha=0.5)
            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets) 
            
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax)
            return ax
 
        # Style 4: Text-only heatmap
        elif style == 4:
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    weight = 'bold' if abs(value) > np.percentile(np.abs(data4heatmap.values.flatten()), 75) else 'normal'
                    size = fontsize * (1 + 0.5 * abs(value) / max(abs(vmax), abs(vmin))) if "corr" in kind else fontsize
                    
                    ax.text(j, i, f"{value:{fmt}}",
                        ha='center', va='center',
                        color=color,
                        fontsize=size,
                        fontweight=weight,
                        bbox=dict(boxstyle="round,pad=0.3",
                                facecolor='white',
                                alpha=0.7,
                                edgecolor='lightgray'))
              

            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets) 
            
            for spine in ax.spines.values():
                spine.set_visible(False)
            return ax

        elif style == 5:# Gradient background with cell borders
            """Gradient background with cell borders""" 
            
            # Create gradient background
            im = ax.imshow(data4heatmap.values, cmap=cmap, aspect='auto', 
                        interpolation='nearest', alpha=0.7)
            
            # Add cell borders
            for i in range(n_rows + 1):
                ax.axhline(i - 0.5, color='white', linewidth=1, alpha=0.5)
            for j in range(n_cols + 1):
                ax.axvline(j - 0.5, color='white', linewidth=1, alpha=0.5)
            
            # Add value annotations
            if annot:
                for i in range(n_rows):
                    for j in range(n_cols):
                        value = data4heatmap.iloc[i, j]
                        text_color = 'white' if abs(norm(value)) > 0.5 else 'black'
                        ax.text(j, i, f"{value:{fmt}}",
                            ha='center', va='center',
                            color=text_color,
                            fontsize=fontsize,
                            fontweight='bold',
                            bbox=dict(boxstyle="circle,pad=0.1",
                                        facecolor=cmap(norm(value)),
                                        alpha=0.3,
                                        edgecolor='none'))

            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets)
            return ax
        elif style == 6:# Half-matrix style for correlation matrices
            """Half-matrix style for correlation (combining scatter and text)"""            
            # Create half matrix visualization
            for i in range(n_rows):
                for j in range(n_cols):
                    if (i < j) if "u" in tri.lower() else (j < i):  # Upper triangle: scatter with p-value
                        value = data4heatmap.iloc[i, j]
                        color = cmap(norm(value))
                        
                        # Create scatter with size proportional to absolute correlation
                        ax.scatter(j, i, 
                                s=np.abs(value) * size_scale,
                                color=color,
                                marker='o',
                                edgecolor='white',
                                linewidth=1,
                                alpha=0.8,
                                **kwargs)
                        
                        # Add p-value indicator if available
                        if show_indicator and 'p_' in locals():
                            ax.text(j, i, pval2str(p_.iloc[i, j]),
                                ha='center', va='center',
                                color='white' if abs(value) > 0.5 else 'black',
                                fontsize=fontsize * 0.8)
                    
                    elif (i > j) if "u" in tri.lower() else (j > i): # Lower triangle: text with correlation value
                        value = data4heatmap.iloc[i, j]
                        color = cmap(norm(value))
                        
                        ax.text(j, i, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if abs(value) > 0.7 else 'black',
                            fontsize=fontsize,
                            fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.2",
                                        facecolor=color,
                                        alpha=0.8,
                                        edgecolor='white',
                                        linewidth=1))
                    
                    else:  # Diagonal: variable names
                        ax.text(j, i, data4heatmap.columns[i],
                            ha='center', va='center',
                            fontsize=fontsize * 1.2,
                            fontweight='bold',
                            rotation=45)
            
            # # Set axis properties
            # ax.set_xlim(-0.5, n_cols - 0.5)
            # ax.set_ylim(-0.5, n_rows - 0.5)
            # ax.set_xticks([])
            # ax.set_yticks([])

            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xlim=xlim,ylim=ylim,xticks=[],yticks=[],xticklabels=[],yticklabels=[],xangle=xangle,**kws_figsets)
            for spine in ax.spines.values():
                spine.set_visible(True)
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.8)
            # cbar.set_label('Correlation Coefficient', fontsize=fontsize)
            
            return ax
        elif style == 7:#Tile-style heatmap with gradient edges
            """Tile-style heatmap with gradient edges"""
            from matplotlib.patches import FancyBboxPatch 
            
            # Create fancy boxes for each cell
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    base_color = cmap(norm(value))
                    
                    # Create gradient edge effect
                    edge_color = tuple([min(1.0, c * 1.2) for c in base_color[:3]] + [1.0])
                    
                    # Create rounded rectangle
                    box = FancyBboxPatch((j - 0.4, i - 0.4),
                                        width=0.8, height=0.8,
                                        boxstyle="round,pad=0.02,rounding_size=0.1",
                                        facecolor=base_color,
                                        edgecolor=edge_color,
                                        linewidth=2,
                                        alpha=0.9)
                    ax.add_patch(box)
                    
                    # Add value annotation
                    if annot:
                        ax.text(j, i, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if norm(value) > 0.7 else 'black',
                            fontsize=fontsize,
                            fontweight='bold')
            
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xlim=xlim,ylim=ylim,xticks=[],yticks=[],xticklabels=[],yticklabels=[],xangle=xangle,**kws_figsets)

            # Add subtle grid
            ax.grid(True, which='both', color='white', linestyle='-', 
                    linewidth=0.5, alpha=0.3)
            
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax, pad=0.02)
            
            return ax
        elif style == 8: # (Fan/Sector) style heatmap - circular segments
            """扇形 (Fan/Sector) style heatmap - circular segments""" 
            # Create polar-like fan segments
            n_rows = n_rows
            n_cols = n_cols
            
            # Calculate angles for each sector
            total_angle = 360
            sector_angle = total_angle / n_cols
            
            # Create concentric circles for rows
            max_radius = min(n_rows, 5)  # Limit radius for better visualization
            
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Calculate sector parameters
                    radius = (i + 1) * (max_radius / n_rows)
                    start_angle = j * sector_angle
                    end_angle = (j + 1) * sector_angle
                    
                    # Create wedge (扇形)
                    wedge = patches.Wedge(
                        center=(0, 0),
                        r=radius,
                        theta1=start_angle,
                        theta2=end_angle,
                        width=radius - (radius * 0.8 if i > 0 else 0),  # For inner circles
                        color=color,
                        alpha=0.8,
                        linewidth=1,
                        edgecolor='white'
                    )
                    ax.add_patch(wedge)
                    
                    # Add label in the middle of the sector
                    if annot:
                        mid_angle = (start_angle + end_angle) / 2
                        mid_radius = radius - (radius - (radius * 0.8 if i > 0 else 0)) / 2
                        
                        # Convert polar to cartesian coordinates
                        x = mid_radius * np.cos(np.radians(mid_angle))
                        y = mid_radius * np.sin(np.radians(mid_angle))
                        
                        ax.text(x, y, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if norm(value) > 0.7 else 'black',
                            fontsize=fontsize * 0.8,
                            rotation=mid_angle - 90 if abs(mid_angle) > 90 else mid_angle)
            

            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            ax.set_xlim(-max_radius * 1.2, max_radius * 1.2)
            ax.set_ylim(-max_radius * 1.2, max_radius * 1.2)
            
            # Add radial labels
            for i in range(n_rows):
                radius = (i + 0.5) * (max_radius / n_rows)
                angle = -5  # Text position
                x = radius * np.cos(np.radians(angle))
                y = radius * np.sin(np.radians(angle))
                ax.text(x, y, data4heatmap.index[i] if i < n_rows else f"Row {i}",
                    ha='right', va='center', fontsize=fontsize * 0.7)
            
            # Add angular labels
            for j in range(n_cols):
                angle = j * sector_angle + sector_angle / 2
                radius = max_radius * 1.1
                x = radius * np.cos(np.radians(angle))
                y = radius * np.sin(np.radians(angle))
                
                ax.text(x, y, data4heatmap.columns[j] if j < n_cols else f"Col {j}",
                    ha='center', va='center',
                    fontsize=fontsize * 0.7,
                    rotation=angle - 90 if angle > 90 and angle < 270 else angle)
            
            # Remove axis frames
            ax.set_frame_on(False)
            ax.set_xticks([])
            ax.set_yticks([])
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax, pad=0.05, shrink=0.8)
            
            return ax
        elif style == 9:# Radial heatmap - rays emanating from center
            """放射状 (Radial) heatmap - rays emanating from center""" 
            n_rows = n_rows
            n_cols = n_cols
            
            # Create radial layout
            center = (0, 0)
            max_radius = min(n_rows, n_cols) / 2
            
            # Create rays for each column
            for j in range(n_cols):
                angle = j * (360 / n_cols)
                rad_angle = np.radians(angle)
                
                # Create points along the ray for each row
                for i in range(n_rows):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Calculate position
                    radius = (i + 1) * (max_radius / n_rows)
                    x = radius * np.cos(rad_angle)
                    y = radius * np.sin(rad_angle)
                    
                    # Create a circle at this position
                    circle = patches.Circle((x, y),
                                        radius=0.2 * max_radius / n_rows * (1 + abs(value) / max(abs(vmax), abs(vmin))),
                                        color=color,
                                        alpha=0.8,
                                        linewidth=1,
                                        edgecolor='white')
                    ax.add_patch(circle)
                    
                    # Add value
                    if annot:
                        ax.text(x, y, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if norm(value) > 0.7 else 'black',
                            fontsize=fontsize * 0.7)
            
            # Add connecting lines between same-row points
            for i in range(n_rows):
                points = []
                for j in range(n_cols):
                    angle = j * (360 / n_cols)
                    radius = (i + 1) * (max_radius / n_rows)
                    x = radius * np.cos(np.radians(angle))
                    y = radius * np.sin(np.radians(angle))
                    points.append((x, y))
                
                # Close the polygon
                points.append(points[0])
                
                # Draw connecting line
                xs, ys = zip(*points)
                ax.plot(xs, ys, color='gray', alpha=0.3, linewidth=0.5)
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            ax.set_xlim(-max_radius * 1.5, max_radius * 1.5)
            ax.set_ylim(-max_radius * 1.5, max_radius * 1.5)
            
            # Add labels
            for i in range(n_rows):
                radius = (i + 0.5) * (max_radius / n_rows)
                ax.text(radius, 0, data4heatmap.index[i] if i < n_rows else f"R{i}",
                    ha='left', va='center', fontsize=fontsize * 0.7)
            
            for j in range(n_cols):
                angle = j * (360 / n_cols)
                radius = max_radius * 1.2
                x = radius * np.cos(np.radians(angle))
                y = radius * np.sin(np.radians(angle))
                
                ax.text(x, y, data4heatmap.columns[j] if j < n_cols else f"C{j}",
                    ha='center', va='center',
                    fontsize=fontsize * 0.7,
                    rotation=angle - 90 if angle > 90 and angle < 270 else angle)
            
            ax.set_frame_on(False)
            ax.set_xticks([])
            ax.set_yticks([])
            
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax, pad=0.05, shrink=0.8)
            
            return ax
        elif style == 10:# Hexagonal heatmap - honeycomb pattern
            """蜂窝 (Hexagonal) heatmap - honeycomb pattern""" 
            n_rows = n_rows
            n_cols = n_cols
            
            # Hexagon parameters
            hex_radius = 0.4
            hex_height = hex_radius * np.sqrt(3)
            
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Stagger rows for honeycomb pattern
                    x_offset = 0 if i % 2 == 0 else hex_radius * 0.5
                    x = j * hex_radius * 1.5 + x_offset
                    y = i * hex_height * 0.75
                    
                    # Create hexagon vertices
                    hexagon = patches.RegularPolygon(
                        (x, y),
                        numVertices=6,
                        radius=hex_radius,
                        orientation=np.pi/6,  # Rotate 30 degrees
                        facecolor=color,
                        edgecolor='white',
                        linewidth=1,
                        alpha=0.9
                    )
                    ax.add_patch(hexagon)
                    
                    # Add value
                    if annot:
                        ax.text(x, y, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if norm(value) > 0.7 else 'black',
                            fontsize=fontsize * 0.8,
                            fontweight='bold')
            
            # Set axis limits
            ax.set_xlim(-hex_radius, n_cols * hex_radius * 1.5 + hex_radius)
            ax.set_ylim(-hex_height, n_rows * hex_height * 0.75 + hex_height)
            
            # Add labels
            for i in range(n_rows):
                ax.text(-hex_radius * 2, i * hex_height * 0.75,
                    data4heatmap.index[i] if i < n_rows else f"R{i}",
                    ha='right', va='center', fontsize=fontsize)
            
            for j in range(n_cols):
                ax.text(j * hex_radius * 1.5, -hex_height * 2,
                    data4heatmap.columns[j] if j < n_cols else f"C{j}",
                    ha='center', va='top', fontsize=fontsize, rotation=90)
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            ax.set_frame_on(False)
            ax.set_xticks([])
            ax.set_yticks([])

            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax, pad=0.05, shrink=0.8)
            
            return ax
        elif style == 11:
            """螺旋 (Spiral) heatmap - spiral layout""" 
            n_rows = n_rows
            n_cols = n_cols
            total_cells = n_rows * n_cols
            
            # Create spiral layout
            center = (0, 0)
            a = 0.1  # Spiral tightness
            b = 0.05  # Spiral growth rate
            
            cell_index = 0
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Calculate spiral position
                    angle = cell_index * (360 / total_cells) * 0.5
                    radius = a + b * angle
                    
                    x = radius * np.cos(np.radians(angle))
                    y = radius * np.sin(np.radians(angle))
                    
                    # Create spiral segment
                    circle = patches.Circle((x, y),
                                        radius=0.05 * (1 + abs(value) / max(abs(vmax), abs(vmin))),
                                        color=color,
                                        alpha=0.8,
                                        linewidth=1,
                                        edgecolor='white')
                    ax.add_patch(circle)
                    
                    # Add small label for extreme values
                    if annot and (abs(value) > np.percentile(np.abs(data4heatmap.values.flatten()), 75)):
                        ax.text(x, y, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white',
                            fontsize=fontsize * 0.6)
                    
                    # Draw line to next point (creates spiral effect)
                    if cell_index > 0:
                        prev_angle = (cell_index - 1) * (360 / total_cells) * 0.5
                        prev_radius = a + b * prev_angle
                        prev_x = prev_radius * np.cos(np.radians(prev_angle))
                        prev_y = prev_radius * np.sin(np.radians(prev_angle))
                        
                        ax.plot([prev_x, x], [prev_y, y], 
                            color='gray', alpha=0.2, linewidth=0.5)
                    
                    cell_index += 1
                
            patch_min = patches.Patch(color=cmap(norm(vmin)))
            patch_max = patches.Patch(color=cmap(norm(vmax)))

            ax.legend(
                handles=[patch_min, patch_max],
                labels=[f"Min: {vmin:{fmt}}", f"Max: {vmax:{fmt}}"],
                loc="upper right",
                fontsize=fontsize * 0.7
            )
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            max_radius = a + b * 360
            # ax.set_xlim(-max_radius * 1.2, max_radius * 1.2)
            # ax.set_ylim(-max_radius * 1.2, max_radius * 1.2)
            
            ax.set_frame_on(False)
            ax.set_xticks([])
            ax.set_yticks([])
            
            return ax
        elif style == 12:
            """太极 (Yin-Yang) style for correlation matrices"""
            if "corr" not in kind:
                # print("Style 12 is designed for correlation matrices. Switching to style 1.")
                return heatmap(data, ax=ax, kind=kind, method=method, style=1, 
                                fontsize=fontsize, tri=tri, mask=mask, k=k, 
                                vmin=vmin, vmax=vmax, size_scale=size_scale, 
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs) 
            # Create yin-yang style visualization
            for i in range(n_rows):
                for j in range(n_cols):
                    if i == j:  # Diagonal: full yin-yang
                        # Create yin-yang symbol
                        from matplotlib.patches import Arc
                        
                        # Outer circle
                        circle = patches.Circle((j, i), radius=0.4,
                                            facecolor='black', alpha=0.1)
                        ax.add_patch(circle)
                        
                        # Add variable name
                        ax.text(j, i, data4heatmap.columns[i],
                            ha='center', va='center',
                            fontsize=fontsize * 1.2,
                            fontweight='bold',
                            rotation=45)
                        
                    elif i < j:  # Upper triangle: yang (white) side
                        value = data4heatmap.iloc[i, j]
                        if value > 0:
                            # White yang side
                            circle = patches.Wedge((j, i), r=0.3,
                                                theta1=90, theta2=270,
                                                facecolor='white',
                                                edgecolor='black',
                                                linewidth=1)
                        else:
                            # Black yin side (flipped)
                            circle = patches.Wedge((j, i), r=0.3,
                                                theta1=270, theta2=90,
                                                facecolor='black',
                                                edgecolor='white',
                                                linewidth=1)
                        ax.add_patch(circle)
                        
                        # Add small opposite circle
                        if value > 0:
                            small_circle = patches.Circle((j - 0.15, i), radius=0.1,
                                                        facecolor='black')
                        else:
                            small_circle = patches.Circle((j + 0.15, i), radius=0.1,
                                                        facecolor='white')
                        ax.add_patch(small_circle)
                        
                        # Add correlation value
                        if annot:
                            ax.text(j, i, f"{value:{fmt}}",
                                ha='center', va='center',
                                color='black' if value > 0 else 'white',
                                fontsize=fontsize * 0.8)
                    
                    else:  # Lower triangle: simplified representation
                        value = data4heatmap.iloc[i, j]
                        color_intensity = abs(value)
                        
                        # Create circle with yin-yang inspired gradient
                        if value > 0:
                            # More white
                            circle = patches.Circle((j, i), radius=0.35,
                                                facecolor=cmap(norm(value)),
                                                edgecolor='white',
                                                linewidth=2,
                                                alpha=0.8)
                        else:
                            # More black
                            circle = patches.Circle((j, i), radius=0.35,
                                                facecolor=cmap(norm(value)),
                                                edgecolor='black',
                                                linewidth=2,
                                                alpha=0.8)
                        ax.add_patch(circle)
                        
                        if annot:
                            ax.text(j, i, f"{value:{fmt}}",
                                ha='center', va='center',
                                color='white' if abs(value) > 0.5 else 'black',
                                fontsize=fontsize * 0.8)
            
            ax.set_xlim(-0.5, n_cols - 0.5)
            ax.set_ylim(-0.5, n_rows - 0.5)
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Add yin-yang legend
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', label='Positive Correlation',
                    markerfacecolor='white', markersize=10, markeredgecolor='black'),
                Line2D([0], [0], marker='o', color='w', label='Negative Correlation',
                    markerfacecolor='black', markersize=10, markeredgecolor='white')
            ]
            ax.legend(handles=legend_elements, loc='upper right', fontsize=fontsize * 0.7)
            
            return ax
        elif style == 13:
            """波浪 (Wave) style heatmap - wave pattern visualization""" 
            n_rows = n_rows
            n_cols = n_cols
            
            # Create wave pattern
            for i in range(n_rows):
                # Create wave line for this row
                x_vals = np.linspace(0, n_cols - 1, 100)
                y_base = i
                
                # Calculate wave amplitude based on row values
                row_mean = np.mean(data4heatmap.iloc[i, :].values)
                amplitude = norm(row_mean) * 0.5  # Scale amplitude
                
                y_vals = y_base + amplitude * np.sin(2 * np.pi * x_vals / n_cols * 2)
                
                # Plot wave line
                ax.plot(x_vals, y_vals, color='gray', alpha=0.3, linewidth=1)
                
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Position on wave
                    wave_y = y_base + amplitude * np.sin(2 * np.pi * j / n_cols * 2)
                    
                    # Create wave peak/valley marker
                    marker_size = 50 * (1 + abs(value) / max(abs(vmax), abs(vmin)))
                    
                    ax.scatter(j, wave_y, 
                            s=marker_size,
                            color=color,
                            marker='^' if value > 0 else 'v',  # Up for positive, down for negative
                            edgecolor='white',
                            linewidth=1,
                            alpha=0.8)
                    
                    # Add value label
                    if annot:
                        offset = 0.15 if value > 0 else -0.15
                        ax.text(j, wave_y + offset, f"{value:{fmt}}",
                            ha='center', va='center' if value > 0 else 'center',
                            color='k',#'white' if abs(norm(value)) > 0.7 else 'black',
                            fontsize=fontsize * 0.7)
            
            
            # Add labels
            for i in range(n_rows):
                ax.text(-0.8, i, data4heatmap.index[i] if i < n_rows else f"R{i}",
                    ha='right', va='center', fontsize=fontsize)
            
            ax.set_xticks(range(n_cols))
            ax.set_xticklabels(data4heatmap.columns, rotation=45, ha='right')
            ax.set_yticks([])
            
            # Set axis properties
            ax.set_xlim(-0.5, n_cols - 0.5)
            ax.set_ylim(-1, n_rows)
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            
            figsets({**kws_figsets})
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax, pad=0.05)
            
            return ax
        elif style == 14:
            """拼图 (Jigsaw Puzzle) style heatmap - puzzle pieces""" 
            # Function to create puzzle piece path
            def create_puzzle_piece(x, y, width=0.8, height=0.8):
                from matplotlib.path import Path

                
                # Puzzle piece vertices (simplified)
                vertices = [
                    (x - width/2, y - height/2),  # 0: bottom-left
                    (x - width/2, y - height/4),  # 1
                    (x - width/4, y - height/4),  # 2
                    (x - width/4, y + height/4),  # 3
                    (x - width/2, y + height/4),  # 4
                    (x - width/2, y + height/2),  # 5: top-left
                    (x + width/2, y + height/2),  # 6: top-right
                    (x + width/2, y + height/4),  # 7
                    (x + width/4, y + height/4),  # 8
                    (x + width/4, y - height/4),  # 9
                    (x + width/2, y - height/4),  # 10
                    (x + width/2, y - height/2),  # 11: bottom-right
                    (x, y - height/2),  # 12: bottom-middle
                    (x - width/2, y - height/2),  # 13: back to start
                ]
                
                codes = [
                    Path.MOVETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.LINETO,
                    Path.CLOSEPOLY,
                ]
                
                return Path(vertices, codes)
            
            # Create puzzle pieces
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Create puzzle piece
                    path = create_puzzle_piece(j, i)
                    patch = patches.PathPatch(path, 
                                            facecolor=color,
                                            edgecolor='white',
                                            linewidth=1.5,
                                            alpha=0.9)
                    ax.add_patch(patch)
                    
                    # Add value
                    if annot:
                        ax.text(j, i, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if abs(norm(value)) > 0.7 else 'black',
                            fontsize=fontsize,
                            fontweight='bold')
            
            
            # # Add labels
            ax.set_xticks(range(n_cols))
            ax.set_yticks(range(n_rows))
            ax.set_xticklabels(data4heatmap.columns, rotation=45, ha='right')
            ax.set_yticklabels(data4heatmap.index)
            
            # Set axis properties
            ax.set_xlim(-0.6, n_cols - 0.4)
            ax.set_ylim(-0.6, n_rows - 0.4)
            
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets({**kws_figsets})
            # Add subtle grid
            ax.grid(True, which='both', color='lightgray', 
                    linestyle=':', linewidth=0.5, alpha=0.3)
            
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            plt.colorbar(sm, ax=ax, pad=0.05)
            
            return ax
        elif style == 15:
            if "corr" not in kind:
                # For non-correlation data, use a simplified version
                ax = sns.heatmap(
                    data4heatmap,
                    ax=ax,
                    annot=annot,
                    cmap=cmap,
                    fmt=fmt,
                    square=True if set_aspect else False,
                    cbar_kws={'shrink': 0.8, 'label': 'Value'},
                    linewidths=0.5,
                    linecolor='gray',
                    **kwargs
                )
                return ax 
            # Create a clean correlation matrix
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Create cell
                    rect = patches.Rectangle(
                        (j - 0.5, i - 0.5), 1, 1,
                        facecolor=color,
                        edgecolor='white',
                        linewidth=0.5
                    )
                    ax.add_patch(rect)
                    
                    # Add correlation value with significance stars if available
                    if annot:
                        text=''
                        if 'p_' in locals() and hasattr(p_, 'iloc'):
                            text = f"{value:{fmt}}\n"+pval2str(p_.iloc[i, j]) if not is_nan(pval2str(p_.iloc[i, j])) else f"{value:{fmt}}"
                        ax.text(j, i, text,
                            ha='center', va='center',
                            color='white' if abs(value) > 0.7 else 'black',
                            fontsize=fontsize,
                            fontweight='normal')
            
            # Clean axis formatting
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)

            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets) 
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.8)

            return ax

        elif style == 16:
            if "corr" in kind:
                max_abs = max(abs(vmin), abs(vmax))
                vmin, vmax = -max_abs, max_abs
            
            # Use a diverging colormap
            if isinstance(cmap, str):
                cmap = get_cmap(cmap)
            
            norm = plt.Normalize(vmin=vmin, vmax=vmax)
            
            # Create heatmap cells
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Create cell with border
                    rect = patches.Rectangle(
                        (j - 0.5, i - 0.5), 1, 1,
                        facecolor=color,
                        edgecolor='white',
                        linewidth=0.5,
                        alpha=0.9
                    )
                    ax.add_patch(rect)
                    
                    # Add value if significant or above threshold
                    if annot:
                        # For correlation, only show significant or large values
                        if "corr" in kind:
                            if abs(value) > 0.3 or ('p_' in locals() and hasattr(p_, 'iloc') and p_.iloc[i, j] < 0.05):
                                ax.text(j, i, f"{value:{fmt}}",
                                    ha='center', va='center',
                                    color='white' if abs(norm(value)) > 0.7 else 'black',
                                    fontsize=fontsize * 0.9,
                                    fontweight='bold')
                        else:
                            # For non-correlation, show all values
                            ax.text(j, i, f"{value:{fmt}}",
                                ha='center', va='center',
                                color='white' if abs(norm(value) - 0.5) > 0.4 else 'black',
                                fontsize=fontsize * 0.9) 
            ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
            ax.grid(which='minor', color='white', linestyle='-', linewidth=0.5)
            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets) 

            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, pad=0.02)
            cbar.ax.tick_params(labelsize=fontsize)
            
            return ax

        elif style == 17:
            """ Cluster-annotated heatmap"""
            # First create a standard heatmap
            ax = sns.heatmap(
                data4heatmap,
                ax=ax,
                annot=annot,
                cmap=cmap,
                fmt=fmt,
                square=True if set_aspect else False,
                cbar_kws={'shrink': 0.8},
                linewidths=0.5,
                linecolor='gray',
                **kwargs
            ) 
            # Check if we're doing correlation (symmetric matrix)
            if len(data4heatmap.index) == len(data4heatmap.columns) and all(data4heatmap.index == data4heatmap.columns):
                # For correlation matrix, add cluster annotations on both sides
                n_items = n_cols
                
                # Simulate cluster assignments (in real use, these would come from clustering)
                n_clusters = min(5, n_items)
                cluster_assignments = np.array_split(range(n_items), n_clusters)
                
                # Add colored bars for clusters
                y_pos = -0.05
                for cluster_idx, items in enumerate(cluster_assignments):
                    if len(items) > 0:
                        start = min(items)
                        end = max(items)
                        width = end - start + 1
                        
                        # Add colored rectangle above heatmap
                        rect_top = patches.Rectangle(
                            (start - 0.5, -0.1),
                            width, 0.08,
                            facecolor=f'C{cluster_idx % 10}',
                            edgecolor='black',
                            linewidth=0.5,
                            alpha=0.7
                        )
                        ax.add_patch(rect_top)
                        
                        # Add colored rectangle left of heatmap
                        rect_left = patches.Rectangle(
                            (-0.1, start - 0.5),
                            0.08, width,
                            facecolor=f'C{cluster_idx % 10}',
                            edgecolor='black',
                            linewidth=0.5,
                            alpha=0.7
                        )
                        ax.add_patch(rect_left)
            
            # Adjust layout to make room for cluster annotations
            ax.set_position([0.15, 0.15, 0.7, 0.7])
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xangle=xangle,**kws_figsets) 

            return ax

        elif style == 18:
            """ Value-sized circles with color""" 
            # Calculate circle sizes
            if "corr" in kind:
                # For correlation, size represents absolute value
                sizes = np.abs(data4heatmap.values) * size_scale
            else:
                # For other data, normalize sizes
                data_norm = (data4heatmap.values - vmin) / (vmax - vmin)
                sizes = data_norm * size_scale
            
            # Create circles
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    size = sizes[i, j] if i < len(sizes) and j < len(sizes[i]) else size_scale * 0.5
                    
                    # Create circle
                    circle = patches.Circle(
                        (j, i),
                        radius=size / (2 * size_scale),  # Convert size to radius
                        facecolor=color,
                        edgecolor='white',
                        linewidth=1,
                        alpha=0.8
                    )
                    ax.add_patch(circle)
                    
                    # Add value if circle is large enough
                    if annot and size > size_scale * 0.3:
                        ax.text(j, i, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if abs(norm(value)) > 0.7 else 'black',
                            fontsize=fontsize * 0.8,
                            fontweight='bold') 
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets) 

            ax.grid(True, which='both', color='lightgray', linestyle='-', 
                    linewidth=0.5, alpha=0.3)
            
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.8)
            
            # Add size legend for circles
            if "corr" in kind:
                legend_text = f" circle size: | r | "
            else:
                legend_text = f" circle size = value "
            
            ax.text(0.98, 1.05, legend_text,
                    transform=ax.transAxes,
                    fontsize=fontsize * 0.9,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round', 
                                facecolor='wheat', 
                                alpha=0.5)
                    )
            
            return ax

        elif style == 19:
            """  Hierarchical clustering dendrogram heatmap""" 
            if not cluster:
                # print("Style 19 requires clustering. Setting cluster=True.")
                cluster = True
            
            # Use clustermap but with publication-quality settings
            if "corr" in kind:
                # For correlation matrices
                g = sns.clustermap(
                    data4heatmap,
                    method='average',
                    metric='euclidean',
                    cmap=cmap,
                    figsize=figsize,
                    row_cluster=row_cluster,
                    col_cluster=col_cluster,
                    dendrogram_ratio=(0.15, 0.15),
                    cbar_pos=(0.02, 0.8, 0.03, 0.15),
                    tree_kws=dict(linewidths=1.5),
                    annot=annot,
                    fmt=fmt,
                    annot_kws={"size": fontsize * 0.8},
                    xticklabels=xticklabels,
                    yticklabels=yticklabels,
                    **kwargs
                )
            else:
                # For general data
                g = sns.clustermap(
                    data4heatmap,
                    method='ward',
                    metric='euclidean',
                    cmap=cmap,
                    figsize=figsize,
                    row_cluster=row_cluster,
                    col_cluster=col_cluster,
                    dendrogram_ratio=(0.15, 0.15),
                    cbar_pos=(0.02, 0.8, 0.03, 0.15),
                    tree_kws=dict(linewidths=1.5),
                    annot=annot,
                    fmt=fmt,
                    annot_kws={"size": fontsize * 0.8},
                    xticklabels=xticklabels,
                    yticklabels=yticklabels,
                    **kwargs
                )
            
            # Customize for publication
            g.ax_heatmap.set_xticklabels(g.ax_heatmap.get_xticklabels(), 
                                        rotation=45, ha='right', fontsize=fontsize)
            g.ax_heatmap.set_yticklabels(g.ax_heatmap.get_yticklabels(), 
                                        fontsize=fontsize)
            
            # Add title if needed
            if "corr" in kind:
                g.fig.suptitle(f"Correlation Heatmap ({method.title()} correlation)", 
                            fontsize=fontsize * 1.2, y=0.98)
            else:
                g.fig.suptitle("Clustered Heatmap", fontsize=fontsize * 1.2, y=0.98)
            
            # Tight layout
            g.fig.tight_layout()
            
            # Return the heatmap axis for further customization
            return g.ax_heatmap

        elif style == 20:
            """Matrix with row/column summaries""" 
            n_rows = n_rows
            n_cols = n_cols
            
            # Calculate row and column summaries
            row_means = data4heatmap.mean(axis=1)
            col_means = data4heatmap.mean(axis=0)
            
            # Create main heatmap
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Offset for summary bars
                    offset_i = i + 0.5  # Half-cell offset for summary bars
                    offset_j = j + 0.5
                    
                    # Main cell
                    rect = patches.Rectangle(
                        (j, i), 1, 1,
                        facecolor=color,
                        edgecolor='white',
                        linewidth=0.5,
                        alpha=0.9
                    )
                    ax.add_patch(rect)
                    
                    # Add value
                    if annot and (abs(value) > np.percentile(np.abs(data4heatmap.values.flatten()), 75)):
                        ax.text(j + 0.5, i + 0.5, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if abs(norm(value)) > 0.7 else 'black',
                            fontsize=fontsize)
            
            # Add row summary bars (right side)
            for i in range(n_rows):
                row_mean_norm = norm(row_means.iloc[i])
                row_color = cmap(row_mean_norm)
                
                # Summary bar
                summary_width = 0.5  # Width of summary bar
                rect = patches.Rectangle(
                    (n_cols, i), summary_width, 1,
                    facecolor=row_color,
                    edgecolor='black',
                    linewidth=0.5,
                    alpha=0.8
                )
                ax.add_patch(rect)
                
                # Add mean value
                ax.text(n_cols + summary_width / 2, i + 0.5, f"{row_means.iloc[i]:{fmt}}",
                    ha='center', va='center',
                    color='white' if abs(row_mean_norm) > 0.7 else 'black',
                    fontsize=fontsize * 0.7,
                    rotation=90)
            
            # Add column summary bars (bottom)
            for j in range(n_cols):
                col_mean_norm = norm(col_means.iloc[j])
                col_color = cmap(col_mean_norm)
                
                # Summary bar
                summary_height = 0.5  # Height of summary bar
                rect = patches.Rectangle(
                    (j, n_rows), 1, summary_height,
                    facecolor=col_color,
                    edgecolor='black',
                    linewidth=0.5,
                    alpha=0.8
                )
                ax.add_patch(rect)
                
                # Add mean value
                ax.text(j + 0.5, n_rows + summary_height / 2, f"{col_means.iloc[j]:{fmt}}",
                    ha='center', va='center',
                    color='white' if abs(col_mean_norm) > 0.7 else 'black',
                    fontsize=fontsize * 0.7)
            
            
            # Add labels
            ax.set_xticks(np.arange(0.5, n_cols + 0.5, 1))
            ax.set_yticks(np.arange(0.5, n_rows + 0.5, 1))
            ax.set_xticklabels(data4heatmap.columns, rotation=45, ha='right', fontsize=fontsize)
            ax.set_yticklabels(data4heatmap.index, fontsize=fontsize)
            
            # Set axis limits Extra space for summary
            ax.set_xlim(0, n_cols + 0.5)
            ax.set_ylim(0, n_rows + 0.5)

            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            # Add summary labels
            ax.text(n_cols + 0.25, -0.5, "Row\nMean", ha='center', va='center', fontsize=fontsize * 0.8)
            ax.text(-0.5, n_rows + 0.25, "Col\nMean", ha='center', va='center', fontsize=fontsize * 0.8, rotation=90)
            print(kws_figsets)
            figsets(xangle=xangle,**kws_figsets) 

            # Add grid
            ax.set_xticks(np.arange(0, n_cols + 1.5, 1), minor=True)
            ax.set_yticks(np.arange(0, n_rows + 1.5, 1), minor=True)
            ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
            
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, pad=0.05, shrink=0.9)
            cbar.ax.tick_params(labelsize=fontsize)
            return ax

        elif style == 21:
            """ Gradient cells with value bars""" 
            # Create gradient-filled cells with value bars
            cell_width = 0.8
            cell_height = 0.8
            
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Background cell with gradient (simulated)
                    rect_bg = patches.Rectangle(
                        (j - cell_width/2, i - cell_height/2),
                        cell_width, cell_height,
                        facecolor=color,
                        edgecolor='white',
                        linewidth=1,
                        alpha=0.7
                    )
                    ax.add_patch(rect_bg)
                    
                    # Value bar (horizontal)
                    bar_height = 0.1
                    bar_width = cell_width * (value - vmin) / (vmax - vmin)
                    bar_color = 'darkred' if value > (vmax + vmin) / 2 else 'darkblue'
                    
                    rect_bar = patches.Rectangle(
                        (j - cell_width/2, i - cell_height/2),
                        bar_width, bar_height,
                        facecolor=bar_color,
                        edgecolor='none',
                        alpha=0.9
                    )
                    ax.add_patch(rect_bar)
                    
                    # Add value text
                    if annot:
                        ax.text(j, i, f"{value:{fmt}}",
                            ha='center', va='center',
                            color='white' if abs(norm(value) - 0.5) > 0.4 else 'black',
                            fontsize=fontsize,
                            fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.1",
                                        facecolor=color,
                                        alpha=0.7,
                                        edgecolor='none'))
            
            
            # Add labels
            ax.set_xticks(range(n_cols))
            ax.set_yticks(range(n_rows))
            ax.set_xticklabels(data4heatmap.columns, rotation=45, ha='right', fontsize=fontsize)
            ax.set_yticklabels(data4heatmap.index, fontsize=fontsize)
            
            # Set axis properties
            ax.set_xlim(-0.6, n_cols - 0.4)
            ax.set_ylim(-0.6, n_rows - 0.4)

            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            
            figsets(xangle=xangle,**kws_figsets)
            # Add colorbar with custom ticks
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.8)
            cbar.set_label('Value', fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
            
            # Add legend for value bars
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color='darkred', lw=4, label='Above average'),
                Line2D([0], [0], color='darkblue', lw=4, label='Below average')
            ]
            # ax.legend(handles=legend_elements, loc='upper right', fontsize=fontsize * 0.8)
            
            return ax

        elif style == 22:
            """Scientific style 8: Publication-ready correlation matrix with half-mask"""
            """Clean, publication-ready style for correlation matrices"""
            if "corr" not in kind:
                # For non-correlation, use a clean heatmap
                ax = sns.heatmap(
                    data4heatmap,
                    ax=ax,
                    annot=annot,
                    cmap=cmap,
                    fmt=fmt,
                    square=True if set_aspect else False,
                    cbar_kws={'shrink': 0.8, 'label': 'Value'},
                    linewidths=0.5,
                    linecolor='white',
                    **kwargs
                )
                return ax 
            # Create mask for upper/lower triangle
            mask_array = np.zeros_like(data4heatmap, dtype=bool)
            if tri.lower() == 'u' or tri.lower() == 'upper':
                mask_array = np.triu(np.ones_like(data4heatmap, dtype=bool), k=k)
            else:
                mask_array = np.tril(np.ones_like(data4heatmap, dtype=bool), k=k)
            
            # Plot with mask
            for i in range(n_rows):
                for j in range(n_cols):
                    if not mask_array[i, j]:
                        value = data4heatmap.iloc[i, j]
                        color = cmap(norm(value))
                        
                        # Cell
                        rect = patches.Rectangle(
                            (j - 0.5, i - 0.5), 1, 1,
                            facecolor=color,
                            edgecolor='white',
                            linewidth=0.5,
                            alpha=0.9
                        )
                        ax.add_patch(rect)
                        
                        # Add value with significance if available
                        if annot:
                            text = f"{value:{fmt}}\n"+pval2str(p_.iloc[i, j]) if not is_nan(pval2str(p_.iloc[i, j])) else f"{value:{fmt}}"
                            ax.text(j, i, text,
                                ha='center', va='center',
                                color='white' if abs(value) > 0.7 else 'black',
                                fontsize=fontsize)
                    else:
                        # Masked cells (diagonal or other half)
                        if i == j:
                            # Diagonal: variable names
                            ax.text(j, i, data4heatmap.columns[i],
                                ha='right' if 'u' not in tri.lower() else 'left', va='center',
                                fontsize=fontsize * 1.1,
                                fontweight='bold',
                                rotation=0,
                                bbox=dict(boxstyle="round,pad=0.2",
                                            facecolor='lightgray',
                                            alpha=0.5))
            
            
            # Add labels only on one side for cleaner look
            ax.set_xticks(range(n_cols))
            ax.set_yticks([])  # Hide y ticks for cleaner look
            
            # Rotate x labels
            ax.set_xticklabels(data4heatmap.columns, rotation=45, ha='right', fontsize=fontsize)
            
            # Add subtle grid
            ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, n_cols, 1), minor=True)
            ax.grid(which='minor', color='white', linestyle='-', linewidth=1)
            
            # Set axis properties
            ax.set_xlim(-0.5, n_cols - 0.5)
            ax.set_ylim(-0.5, n_rows - 0.5)
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            
            ax.invert_yaxis()
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xangle=xangle,box='b',**kws_figsets)

            # Add colorbar with scientific notation
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.8, pad=0.02)
            cbar.set_label('Correlation (r)', fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
            
            # Add significance legend
            if annot and 'p_' in locals():
                p_loc = (0.02, 0.02) if 'u' not in tri.lower() else (0.6,0.95)
                ax.text(*p_loc, "* p < 0.05, ** p < 0.01, *** p < 0.001",
                        transform=ax.transAxes,
                        fontsize=fontsize * 0.7,
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            return ax
        elif style == 23:
            """Scientific style 9: Gradient background with cell highlights"""
            """Common in economics and social sciences""" 
            # Create gradient background
            im = ax.imshow(data4heatmap.values, cmap=cmap, aspect='auto',
                        vmin=vmin, vmax=vmax, alpha=0.3)
            
            # Add highlighted cells with borders
            cell_width = 0.9
            cell_height = 0.9
            
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Determine if cell should be highlighted (e.g., extreme values)
                    highlight = False
                    if "corr" in kind:
                        highlight = abs(value) > 0.5
                    else:
                        # Highlight top and bottom 25%
                        q75 = np.percentile(data4heatmap.values.flatten(), 75)
                        q25 = np.percentile(data4heatmap.values.flatten(), 25)
                        highlight = value > q75 or value < q25
                    
                    if highlight:
                        # Create highlighted cell
                        rect = patches.Rectangle(
                            (j - cell_width/2, i - cell_height/2),
                            cell_width, cell_height,
                            facecolor=color,
                            edgecolor='black',
                            linewidth=2,
                            alpha=0.9
                        )
                    else:
                        # Create subtle cell
                        rect = patches.Rectangle(
                            (j - cell_width/2, i - cell_height/2),
                            cell_width, cell_height,
                            facecolor=color,
                            edgecolor='white',
                            linewidth=0.5,
                            alpha=0.7
                        )
                    ax.add_patch(rect)
                    
                    # Add value for highlighted cells or all if annot=True
                    if annot and (highlight or annot):
                        text_color = 'white' if abs(norm(value) - 0.5) > 0.4 else 'black'
                        if highlight:
                            # Bold for highlighted cells
                            ax.text(j, i, f"{value:{fmt}}",
                                ha='center', va='center',
                                color=text_color,
                                fontsize=fontsize,
                                fontweight='bold')
                        else:
                            # Normal for other cells
                            ax.text(j, i, f"{value:{fmt}}",
                                ha='center', va='center',
                                color=text_color,
                                fontsize=fontsize * 0.9) 
            
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets) 
            ax.grid(True, which='both', color='white', linestyle='-', 
                    linewidth=0.5, alpha=0.3)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Value' if "corr" not in kind else 'Correlation', fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
            
            # # Add highlight legend
            # if any(np.abs(data4heatmap.values.flatten()) > 0.5) if "corr" in kind else True:
            #     from matplotlib.patches import Patch
            #     legend_elements = [
            #         Patch(facecolor='gray', edgecolor='black', linewidth=2,
            #             label='Significant values' if "corr" in kind else 'Extreme values (top/bottom 25%)'),
            #         Patch(facecolor='gray', edgecolor='white', linewidth=0.5,
            #             label='Other values')
            #     ]
            #     ax.legend(handles=legend_elements, loc='upper right', fontsize=fontsize * 0.8)
            
            return ax

        elif style == 24:  
            if "corr" not in kind:
                return heatmap(data, ax=ax, kind=kind, method=method, style=22,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs) 
            n_vars = n_cols
            
            # Create triangular layout (upper triangle only)
            for i in range(n_vars):
                for j in range(i + 1, n_vars):  # Only upper triangle
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Create triangle coordinates
                    # Position triangles in a compact triangular layout
                    offset = 0.2  # Small gap between triangles
                    x_center = j + (i * 0.5)  # Stagger rows
                    y_center = i
                    
                    # Create triangle (pointing up or down based on value)
                    if value > 0:
                        # Upward triangle for positive correlation
                        triangle = patches.RegularPolygon(
                            (x_center, y_center),
                            numVertices=3,
                            radius=0.4,
                            orientation=np.pi,  # Point up
                            facecolor=color,
                            edgecolor='white',
                            linewidth=0.5,
                            alpha=0.9
                        )
                    else:
                        # Downward triangle for negative correlation
                        triangle = patches.RegularPolygon(
                            (x_center, y_center),
                            numVertices=3,
                            radius=0.4,
                            orientation=0,  # Point down
                            facecolor=color,
                            edgecolor='white',
                            linewidth=0.5,
                            alpha=0.9
                        )
                    ax.add_patch(triangle)
                    
                    # Add correlation value inside triangle
                    if annot:
                        text_color = 'white' if abs(value) > 0.7 else 'black'
                        ax.text(x_center, y_center, f"{value:{fmt}}",
                            ha='center', va='center',
                            color=text_color,
                            fontsize=fontsize * 0.8,
                            fontweight='bold')
            
            # Add variable labels on the sides
            for i in range(n_vars):
                # Left side labels
                ax.text(-0.5, i, data4heatmap.columns[i],
                    ha='right', va='center',
                    fontsize=fontsize,
                    fontweight='bold')
                
                # Bottom side labels (rotated)
                ax.text(i + (i * 0.5), -0.5, data4heatmap.columns[i],
                    ha='center', va='top',
                    fontsize=fontsize,
                    fontweight='bold',
                    rotation=45)
            
            # Hide axes
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Set axis limits
            ax.set_xlim(-1, n_vars + (n_vars * 0.5))
            ax.set_ylim(-1, n_vars)
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.7, pad=0.05)
            # cbar.set_label('Correlation Coefficient', fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
            
            # Add triangle legend
            from matplotlib.patches import Patch
            legend_elements = [
                
                patches.RegularPolygon((0, 0),
                                    numVertices=3,
                                    radius=0.3,
                                    orientation = np.pi,
                                    facecolor='gray', label='Positive correlation'),
                patches.RegularPolygon((0, 0),
                                    numVertices=3,
                                    radius=0.3,
                                    orientation = 0,
                                    facecolor='gray', label='Negative correlation')
            ]
            ax.legend(handles=legend_elements, loc='upper right',
                    fontsize=fontsize * 0.8, framealpha=0.9)
            
            return ax

        elif style == 25: 
            n_levels = 10
            # Create contour levels
            levels = np.linspace(vmin, vmax, n_levels + 1)
            
            # Create filled contour plot
            X, Y = np.meshgrid(np.arange(n_cols),
                            np.arange(n_rows))
            
            # Create contourf plot
            contour = ax.contourf(X, Y, data4heatmap.values,
                                levels=levels, cmap=cmap, alpha=0.8)
            
            # Add contour lines
            ax.contour(X, Y, data4heatmap.values,
                    levels=levels, colors='black', linewidths=0.5, alpha=0.5)
            
            # Add cell values at contour centers
            if annot:
                for i in range(n_rows):
                    for j in range(n_cols):
                        value = data4heatmap.iloc[i, j]
                        
                        # Only label cells that are near contour levels or are local extrema
                        if any(abs(value - level) < (vmax - vmin) * 0.05 for level in levels):
                            text_color = 'white' if norm(value) > 0.7 else 'black'
                            ax.text(j, i, f"{value:{fmt}}",
                                ha='center', va='center',
                                color=text_color,
                                fontsize=fontsize * 0.9,
                                fontweight='bold',
                                bbox=dict(boxstyle="round,pad=0.1",
                                            facecolor=cmap(norm(value)),
                                            alpha=0.7,
                                            edgecolor='none'))
            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets) 

            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            # Add grid
            ax.grid(True, which='both', color='white', linestyle='-',
                    linewidth=0.5, alpha=0.3)
            
            # Add colorbar with contour levels
            cbar = plt.colorbar(contour, ax=ax, shrink=0.8)
            cbar.set_label('Value', fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
            
            return ax

        elif style == 26: 
            if "corr" not in kind:
                return heatmap(data, ax=ax, kind=kind, method=method, style=18,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs) 
            n_vars = n_cols
            
            # Arrange variables in a circle
            radius = n_vars * 0.4
            angles = np.linspace(0, 2 * np.pi, n_vars, endpoint=False)
            positions = np.array([(radius * np.cos(angle), radius * np.sin(angle))
                                for angle in angles])
            
            # Plot correlation lines
            line_alpha = 0.7
            line_width_scale = 3
            
            for i in range(n_vars):
                for j in range(i + 1, n_vars):  # Only upper triangle
                    value = data4heatmap.iloc[i, j]
                    
                    if abs(value) > 0.2:  # Only show meaningful correlations
                        color = cmap(norm(value))
                        line_width = abs(value) * line_width_scale
                        
                        # Draw line between variables
                        ax.plot([positions[i, 0], positions[j, 0]],
                            [positions[i, 1], positions[j, 1]],
                            color=color,
                            linewidth=line_width,
                            alpha=line_alpha,
                            solid_capstyle='round')
                        
                        # Add correlation value near the midpoint
                        if annot and abs(value) > 0.5:
                            mid_x = (positions[i, 0] + positions[j, 0]) / 2
                            mid_y = (positions[i, 1] + positions[j, 1]) / 2
                            
                            # Offset text slightly
                            offset_x = (positions[j, 1] - positions[i, 1]) * 0.1
                            offset_y = (positions[i, 0] - positions[j, 0]) * 0.1
                            
                            ax.text(mid_x + offset_x, mid_y + offset_y, f"{value:{fmt}}",
                                ha='center', va='center',
                                color=color,
                                fontsize=fontsize * 0.8,
                                fontweight='bold',
                                bbox=dict(boxstyle="round,pad=0.2",
                                            facecolor='white',
                                            alpha=0.8,
                                            edgecolor=color))
            
            # Plot variable nodes
            node_size = 300
            for i in range(n_vars):
                # Calculate average correlation for node color
                avg_corr = data4heatmap.iloc[i, :].mean()
                node_color = cmap(norm(avg_corr))
                
                # Draw node
                ax.scatter(positions[i, 0], positions[i, 1],
                        s=node_size,
                        color=node_color,
                        edgecolor='white',
                        linewidth=2,
                        alpha=0.9,
                        zorder=10)  # Ensure nodes are on top
                
                # Add variable label
                label_radius = radius * 1.15
                label_x = label_radius * np.cos(angles[i])
                label_y = label_radius * np.sin(angles[i])
                
                ax.text(label_x, label_y, data4heatmap.columns[i],
                    ha='center', va='center',
                    fontsize=fontsize,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3",
                                facecolor='white',
                                alpha=0.9,
                                edgecolor='gray'))
            
            # Set equal aspect and limits
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            margin = radius * 0.3
            ax.set_xlim(-radius - margin, radius + margin)
            ax.set_ylim(-radius - margin, radius + margin)
            
            # Hide axes
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.7, pad=0.05)
            # cbar.set_label('Correlation Coefficient', fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
            
            # Add legend for line widths
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color='gray', lw=0.5, label='|r| ≈ 0.2'),
                Line2D([0], [0], color='gray', lw=1.5, label='|r| ≈ 0.5'),
                Line2D([0], [0], color='gray', lw=3, label='|r| ≈ 1.0')
            ]
            ax.legend(handles=legend_elements, loc='upper left',
                    fontsize=fontsize * 0.8, title='Line width indicates |r|',
                    title_fontsize=fontsize * 0.8)
            return ax

        elif style == 27: 
            if "corr" not in kind:
                # print("Style 27 is designed for correlation matrices with scatterplots.")
                return heatmap(data, ax=ax, kind=kind, method=method, style=22,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs)

            if 'df_numeric' not in locals():
                # Fall back to standard correlation plot
                return heatmap(data, ax=ax, kind=kind, method=method, style=22,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs) 

            n_vars = n_cols

            fig = ax.figure
            fig.clf()
            # Create grid of subplots
            gs = fig.add_gridspec(n_vars, n_vars, hspace=0.1, wspace=0.1)
            for i in range(n_vars):
                for j in range(n_vars):
                    ax_sub = fig.add_subplot(gs[i, j])
                    if i == j:
                        # Diagonal: variable name and distribution
                        ax_sub.text(0.5, 0.5, data4heatmap.columns[i],
                                ha='center', va='center',
                                fontsize=fontsize * 1.2,
                                fontweight='bold',
                                transform=ax_sub.transAxes)
                        
                        # Add histogram or density plot if data is available
                        if i < len(df_numeric.columns):
                            var_data = df_numeric.iloc[:, i].dropna()
                            if len(var_data) > 0:
                                # Create small histogram
                                ax_sub.hist(var_data, bins=20, alpha=0.5,
                                        density=True, color='gray')
                        
                        ax_sub.set_xticks([])
                        ax_sub.set_yticks([])
                        
                    elif i > j:
                        # Lower triangle: scatterplot
                        x_data = df_numeric.iloc[:, j]
                        y_data = df_numeric.iloc[:, i]
                        
                        # Remove NaNs
                        mask = ~(x_data.isna() | y_data.isna())
                        x_clean = x_data[mask]
                        y_clean = y_data[mask]
                        
                        if len(x_clean) > 0 and len(y_clean) > 0:
                            # Calculate correlation for color
                            corr_value = data4heatmap.iloc[i, j]
                            color = cmap(norm(corr_value)) 
                            
                            # Scatter plot
                            ax_sub.scatter(x_clean, y_clean,
                                        alpha=0.6,
                                        s=20,
                                        color=color,
                                        edgecolor='none',
                                        linewidth=0.5)
                            
                            # Add regression line
                            if len(x_clean) > 1:
                                z = np.polyfit(x_clean, y_clean, 1)
                                p = np.poly1d(z)
                                x_range = np.linspace(x_clean.min(), x_clean.max(), 100)
                                ax_sub.plot(x_range, p(x_range),
                                        color='red',
                                        linewidth=1,
                                        alpha=0.8)
                        
                        # Hide ticks for cleaner look
                        ax_sub.set_xticks([])
                        ax_sub.set_yticks([])
                        
                        # Only show labels on edge subplots
                        if i == n_vars - 1:
                            ax_sub.set_xlabel(data4heatmap.columns[j], fontsize=fontsize * 0.8)
                        if j == 0:
                            ax_sub.set_ylabel(data4heatmap.columns[i], fontsize=fontsize * 0.8)
                        
                    else:
                        # Upper triangle: correlation value with background color
                        corr_value = data4heatmap.iloc[i, j]
                        color = cmap(norm(corr_value)) 
                        
                        # Fill cell with color
                        ax_sub.add_patch(patches.Rectangle((0, 0), 1, 1,
                                                        facecolor=color,
                                                        transform=ax_sub.transAxes,
                                                        alpha=0.8))
                        
                        # Add correlation value
                        ax_sub.text(0.5, 0.5, f"{corr_value:{fmt}}",
                                ha='center', va='center',
                                fontsize=fontsize,
                                fontweight='bold',
                                color='white' if abs(corr_value) > 0.7 else 'black',
                                transform=ax_sub.transAxes)
                        
                        # Hide ticks
                        ax_sub.set_xticks([])
                        ax_sub.set_yticks([])
            
            # Adjust layout
            fig.tight_layout()
            plt.close(fig)
            # Return the figure instead of axis for this style
            return fig

        elif style == 271: 
            if "corr" not in kind:
                # print("Style 27 is designed for correlation matrices with scatterplots.")
                return heatmap(data, ax=ax, kind=kind, method=method, style=22,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs)
            
            # This style requires access to original data for scatterplots
            # We'll need to pass the original numeric data
            if 'df_numeric' not in locals():
                # Fall back to standard correlation plot
                return heatmap(data, ax=ax, kind=kind, method=method, style=22,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs) 
            norm = plt.Normalize(vmin=vmin, vmax=vmax)
            n_vars = n_cols
            
            # Create subplot grid within the given axis
            fig = ax.figure
            fig.clf()  # Clear the figure
            
            # Create grid of subplots
            gs = fig.add_gridspec(n_vars, n_vars, hspace=0.1, wspace=0.1)
            
            # Plot scatterplots in lower triangle, correlations in upper triangle
            for i in range(n_vars):
                for j in range(n_vars):
                    ax_sub = fig.add_subplot(gs[i, j])
                    
                    if i == j:
                        # Diagonal: variable name and distribution
                        ax_sub.text(0.5, 0.5, data4heatmap.columns[i],
                                ha='center', va='center',
                                fontsize=fontsize * 1.2,
                                fontweight='bold',
                                transform=ax_sub.transAxes)
                        
                        # Add histogram or density plot if data is available
                        if i < len(df_numeric.columns):
                            var_data = df_numeric.iloc[:, i].dropna()
                            if len(var_data) > 0:
                                # Create small histogram
                                ax_sub.hist(var_data, bins=20, alpha=0.5,
                                        density=True, color='gray')
                        
                        ax_sub.set_xticks([])
                        ax_sub.set_yticks([])
                        
                    elif i > j:
                        # Lower triangle: scatterplot
                        x_data = df_numeric.iloc[:, j]
                        y_data = df_numeric.iloc[:, i]
                        
                        # Remove NaNs
                        mask = ~(x_data.isna() | y_data.isna())
                        x_clean = x_data[mask]
                        y_clean = y_data[mask]
                        
                        if len(x_clean) > 0 and len(y_clean) > 0:
                            # Calculate correlation for color
                            corr_value = data4heatmap.iloc[i, j]
                            color = cmap(norm(corr_value)) 
                            
                            # Scatter plot
                            ax_sub.scatter(x_clean, y_clean,
                                        alpha=0.6,
                                        s=5,
                                        color=color,
                                        edgecolor='none',
                                        linewidth=0.5)
                            
                            # Add regression line
                            if len(x_clean) > 1:
                                z = np.polyfit(x_clean, y_clean, 1)
                                p = np.poly1d(z)
                                x_range = np.linspace(x_clean.min(), x_clean.max(), 100)
                                ax_sub.plot(x_range, p(x_range),
                                        color='red',
                                        linewidth=1,
                                        alpha=0.8)
                        
                        # Hide ticks for cleaner look
                        ax_sub.set_xticks([])
                        ax_sub.set_yticks([])
                        
                        # Only show labels on edge subplots
                        if i == n_vars - 1:
                            ax_sub.set_xlabel(data4heatmap.columns[j], fontsize=fontsize * 0.8)
                        if j == 0:
                            ax_sub.set_ylabel(data4heatmap.columns[i], fontsize=fontsize * 0.8)
                        
                    else:
                        # Upper triangle: correlation value with background color
                        corr_value = data4heatmap.iloc[i, j]
                        color = cmap(norm(corr_value)) 
                        
                        # Fill cell with color
                        ax_sub.add_patch(patches.Rectangle((0, 0), 1, 1,
                                                        facecolor=color,
                                                        transform=ax_sub.transAxes,
                                                        alpha=0.8))
                        
                        # Add correlation value
                        ax_sub.text(0.5, 0.5, f"{corr_value:{fmt}}",
                                ha='center', va='center',
                                fontsize=fontsize,
                                fontweight='bold',
                                color='white' if abs(corr_value) > 0.7 else 'black',
                                transform=ax_sub.transAxes)
                        
                        # Hide ticks
                        ax_sub.set_xticks([])
                        ax_sub.set_yticks([])
            
            # Adjust layout
            fig.tight_layout()
            
            # Return the figure instead of axis for this style
            return fig
        elif style == 28:  
            # For correlation matrices, it shows bars with bootstrap CIs 
            n_rows = n_rows
            n_cols = n_cols
            
            # Bar parameters
            bar_width = 0.6
            bar_height = 0.6
            
            for i in range(n_rows):
                for j in range(n_cols):
                    value = data4heatmap.iloc[i, j]
                    color = cmap(norm(value))
                    
                    # Create gradient bar (simulated with multiple rectangles)
                    n_gradient_segments = 5
                    segment_height = bar_height / n_gradient_segments
                    
                    for seg in range(n_gradient_segments):
                        # Vary alpha for gradient effect
                        seg_alpha = 0.3 + 0.7 * (seg / n_gradient_segments)
                        
                        # Vary width based on value (simulating bar length)
                        seg_width = bar_width * (value - vmin) / (vmax - vmin)
                        
                        rect = patches.Rectangle(
                            (j - bar_width/2, i - bar_height/2 + seg * segment_height),
                            seg_width, segment_height,
                            facecolor=color,
                            edgecolor='none',
                            alpha=seg_alpha
                        )
                        ax.add_patch(rect)
                    
                    # Add confidence interval error bars if available
                    # This would typically come from additional data
                    ci_width = bar_width * 0.1  # Default CI width
                    
                    # Draw error bar
                    error_x = j - bar_width/2 + bar_width * (value - vmin) / (vmax - vmin)
                    ax.plot([error_x - ci_width/2, error_x + ci_width/2],
                        [i, i],
                        color='black',
                        linewidth=1,
                        alpha=0.7,
                        solid_capstyle='round')
                    
                    # Add value text
                    if annot:
                        # Position text at the end of the bar
                        text_x = j - bar_width/2 + bar_width * (value - vmin) / (vmax - vmin) + 0.1
                        text_ha = 'left' if value > (vmax + vmin) / 2 else 'right'
                        text_x = j - bar_width/2 + bar_width * (value - vmin) / (vmax - vmin)
                        if value > (vmax + vmin) / 2:
                            text_x += 0.1
                            text_ha = 'left'
                        else:
                            text_x -= 0.1
                            text_ha = 'right'
                        
                        ax.text(text_x, i, f"{value:{fmt}}",
                            ha=text_ha, va='center',
                            color='black',
                            fontsize=fontsize * 0.9,
                            fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.1",
                                        facecolor='white',
                                        alpha=0.8,
                                        edgecolor='none'))
            
            # Add labels
            ax.set_xticks(range(n_cols))
            ax.set_yticks(range(n_rows))
            ax.set_xticklabels(data4heatmap.columns, rotation=45, ha='right', fontsize=fontsize)
            ax.set_yticklabels(data4heatmap.index, fontsize=fontsize)
            
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            # Set axis properties
            ax.set_xlim(-0.6, n_cols - 0.4)
            ax.set_ylim(-0.6, n_rows - 0.4)
            figsets(**kws_figsets) 
            # Add reference line at zero or mean
            if "corr" in kind:
                # For correlation, add zero line
                ax.axvline(x=-0.5, color='gray', linestyle='--', alpha=0.5)
                ax.text(-0.45, n_rows + 0.2, "r = 0",
                    ha='left', va='bottom', fontsize=fontsize * 0.8, color='gray')
            
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.8)
            cbar.set_label('Value', fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
            
            # Add legend for error bars
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color='black', lw=1, marker='|', markersize=10,
                    label='95% Confidence Interval')
            ]
            ax.legend(handles=legend_elements, loc='upper right',
                    fontsize=fontsize * 0.8)
            
            return ax

        elif style == 29:
            """Scientific style 15: 3D surface projection"""
            """Creates a pseudo-3D effect for the heatmap"""
            from matplotlib.colors import LightSource 
            # Create meshgrid for 3D surface
            X, Y = np.meshgrid(np.arange(n_cols),
                            np.arange(n_rows))
            Z = data4heatmap.values
            
            # Create light source for shading
            ls = LightSource(azdeg=315, altdeg=45)
            
            # Shade the data, creating an rgb array for each cell
            rgb = ls.shade(Z, cmap=cmap, vert_exag=0.1, blend_mode='soft')
            
            # Display the shaded image
            ax.imshow(rgb, extent=[-0.5, n_cols - 0.5,
                                -0.5, n_rows - 0.5],
                    aspect='auto', alpha=0.9)
            
            # Add contour lines
            if n_cols > 1 and n_rows > 1:
                contour = ax.contour(X, Y, Z,
                                levels=10,
                                colors='black',
                                linewidths=0.5,
                                alpha=0.5)
                ax.clabel(contour, inline=True, fontsize=fontsize * 0.7)
            
            # Add cell values for significant points
            if annot:
                for i in range(n_rows):
                    for j in range(n_cols):
                        value = data4heatmap.iloc[i, j]
                        
                        # Only label local maxima/minima or extreme values
                        is_extreme = False
                        if i > 0 and i < n_rows - 1 and j > 0 and j < n_cols - 1:
                            # Check if local extremum
                            neighbors = [
                                data4heatmap.iloc[i-1, j-1], data4heatmap.iloc[i-1, j], data4heatmap.iloc[i-1, j+1],
                                data4heatmap.iloc[i, j-1], data4heatmap.iloc[i, j+1],
                                data4heatmap.iloc[i+1, j-1], data4heatmap.iloc[i+1, j], data4heatmap.iloc[i+1, j+1]
                            ]
                            if value > max(neighbors) or value < min(neighbors):
                                is_extreme = True
                        
                        if is_extreme or abs(value) > np.percentile(np.abs(Z.flatten()), 90):
                            # Add value with shadow effect for 3D look
                            shadow_color = 'black' if norm(value) > 0.5 else 'white'
                            text_color = 'white' if norm(value) > 0.7 else 'black'
                            
                            # Shadow
                            ax.text(j + 0.03, i - 0.03, f"{value:{fmt}}",
                                ha='center', va='center',
                                color=shadow_color,
                                fontsize=fontsize,
                                fontweight='bold',
                                alpha=0.3)
                            
                            # Main text
                            ax.text(j, i, f"{value:{fmt}}",
                                ha='center', va='center',
                                color=text_color,
                                fontsize=fontsize,
                                fontweight='bold',
                                bbox=dict(boxstyle="round,pad=0.2",
                                            facecolor=cmap(norm(value)),
                                            alpha=0.7,
                                            edgecolor='none'))
            
            # Add labels
            # ax.set_xticks(range(n_cols))
            # ax.set_yticks(range(n_rows))
            # ax.set_xticklabels(data4heatmap.columns, rotation=45, ha='right', fontsize=fontsize)
            # ax.set_yticklabels(data4heatmap.index, fontsize=fontsize)
            
            # Add grid with 3D effect
            for i in range(n_rows + 1):
                ax.axhline(i - 0.5, color='white', alpha=0.2, linewidth=0.5)
            for j in range(n_cols + 1):
                ax.axvline(j - 0.5, color='white', alpha=0.2, linewidth=0.5)
            
            # # Set axis properties
            # ax.set_xlim(-0.5, n_cols - 0.5)
            # ax.set_ylim(-0.5, n_rows - 0.5)
            
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            figsets(xlim=xlim,ylim=ylim,xticks=xticks,yticks=yticks,xticklabels=xticklabels,yticklabels=yticklabels,xangle=xangle,**kws_figsets)             
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.8)
            cbar.set_label('Value', fontsize=fontsize)
            cbar.ax.tick_params(labelsize=fontsize)
            
            # Add elevation indicator
            ax.text(0.02, 0.98, "Height ∝ Value",
                transform=ax.transAxes,
                fontsize=fontsize * 0.8,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            return ax
        elif style == 30:
            """Scientific style 16: Chord diagram for correlations"""
            """Circular layout showing correlations as connecting chords"""
            if "corr" not in kind:
                return heatmap(data, ax=ax, kind=kind, method=method, style=26,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs) 
            
            # Check if it's a square matrix
            if n_rows != n_cols or not all(data4heatmap.index == data4heatmap.columns):
                return heatmap(data, ax=ax, kind=kind, method=method, style=1,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs)
            
            n_vars = n_cols
            
            # Circular layout
            radius = 1.0
            
            # Calculate node positions on circle
            angles = np.linspace(0, 2 * np.pi, n_vars, endpoint=False)
            node_positions = []
            for angle in angles:
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                node_positions.append((x, y))
            
            # Define visual encoding parameters
            # Line width encoding: absolute correlation strength
            min_linewidth = 0.5
            max_linewidth = 30.0
            linewidth_range = max_linewidth - min_linewidth
            
            # Line opacity encoding: also based on correlation strength
            min_alpha = 0.3
            max_alpha = 0.8
            alpha_range = max_alpha - min_alpha
            
            # Color encoding: correlation value (red for positive, blue for negative)
            # We'll use the provided colormap
            
            # Sort connections by strength to draw weaker ones first
            connections = []
            for i in range(n_vars):
                for j in range(i + 1, n_vars):
                    corr = data4heatmap.iloc[i, j]
                    if not pd.isna(corr):
                        abs_corr = abs(corr)
                        connections.append((i, j, corr, abs_corr))
            
            # Sort by absolute correlation (draw weakest first)
            connections.sort(key=lambda x: x[3])
            
            # Minimum threshold (optional, can be 0 to show all)
            min_threshold = 0.0  # Set to 0.1 or 0.2 if too many weak connections
            
            # Plot all chords
            for i, j, corr, abs_corr in connections:
                if abs_corr < min_threshold:
                    continue
                    
                # Calculate visual properties based on correlation
                color = cmap(norm(corr))
                
                # Line width: proportional to absolute correlation
                linewidth = min_linewidth + abs_corr * linewidth_range
                
                # Opacity: also proportional to correlation strength
                # Stronger correlations are more opaque
                alpha = min_alpha + abs_corr * alpha_range
                
                # Calculate chord parameters
                angle_i = angles[i]
                angle_j = angles[j]
                
                # Sort angles for proper arc drawing
                if angle_j < angle_i:
                    angle_i, angle_j = angle_j, angle_i
                
                # Draw chord as Bezier curve
                # Control point position depends on correlation strength AND sign
                # Stronger correlations have curves that bulge more toward center
                # Positive correlations bulge in one direction, negative in opposite
                
                # Base control radius: stronger correlations curve more
                control_radius_factor = 0.3 + abs_corr * 0.5  # 0.3 to 0.8
                
                # For positive correlations, bulge in normal direction
                # For negative correlations, bulge in opposite direction
                sign = 1 if corr > 0 else -1
                control_radius = control_radius_factor * radius
                
                control_angle = (angle_i + angle_j) / 2
                
                # Offset control angle slightly based on correlation value
                # This helps separate positive and negative correlations visually
                angle_offset = 0.1 * sign * (1 - abs_corr)  # Weaker correlations offset more
                control_angle += angle_offset
                
                control_x = control_radius * np.cos(control_angle)
                control_y = control_radius * np.sin(control_angle)
                
                # Create Bezier curve
                from matplotlib.path import Path
                import matplotlib.patches as patches
                
                vertices = [
                    node_positions[i],  # Start at node i
                    (control_x, control_y),  # Control point
                    node_positions[j],  # End at node j
                ]
                
                codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]

                path = Path(vertices, codes)
                patch = patches.PathPatch(path,
                                        facecolor='none',
                                        edgecolor=color,
                                        linewidth=linewidth,
                                        alpha=alpha,
                                        capstyle='round',
                                        joinstyle='round',
                                        zorder=int(abs_corr * 10))  # Stronger on top
                
                ax.add_patch(patch)
                
                # Add correlation value at midpoint for strong correlations
                if annot and abs_corr > 0.7:
                    # Calculate position along the quadratic Bezier curve at t=0.5
                    t = 0.5
                    start_x, start_y = node_positions[i]
                    end_x, end_y = node_positions[j]
                    
                    # Quadratic Bezier formula: (1-t)² * P0 + 2 * (1-t) * t * P1 + t² * P2
                    text_x = (1-t)**2 * start_x + 2 * (1-t) * t * control_x + t**2 * end_x
                    text_y = (1-t)**2 * start_y + 2 * (1-t) * t * control_y + t**2 * end_y
                    
                    # Calculate tangent for text offset
                    dx = 2 * (1-t) * (control_x - start_x) + 2 * t * (end_x - control_x)
                    dy = 2 * (1-t) * (control_y - start_y) + 2 * t * (end_y - control_y)
                    
                    # Offset perpendicular to the curve
                    length = np.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        # Normalize and rotate 90 degrees
                        dx_norm = dx / length
                        dy_norm = dy / length
                        offset_x = -dy_norm * 0.15 * (1 if corr > 0 else -1)
                        offset_y = dx_norm * 0.15 * (1 if corr > 0 else -1)
                        text_x += offset_x
                        text_y += offset_y
                    
                    # Text color: white for strong colors, black for weak
                    text_color = 'white' if abs(norm(corr)) > 0.7 else 'black'
                    
                    ax.text(text_x, text_y, f"{corr:{fmt}}",
                        ha='center', va='center',
                        color=text_color,
                        fontsize=fontsize * (0.7 + 0.3 * abs_corr),  # Bigger for stronger correlations
                        fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.2",
                                    facecolor=color,
                                    alpha=0.9,
                                    edgecolor='none',
                                    linewidth=0.5), 
                        zorder=100)  # Ensure text is on top
            
            # Plot nodes with size and color based on connectivity
            for i, (x, y) in enumerate(node_positions):
                # Calculate node properties based on its correlations
                node_correlations = data4heatmap.iloc[i, :].values
                node_correlations = node_correlations[~np.isnan(node_correlations)]
                
                if len(node_correlations) > 0:
                    # Node color: average correlation (could also use max or sum)
                    avg_corr = np.sum(node_correlations)
                    node_color = cmap(norm(avg_corr))
                    
                    # Node size: based on connection strength sum
                    abs_sum = np.sum(np.abs(node_correlations))
                    node_size_factor = 0.05 + 0.1 * (abs_sum / len(node_correlations))
                else:
                    node_color = 'gray'
                    node_size_factor = 0.05
                
                # Draw node
                circle = patches.Circle((x, y), radius=node_size_factor,
                                    facecolor=node_color,
                                    edgecolor='w',
                                    linewidth=1,
                                    alpha=0.9,
                                    zorder=50)  # Nodes above chords
                
                ax.add_patch(circle)
                
                # Add variable label
                label_radius = radius * 1.2
                label_x = label_radius * np.cos(angles[i])
                label_y = label_radius * np.sin(angles[i])
                
                # Smart label positioning
                ha = 'left' if -np.pi/2 <= angles[i] <= np.pi/2 else 'right'
                va = 'center'
                
                # Adjust for top/bottom positions
                if abs(angles[i] - np.pi/2) < np.pi/6:  # Near top
                    va = 'bottom'
                elif abs(angles[i] - 3*np.pi/2) < np.pi/6:  # Near bottom
                    va = 'top'
                
                ax.text(label_x, label_y, data4heatmap.columns[i],
                    ha=ha, va=va,
                    fontsize=fontsize,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2",
                                facecolor="none",
                                alpha=0.8,
                                edgecolor='none',
                                linewidth=1),
                    rotation=kwargs.get("rotation",0))
            
            # Set equal aspect and limits
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            margin = radius * 0.4
            ax.set_xlim(-radius - margin, radius + margin)
            ax.set_ylim(-radius - margin, radius + margin)
            
            # Hide axes
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # # Add colorbar with modified ticks
            # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            # sm.set_array([])
            # cbar = plt.colorbar(sm, ax=ax, shrink=0.7, pad=0.05)
            # cbar.set_label('Correlation Value', fontsize=fontsize)
            # cbar.ax.tick_params(labelsize=fontsize)
            
            # # Add comprehensive legend
            # from matplotlib.lines import Line2D
            # from matplotlib.patches import Patch
            
            # # Create example lines for the legend
            # legend_elements = [
            #     # Line width examples
            #     Line2D([0], [0], color='gray', lw=min_linewidth, 
            #         label=f'Weak (|r| ≈ {min_threshold:.1f})'),
            #     Line2D([0], [0], color='gray', lw=(min_linewidth + max_linewidth)/3, 
            #         label='Moderate (|r| ≈ 0.5)'),
            #     Line2D([0], [0], color='gray', lw=max_linewidth, 
            #         label='Strong (|r| ≈ 1.0)'),
                
            #     # Color examples
            #     Patch(facecolor=cmap(norm(0.8)), edgecolor='black', 
            #         label='Strong positive'),
            #     Patch(facecolor=cmap(norm(0.3)), edgecolor='black', 
            #         label='Moderate positive'),
            #     Patch(facecolor=cmap(norm(-0.3)), edgecolor='black', 
            #         label='Moderate negative'),
            #     Patch(facecolor=cmap(norm(-0.8)), edgecolor='black', 
            #         label='Strong negative'),
                
            #     # Node size example
            #     patches.Circle((0, 0), radius=0.03, facecolor='gray', 
            #                 edgecolor='black', label='Node: size ∝ connectivity'),
                
            #     # Opacity note
            #     Line2D([0], [0], color='black', lw=2, alpha=min_alpha, 
            #         label=f'Opacity ∝ |r| ({min_alpha:.1f}-{max_alpha:.1f})'),
            # ]
            
            # # Position legend
            # ax.legend(handles=legend_elements, 
            #         loc='upper left',
            #         bbox_to_anchor=(1.05, 1),
            #         fontsize=fontsize * 0.7,
            #         title='Visual Encoding',
            #         title_fontsize=fontsize * 0.8,
            #         framealpha=0.9)
            
            # # Add summary statistics
            # total_connections = len(connections)
            # strong_connections = sum(1 for _, _, _, abs_corr in connections if abs_corr > 0.7)
            # positive_connections = sum(1 for _, _, corr, _ in connections if corr > 0)
            
            # stats_text = (f"Connections: {total_connections}\n"
            #             f"Strong (|r|>0.7): {strong_connections}\n"
            #             f"Positive: {positive_connections}\n"
            #             f"Negative: {total_connections - positive_connections}")
            
            # ax.text(1.05, 0.5, stats_text,
            #     transform=ax.transAxes,
            #     fontsize=fontsize * 0.7,
            #     verticalalignment='center',
            #     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # Adjust layout to make room for legend
            plt.tight_layout(rect=[0, 0, 0.85, 1])
            
            return ax
        elif style == 31:
            """Bipartite Chord Diagram for two datasets"""
            if not has_two_datasets or "corr" not in kind:
                return heatmap(data, ax=ax, kind=kind, method=method, style=30,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs)
            
            # Separate the two sides
            n_vars_x = n_rows  # Dataset 1 items
            n_vars_y = n_cols  # Dataset 2 items
            
            # Create two semi-circles
            radius = 1.0
            
            # Dataset 1 nodes on left semi-circle
            angles_x = np.linspace(np.pi/2, 3*np.pi/2, n_vars_x, endpoint=False)
            node_positions_x = []
            for angle in angles_x:
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                node_positions_x.append((x, y))
            
            # Dataset 2 nodes on right semi-circle
            angles_y = np.linspace(-np.pi/2, np.pi/2, n_vars_y, endpoint=False)
            node_positions_y = []
            for angle in angles_y:
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                node_positions_y.append((x, y))
            
            # Plot chords between datasets (not within)
            chord_alpha = 0.6
            min_corr_threshold = 0.05
            
            # Store connection lines for legend
            connection_lines = []
            
            for i in range(n_vars_x):
                for j in range(n_vars_y):
                    corr = data4heatmap.iloc[i, j]
                    abs_corr = abs(corr)
                    
                    if abs_corr >= min_corr_threshold:
                        color = cmap(norm(corr))
                        
                        # Get positions
                        start_x, start_y = node_positions_x[i]
                        end_x, end_y = node_positions_y[j]
                        
                        # Create gentle curve using Bezier curve
                        # Control point is offset based on correlation strength and sign
                        from matplotlib.path import Path
                        import matplotlib.patches as patches
                        
                        # Calculate mid-point
                        mid_x = (start_x + end_x) / 2
                        mid_y = (start_y + end_y) / 2
                        
                        # Calculate curve strength based on correlation
                        curve_strength = abs_corr * 0.5  # Adjust this factor for more/less curve
                        
                        # Determine curve direction based on correlation sign
                        if corr > 0:  # Positive correlation - curve upward
                            ctrl_x = mid_x
                            ctrl_y = mid_y + curve_strength
                        else:  # Negative correlation - curve downward
                            ctrl_x = mid_x
                            ctrl_y = mid_y - curve_strength
                        
                        # Create Bezier curve with one control point (quadratic)
                        vertices = [
                            (start_x, start_y),  # Start point
                            (ctrl_x, ctrl_y),    # Control point
                            (end_x, end_y),      # End point
                        ]
                        
                        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
                        
                        path = Path(vertices, codes)
                        patch = patches.PathPatch(path,
                                                facecolor='none',
                                                edgecolor=color,
                                                linewidth=abs_corr * 3,
                                                alpha=chord_alpha,
                                                capstyle='round',
                                                joinstyle='round')
                        ax.add_patch(patch)
                        
                        # Store for potential legend
                        connection_lines.append((corr, abs_corr))
                        
                        # # Add correlation value at midpoint for strong correlations
                        # if annot and abs_corr > 0.7:
                        #     # Calculate position along the curve
                        #     t = 0.5  # Midpoint parameter
                        #     # Quadratic Bezier formula: (1-t)² * P0 + 2 * (1-t) * t * P1 + t² * P2
                        #     text_x = (1-t)**2 * start_x + 2 * (1-t) * t * ctrl_x + t**2 * end_x
                        #     text_y = (1-t)**2 * start_y + 2 * (1-t) * t * ctrl_y + t**2 * end_y
                            
                        #     # Offset text slightly perpendicular to the curve
                        #     # Calculate tangent direction
                        #     dx = 2 * (1-t) * (ctrl_x - start_x) + 2 * t * (end_x - ctrl_x)
                        #     dy = 2 * (1-t) * (ctrl_y - start_y) + 2 * t * (end_y - ctrl_y)
                            
                        #     # Normalize and rotate 90 degrees for perpendicular offset
                        #     length = np.sqrt(dx*dx + dy*dy)
                        #     if length > 0:
                        #         dx_norm = dx / length
                        #         dy_norm = dy / length
                        #         # Rotate 90 degrees
                        #         offset_x = -dy_norm * 0.1
                        #         offset_y = dx_norm * 0.1
                                
                        #         text_x += offset_x
                        #         text_y += offset_y
                            
                        #     ax.text(text_x, text_y, f"{corr:{fmt}}",
                        #         ha='center', va='center',
                        #         color='black' if abs_corr > 0.8 else 'white',
                        #         fontsize=fontsize * 0.7,
                        #         fontweight='bold',
                        #         bbox=dict(boxstyle="round,pad=0.1",
                        #                     facecolor='white' if abs_corr > 0.8 else color,
                        #                     alpha=0.8,
                        #                     edgecolor='none'))
            
            # Plot nodes for dataset 1 (left side)
            node_size = 300
            for i, (x, y) in enumerate(node_positions_x):
                # Calculate average correlation for this node
                avg_corr = data4heatmap.iloc[i, :].mean() if n_vars_y > 0 else 0
                node_color = cmap(norm(avg_corr)) if "corr" in kind else 'blue'
                
                # Draw node
                circle = patches.Circle((x, y), radius=0.08,
                                    facecolor=node_color,
                                    edgecolor='white',
                                    linewidth=2,
                                    alpha=0.9,
                                    zorder=10)
                ax.add_patch(circle)
                
                # Add variable label (outside the circle)
                label_radius = radius * 1.25
                label_x = label_radius * np.cos(angles_x[i])
                label_y = label_radius * np.sin(angles_x[i])
                
                # Determine text alignment based on position
                ha = 'right' if x < 0 else 'left'
                va = 'center'
                
                # Adjust for very top/bottom positions
                if abs(y) > radius * 0.8:
                    va = 'bottom' if y > 0 else 'top'
                
                ax.text(label_x, label_y, data4heatmap.index[i],
                    ha=ha, va=va,
                    fontsize=fontsize,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2",
                                facecolor='lightblue',
                                alpha=0.9,
                                edgecolor='gray'))
            
            # Plot nodes for dataset 2 (right side)
            for j, (x, y) in enumerate(node_positions_y):
                # Calculate average correlation for this node
                avg_corr = data4heatmap.iloc[:, j].mean() if n_vars_x > 0 else 0
                node_color = cmap(norm(avg_corr)) if "corr" in kind else 'red'
                
                # Draw node
                circle = patches.Circle((x, y), radius=0.08,
                                    facecolor=node_color,
                                    edgecolor='white',
                                    linewidth=2,
                                    alpha=0.9,
                                    zorder=10)
                ax.add_patch(circle)
                
                # Add variable label (outside the circle)
                label_radius = radius * 1.25
                label_x = label_radius * np.cos(angles_y[j])
                label_y = label_radius * np.sin(angles_y[j])
                
                # Determine text alignment based on position
                ha = 'right' if x < 0 else 'left'
                va = 'center'
                
                # Adjust for very top/bottom positions
                if abs(y) > radius * 0.8:
                    va = 'bottom' if y > 0 else 'top'
                
                ax.text(label_x, label_y, data4heatmap.columns[j],
                    ha=ha, va=va,
                    fontsize=fontsize,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2",
                                facecolor='lightcoral',
                                alpha=0.9,
                                edgecolor='gray'))
            
            # Add dataset labels
            ax.text(-radius * 1.5, 0, "Dataset 1",
                ha='center', va='center',
                fontsize=fontsize * 1.2,
                fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3",
                            facecolor='lightblue',
                            alpha=0.8))
            
            ax.text(radius * 1.5, 0, "Dataset 2",
                ha='center', va='center',
                fontsize=fontsize * 1.2,
                fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3",
                            facecolor='lightcoral',
                            alpha=0.8))
            
            # Set equal aspect and limits
            # Hide axes
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            margin = radius * 0.5
            ax.set_xlim(-radius - margin, radius + margin)
            ax.set_ylim(-radius - margin, radius + margin)
            
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Add colorbar
            # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            # sm.set_array([])
            # cbar = plt.colorbar(sm, ax=ax, shrink=0.6, pad=0.05)
            # cbar.set_label('Correlation Coefficient', fontsize=fontsize)
            # cbar.ax.tick_params(labelsize=fontsize)
            
            # # Add legend for line widths
            # from matplotlib.lines import Line2D
            # legend_elements = [
            #     Line2D([0], [0], color='gray', lw=1, label='|r| ≈ 0.3'),
            #     Line2D([0], [0], color='gray', lw=2, label='|r| ≈ 0.6'),
            #     Line2D([0], [0], color='gray', lw=3, label='|r| ≈ 1.0'),
            #     Line2D([0], [0], color='red', lw=2, linestyle='-', label='Positive correlation'),
            #     Line2D([0], [0], color='blue', lw=2, linestyle='-', label='Negative correlation'),
            #     patches.Circle((0, 0), radius=0.1, facecolor='lightblue', 
            #                 edgecolor='black', label='Dataset 1 nodes'),
            #     patches.Circle((0, 0), radius=0.1, facecolor='lightcoral', 
            #                 edgecolor='black', label='Dataset 2 nodes')
            # ]
            
            # # Position legend outside the plot
            # ax.legend(handles=legend_elements, loc='upper center',
            #         bbox_to_anchor=(0.5, -0.05),
            #         fontsize=fontsize * 0.7, ncol=3,
            #         title='Bipartite Network Guide',
            #         title_fontsize=fontsize * 0.8)
            
            # Add title
            if title is None:
                if hasattr(data, 'name') and hasattr(data_y, 'name'):
                    title = f"Cross-correlation: {data.name} ↔ {data_y.name}"
                else:
                    title = "Cross-correlation Network"
            figsets(**kws_figsets)
            # ax.set_title(title, fontsize=fontsize * 1.3, pad=20)
            
            return ax
        elif style == 32:
            """Sankey-style diagram for two datasets"""
            if not has_two_datasets or "corr" not in kind:
                return heatmap(data, ax=ax, kind=kind, method=method, style=30,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs)
            
            # Place dataset 1 on left, dataset 2 on right
            left_x = 0.1
            right_x = 0.9
            
            # Calculate y positions
            n_vars_x = n_rows
            n_vars_y = n_cols
            total_items = max(n_vars_x, n_vars_y)
            
            y_positions_x = np.linspace(0.9, 0.1, n_vars_x)
            y_positions_y = np.linspace(0.9, 0.1, n_vars_y)
            
            # Plot connections
            for i in range(n_vars_x):
                for j in range(n_vars_y):
                    corr = data4heatmap.iloc[i, j]
                    abs_corr = abs(corr)
                    
                    if abs_corr >= 0.3:  # Only show strong correlations
                        color = cmap(norm(corr))
                        
                        # Draw curved connection
                        from matplotlib.path import Path
                        import matplotlib.patches as patches
                        
                        vertices = [
                            (left_x, y_positions_x[i]),  # Start
                            ((left_x + right_x)/2, y_positions_x[i]),  # Control 1
                            ((left_x + right_x)/2, y_positions_y[j]),  # Control 2
                            (right_x, y_positions_y[j]),  # End
                        ]
                        
                        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                        path = Path(vertices, codes)
                        patch = patches.PathPatch(path, facecolor='none', 
                                                edgecolor=color, linewidth=abs_corr*5,
                                                alpha=0.6)
                        ax.add_patch(patch)
            
            # Add labels
            for i in range(n_vars_x):
                ax.text(left_x - 0.05, y_positions_x[i], data4heatmap.index[i],
                    ha='right', va='center', fontsize=fontsize)
                ax.scatter(left_x, y_positions_x[i], s=100, color='blue')
            
            for j in range(n_vars_y):
                ax.text(right_x + 0.05, y_positions_y[j], data4heatmap.columns[j],
                    ha='left', va='center', fontsize=fontsize)
                ax.scatter(right_x, y_positions_y[j], s=100, color='red')

            
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            figsets(**kws_figsets)
            return ax
        elif style == 33:
            """Sankey-style diagram for two datasets (shows all connections)"""
            if not has_two_datasets or "corr" not in kind:
                return heatmap(data, ax=ax, kind=kind, method=method, style=30,
                                fontsize=fontsize, tri=tri, mask=mask, k=k,
                                vmin=vmin, vmax=vmax, size_scale=size_scale,
                                annot=annot, cmap=cmap, fmt=fmt, kws_figsets=kws_figsets, **kwargs)
            
            # Get dimensions
            n_vars_x = n_rows  # Dataset 1 items
            n_vars_y = n_cols  # Dataset 2 items
            
            # Set up layout - dataset 1 on left, dataset 2 on right
            left_x = 0.1
            right_x = 0.9
            
            # Calculate vertical positions with some spacing
            if n_vars_x > 1:
                y_positions_x = np.linspace(0.95, 0.05, n_vars_x)
            else:
                y_positions_x = [0.5]
            
            if n_vars_y > 1:
                y_positions_y = np.linspace(0.95, 0.05, n_vars_y)
            else:
                y_positions_y = [0.5]
            
            # Adjust for large number of items
            if max(n_vars_x, n_vars_y) > 20:
                # Use thinner lines for many connections
                linewidth_factor = 2
                alpha = 0.4
            elif max(n_vars_x, n_vars_y) > 10:
                linewidth_factor = 3
                alpha = 0.5
            else:
                linewidth_factor = 5
                alpha = 0.6
            
            # Create a grid to track connection density (for potential optimization)
            connection_grid = np.zeros((n_vars_x, n_vars_y))
            
            # Plot ALL connections
            from matplotlib.path import Path
            import matplotlib.patches as patches
            
            # Store connections for sorting (optional: draw strongest last)
            connections = []
            for i in range(n_vars_x):
                for j in range(n_vars_y):
                    corr = data4heatmap.iloc[i, j]
                    if not pd.isna(corr):
                        abs_corr = abs(corr)
                        connections.append((i, j, corr, abs_corr))
            
            # Optional: Sort by absolute correlation (draw weakest first, strongest last)
            connections.sort(key=lambda x: x[3])  # Sort by abs_corr
            
            for i, j, corr, abs_corr in connections:
                color = cmap(norm(corr))
                
                # Calculate line width based on absolute correlation
                linewidth = max(0.5, abs_corr * linewidth_factor)
                
                # Use cubic Bezier curve for smooth connection
                # Control points create a gentle curve
                start_x, start_y = left_x, y_positions_x[i]
                end_x, end_y = right_x, y_positions_y[j]
                
                # Calculate horizontal distance
                dx = end_x - start_x
                
                # Control points at 1/3 and 2/3 of the way, with vertical offset
                # The offset creates a curve that avoids other lines
                ctrl1_x = start_x + dx * 0.33
                ctrl2_x = start_x + dx * 0.67
                
                # Calculate vertical difference
                dy = end_y - start_y
                
                # Create a gentle curve - more curve for larger vertical differences
                curve_factor = 0.3  # Controls how much curve
                ctrl1_y = start_y + dy * 0.33 + (np.random.random() * 0.05 if n_vars_x * n_vars_y > 50 else 0)
                ctrl2_y = start_y + dy * 0.67 + (np.random.random() * 0.05 if n_vars_x * n_vars_y > 50 else 0)
                
                # Add slight random offset for many connections to reduce overlap
                if n_vars_x * n_vars_y > 100:
                    ctrl1_x += (np.random.random() - 0.5) * 0.02
                    ctrl2_x += (np.random.random() - 0.5) * 0.02
                
                vertices = [
                    (start_x, start_y),      # Start point
                    (ctrl1_x, ctrl1_y),      # First control point
                    (ctrl2_x, ctrl2_y),      # Second control point
                    (end_x, end_y),          # End point
                ]
                
                codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                
                path = Path(vertices, codes)
                patch = patches.PathPatch(path, 
                                        facecolor='none',
                                        edgecolor=color,
                                        linewidth=linewidth,
                                        alpha=alpha,
                                        capstyle='round',
                                        joinstyle='round')
                ax.add_patch(patch)
                
                # Track connection density for annotation positioning
                connection_grid[i, j] = abs_corr
                
                # Add correlation value for strong correlations if annot is True
                if annot and abs_corr > 0.7:
                    # Calculate midpoint along the curve
                    t = 0.5
                    # Cubic Bezier formula
                    mt = 1 - t
                    text_x = (mt**3 * start_x + 3 * mt**2 * t * ctrl1_x + 
                            3 * mt * t**2 * ctrl2_x + t**3 * end_x)
                    text_y = (mt**3 * start_y + 3 * mt**2 * t * ctrl1_y + 
                            3 * mt * t**2 * ctrl2_y + t**3 * end_y)
                    
                    # Add text with contrasting color
                    text_color = 'white' if abs(norm(corr)) > 0.7 else 'black'
                    ax.text(text_x, text_y, f"{corr:{fmt}}",
                        ha='center', va='center',
                        color=text_color,
                        fontsize=fontsize * 0.7,
                        fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.1",
                                    facecolor=color,
                                    alpha=0.8,
                                    edgecolor='none'))
            
            # Add nodes for dataset 1 (left side)
            node_size_base = 300
            for i, y in enumerate(y_positions_x):
                # Calculate node color based on average correlation
                avg_corr = data4heatmap.iloc[i, :].mean(skipna=True)
                node_color = cmap(norm(avg_corr)) if not pd.isna(avg_corr) else 'gray'
                
                # Node size based on connection strength
                node_connections = connection_grid[i, :]
                avg_strength = np.nanmean(node_connections) if np.any(node_connections > 0) else 0
                node_size = node_size_base * (1 + avg_strength * 0.5)
                
                # Draw node
                circle = patches.Circle((left_x, y), radius=0.02,
                                    facecolor=node_color,
                                    edgecolor='none',
                                    linewidth=1.5,
                                    alpha=0.9,
                                    zorder=10)
                ax.add_patch(circle)
                
                # Add variable label
                ax.text(left_x - 0.04, y, data4heatmap.index[i],
                    ha='right', va='center',
                    fontsize=fontsize,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2",
                                facecolor='lightblue',
                                alpha=0.8,
                                edgecolor='none'))
            
            # Add nodes for dataset 2 (right side)
            for j, y in enumerate(y_positions_y):
                # Calculate node color based on average correlation
                avg_corr = data4heatmap.iloc[:, j].mean(skipna=True)
                node_color = cmap(norm(avg_corr)) if not pd.isna(avg_corr) else 'gray'
                
                # Node size based on connection strength
                node_connections = connection_grid[:, j]
                avg_strength = np.nanmean(node_connections) if np.any(node_connections > 0) else 0
                node_size = node_size_base * (1 + avg_strength * 0.5)
                
                # Draw node
                circle = patches.Circle((right_x, y), radius=0.02,
                                    facecolor=node_color,
                                    edgecolor='white',
                                    linewidth=1.5,
                                    alpha=0.9,
                                    zorder=10)
                ax.add_patch(circle)
                
                # Add variable label
                ax.text(right_x + 0.04, y, data4heatmap.columns[j],
                    ha='left', va='center',
                    fontsize=fontsize,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2",
                                facecolor='lightcoral',
                                alpha=0.8,
                                edgecolor='gray'))
            
            # Add dataset labels
            ax.text(left_x, 1.02, "Dataset 1",
                ha='center', va='bottom',
                fontsize=fontsize * 1.2,
                fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3",
                            facecolor='lightblue',
                            alpha=0.9))
            
            ax.text(right_x, 1.02, "Dataset 2",
                ha='center', va='bottom',
                fontsize=fontsize * 1.2,
                fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3",
                            facecolor='lightcoral',
                            alpha=0.9))
            
            # Add title
            total_connections = np.sum(connection_grid > 0)
            ax.set_title(f"Cross-correlation Network ({total_connections} connections)",
                        fontsize=fontsize * 1.3, pad=20)
            
            # Set axis limits
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.invert_yaxis() if invert_yaxis else None
            ax.set_aspect('equal') if set_aspect else ax.set_aspect('auto')
            
            # Hide axes
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            figsets(**kws_figsets)
            # # Add colorbar
            # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            # sm.set_array([])
            # cbar = plt.colorbar(sm, ax=ax, shrink=0.8, pad=0.02)
            # cbar.set_label('Correlation Coefficient', fontsize=fontsize)
            # cbar.ax.tick_params(labelsize=fontsize)
            
            # # Add legend for line widths
            # from matplotlib.lines import Line2D
            # if linewidth_factor == 5:
            #     legend_lines = [
            #         Line2D([0], [0], color='gray', lw=0.5, label='|r| ≈ 0.1'),
            #         Line2D([0], [0], color='gray', lw=1.5, label='|r| ≈ 0.3'),
            #         Line2D([0], [0], color='gray', lw=2.5, label='|r| ≈ 0.5'),
            #         Line2D([0], [0], color='gray', lw=4, label='|r| ≈ 0.8'),
            #         Line2D([0], [0], color='red', lw=2, label='Positive'),
            #         Line2D([0], [0], color='blue', lw=2, label='Negative'),
            #     ]
            # elif linewidth_factor == 3:
            #     legend_lines = [
            #         Line2D([0], [0], color='gray', lw=0.3, label='|r| ≈ 0.1'),
            #         Line2D([0], [0], color='gray', lw=0.9, label='|r| ≈ 0.3'),
            #         Line2D([0], [0], color='gray', lw=1.5, label='|r| ≈ 0.5'),
            #         Line2D([0], [0], color='gray', lw=2.4, label='|r| ≈ 0.8'),
            #     ]
            # else:
            #     legend_lines = [
            #         Line2D([0], [0], color='gray', lw=0.2, label='|r| ≈ 0.1'),
            #         Line2D([0], [0], color='gray', lw=0.6, label='|r| ≈ 0.3'),
            #         Line2D([0], [0], color='gray', lw=1.0, label='|r| ≈ 0.5'),
            #         Line2D([0], [0], color='gray', lw=1.6, label='|r| ≈ 0.8'),
            #     ]
            
            # # Add node examples to legend
            # from matplotlib.patches import Patch
            # legend_patches = [
            #     Patch(facecolor='lightblue', edgecolor='black', label='Dataset 1'),
            #     Patch(facecolor='lightcoral', edgecolor='black', label='Dataset 2'),
            # ]
            
            # # Combine and display legend
            # all_legend_elements = legend_lines + legend_patches
            # ax.legend(handles=all_legend_elements, 
            #         loc='upper center',
            #         bbox_to_anchor=(0.5, -0.05),
            #         fontsize=fontsize * 0.7,
            #         ncol=3,
            #         title='Visual Encoding Guide',
            #         title_fontsize=fontsize * 0.8)
            
            # Add note about number of connections
            if total_connections > 50:
                ax.text(0.5, -0.15, f"Showing {total_connections} connections. "
                        f"Lines are semi-transparent to show overlap.",
                        transform=ax.transAxes,
                        ha='center', va='top',
                        fontsize=fontsize * 0.7,
                        style='italic')
            
            return ax
        else:
            # Default fallback
            ax = sns.heatmap(
                data4heatmap,
                ax=ax,
                mask=mask_array,
                annot=annot,
                cmap=cmap,
                fmt=fmt,
                **kwargs,
            )
            return ax

def circular(
    data: Union[pd.DataFrame, List],
    data_y: Optional[pd.DataFrame] = None,
    kind: str = "chord",
    cmap: Union[str, List[str]] = "coolwarm",
    space: float = 5,
    figsize: Tuple[int, int] = (10, 10),
    title: Optional[str] = '',
    annot: bool = False,
    fmt: str = ".2f",
    threshold: float = 0.0,
    directed: bool = False,
    group_labels: Optional[List[str]] = None,
    group_colors: Optional[List[str]] = None,
    show_legend: bool = True,
    fontsize: int = 12,
    linewidth: float = 0.5,
    method: str = "pearson",  # for correlation
    columns_x: Optional[List[str]] = None,
    columns_y: Optional[List[str]] = None,
    matrix_type: str = "correlation",  # "correlation", "adjacency", "flow"
    style: int = 0,  # Style variation for each kind
    exclude_self: bool = True,
    diagonal_value: Union[float, str] = 0,  #  0, 'nan', or 'min'
    **kwargs,
):
    """
    Circular visualizations with pycirclize backend.

    Parameters:
    -----------
    data : pd.DataFrame or list
        Main data matrix or dataframe.
    data_y : pd.DataFrame, optional
        Second dataset for cross-dataset chord diagrams.
    kind : str, default="chord"
        Type of circular plot:
        - "chord": Chord/arc diagram
        - "circos": General circos plot
        - "genomics": Genome visualization
        - "tree": Phylogenetic tree
        - "radar": Radar/spider chart
        - "heatmap": Circular heatmap
    cmap : str or list, default="coolwarm"
        Colormap for visualization.
    space : float, default=5
        Space between sectors (degrees).
    figsize : tuple, default=(10, 10)
        Figure size.
    title : str, optional
        Plot title.
    annot : bool, default=False
        Whether to annotate values.
    fmt : str, default=".2f"
        Format string for annotations.
    threshold : float, default=0.0
        Minimum value to show connection/link.
    directed : bool, default=False
        Whether links are directed (for chord diagram). 
    group_labels : list, optional
        Group labels for sectors/nodes.
    group_colors : list, optional
        Colors for each group.
    show_legend : bool, default=True
        Whether to show legend.
    fontsize : int, default=12
        Label font size.
    linewidth : float, default=0.5
        Width of links in chord diagram.
    method : str, default="pearson"
        Correlation method for correlation matrices.
    columns_x, columns_y : list, optional
        Columns to use from datasets.
    matrix_type : str, default="correlation"
        Type of matrix: "correlation", "adjacency", "flow"
    style : int, default=0
        Style variation for each plot type.
    exclude_self : bool, default=True
        Whether to exclude self-correlations (diagonal values).
        For correlation matrices, self-correlation is always 1.0
        and should be excluded for meaningful visualization.
    diagonal_value : float or str, default=0
        What to set diagonal values to when exclude_self=True:
        - 0: Set to zero (default, most common)
        - 'nan': Set to NaN (will not be plotted)
        - 'min': Set to minimum off-diagonal value
        - Any number: Set to that specific value
    **kwargs :
        Additional parameters passed to pycirclize.
    """

    from matplotlib.colors import LinearSegmentedColormap, Normalize
    from matplotlib.cm import ScalarMappable

    try:
        from pycirclize import Circos
        from pycirclize.utils import ColorCycler

        PYCIRC_AVAILABLE = True
    except ImportError:
        PYCIRC_AVAILABLE = False
        raise ImportError(
            "Please install pycirclize for circular visualizations:\n"
            "pip install pycirclize"
        )
    if run_once_within(10):
        print("""
        circular(
            data1,
            data_y=data2,
            kind="chord",
            cmap=get_cmap("tab20", 15, return_list=1).tolist(),
            # threshold=0.1,
            space=5,
            annot=True,
            directed=True,
            figsize=(12, 12),
            matrix_type="adjacency",
        )
              """)
    #### helper functions ##### 
    def _fix_zero_sectors(matrix, min_value=1e-3, preserve_zeros=True):
        """
        Ensure all sectors in a chord/circos matrix have positive span.
        Removes zero/tiny rows/columns and pads remaining ones so pycirclize
        cannot produce sectors with size == 0.
        
        Parameters:
        -----------
        matrix : pd.DataFrame
            Input matrix
        min_value : float, default=1e-3
            Minimum value to pad
        preserve_zeros : bool, default=False
            If True, preserve zero values (don't add min_value to zeros)
        """
        df = matrix.copy()
        
        # First, identify which values are truly zero (after thresholding)
        if preserve_zeros:
            zero_mask = df.abs() == 0
        
        # 1. Remove all-zero rows/columns
        nonzero = df.sum(axis=1) != 0
        df = df.loc[nonzero, nonzero]
        
        # If everything removed → restore tiny noise
        if df.shape[0] < 2:
            # Only add min_value where it was originally zero
            if preserve_zeros:
                result = matrix.copy()
                result[~zero_mask] = result[~zero_mask] + min_value
                return result
            else:
                return matrix + min_value
        
        # 2. Pad extremely small values: avoids start=end
        # But preserve zeros if requested
        if preserve_zeros:
            # Only add min_value to non-zero elements
            non_zero_mask = df.abs() > 0
            df[non_zero_mask] = df[non_zero_mask] + min_value
        else:
            # Original behavior: add to all elements
            df = df + min_value
        
        # 3. Ensure diagonal is non-zero: pycirclize uses diagonal for block span
        for col in df.columns:
            if df.loc[col, col] < min_value:
                df.loc[col, col] = min_value
        
        return df
    def _create_cross_dataset_chord(data, data_y, **params):
        """Create chord diagram for two datasets."""
        from pycirclize import Circos
        import numpy as np

        # Extract parameters
        cmap = params.pop("cmap", "coolwarm")
        space = params.pop("space", 5)
        figsize = params.pop("figsize", (10, 10))
        title = params.pop("title", None)
        annot = params.pop("annot", False)
        fmt = params.pop("fmt", ".2f")
        threshold = params.pop("threshold", 0.0)
        directed = params.pop("directed", False)
        label_size = params.pop("fontsize", 12)
        link_width = params.pop("linewidth", 0.5)
        method = params.pop("method", "pearson")
        columns_x = params.pop("columns_x", None)
        columns_y = params.pop("columns_y", None)
        matrix_type = params.pop("matrix_type", "correlation")
        style = params.pop("style", 0)

        # Select columns if specified
        if columns_x is None:
            df1 = data.select_dtypes(include=[np.number])
        else:
            df1 = data[columns_x]

        if columns_y is None:
            df2 = data_y.select_dtypes(include=[np.number])
        else:
            df2 = data_y[columns_y]

        # Calculate cross-correlation
        from scipy.stats import pearsonr, spearmanr, kendalltau

        if method == "pearson":
            corr_func = pearsonr
        elif method == "spearman":
            corr_func = spearmanr
        elif method == "kendall":
            corr_func = kendalltau
        else:
            corr_func = pearsonr

        cross_matrix = pd.DataFrame(index=df1.columns, columns=df2.columns)

        for i, col1 in enumerate(df1.columns):
            for j, col2 in enumerate(df2.columns):
                try:
                    x_vals = df1[col1].dropna()
                    y_vals = df2[col2].dropna()
                    common_idx = x_vals.index.intersection(y_vals.index)
                    if len(common_idx) > 1:
                        x_common = x_vals.loc[common_idx]
                        y_common = y_vals.loc[common_idx]
                        corr, _ = corr_func(x_common, y_common)
                        cross_matrix.iloc[i, j] = corr
                    else:
                        cross_matrix.iloc[i, j] = 0
                except:
                    cross_matrix.iloc[i, j] = 0

        # Apply threshold
        if threshold > 0:
            cross_matrix = cross_matrix.where(np.abs(cross_matrix) >= threshold, 0)

        # Create block matrix for pycirclize
        row_names = list(cross_matrix.index)
        col_names = list(cross_matrix.columns)
        all_names = row_names + col_names

        # Create square matrix
        block_matrix = pd.DataFrame(0, index=all_names, columns=all_names)

        # Fill cross-correlation blocks
        block_matrix.loc[row_names, col_names] = cross_matrix.values
        if not directed:
            block_matrix.loc[col_names, row_names] = cross_matrix.values.T

        # Configure pycirclize parameters
        link_kws=dict(ec="black",lw=link_width,direction = 1 if directed else 0)
        link_kws.update(params.get("link_kws", {}))
        label_kws=dict(size=label_size, orientation="vertical")
        label_kws.update(params.get("label_kws", {}))
        
        if isinstance(cmap, str):
            cmap=cmap
        elif isinstance(cmap, list):
            cmap = {name: cmap[i % len(cmap)] for i, name in enumerate(block_matrix.index)}
        else:
            print(f"Custom Color must be a list:e.g.,  cmap=get_cmap('coolwarm', 8, return_list=1).tolist()")
            cmap="tab10" 
        params=handle_kwargs(params, Circos.chord_diagram,how="pop",exclude_list=['cmap',"space","label_kws","link_kws"])
        # Create chord diagram
        circos = Circos.chord_diagram(
            block_matrix,# _fix_zero_sectors(block_matrix),
            space=space,
            cmap=cmap,
            link_kws=link_kws,
            label_kws=label_kws,
            **params,
        )

        # Add title
        if title is None:
            title = f"Cross-dataset ({method}): {len(row_names)} × {len(col_names)}"

        circos.text(title, size=label_size + 4)

        # Plot figure
        fig = circos.plotfig(figsize=figsize)
        plt.close(fig)
        return fig

    def _create_single_dataset_plot(data, **params):
        """Create various circular plots for single dataset."""
        from pycirclize import Circos
        from pycirclize.utils import ColorCycler
        import numpy as np

        # Extract parameters
        kind = params.get("kind", "chord")
        cmap = params.get("cmap", "coolwarm")
        space = params.get("space", 5)
        figsize = params.get("figsize", (10, 10))
        title = params.get("title", None)
        annot = params.get("annot", False)
        fmt = params.get("fmt", ".2f")
        threshold = params.get("threshold", 0.0)
        directed = params.get("directed", False)
        group_labels = params.get("group_labels", None)
        group_colors = params.get("group_colors", None)
        show_legend = params.get("show_legend", True)
        label_size = params.get("fontsize", 12)
        link_width = params.get("linewidth", 0.5)
        method = params.get("method", "pearson")
        columns_x = params.get("columns_x", None)
        matrix_type = params.get("matrix_type", "correlation")
        style = params.get("style", 0)
        kwargs = params.get("kwargs", {})

        # Prepare data based on kind
        if kind == "chord":
            return _create_chord_diagram(data, **params)
        elif kind == "radar":
            return _create_radar_chart(data, **params)
        elif kind == "heatmap":
            return _create_circular_heatmap(data, **params)
        elif kind == "tree":
            return _create_tree_plot(data, **params)
        elif kind == "genomics":
            return _create_genomics_plot(data, **params)
        elif kind == "circos":
            return _create_circos_plot(data, **params)
        else:
            raise ValueError(f"Unknown plot kind: {kind}")

    def _create_radar_chart(data, **params):
        """Create radar/spider chart."""
        from pycirclize import Circos

        # Extract parameters
        cmap = params.get("cmap", "coolwarm")
        figsize = params.get("figsize", (10, 10))
        title = params.get("title", None)
        show_legend = params.get("show_legend", True)
        kwargs = params.get("kwargs", {})

        # Create radar chart
        circos = Circos.radar_chart(
            data,
            vmax=kwargs.get("vmax", 100),
            marker_size=kwargs.get("marker_size", 6),
            grid_interval_ratio=kwargs.get("grid_interval_ratio", 0.2),
            cmap=cmap,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["vmax", "marker_size", "grid_interval_ratio"]
            },
        )

        # Add title
        if title:
            circos.text(title, size=14)

        # Plot figure
        fig = circos.plotfig(figsize=figsize)

        # Add legend
        if show_legend:
            circos.ax.legend(loc="upper right", fontsize=10)

        plt.close(fig)
        return fig



    def _create_chord_diagram(data, **params):
        from pycirclize import Circos
        import numpy as np
        import warnings

        cmap = params.get("cmap", "coolwarm")
        space = params.get("space", 5)
        figsize = params.get("figsize", (10, 10))
        title = params.get("title", None)
        threshold = params.get("threshold", 0.0)
        directed = params.get("directed", False)
        label_size = params.get("fontsize", 12)
        link_width = params.get("linewidth", 0.5)
        method = params.get("method", "pearson")
        columns_x = params.get("columns_x", None)
        matrix_type = params.get("matrix_type", "correlation")
        exclude_self = params.get("exclude_self", True)
        diagonal_value = params.get("diagonal_value", 0)
        
        def _remove_self_correlations(matrix, exclude_self, diagonal_value):
            """Remove or modify diagonal values in square matrix."""
            if not exclude_self or matrix.shape[0] != matrix.shape[1]:
                return matrix
            
            matrix_copy = matrix.copy()
            n = matrix_copy.shape[0]
            
            # Handle different diagonal value options
            if diagonal_value == 'nan':
                np.fill_diagonal(matrix_copy.values, np.nan)
            elif diagonal_value == 'min':
                mask = ~np.eye(n, dtype=bool)
                off_diag_values = matrix_copy.values[mask]
                if len(off_diag_values) > 0 and not np.all(np.isnan(off_diag_values)):
                    min_val = np.nanmin(off_diag_values)
                    np.fill_diagonal(matrix_copy.values, min_val)
                else:
                    np.fill_diagonal(matrix_copy.values, 0)
            elif isinstance(diagonal_value, (int, float)):
                np.fill_diagonal(matrix_copy.values, diagonal_value)
            else:
                np.fill_diagonal(matrix_copy.values, 0)
            return matrix_copy
        
        def _apply_threshold(matrix, threshold, verbose=True):
            """Apply threshold to matrix and optionally filter zeros."""
            if threshold <= 0:
                return matrix
            
            matrix_copy = matrix.copy()
            
            # Apply absolute threshold - set values below threshold to 0
            mask = np.abs(matrix_copy.values) < threshold
            matrix_copy.values[mask] = 0
            
            # Count connections before filtering
            n_connections = np.sum(np.abs(matrix_copy.values) > 0)
            if verbose:
                print(f"Threshold applied: |value| >= {threshold}")
                print(f"  Non-zero connections after threshold: {n_connections}")
            
            # For visualization, we need to ensure at least 2 nodes have connections
            if n_connections == 0:
                warnings.warn(f"No connections remain after threshold {threshold}. Consider lowering the threshold.")
                return matrix_copy
            
            # Filter out nodes with no connections at all
            if matrix_copy.shape[0] == matrix_copy.shape[1]:
                # Square matrix - filter both rows and columns
                has_connections = (np.abs(matrix_copy.values).sum(axis=0) > 0) | \
                                (np.abs(matrix_copy.values).sum(axis=1) > 0)
                if np.sum(has_connections) >= 2:  # Need at least 2 nodes
                    matrix_copy = matrix_copy.iloc[has_connections, has_connections]
                    if verbose:
                        print(f"  Filtered to {matrix_copy.shape[0]} nodes with connections")
            
            return matrix_copy
        
        def _prepare_matrix(data, params):
            """Prepare correlation/adjacency matrix with all preprocessing."""
            matrix_type = params.get("matrix_type", "correlation")
            exclude_self = params.get("exclude_self", True)
            diagonal_value = params.get("diagonal_value", 0)
            threshold = params.get("threshold", 0.0)
            method = params.get("method", "pearson")
            columns_x = params.get("columns_x", None)
            verbose = params.get("verbose", True)
            
            if isinstance(data, pd.DataFrame):
                # Check if it's already a correlation-like matrix
                if data.shape[0] == data.shape[1] and all(data.index == data.columns):
                    matrix = data.copy()
                    if verbose:
                        print(f"Input is square matrix ({matrix.shape[0]}×{matrix.shape[1]})")
                    
                    # Show diagonal values before exclusion
                    if exclude_self:
                        if verbose:
                            print(f"  Removing self-correlations (diagonal values)")
                        matrix = _remove_self_correlations(matrix, exclude_self, diagonal_value)
                else:
                    # Calculate correlation
                    if verbose:
                        print(f"Calculating {method} correlation matrix...")
                    if columns_x is None:
                        numeric_data = data.select_dtypes(include=[np.number])
                        if verbose:
                            print(f"  Using all numeric columns ({numeric_data.shape[1]} columns)")
                    else:
                        numeric_data = data[columns_x]
                        if verbose:
                            print(f"  Using specified columns ({len(columns_x)} columns)")
                    
                    if method == "pearson":
                        matrix = numeric_data.corr()
                    elif method == "spearman":
                        matrix = numeric_data.corr(method="spearman")
                    elif method == "kendall":
                        matrix = numeric_data.corr(method="kendall")
                    else:
                        matrix = numeric_data.corr()
                    
                    # Remove self-correlations
                    if exclude_self:
                        if verbose:
                            print(f"  Removing self-correlations (diagonal values)")
                        matrix = _remove_self_correlations(matrix, exclude_self, diagonal_value)
            else:
                matrix = pd.DataFrame(data)
                # Remove self-correlations if it's square
                if exclude_self and matrix.shape[0] == matrix.shape[1]:
                    matrix = _remove_self_correlations(matrix, exclude_self, diagonal_value)
            
            # Apply threshold to filter out small values
            if threshold > 0:
                matrix = _apply_threshold(matrix, threshold, verbose)
            
            return matrix
        
        # Prepare the matrix with all preprocessing
        matrix = _prepare_matrix(data, params)
        
        # Debug: print matrix values
        print("\nMatrix values after thresholding:")
        print(f"Shape: {matrix.shape}")
        print(f"Total elements: {matrix.size}")
        print(f"Non-zero elements: {np.sum(matrix.values != 0)}")
        print(f"Min value: {np.min(matrix.values[matrix.values != 0]) if np.any(matrix.values != 0) else 0}")
        print(f"Max value: {np.max(matrix.values)}")
        
        # Check if we have enough data to plot
        if matrix.shape[0] < 2:
            # Create an error plot
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, f"Not enough connections after threshold {threshold}", 
                    ha='center', va='center', fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            plt.close(fig)
            return fig
        
        # Fix zero sectors for pycirclize - PRESERVE ZEROS!
        # matrix = _fix_zero_sectors(matrix, preserve_zeros=True)
        
        # Debug: print matrix values after fixing
        print("\nMatrix values after fixing zero sectors:")
        print(f"Shape: {matrix.shape}")
        print(f"Total elements: {matrix.size}")
        print(f"Non-zero elements: {np.sum(matrix.values != 0)}")
        print(f"Min value: {np.min(matrix.values[matrix.values != 0]) if np.any(matrix.values != 0) else 0}")
        print(f"Max value: {np.max(matrix.values)}")

        # Configure pycirclize parameters
        link_kws=dict(ec="black",lw=link_width,direction = 1 if directed else 0)
        link_kws.update(params.get("link_kws", {}))
        label_kws=dict(size=label_size, orientation="vertical")
        label_kws.update(params.get("label_kws", {}))

        # Handle colormap
        if isinstance(cmap, str):
            pass  # Use string as is
        elif isinstance(cmap, list):
            cmap = {name: cmap[i % len(cmap)] for i, name in enumerate(matrix.index)}
        else:
            print(f"Custom Color must be a list: e.g., cmap=get_cmap('coolwarm', 8, return_list=1).tolist()")
            cmap = "tab10"
        params=handle_kwargs(params, Circos.chord_diagram,how="pop",exclude_list=['cmap',"space","label_kws","link_kws"])
        try:
            # Create chord diagram with the thresholded matrix
            circos = Circos.chord_diagram(
                matrix,
                space=space,
                cmap=cmap,
                label_kws=label_kws,
                link_kws=link_kws,
                **params,
            )

            if title:
                circos.text(title, size=label_size + 4)
            if matrix_type == "correlation" and title is None:
                title_text = f"{method} correlation (threshold={threshold})"
                circos.text(title_text, size=label_size + 4)

            # Plot figure
            fig = circos.plotfig(figsize=figsize)
            plt.close(fig)
            return fig
        except Exception as e:
            print(f"Error creating chord diagram: {e}")
            # Create a simple error plot
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, f"Error: {str(e)}", 
                    ha='center', va='center', fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            plt.close(fig)
            return fig
    def _create_circular_heatmap(data, **params):
        """Create circular heatmap."""
        from pycirclize import Circos
        import matplotlib.pyplot as plt

        # Extract parameters
        cmap = params.get("cmap", "coolwarm")
        space = params.get("space", 5)
        figsize = params.get("figsize", (10, 10))
        title = params.get("title", None)
        annot = params.get("annot", False)
        fmt = params.get("fmt", ".2f")
        kwargs = params.get("kwargs", {})

        # Prepare data
        if isinstance(data, pd.Series):
            sectors = data.to_dict()
        elif isinstance(data, pd.DataFrame):
            if data.shape[1] == 1:
                sectors = data.iloc[:, 0].to_dict()
            else:
                sectors = {str(i): 100 for i in range(len(data))}
        else:
            sectors = dict(data)

        # Initialize circos
        circos = Circos(sectors, space=space)

        # Add title
        if title:
            circos.text(title, size=14)

        # Get colormap
        cmap_obj = plt.cm.get_cmap(cmap) if isinstance(cmap, str) else cmap

        # Add heatmap tracks
        for i, sector in enumerate(circos.sectors):
            track = sector.add_track((80, 100), r_pad_ratio=0.1)
            track.axis()

            if isinstance(data, pd.DataFrame) and i < len(data):
                if data.shape[1] > 1:
                    # Multi-dimensional data
                    row_data = data.iloc[i].values
                    n_features = len(row_data)
                    feature_width = (sector.end - sector.start) / n_features

                    for j, value in enumerate(row_data):
                        start = sector.start + j * feature_width
                        end = start + feature_width

                        # Normalize value for color mapping
                        norm_value = value / row_data.max() if row_data.max() > 0 else 0
                        color = cmap_obj(norm_value)

                        track.rect(start, end, 80, 100, fc=color, ec="none")

                        if annot:
                            mid = (start + end) / 2
                            track.text(f"{value:{fmt}}", mid, 90, size=8)
                else:
                    # Single value per sector
                    value = data.iloc[i, 0]
                    max_val = (
                        data.max().max()
                        if isinstance(data, pd.DataFrame)
                        else max(data.values())
                    )
                    norm_value = value / max_val if max_val > 0 else 0
                    color = cmap_obj(norm_value)

                    track.rect(
                        start=sector.start,
                        end=sector.end,
                        fc=color,
                        ec="none"
                    )

                    if annot:
                        mid = (sector.start + sector.end) / 2
                        track.text(f"{value:{fmt}}", mid, 90, size=10)

        # Plot figure
        fig = circos.plotfig(figsize=figsize)
        plt.close(fig)
        return fig

    def _create_tree_plot(data, **params):
        """Create phylogenetic tree plot."""
        from pycirclize import Circos
        from matplotlib.lines import Line2D

        # Extract parameters
        cmap = params.get("cmap", "coolwarm")
        figsize = params.get("figsize", (10, 10))
        title = params.get("title", None)
        show_legend = params.get("show_legend", True)
        kwargs = params.get("kwargs", {})

        # Prepare tree data
        if isinstance(data, pd.DataFrame):
            tree_str = data.iloc[0, 0] if data.shape[1] > 0 else str(data)
        else:
            tree_str = str(data)

        # Initialize from tree
        circos, tv = Circos.initialize_from_tree(
            tree_str,
            r_lim=(30, 100),
            leaf_label_size=8,
            line_kws=dict(color="lightgrey", lw=1.0),
            **kwargs,
        )

        # Add title
        if title:
            circos.text(title, size=14)

        # Plot figure
        fig = circos.plotfig(figsize=figsize)
        plt.close(fig)
        return fig

    def _create_genomics_plot(data, **params):
        """Create genomics circular plot."""
        from pycirclize import Circos

        # Extract parameters
        space = params.get("space", 5)
        figsize = params.get("figsize", (10, 10))
        title = params.get("title", None)
        kwargs = params.get("kwargs", {})

        # Prepare sectors
        if isinstance(data, dict):
            sectors = data
        elif hasattr(data, "get_seqid2size"):
            sectors = data.get_seqid2size()
        else:
            raise ValueError(
                "For genomics plot, provide dict of sector sizes or Genbank object"
            )

        # Create circos
        space_val = 0 if len(sectors) == 1 else space
        circos = Circos(sectors, space=space_val)

        # Add title
        if title:
            circos.text(title, size=14)

        # Plot figure
        fig = circos.plotfig(figsize=figsize)
        plt.close(fig)
        return fig

    def _create_circos_plot(data, **params):
        """Create general circos plot."""
        from pycirclize import Circos
        import numpy as np

        # Extract parameters
        space = params.get("space", 5)
        figsize = params.get("figsize", (10, 10))
        title = params.get("title", None)
        kwargs = params.get("kwargs", {})

        # Prepare sectors
        if isinstance(data, dict):
            sectors = data
        elif isinstance(data, pd.Series):
            sectors = data.to_dict()
        elif isinstance(data, pd.DataFrame) and data.shape[1] >= 2:
            sectors = dict(zip(data.iloc[:, 0], data.iloc[:, 1]))
        else:
            sectors = {f"Sector_{i}": 100 for i in range(len(data))}

        # Initialize circos
        circos = Circos(sectors, space=space)

        # Add title
        if title:
            circos.text(title, size=14)

        # Add example tracks (customize as needed)
        for sector in circos.sectors:
            sector.text(f"Sector: {sector.name}", r=110, size=12)

            # Example line plot
            track1 = sector.add_track((80, 100), r_pad_ratio=0.1)
            track1.axis()
            x = np.arange(sector.start, sector.end) + 0.5
            y = np.random.randint(0, 100, len(x))
            track1.line(x, y)

            # Example scatter plot
            track2 = sector.add_track((55, 75), r_pad_ratio=0.1)
            track2.axis()
            track2.scatter(x, y)

        # Plot figure
        fig = circos.plotfig(figsize=figsize)
        plt.close(fig)
        return fig
    def circos_heatmap(
        data: pd.DataFrame,
        **kwargs
    ):
        """
        Quick circular heatmap.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Data for circular heatmap.
        **kwargs : 
            Additional parameters for circular().
            
        Returns:
        --------
        matplotlib.figure.Figure
        """
        return circular(data, kind="heatmap", **kwargs)


    # ========== Integration with your corr_heatmap ==========

    def corr_heatmap_with_circular(
        data: pd.DataFrame,
        data_y: Optional[pd.DataFrame] = None,
        style: int = 30,
        **kwargs
    ):
        """
        Your corr_heatmap function with circular visualization option.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Main data.
        data_y : pd.DataFrame, optional
            Second dataset.
        style : int, default=30
            Style 30 uses circular chord diagram.
        **kwargs : 
            Additional parameters.
            
        Returns:
        --------
        matplotlib.figure.Figure or other return types
        """
        if style == 30:
            # Use chord diagram
            return circular(data, data_y=data_y, kind="chord", **kwargs)
        elif style == 31:
            # Use radar chart
            return circular(data, kind="radar", **kwargs)
        elif style == 32:
            # Use circular heatmap
            return circular(data, kind="heatmap", **kwargs)
        else:
            # Call your original heatmap for other styles
            # You would need to import your original function here
            raise ValueError(f"Style {style} not implemented in circular function. "
                            f"Use styles 30-32 for circular visualizations.")


    #### Main Func ######
    # Parse kind parameter
    kind_match = strcmp(kind, ["chord", "circos", "genomics", "tree", "radar", "heatmap"])[0]

    # Handle list input for backward compatibility
    if isinstance(data, list) and len(data) == 2 and data_y is None:
        print("Using list input: data[0] -> data, data[1] -> data_y")
        data_y = data[1]
        data = data[0]

    # Handle two datasets
    has_two_datasets = data_y is not None

    # Prepare data based on kind and dataset configuration
    if has_two_datasets and kind_match in ["chord", "circos"]:
        # Cross-dataset chord diagram
        return _create_cross_dataset_chord(
            data,
            data_y,
            cmap=cmap,
            space=space,
            figsize=figsize,
            title=title,
            annot=annot,
            fmt=fmt,
            threshold=threshold,
            directed=directed,
            group_labels=group_labels,
            group_colors=group_colors,
            show_legend=show_legend,
            fontsize=fontsize,
            linewidth=linewidth,
            method=method,
            columns_x=columns_x,
            columns_y=columns_y,
            matrix_type=matrix_type,
            style=style,
            **kwargs,
        )
    else:
        # Single dataset or other plot types
        return _create_single_dataset_plot(
            data,
            kind=kind_match,
            cmap=cmap,
            space=space,
            figsize=figsize,
            title=title,
            annot=annot,
            fmt=fmt,
            threshold=threshold,
            directed=directed,
            group_labels=group_labels,
            group_colors=group_colors,
            show_legend=show_legend,
            fontsize=fontsize,
            linewidth=linewidth,
            method=method,
            columns_x=columns_x,
            matrix_type=matrix_type,
            style=style,
            **kwargs,
        )


def stackplot(
    data: pd.DataFrame,
    kind: str = "area",
    normalize: bool = False,
    y_axis_percent: bool = False,
    sort_by: Optional[str] = None,  # "row", "column", or None
    ascending: bool = False,
    figsize: tuple = (14, 6),
    palette: Optional[str] = "tab20",
    alpha: float = 0.85,
    linewidth: float = 0,
    legend: bool = True,
    title_legend:str = None,
    ax: Optional[plt.Axes] = None,
    apply_pivot:bool= False,
    index_col: Optional[str] = None,      # x-axis grouping
    group_col: Optional[str] = None,      # stack categories
    value_col: Optional[str] = None,      # values to plot
    aggfunc: str = 'mean',
    **kwargs,
):
    """
    A versatile stackplot function supporting:
    - 'area': matplotlib stackplot
    - 'bar' : stacked bar chart
    """
    if run_once_within(10):
        print("""
data = generate_test_data("mix", n=100)
print(data.head(3))
nexttile = subplot(2, 3, figsize=[7, 5])

ax = nexttile()
stackplot(
    data=data,
    kind="bar",
    ax=nexttile(1, 2),
    normalize=True,
    aggfunc="sum",
    apply_pivot= True,# auto
    figsets=dict(
        fontsize=8,
        xlim=[-0.3, 2.3],
        sp=5,
        ylim=[0, 1],
        yticks=np.arange(0, 1.1, 0.25),
        legend=dict(title="markers", loc=2, bbox_to_anchor=(1.05, 1)),
        # xangle=90,
        yperc=1,
    ),
)
              """)
    kws_figsets = kwargs.pop("figsets", {})
    if ax is None:
        ax=plt.gca()
    df_plot = data.copy() 

    if (index_col is not None) and (group_col is not None) and (value_col is not None):
        # user explicitly specified long format
        if df_plot.duplicated(subset=[index_col, group_col]).any():
            df_plot = df_plot.pivot_table(
                index=index_col, columns=group_col, values=value_col, aggfunc=aggfunc
            )
        else:
            df_plot = df_plot.pivot(index=index_col, columns=group_col, values=value_col)
    elif apply_pivot:
        # auto-detect long format
        if df_plot.shape[1] >= 3:
            # separate numeric and categorical columns
            numeric_cols = df_plot.select_dtypes(include=np.number).columns.tolist()
            categorical_cols = df_plot.select_dtypes(exclude=np.number).columns.tolist()
            
            if len(numeric_cols) == 0 or len(categorical_cols) < 2:
                # fallback: treat as wide
                pass
            else:
                val = numeric_cols[0]  # pick first numeric column as value
                idx, grp = categorical_cols[:2]  # pick first two categoricals as index/group
                print(f"[stackplot] Auto-detected long format: index='{idx}', group='{grp}', value='{val}'")
                if df_plot.duplicated(subset=[idx, grp]).any():
                    df_plot = df_plot.pivot_table(
                        index=idx, columns=grp, values=val, aggfunc=aggfunc
                    )
                else:
                    df_plot = df_plot.pivot(index=idx, columns=grp, values=val)

        # wide-format assumed, do nothing

    if normalize and aggfunc=='sum':
        df_plot = df_plot.div(df_plot.sum(axis=1), axis=0)
    if normalize and aggfunc != "sum":
        print(f"Warning: Normalizing a pivot table aggregated with '{aggfunc}' may be misleading.")


    # Sorting
    sort_by = strcmp(sort_by, ["row", "column"])[0]
    if sort_by == "row":
        df_plot = df_plot.loc[
            df_plot.sum(axis=1).sort_values(ascending=ascending).index
        ]
    elif sort_by == "column":
        df_plot = df_plot.loc[
            :, df_plot.sum(axis=0).sort_values(ascending=ascending).index
        ]

    # AREA style
    if kind == "area":
        x = np.arange(len(df_plot))
        y = df_plot.values.T
        colors = get_color(n=df_plot.shape[1], cmap=palette)

        # stackplot on the provided axis
        ax.stackplot(
            x,
            y,
            labels=df_plot.columns,
            colors=colors,
            alpha=alpha,
            linewidth=linewidth,
            **kwargs,
        )
        figsets(ax, **kws_figsets)
        try:
            ax.set_xticks(x)
            ax.set_xticklabels(df_plot.index)
        except:
            pass
        if y_axis_percent:
            import matplotlib.ticker as mtick

            ax.set_ylabel("Percentage")
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))  # 0–1 -> 0–100%

        if legend:
            ax.legend(bbox_to_anchor=(1.05, 1),title=title_legend)
        return ax
    # BAR style
    elif kind == "bar":
        df_plot.plot(kind="bar", stacked=True, colormap=palette, ax=ax, **kwargs) 
        if y_axis_percent:
            import matplotlib.ticker as mtick

            ax.set_ylabel("Percentage")
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))  # 0–1 -> 0–100%

        if legend:
            ax.legend(bbox_to_anchor=(1.05, 1), title=title_legend)
        figsets(ax, **kws_figsets)
        return ax
    else:
        raise ValueError("kind must be 'area' or 'bar'.")
@decorators.Timer()
def catplot(data, *args, **kwargs):
    """
    catplot(data, opt=None, ax=None)
    The catplot function is designed to provide a flexible way to create various types of
    categorical plots. It supports multiple plot layers such as bars, error bars, scatter
    plots, box plots, violin plots, and lines. Each plot type is handled by its own internal
    function, allowing for separation of concerns and modularity in the design.
    Args:
        data (array): data matrix
    """
    from matplotlib.colors import to_rgba
    import os

    def plot_bars(data, data_m, opt_b, xloc, ax, label=None):
        if "l" in opt_b["loc"]:
            xloc_s = xloc - opt_b["x_dist"]
        elif "r" in opt_b["loc"]:
            xloc_s = xloc + opt_b["x_dist"]
        elif "i" in opt_b["loc"]:
            xloc_s = xloc
            xloc_s[:, 0] += opt_b["x_dist"]
            xloc_s[:, -1] -= opt_b["x_dist"]
        elif "o" in opt_b["loc"]:
            xloc_s = xloc
            xloc_s[:, 0] -= opt_b["x_dist"]
            xloc_s[:, -1] += opt_b["x_dist"]
        elif "c" in opt_b["loc"] or "m" in opt_b["loc"]:
            xloc_s = xloc
        else:
            xloc_s = xloc

        bar_positions = get_positions(
            xloc_s, opt_b["loc"], opt_b["x_width"], data.shape[0]
        )
        bar_positions = np.nanmean(bar_positions, axis=0)
        for i, (x, y) in enumerate(zip(bar_positions, data_m)):
            color = to_rgba(opt_b["FaceColor"][i % len(opt_b["FaceColor"])])
            if label is not None and i < len(label):
                ax.bar(
                    x,
                    y,
                    width=opt_b["x_width"],
                    color=color,
                    edgecolor=opt_b["EdgeColor"],
                    alpha=opt_b["FaceAlpha"],
                    linewidth=opt_b["LineWidth"],
                    hatch=opt_b["hatch"],
                    label=label[i],
                )
            else:
                ax.bar(
                    x,
                    y,
                    width=opt_b["x_width"],
                    color=color,
                    edgecolor=opt_b["EdgeColor"],
                    alpha=opt_b["FaceAlpha"],
                    linewidth=opt_b["LineWidth"],
                    hatch=opt_b["hatch"],
                )

    def plot_errors(data, data_m, opt_e, xloc, ax, label=None):
        error_positions = get_positions(
            xloc, opt_e["loc"], opt_e["x_dist"], data.shape[0]
        )
        error_positions = np.nanmean(error_positions, axis=0)
        errors = np.nanstd(data, axis=0, ddof=1)
        if opt_e["error"] == "sem":
            errors /= np.sqrt(np.sum(~np.isnan(data), axis=0))
        if opt_e["LineStyle"] != "none":
            # draw lines
            ax.plot(
                error_positions,
                data_m,
                color=opt_e["LineColor"],
                linestyle=opt_e["LineStyle"],
                linewidth=opt_e["LineWidth"],
                alpha=opt_e["LineAlpha"],
            )

        if not isinstance(opt_e["FaceColor"], list):
            opt_e["FaceColor"] = [opt_e["FaceColor"]]
        if not isinstance(opt_e["MarkerEdgeColor"], list):
            opt_e["MarkerEdgeColor"] = [opt_e["MarkerEdgeColor"]]
        for i, (x, y, err) in enumerate(zip(error_positions, data_m, errors)):
            if label is not None and i < len(label):
                if opt_e["MarkerSize"] == "auto":
                    ax.errorbar(
                        x,
                        y,
                        yerr=err,
                        fmt=opt_e["Marker"],
                        ecolor=opt_e["LineColor"],
                        elinewidth=opt_e["LineWidth"],
                        lw=opt_e["LineWidth"],
                        ls=opt_e["LineStyle"],
                        capsize=opt_e["CapSize"],
                        capthick=opt_e["CapLineWidth"],
                        mec=opt_e["MarkerEdgeColor"][i % len(opt_e["MarkerEdgeColor"])],
                        mfc=opt_e["FaceColor"][i % len(opt_e["FaceColor"])],
                        visible=opt_e["Visible"],
                        label=label[i],
                    )
                else:
                    ax.errorbar(
                        x,
                        y,
                        yerr=err,
                        fmt=opt_e["Marker"],
                        ecolor=opt_e["LineColor"],
                        elinewidth=opt_e["LineWidth"],
                        lw=opt_e["LineWidth"],
                        ls=opt_e["LineStyle"],
                        capsize=opt_e["CapSize"],
                        capthick=opt_e["CapLineWidth"],
                        markersize=opt_e["MarkerSize"],
                        mec=opt_e["MarkerEdgeColor"][i % len(opt_e["MarkerEdgeColor"])],
                        mfc=opt_e["FaceColor"][i % len(opt_e["FaceColor"])],
                        visible=opt_e["Visible"],
                        label=label[i],
                    )
            else:
                if opt_e["MarkerSize"] == "auto":
                    ax.errorbar(
                        x,
                        y,
                        yerr=err,
                        fmt=opt_e["Marker"],
                        ecolor=opt_e["LineColor"],
                        elinewidth=opt_e["LineWidth"],
                        lw=opt_e["LineWidth"],
                        ls=opt_e["LineStyle"],
                        capsize=opt_e["CapSize"],
                        capthick=opt_e["CapLineWidth"],
                        mec=opt_e["MarkerEdgeColor"][i % len(opt_e["MarkerEdgeColor"])],
                        mfc=opt_e["FaceColor"][i % len(opt_e["FaceColor"])],
                        visible=opt_e["Visible"],
                    )
                else:
                    ax.errorbar(
                        x,
                        y,
                        yerr=err,
                        fmt=opt_e["Marker"],
                        ecolor=opt_e["LineColor"],
                        elinewidth=opt_e["LineWidth"],
                        lw=opt_e["LineWidth"],
                        ls=opt_e["LineStyle"],
                        capsize=opt_e["CapSize"],
                        capthick=opt_e["CapLineWidth"],
                        markersize=opt_e["MarkerSize"],
                        mec=opt_e["MarkerEdgeColor"][i % len(opt_e["MarkerEdgeColor"])],
                        mfc=opt_e["FaceColor"][i % len(opt_e["FaceColor"])],
                        visible=opt_e["Visible"],
                    )

    def plot_scatter(data, opt_s, xloc, ax, label=None):
        if "l" in opt_s["loc"]:
            xloc_s = xloc - opt_s["x_dist"]
        elif "r" in opt_s["loc"]:
            xloc_s = xloc + opt_s["x_dist"]
        elif "i" in opt_s["loc"]:
            xloc_s = xloc
            xloc_s[:, 0] += opt_s["x_dist"]
            xloc_s[:, -1] -= opt_s["x_dist"]
        elif "o" in opt_s["loc"]:
            xloc_s = xloc
            xloc_s[:, 0] -= opt_s["x_dist"]
            xloc_s[:, -1] += opt_s["x_dist"]
        elif "c" in opt_s["loc"] or "m" in opt_s["loc"]:
            xloc_s = xloc
        else:
            xloc_s = xloc

        scatter_positions = get_positions(
            xloc_s, opt_s["loc"], opt_s["x_width"], data.shape[0]
        )
        for i, (x, y) in enumerate(zip(scatter_positions.T, data.T)):
            color = to_rgba(opt_s["FaceColor"][i % len(opt_s["FaceColor"])])
            if label is not None and i < len(label):
                ax.scatter(
                    x,
                    y,
                    color=color,
                    alpha=opt_s["FaceAlpha"],
                    edgecolor=opt_s["MarkerEdgeColor"],
                    s=opt_s["MarkerSize"],
                    marker=opt_s["Marker"],
                    linewidths=opt_s["LineWidth"],
                    cmap=opt_s["cmap"],
                    label=label[i],
                )
            else:
                ax.scatter(
                    x,
                    y,
                    color=color,
                    alpha=opt_s["FaceAlpha"],
                    edgecolor=opt_s["MarkerEdgeColor"],
                    s=opt_s["MarkerSize"],
                    marker=opt_s["Marker"],
                    linewidths=opt_s["LineWidth"],
                    cmap=opt_s["cmap"],
                )

    def plot_boxplot(data, bx_opt, xloc, ax, label=None):
        if "l" in bx_opt["loc"]:
            X_bx = xloc - bx_opt["x_dist"]
        elif "r" in bx_opt["loc"]:
            X_bx = xloc + bx_opt["x_dist"]
        elif "i" in bx_opt["loc"]:
            X_bx = xloc
            X_bx[:, 0] += bx_opt["x_dist"]
            X_bx[:, -1] -= bx_opt["x_dist"]
        elif "o" in bx_opt["loc"]:
            X_bx = xloc
            X_bx[:, 0] -= bx_opt["x_dist"]
            X_bx[:, -1] += bx_opt["x_dist"]
        elif "c" in bx_opt["loc"] or "m" in bx_opt["loc"]:
            X_bx = xloc
        else:
            X_bx = xloc

        boxprops = dict(color=bx_opt["EdgeColor"], linewidth=bx_opt["BoxLineWidth"])
        flierprops = dict(
            marker=bx_opt["OutlierMarker"],
            markerfacecolor=bx_opt["OutlierFaceColor"],
            markeredgecolor=bx_opt["OutlierEdgeColor"],
            markersize=bx_opt["OutlierSize"],
        )
        whiskerprops = dict(
            linestyle=bx_opt["WhiskerLineStyle"],
            color=bx_opt["WhiskerLineColor"],
            linewidth=bx_opt["WhiskerLineWidth"],
        )
        capprops = dict(
            color=bx_opt["CapLineColor"],
            linewidth=bx_opt["CapLineWidth"],
        )
        medianprops = dict(
            linestyle=bx_opt["MedianLineStyle"],
            color=bx_opt["MedianLineColor"],
            linewidth=bx_opt["MedianLineWidth"],
        )
        meanprops = dict(
            linestyle=bx_opt["MeanLineStyle"],
            color=bx_opt["MeanLineColor"],
            linewidth=bx_opt["MeanLineWidth"],
        )
        # MeanLine or MedianLine only keep only one
        if bx_opt["MeanLine"]:  # MeanLine has priority
            bx_opt["MedianLine"] = False
        # rm NaNs
        cleaned_data = [data[~np.isnan(data[:, i]), i] for i in range(data.shape[1])]

        bxp = ax.boxplot(
            cleaned_data,
            positions=X_bx,
            notch=bx_opt["Notch"],
            patch_artist=True,
            boxprops=boxprops,
            flierprops=flierprops,
            whiskerprops=whiskerprops,
            capwidths=bx_opt["CapSize"],
            showfliers=bx_opt["Outliers"],
            showcaps=bx_opt["Caps"],
            capprops=capprops,
            medianprops=medianprops,
            meanline=bx_opt["MeanLine"],
            showmeans=bx_opt["MeanLine"],
            meanprops=meanprops,
            widths=bx_opt["x_width"],
            label=label,
        )
        if not bx_opt["MedianLine"]:
            for median in bxp["medians"]:
                median.set_visible(False)

        if bx_opt["BoxLineWidth"] < 0.1:
            bx_opt["EdgeColor"] = "none"
        else:
            bx_opt["EdgeColor"] = bx_opt["EdgeColor"]
        if not isinstance(bx_opt["FaceColor"], list):
            bx_opt["FaceColor"] = [bx_opt["FaceColor"]]
        if len(bxp["boxes"]) != len(bx_opt["FaceColor"]) and (
            len(bx_opt["FaceColor"]) == 1
        ):
            bx_opt["FaceColor"] = bx_opt["FaceColor"] * len(bxp["boxes"])
        for patch, color in zip(bxp["boxes"], bx_opt["FaceColor"]):
            patch.set_facecolor(to_rgba(color, bx_opt["FaceAlpha"]))

        if bx_opt["MedianLineTop"]:
            ax.set_children(ax.get_children()[::-1])  # move median line forward

    def plot_violin(data, opt_v, xloc, ax, label=None, vertical=True):
        violin_positions = get_positions(
            xloc, opt_v["loc"], opt_v["x_dist"], data.shape[0]
        )
        violin_positions = np.nanmean(violin_positions, axis=0)
        for i, (x, ys) in enumerate(zip(violin_positions, data.T)):
            ys = ys[~np.isnan(ys)]
            if np.all(ys == ys[0]):  # Check if data is constant
                print(
                    "Data is constant; KDE cannot be applied. Plotting a flat line instead."
                )
                if vertical:
                    ax.plot(
                        [x - opt_v["x_width"] / 2, x + opt_v["x_width"] / 2],
                        [ys[0], ys[0]],
                        color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                        lw=2,
                        label=label[i] if label else None,
                    )
                else:
                    ax.plot(
                        [ys[0], ys[0]],
                        [x - opt_v["x_width"] / 2, x + opt_v["x_width"] / 2],
                        color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                        lw=2,
                        label=label[i] if label else None,
                    )
            else:
                from scipy.stats import gaussian_kde

                kde = gaussian_kde(ys, bw_method=opt_v["BandWidth"])
                min_val, max_val = ys.min(), ys.max()
                y_vals = np.linspace(min_val, max_val, opt_v["NumPoints"])
                kde_vals = kde(y_vals)
                kde_vals = kde_vals / kde_vals.max() * opt_v["x_width"]
                if label is not None and i < len(label):
                    if len(ys) > 1:
                        if "r" in opt_v["loc"].lower():
                            ax.fill_betweenx(
                                y_vals,
                                x,
                                x + kde_vals,
                                color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                                alpha=opt_v["FaceAlpha"],
                                edgecolor=opt_v["EdgeColor"],
                                label=label[i],
                                lw=opt_v["LineWidth"],
                                hatch=(
                                    opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                    if opt_v["hatch"] is not None
                                    else None
                                ),
                            )
                        elif (
                            "l" in opt_v["loc"].lower()
                            and not "f" in opt_v["loc"].lower()
                        ):
                            ax.fill_betweenx(
                                y_vals,
                                x - kde_vals,
                                x,
                                color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                                alpha=opt_v["FaceAlpha"],
                                edgecolor=opt_v["EdgeColor"],
                                label=label[i],
                                lw=opt_v["LineWidth"],
                                hatch=(
                                    opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                    if opt_v["hatch"] is not None
                                    else None
                                ),
                            )
                        elif (
                            "o" in opt_v["loc"].lower()
                            or "both" in opt_v["loc"].lower()
                        ):
                            ax.fill_betweenx(
                                y_vals,
                                x - kde_vals,
                                x + kde_vals,
                                color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                                alpha=opt_v["FaceAlpha"],
                                edgecolor=opt_v["EdgeColor"],
                                label=label[i],
                                lw=opt_v["LineWidth"],
                                hatch=(
                                    opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                    if opt_v["hatch"] is not None
                                    else None
                                ),
                            )
                        elif "i" in opt_v["loc"].lower():
                            if i % 2 == 1:  # odd number
                                ax.fill_betweenx(
                                    y_vals,
                                    x - kde_vals,
                                    x,
                                    color=opt_v["FaceColor"][
                                        i % len(opt_v["FaceColor"])
                                    ],
                                    alpha=opt_v["FaceAlpha"],
                                    edgecolor=opt_v["EdgeColor"],
                                    label=label[i],
                                    lw=opt_v["LineWidth"],
                                    hatch=(
                                        opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                        if opt_v["hatch"] is not None
                                        else None
                                    ),
                                )
                            else:
                                ax.fill_betweenx(
                                    y_vals,
                                    x,
                                    x + kde_vals,
                                    color=opt_v["FaceColor"][
                                        i % len(opt_v["FaceColor"])
                                    ],
                                    alpha=opt_v["FaceAlpha"],
                                    edgecolor=opt_v["EdgeColor"],
                                    label=label[i],
                                    lw=opt_v["LineWidth"],
                                    hatch=(
                                        opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                        if opt_v["hatch"] is not None
                                        else None
                                    ),
                                )
                        elif "f" in opt_v["loc"].lower():
                            ax.fill_betweenx(
                                y_vals,
                                x - kde_vals,
                                x + kde_vals,
                                color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                                alpha=opt_v["FaceAlpha"],
                                edgecolor=opt_v["EdgeColor"],
                                label=label[i],
                                lw=opt_v["LineWidth"],
                                hatch=(
                                    opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                    if opt_v["hatch"] is not None
                                    else None
                                ),
                            )
                else:
                    if "r" in opt_v["loc"].lower():
                        ax.fill_betweenx(
                            y_vals,
                            x,
                            x + kde_vals,
                            color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                            alpha=opt_v["FaceAlpha"],
                            edgecolor=opt_v["EdgeColor"],
                            lw=opt_v["LineWidth"],
                            hatch=(
                                opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                if opt_v["hatch"] is not None
                                else None
                            ),
                        )
                    elif (
                        "l" in opt_v["loc"].lower() and not "f" in opt_v["loc"].lower()
                    ):
                        ax.fill_betweenx(
                            y_vals,
                            x - kde_vals,
                            x,
                            color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                            alpha=opt_v["FaceAlpha"],
                            edgecolor=opt_v["EdgeColor"],
                            lw=opt_v["LineWidth"],
                            hatch=(
                                opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                if opt_v["hatch"] is not None
                                else None
                            ),
                        )
                    elif "o" in opt_v["loc"].lower() or "both" in opt_v["loc"].lower():
                        ax.fill_betweenx(
                            y_vals,
                            x - kde_vals,
                            x + kde_vals,
                            color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                            alpha=opt_v["FaceAlpha"],
                            edgecolor=opt_v["EdgeColor"],
                            lw=opt_v["LineWidth"],
                            hatch=(
                                opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                if opt_v["hatch"] is not None
                                else None
                            ),
                        )
                    elif "i" in opt_v["loc"].lower():
                        if i % 2 == 1:  # odd number
                            ax.fill_betweenx(
                                y_vals,
                                x - kde_vals,
                                x,
                                color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                                alpha=opt_v["FaceAlpha"],
                                edgecolor=opt_v["EdgeColor"],
                                lw=opt_v["LineWidth"],
                                hatch=(
                                    opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                    if opt_v["hatch"] is not None
                                    else None
                                ),
                            )
                        else:
                            ax.fill_betweenx(
                                y_vals,
                                x,
                                x + kde_vals,
                                color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                                alpha=opt_v["FaceAlpha"],
                                edgecolor=opt_v["EdgeColor"],
                                lw=opt_v["LineWidth"],
                                hatch=(
                                    opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                    if opt_v["hatch"] is not None
                                    else None
                                ),
                            )
                    elif "f" in opt_v["loc"].lower():
                        ax.fill_betweenx(
                            y_vals,
                            x - kde_vals,
                            x + kde_vals,
                            color=opt_v["FaceColor"][i % len(opt_v["FaceColor"])],
                            alpha=opt_v["FaceAlpha"],
                            edgecolor=opt_v["EdgeColor"],
                            lw=opt_v["LineWidth"],
                            hatch=(
                                opt_v["hatch"][i % len(opt_v["FaceColor"])]
                                if opt_v["hatch"] is not None
                                else None
                            ),
                        )

    def plot_ridgeplot(data, x, y, opt_r, **kwargs_figsets):
        # in the sns.FacetGrid class, the 'hue' argument is the one that is the one that will be represented by colors with 'palette'
        if opt_r["column4color"] is None:
            column4color = x
        else:
            column4color = opt_r["column4color"]

        if opt_r["row_labels"] is None:
            opt_r["row_labels"] = data[x].unique().tolist()

        if isinstance(opt_r["FaceColor"], str):
            opt_r["FaceColor"] = [opt_r["FaceColor"]]
        if len(opt_r["FaceColor"]) == 1:
            opt_r["FaceColor"] = np.tile(
                opt_r["FaceColor"], [1, len(opt_r["row_labels"])]
            )[0]
        if len(opt_r["FaceColor"]) > len(opt_r["row_labels"]):
            opt_r["FaceColor"] = opt_r["FaceColor"][: len(opt_r["row_labels"])]

        g = sns.FacetGrid(
            data=data,
            row=x,
            hue=column4color,
            aspect=opt_r["aspect"],
            height=opt_r["subplot_height"],
            palette=opt_r["FaceColor"],
        )

        # kdeplot
        g.map(
            sns.kdeplot,
            y,
            bw_adjust=opt_r["bw_adjust"],
            clip_on=opt_r["clip"],
            fill=opt_r["fill"],
            alpha=opt_r["FaceAlpha"],
            linewidth=opt_r["EdgeLineWidth"],
        )

        # edge / line of kdeplot
        if opt_r["EdgeColor"] is not None:
            g.map(
                sns.kdeplot,
                y,
                bw_adjust=opt_r["bw_adjust"],
                clip_on=opt_r["clip"],
                color=opt_r["EdgeColor"],
                lw=opt_r["EdgeLineWidth"],
            )
        else:
            g.map(
                sns.kdeplot,
                y,
                bw_adjust=opt_r["bw_adjust"],
                clip_on=opt_r["clip"],
                color=opt_r["EdgeColor"],
                lw=opt_r["EdgeLineWidth"],
            )

        # add a horizontal line
        if opt_r["xLineColor"] is not None:
            g.map(
                plt.axhline,
                y=0,
                lw=opt_r["xLineWidth"],
                clip_on=opt_r["clip"],
                color=opt_r["xLineColor"],
            )
        else:
            g.map(
                plt.axhline,
                y=0,
                lw=opt_r["xLineWidth"],
                clip_on=opt_r["clip"],
            )

        if isinstance(opt_r["color_row_label"], str):
            opt_r["color_row_label"] = [opt_r["color_row_label"]]
        if len(opt_r["color_row_label"]) == 1:
            opt_r["color_row_label"] = np.tile(
                opt_r["color_row_label"], [1, len(opt_r["row_labels"])]
            )[0]

        # loop over the FacetGrid figure axes (g.axes.flat)
        for i, ax in enumerate(g.axes.flat):
            if kwargs_figsets.get("xlim", False):
                ax.set_xlim(kwargs_figsets.get("xlim", False))
            if kwargs_figsets.get("xlim", False):
                ax.set_ylim(kwargs_figsets.get("ylim", False))
            if i == 0:
                row_x = opt_r["row_label_loc_xscale"] * np.abs(
                    np.diff(ax.get_xlim())
                ) + np.min(ax.get_xlim())
                row_y = opt_r["row_label_loc_yscale"] * np.abs(
                    np.diff(ax.get_ylim())
                ) + np.min(ax.get_ylim())
                ax.set_title(kwargs_figsets.get("title", ""))
            ax.text(
                row_x,
                row_y,
                opt_r["row_labels"][i],
                fontweight=opt_r["fontweight"],
                fontsize=opt_r["fontsize"],
                color=opt_r["color_row_label"][i],
            )
            figsets(**kwargs_figsets)

        # we use matplotlib.Figure.subplots_adjust() function to get the subplots to overlap
        g.fig.subplots_adjust(hspace=opt_r["subplot_hspace"])

        # eventually we remove axes titles, yticks and spines
        g.set_titles("")
        g.set(yticks=[])
        g.set(ylabel=opt_r["subplot_ylabel"])
        # if kwargs_figsets:
        #     g.set(**kwargs_figsets)
        if kwargs_figsets.get("xlim", False):
            g.set(xlim=kwargs_figsets.get("xlim", False))
        g.despine(bottom=True, left=True)

        plt.setp(
            ax.get_xticklabels(),
            fontsize=opt_r["fontsize"],
            fontweight=opt_r["fontweight"],
        )
        # if opt_r["ylabel"] is None:
        #     opt_r["ylabel"] = y
        # plt.xlabel(
        #     opt_r["ylabel"], fontweight=opt_r["fontweight"], fontsize=opt_r["fontsize"]
        # )
        return g, opt_r

    def plot_lines(data, opt_l, opt_s, ax):
        if "l" in opt_s["loc"]:
            xloc_s = xloc - opt_s["x_dist"]
        elif "r" in opt_s["loc"]:
            xloc_s = xloc + opt_s["x_dist"]
        elif "i" in opt_s["loc"]:
            xloc_s = xloc
            xloc_s[:, 0] += opt_s["x_dist"]
            xloc_s[:, -1] -= opt_s["x_dist"]
        elif "o" in opt_s["loc"]:
            xloc_s = xloc
            xloc_s[:, 0] -= opt_s["x_dist"]
            xloc_s[:, -1] += opt_s["x_dist"]
        elif "c" in opt_s["loc"] or "m" in opt_s["loc"]:
            xloc_s = xloc
        else:
            xloc_s = xloc

        scatter_positions = get_positions(
            xloc_s, opt_s["loc"], opt_s["x_width"], data.shape[0]
        )
        for incol in range(data.shape[1] - 1):
            for irow in range(data.shape[0]):
                if not np.isnan(data[irow, incol]):
                    if (
                        opt_l["LineStyle"] is not None
                        and not opt_l["LineStyle"] == "none"
                    ):
                        x_data = [
                            scatter_positions[irow, incol],
                            scatter_positions[irow, incol + 1],
                        ]
                        y_data = [data[irow, incol], data[irow, incol + 1]]

                        ax.plot(
                            x_data,
                            y_data,
                            color=opt_l["LineColor"],
                            linestyle=opt_l["LineStyle"],
                            linewidth=opt_l["LineWidth"],
                            alpha=opt_l["LineAlpha"],
                        )

    def get_positions(xloc, loc_type, x_width, n_row=None):
        if "rand" in loc_type:
            scatter_positions = np.zeros((n_row, len(xloc)))
            np.random.seed(111)
            for i, x in enumerate(xloc):
                scatter_positions[:, i] = np.random.uniform(
                    x - x_width, x + x_width, n_row
                )
            return scatter_positions
        elif "l" in loc_type:
            return np.tile(xloc - x_width, (n_row, 1))
        elif "r" in loc_type and not "d" in loc_type:
            return np.tile(xloc + x_width, (n_row, 1))
        elif "i" in loc_type:
            return np.tile(
                np.concatenate([xloc[:1] + x_width, xloc[1:-1], xloc[-1:] - x_width]),
                (n_row, 1),
            )
        elif "o" in loc_type:
            return np.tile(
                np.concatenate([xloc[:1] - x_width, xloc[1:-1], xloc[-1:] + x_width]),
                (n_row, 1),
            )
        else:
            return np.tile(xloc, (n_row, 1))

    def sort_catplot_layers(custom_order, full_order=["b", "bx", "e", "v", "s", "l"]):
        """
        sort layers
        """
        if "r" in full_order:
            return ["r"]
        # Ensure custom_order is a list of strings
        custom_order = [str(layer) for layer in custom_order]
        j = 1
        layers = list(range(len(full_order)))
        for i in range(len(full_order)):
            if full_order[i] not in custom_order:
                layers[i] = i
            else:
                layers[i] = None
        j = 0
        for i in range(len(layers)):
            if layers[i] is None:
                full_order[i] = custom_order[j]
                j += 1
        return full_order
        # # Example usage:
        # custom_order = ['s', 'bx', 'e']
        # full_order = sort_catplot_layers(custom_order)
    data=data.copy()
    ax = kwargs.get("ax", None)
    col = kwargs.get("col", None)
    report = kwargs.get("report", True)
    vertical = kwargs.get("vertical", True)
    stats_subgroup = kwargs.get("stats_subgroup", True)
    if not col:
        kw_figsets = kwargs.get("figsets", None)
        # check the data type
        if isinstance(data, pd.DataFrame):
            df = data.copy()
            x = kwargs.get("x", None)
            y = kwargs.get("y", None)
            hue = kwargs.get("hue", None) 
            data = df2array(data=data, x=x, y=y, hue=hue)
            
            y_max_loc = np.max(data, axis=0)
            xticklabels = []
            if hue is not None:
                # for i in df[x].unique().tolist():
                #     for j in df[hue].unique().tolist():
                #         xticklabels.append(i + "-" + j)
                for i in df[x].unique().tolist():
                    xticklabels.append(i)
                x_len = len(df[x].unique().tolist())
                hue_len = len(df[hue].unique().tolist())
                xticks = generate_xticks_with_gap(x_len, hue_len)
                xticks_x_loc = generate_xticks_x_labels(x_len, hue_len)
                default_x_width = 0.85
                legend_hue = df[hue].unique().tolist()
                default_colors = get_color(hue_len)

                # ! stats info
                stats_param = kwargs.get("stats", False)
                res = pd.DataFrame()  # Initialize an empty DataFrame to store results
                ihue = 1
                for i in df[x].unique().tolist():
                    # print(i)  # to indicate which 'x'
                    if hue and stats_param:
                        if stats_subgroup:
                            data_temp = df[df[x] == i]
                            hue_labels = data_temp[hue].unique().tolist()
                            if isinstance(stats_param, dict):
                                if len(hue_labels) > 2:
                                    if "factor" in stats_param.keys():
                                        res_tmp = FuncMultiCmpt(
                                            data=data_temp, dv=y, **stats_param
                                        )
                                    else:
                                        res_tmp = FuncMultiCmpt(
                                            data=data_temp,
                                            dv=y,
                                            factor=hue,
                                            **stats_param,
                                        )
                                elif bool(stats_param):
                                    res_tmp = FuncMultiCmpt(
                                        data=data_temp, dv=y, factor=hue
                                    )
                                else:
                                    res_tmp = "did not work properly"
                                display_output(res_tmp)
                                res = pd.concat(
                                    [res, pd.DataFrame([res_tmp])],
                                    ignore_index=True,
                                    axis=0,
                                )
                            else:
                                if isinstance(stats_param, dict):
                                    pmc = stats_param.get("pmc", "pmc")
                                    pair = stats_param.get("pair", "unpaired")
                                else:
                                    pmc = "pmc"
                                    pair = "unpair"

                                res_tmp = FuncCmpt(
                                    x1=data_temp.loc[
                                        data_temp[hue] == hue_labels[0], y
                                    ].tolist(),
                                    x2=data_temp.loc[
                                        data_temp[hue] == hue_labels[1], y
                                    ].tolist(),
                                    pmc=pmc,
                                    pair=pair,
                                )
                                display_output(res_tmp)
                        else:
                            if isinstance(stats_param, dict):
                                if len(xticklabels) > 2:
                                    if "factor" in stats_param.keys():
                                        res_tmp = FuncMultiCmpt(
                                            data=df, dv=y, **stats_param
                                        )
                                    else:
                                        res_tmp = FuncMultiCmpt(
                                            data=df[df[x] == i],
                                            dv=y,
                                            factor=hue,
                                            **stats_param,
                                        )
                                elif bool(stats_param):
                                    res_tmp = FuncMultiCmpt(
                                        data=df[df[x] == i], dv=y, factor=hue
                                    )
                                else:
                                    res_tmp = "did not work properly"
                                display_output(res_tmp)
                                res = pd.concat(
                                    [res, pd.DataFrame([res_tmp])],
                                    ignore_index=True,
                                    axis=0,
                                )
                            else:
                                if isinstance(stats_param, dict):
                                    pmc = stats_param.get("pmc", "pmc")
                                    pair = stats_param.get("pair", "unpaired")
                                else:
                                    pmc = "pmc"
                                    pair = "unpair"

                                data_temp = df[df[x] == i]
                                hue_labels = data_temp[hue].unique().tolist()
                                res_tmp = FuncCmpt(
                                    x1=data_temp.loc[
                                        data_temp[hue] == hue_labels[0], y
                                    ].tolist(),
                                    x2=data_temp.loc[
                                        data_temp[hue] == hue_labels[1], y
                                    ].tolist(),
                                    pmc=pmc,
                                    pair=pair,
                                )
                                display_output(res_tmp)
                    ihue += 1

            else:
                # ! stats info
                stats_param = kwargs.get("stats", False)
                for i in df[x].unique().tolist():
                    xticklabels.append(i)
                xticks = np.arange(1, len(xticklabels) + 1).tolist()
                xticks_x_loc = np.arange(1, len(xticklabels) + 1).tolist()
                legend_hue = xticklabels
                default_colors = get_color(len(xticklabels))
                default_x_width = 0.5
                res = None
                if x and stats_param:
                    if isinstance(stats_param, dict):
                        if len(xticklabels) > 2:
                            res = FuncMultiCmpt(data=df, dv=y, factor=x, **stats_param)
                        else:
                            res = FuncCmpt(
                                x1=df.loc[df[x] == xticklabels[0], y].tolist(),
                                x2=df.loc[df[x] == xticklabels[1], y].tolist(),
                                **stats_param,
                            )
                    elif bool(stats_param):
                        if len(xticklabels) > 2:
                            res = FuncMultiCmpt(data=df, dv=y, factor=x)
                        else:
                            res = FuncCmpt(
                                x1=df.loc[df[x] == xticklabels[0], y].tolist(),
                                x2=df.loc[df[x] == xticklabels[1], y].tolist(),
                            )
                    else:
                        res = "did not work properly"
                display_output(res)

            # when the xticklabels are too long, rotate the labels a bit
            try:
                xangle = 30 if max([len(i) for i in xticklabels]) > 50 else 0
            except:
                xangle = 0

            if kw_figsets is not None:
                kw_figsets = {
                    "ylabel": y,
                    # "xlabel": x,
                    "xticks": xticks_x_loc,  # xticks,
                    "xticklabels": xticklabels,
                    "xangle": xangle,
                    **kw_figsets,
                }
            else:
                kw_figsets = {
                    "ylabel": y,
                    # "xlabel": x,
                    "xticks": xticks_x_loc,  # xticks,
                    "xticklabels": xticklabels,
                    "xangle": xangle,
                }
        else:
            if isinstance(data, np.ndarray):
                df = array2df(data)
                x = "group"
                y = "value"
            xticklabels = []
            stats_param = kwargs.get("stats", False)
            for i in df[x].unique().tolist():
                xticklabels.append(i)
            xticks = np.arange(1, len(xticklabels) + 1).tolist()
            xticks_x_loc = np.arange(1, len(xticklabels) + 1).tolist()
            legend_hue = xticklabels
            default_colors = get_color(len(xticklabels),alpha=0.5)
            default_x_width = 0.5
            res = None
            if x and stats_param:
                if isinstance(stats_param, dict):
                    res = FuncMultiCmpt(data=df, dv=y, factor=x, **stats_param)
                elif bool(stats_param):
                    res = FuncMultiCmpt(data=df, dv=y, factor=x)
                else:
                    res = "did not work properly"
            display_output(res)

        # full_order
        opt = kwargs.get("opt", {})

        # load style:
        style_use = None
        for k, v in kwargs.items():
            if "style" in k and "exp" not in k:
                style_use = v
                break
        if style_use is not None:
            try:
                dir_curr_script = os.path.dirname(os.path.abspath(__file__))
                dir_style = dir_curr_script + "/data/styles/"
                if isinstance(style_use, str):
                    style_load = fload(dir_style + style_use + ".json")
                else:
                    style_load = fload(
                        listdir(dir_style, "json", verbose=False).path.tolist()[
                            style_use
                        ]
                    )
                style_load = remove_colors_in_dict(style_load)
                opt.update(style_load)
            except:
                print(f"cannot find the style'{style_use}'")

        color_custom = kwargs.get("c", default_colors)
        if not isinstance(color_custom, list):
            color_custom = list(color_custom)
        # if len(color_custom) < data.shape[1]:
        #     color_custom.extend(get_color(data.shape[1]-len(color_custom),cmap='tab20'))
        opt.setdefault("c", color_custom)

        opt.setdefault("loc", {})
        opt["loc"].setdefault("go", 0)
        opt["loc"].setdefault("xloc", xticks)

        # export setting
        opt.setdefault("style", {})
        opt.setdefault("layer", ["b", "bx", "e", "v", "s", "l"])

        opt.setdefault("b", {})
        opt["b"].setdefault("go", 1)
        opt["b"].setdefault("loc", "c")
        opt["b"].setdefault("FaceColor", color_custom)
        opt["b"].setdefault("FaceAlpha", 1)
        opt["b"].setdefault("EdgeColor", "k")
        opt["b"].setdefault("EdgeAlpha", 1)
        opt["b"].setdefault("LineStyle", "-")
        opt["b"].setdefault("LineWidth", 0.8)
        opt["b"].setdefault("x_width", default_x_width)
        opt["b"].setdefault("x_dist", opt["b"]["x_width"])
        opt["b"].setdefault("ShowBaseLine", "off")
        opt["b"].setdefault("hatch", None)

        opt.setdefault("e", {})
        opt["e"].setdefault("go", 1)
        opt["e"].setdefault("loc", "l")
        opt["e"].setdefault("LineWidth", 2)
        opt["e"].setdefault("CapLineWidth", 1)
        opt["e"].setdefault("CapSize", 2)
        opt["e"].setdefault("Marker", "none")
        opt["e"].setdefault("LineStyle", "none")
        opt["e"].setdefault("LineColor", "k")
        opt["e"].setdefault("LineAlpha", 0.5)
        opt["e"].setdefault("LineJoin", "round")
        opt["e"].setdefault("MarkerSize", "auto")
        opt["e"].setdefault("FaceColor", color_custom)
        opt["e"].setdefault("MarkerEdgeColor", "none")
        opt["e"].setdefault("Visible", True)
        opt["e"].setdefault("Orientation", "vertical")
        opt["e"].setdefault("error", "sem")
        opt["e"].setdefault("x_width", default_x_width / 5)
        opt["e"].setdefault("x_dist", opt["e"]["x_width"])
        opt["e"].setdefault("cap_dir", "b")

        opt.setdefault("s", {})
        opt["s"].setdefault("go", 1)
        opt["s"].setdefault("loc", "r")
        opt["s"].setdefault("FaceColor", color_custom)
        opt["s"].setdefault("cmap", None)
        opt["s"].setdefault("FaceAlpha", 1)
        opt["s"].setdefault("x_width", default_x_width / 5 * 0.5)
        opt["s"].setdefault("x_dist", opt["s"]["x_width"])
        opt["s"].setdefault("Marker", "o")
        opt["s"].setdefault("MarkerSize", 15)
        opt["s"].setdefault("LineWidth", 0.8)
        opt["s"].setdefault("MarkerEdgeColor", "k")

        opt.setdefault("l", {})
        opt["l"].setdefault("go", 0)
        opt["l"].setdefault("LineStyle", "-")
        opt["l"].setdefault("LineColor", "k")
        opt["l"].setdefault("LineWidth", 0.5)
        opt["l"].setdefault("LineAlpha", 0.5)

        opt.setdefault("bx", {})
        opt["bx"].setdefault("go", 0)
        opt["bx"].setdefault("loc", "r")
        opt["bx"].setdefault("FaceColor", color_custom)
        opt["bx"].setdefault("EdgeColor", "k")
        opt["bx"].setdefault("FaceAlpha", 0.85)
        opt["bx"].setdefault("EdgeAlpha", 1)
        opt["bx"].setdefault("LineStyle", "-")
        opt["bx"].setdefault("x_width", default_x_width / 5)
        opt["bx"].setdefault("x_dist", opt["bx"]["x_width"])
        opt["bx"].setdefault("ShowBaseLine", "off")
        opt["bx"].setdefault("Notch", False)
        opt["bx"].setdefault("Outliers", "on")
        opt["bx"].setdefault("OutlierMarker", "+")
        opt["bx"].setdefault("OutlierFaceColor", "r")
        opt["bx"].setdefault("OutlierEdgeColor", "k")
        opt["bx"].setdefault("OutlierSize", 6)
        # opt['bx'].setdefault('PlotStyle', 'traditional')
        # opt['bx'].setdefault('FactorDirection', 'auto')
        opt["bx"].setdefault("LineWidth", 0.5)
        opt["bx"].setdefault("Whisker", opt["bx"]["LineWidth"])
        opt["bx"].setdefault("Orientation", "vertical")
        opt["bx"].setdefault("BoxLineWidth", opt["bx"]["LineWidth"])
        opt["bx"].setdefault("FaceColor", "k")
        opt["bx"].setdefault("WhiskerLineStyle", "-")
        opt["bx"].setdefault("WhiskerLineColor", "k")
        opt["bx"].setdefault("WhiskerLineWidth", opt["bx"]["LineWidth"])
        opt["bx"].setdefault("Caps", True)
        opt["bx"].setdefault("CapLineColor", "k")
        opt["bx"].setdefault("CapLineWidth", opt["bx"]["LineWidth"])
        opt["bx"].setdefault("CapSize", 0.2)
        opt["bx"].setdefault("MedianLine", True)
        opt["bx"].setdefault("MedianLineStyle", "-")
        opt["bx"].setdefault("MedianStyle", "line")
        opt["bx"].setdefault("MedianLineColor", "k")
        opt["bx"].setdefault("MedianLineWidth", opt["bx"]["LineWidth"] * 4)
        opt["bx"].setdefault("MedianLineTop", False)
        opt["bx"].setdefault("MeanLine", False)
        opt["bx"].setdefault("showmeans", opt["bx"]["MeanLine"])
        opt["bx"].setdefault("MeanLineStyle", "-")
        opt["bx"].setdefault("MeanLineColor", "w")
        opt["bx"].setdefault("MeanLineWidth", opt["bx"]["LineWidth"] * 4)

        # Violin plot options
        opt.setdefault("v", {})
        opt["v"].setdefault("go", 0)
        opt["v"].setdefault("x_width", 0.3)
        opt["v"].setdefault("x_dist", opt["v"]["x_width"])
        opt["v"].setdefault("loc", "r")
        opt["v"].setdefault("EdgeColor", "none")
        opt["v"].setdefault("LineWidth", 0.5)
        opt["v"].setdefault("FaceColor", color_custom)
        opt["v"].setdefault("FaceAlpha", 1)
        opt["v"].setdefault("BandWidth", "scott")
        opt["v"].setdefault("Function", "pdf")
        opt["v"].setdefault("Kernel", "gau")
        opt["v"].setdefault("hatch", None)
        opt["v"].setdefault("NumPoints", 500)
        opt["v"].setdefault("BoundaryCorrection", "reflection")

        # ridgeplot
        opt.setdefault("r", {})
        opt["r"].setdefault("go", 0)
        opt["r"].setdefault("bw_adjust", 1)
        opt["r"].setdefault("clip", False)
        opt["r"].setdefault("FaceColor", get_color(20))
        opt["r"].setdefault("FaceAlpha", 1)
        opt["r"].setdefault("EdgeLineWidth", 1.5)
        opt["r"].setdefault("fill", True)
        opt["r"].setdefault("EdgeColor", "none")
        opt["r"].setdefault("xLineWidth", opt["r"]["EdgeLineWidth"] + 0.5)
        opt["r"].setdefault("xLineColor", "none")
        opt["r"].setdefault("aspect", 8)
        opt["r"].setdefault("subplot_hspace", -0.3)  # overlap subplots
        opt["r"].setdefault("subplot_height", 0.75)
        opt["r"].setdefault("subplot_ylabel", "")
        opt["r"].setdefault("column4color", None)
        opt["r"].setdefault("row_labels", None)
        opt["r"].setdefault("row_label_loc_xscale", 0.01)
        opt["r"].setdefault("row_label_loc_yscale", 0.05)
        opt["r"].setdefault("fontweight", plt.rcParams["font.weight"])
        opt["r"].setdefault("fontsize", plt.rcParams["font.size"])
        opt["r"].setdefault("color_row_label", "k")
        opt["r"].setdefault("ylabel", None)

        data_m = np.nanmean(data, axis=0)
        nr, nc = data.shape

        for key in kwargs.keys():
            if key in opt:
                if isinstance(kwargs[key], dict):
                    opt[key].update(kwargs[key])
                else:
                    opt[key] = kwargs[key]
        if isinstance(opt["loc"]["xloc"], list):
            xloc = np.array(opt["loc"]["xloc"])
        else:
            xloc = opt["loc"]["xloc"]
        if opt["r"]["go"]:
            layers = sort_catplot_layers(opt["layer"], "r")
        else:
            layers = sort_catplot_layers(opt["layer"])

        if ("ax" not in locals() or ax is None) and not opt["r"]["go"]:
            ax = plt.gca()
        label = kwargs.get("label", "bar")
        if label:
            if "b" in label:
                legend_which = "b"
            elif "s" in label:
                legend_which = "s"
            elif "bx" in label:
                legend_which = "bx"
            elif "e" in label:
                legend_which = "e"
            elif "v" in label:
                legend_which = "v"
        else:
            legend_which = None
        for layer in layers:
            if layer == "b" and opt["b"]["go"]:
                if legend_which == "b":
                    plot_bars(data, data_m, opt["b"], xloc, ax, label=legend_hue)
                else:
                    plot_bars(data, data_m, opt["b"], xloc, ax, label=None)
            elif layer == "e" and opt["e"]["go"]:
                if legend_which == "e":
                    plot_errors(data, data_m, opt["e"], xloc, ax, label=legend_hue)
                else:
                    plot_errors(data, data_m, opt["e"], xloc, ax, label=None)
            elif layer == "s" and opt["s"]["go"]:
                if legend_which == "s":
                    plot_scatter(data, opt["s"], xloc, ax, label=legend_hue)
                else:
                    plot_scatter(data, opt["s"], xloc, ax, label=None)
            elif layer == "bx" and opt["bx"]["go"]:
                if legend_which == "bx":
                    plot_boxplot(data, opt["bx"], xloc, ax, label=legend_hue)
                else:
                    plot_boxplot(data, opt["bx"], xloc, ax, label=None)
            elif layer == "v" and opt["v"]["go"]:
                if legend_which == "v":
                    plot_violin(
                        data, opt["v"], xloc, ax, label=legend_hue, vertical=vertical
                    )
                else:
                    plot_violin(data, opt["v"], xloc, ax, vertical=vertical, label=None)
            elif layer == "r" and opt["r"]["go"]:
                kwargs_figsets = kwargs.get("figsets", None)
                if x and y:
                    if kwargs_figsets:
                        plot_ridgeplot(df, x, y, opt["r"], **kwargs_figsets)
                    else:
                        plot_ridgeplot(df, x, y, opt["r"])
            elif all([layer == "l", opt["l"]["go"], opt["s"]["go"]]):
                plot_lines(data, opt["l"], opt["s"], ax)

        if kw_figsets is not None and not opt["r"]["go"]:
            figsets(ax=ax, **kw_figsets)
        show_legend = kwargs.get("show_legend", True)
        if show_legend and not opt["r"]["go"]:
            ax.legend()
        # ! add asterisks in the plot
        if stats_param:
            if len(xticklabels) >= 1:
                if hue is None:
                    add_asterisks(
                        ax,
                        res,
                        xticks_x_loc,
                        xticklabels,
                        y_loc=np.nanmax(data),
                        report_go=report,
                    )
                else:  # hue is not None
                    ihue = 1
                    for i in df[x].unique().tolist():
                        data_temp = df[df[x] == i]
                        hue_labels = data_temp[hue].unique().tolist()
                        if stats_param:
                            if len(hue_labels) > 2:
                                if isinstance(stats_param, dict):
                                    if "factor" in stats_param.keys():
                                        res_tmp = FuncMultiCmpt(
                                            data=df, dv=y, **stats_param
                                        )
                                    else:
                                        res_tmp = FuncMultiCmpt(
                                            data=df[df[x] == i],
                                            dv=y,
                                            factor=hue,
                                            **stats_param,
                                        )
                                elif bool(stats_param):
                                    res_tmp = FuncMultiCmpt(
                                        data=df[df[x] == i], dv=y, factor=hue
                                    )
                                else:
                                    res_tmp = "did not work properly"
                                xloc_curr = hue_len * (ihue - 1)

                                add_asterisks(
                                    ax,
                                    res_tmp,
                                    xticks[xloc_curr : xloc_curr + hue_len],
                                    legend_hue,
                                    y_loc=np.nanmax(data),
                                    report_go=report,
                                )
                            else:
                                if isinstance(stats_param, dict):
                                    pmc = stats_param.get("pmc", "pmc")
                                    pair = stats_param.get("pair", "unpaired")
                                else:
                                    pmc = "pmc"
                                    pair = "unpair"
                                res_tmp = FuncCmpt(
                                    x1=data_temp.loc[
                                        data_temp[hue] == hue_labels[0], y
                                    ].tolist(),
                                    x2=data_temp.loc[
                                        data_temp[hue] == hue_labels[1], y
                                    ].tolist(),
                                    pmc=pmc,
                                    pair=pair,
                                )
                                xloc_curr = hue_len * (ihue - 1)
                                add_asterisks(
                                    ax,
                                    res_tmp,
                                    xticks[xloc_curr : xloc_curr + hue_len],
                                    legend_hue,
                                    y_loc=np.nanmax(data),
                                    report_go=report,
                                )
                        ihue += 1
            else:  # 240814: still has some bugs
                if isinstance(res, dict):
                    tab_res = pd.DataFrame(res[1], index=[0])
                    x1 = df.loc[df[x] == xticklabels[0], y].tolist()
                    x2 = df.loc[df[x] == xticklabels[1], y].tolist()
                    tab_res[f"{xticklabels[0]}(mean±sem)"] = [str_mean_sem(x1)]
                    tab_res[f"{xticklabels[1]}(mean±sem)"] = [str_mean_sem(x2)]
                    add_asterisks(
                        ax,
                        res[1],
                        xticks_x_loc,
                        xticklabels,
                        y_loc=np.max([x1, x2]),
                        report_go=report,
                    )
                elif isinstance(res, pd.DataFrame):
                    display(res)
                    print("still has some bugs")
                    x1 = df.loc[df[x] == xticklabels[0], y].tolist()
                    x2 = df.loc[df[x] == xticklabels[1], y].tolist()
                    add_asterisks(
                        ax,
                        res,
                        xticks_x_loc,
                        xticklabels,
                        y_loc=np.max([x1, x2]),
                        report_go=report,
                    )

        style_export = kwargs.get("style_export", None)
        if style_export and (style_export != style_use):
            dir_curr_script = os.path.dirname(os.path.abspath(__file__))
            dir_style = dir_curr_script + "/data/styles/"
            fsave(dir_style + style_export + ".json", opt)

        return ax, opt
    else:
        col_names = data[col].unique().tolist()
        nrow, ncol = kwargs.get("subplots", [len(col_names), 1])
        figsize = kwargs.get("figsize", [3 * ncol, 3 * nrow])
        fig, axs = plt.subplots(nrow, ncol, figsize=figsize, squeeze=False)
        axs = axs.flatten()
        key2rm = ["data", "ax", "col", "subplots"]
        for k2rm in key2rm:
            if k2rm in kwargs:
                del kwargs[k2rm]
        for i, ax in enumerate(axs):
            # ax = axs[i][0] if len(col_names) > 1 else axs[0]
            if i < len(col_names):
                df_sub = data.loc[data[col] == col_names[i]]
                _, opt = catplot(ax=ax, data=df_sub, **kwargs)
                ax.set_title(f"{col}={col_names[i]}")
                x_label = kwargs.get("x", None)
                if x_label:
                    ax.set_xlabel(x_label)
        print(f"Axis layout shape: {axs.shape}")
        return axs, opt

def read_mplstyle(style_file):
    """
    example usage:
    style_file = "/ std-colors.mplstyle"
    style_dict = read_mplstyle(style_file)
    """
    # Load the style file
    plt.style.use(style_file)

    # Get the current style properties
    style_dict = plt.rcParams

    # Convert to dictionary
    style_dict = dict(style_dict)
    # Print the style dictionary
    for i, j in style_dict.items():
        print(f"\n{i}::::{j}")
    return style_dict

def get_color(
    *args,
    n: int = 1,
    cmap: str = "auto",
    by: str = "start",
    alpha: float = 1.0,
    reverse: bool = False,
    output: str = "hue",
    verbose: bool = False,
    **kwargs,
):
    from cycler import cycler

    def cmap2hex(cmap_name):
        cmap_ = matplotlib.pyplot.get_cmap(cmap_name)
        colors = [cmap_(i) for i in range(cmap_.N)]
        return [matplotlib.colors.rgb2hex(color) for color in colors]
        # usage: clist = cmap2hex("viridis")

    # Cycle times, total number is n (default n=10)
    def cycle2list(colorlist, n=10):
        cycler_ = cycler(tmp=colorlist)
        clist = []
        for i, c_ in zip(range(n), cycler_()):
            clist.append(c_["tmp"])
            if i > n:
                break
        return clist

    # Converts hexadecimal color codes to RGBA values
    def hue2rgb(hex_colors, alpha=1.0):
        def hex_to_rgba(hex_color, alpha=1.0):
            """Converts a hexadecimal color code to RGBA values."""
            if hex_color.startswith("#"):
                hex_color = hex_color.lstrip("#")
            rgb = tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
            return rgb + (alpha,)

        if isinstance(hex_colors, str):
            return hex_to_rgba(hex_colors, alpha)
        elif isinstance(hex_colors, list):
            """Converts a list of hexadecimal color codes to a list of RGBA values."""
            rgba_values = [hex_to_rgba(hex_color, alpha) for hex_color in hex_colors]
            return rgba_values

    def rgba2hue(rgba_color):
        if len(rgba_color) == 3:
            r, g, b = rgba_color
            a = 1
        else:
            r, g, b, a = rgba_color
        # Convert each component to a scale of 0-255
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        a = int(a * 255)
        if a < 255:
            return "#{:02X}{:02X}{:02X}{:02X}".format(r, g, b, a)
        else:
            return "#{:02X}{:02X}{:02X}".format(r, g, b)
    #  auto handle args
    if len(args) > 0:
        if isinstance(args[0], str):
            cmap = args[0]
        elif isinstance(args[0], int):
            n = args[0]

    if len(args) > 1:
        # Second positional argument
        if isinstance(args[1], str):
            cmap = args[1]
        elif isinstance(args[1], int):
            n = args[1]
    if verbose:
        print(f"cmap={cmap}, n={n}")
    # sc.pl.palettes.default_20
    cmap_20 = [
        "#1f77b4",
        "#ff7f0e",
        "#279e68",
        "#d62728",
        "#aa40fc",
        "#8c564b",
        "#e377c2",
        "#b5bd61",
        "#17becf",
        "#aec7e8",
        "#ffbb78",
        "#98df8a",
        "#ff9896",
        "#c5b0d5",
        "#c49c94",
        "#f7b6d2",
        "#dbdb8d",
        "#9edae5",
        "#ad494a",
        "#8c6d31",
    ]
    # sc.pl.palettes.zeileis_28
    cmap_28 = [
        "#023fa5",
        "#7d87b9",
        "#bec1d4",
        "#d6bcc0",
        "#bb7784",
        "#8e063b",
        "#4a6fe3",
        "#8595e1",
        "#b5bbe3",
        "#e6afb9",
        "#e07b91",
        "#d33f6a",
        "#11c638",
        "#8dd593",
        "#c6dec7",
        "#ead3c6",
        "#f0b98d",
        "#ef9708",
        "#0fcfc0",
        "#9cded6",
        "#d5eae7",
        "#f3e1eb",
        "#f6c4e1",
        "#f79cd4",
        "#7f7f7f",
        "#c7c7c7",
        "#1CE6FF",
        "#336600",
    ]

    cmap_name_valid = get_valid_cmap_list()
    is_known_cmap= cmap in cmap_name_valid if isinstance(cmap, str) and cmap!="auto" else False
    cmap_valid=strcmp(cmap, cmap_name_valid)[0] if isinstance(cmap, str) and cmap!="auto" else False
    if verbose:
        print(f"is_known_cmap: {is_known_cmap}")
    # cmap correction
    if cmap == "gray":
        cmap = "grey"
    elif cmap == "20":
        cmap = cmap_20
    elif cmap == "28":
        cmap = cmap_28 
    # Determine color list based on cmap parameter
    if isinstance(cmap, str):
        if cmap=="auto":
            if n == 1:
                colorlist = ["#3A4453"]
            elif n == 2:
                colorlist = ["#3A4453", "#FF2C00"]
            elif n == 3:
                # colorlist = ["#66c2a5", "#fc8d62", "#8da0cb"]
                # colorlist = ["#288D8D", "#9F0000", "#8da0cb"]
                colorlist =  ["#3A4453","#FF2C00", "#087cf7"]
            elif n == 4:
                # colorlist = ["#FF2C00", "#087cf7", "#FBAF63", "#3C898A"]
                colorlist = ["#4a2377", "#8cc5e3", "#f55f74", "#0d7d87"]
            elif n == 5:
                colorlist = ["#FF2C00", "#459AA9", "#B25E9D", "#087cf7", "#EF8632"]
            elif n == 6:
                colorlist = [
                    "#3A4453",
                    "#91bfdb",
                    "#B25E9D",
                    "#4B8C3B",
                    "#EF8632",
                    "#1B61AC",
                ]
            elif n == 7:
                colorlist = [
                    "#7F7F7F",
                    "#459AA9",
                    "#B25E9D",
                    "#4B8C3B",
                    "#EF8632",
                    "#24578E",
                    "#FF2C00",
                ]
            elif n == 8:
                # colorlist = ['#1f77b4','#ff7f0e','#367B7F','#51B34F','#d62728','#aa40fc','#e377c2','#17becf']
                # colorlist = ["#367C7E","#51B34F","#881A11","#E9374C","#EF893C","#010072","#385DCB","#EA43E3"]
                # colorlist = [
                #     "#78BFDA",
                #     "#D52E6F",
                #     "#F7D648",
                #     "#A52D28",
                #     "#6B9F41",
                #     "#E18330",
                #     "#E18B9D",
                #     "#3C88CC",
                # ]
                colorlist = [
                    "#003a7d",
                    "#008dff",
                    "#ff7eb6",
                    "#c701ff",
                    "#4ecb8d",
                    "#ff9d3a",
                    "#f9e858",
                    "#d83034",
                ]
            elif n == 9:
                colorlist = [
                    "#1f77b4",
                    "#ff7f0e",
                    "#367B7F",
                    "#ff9896",
                    "#d62728",
                    "#aa40fc",
                    "#e377c2",
                    "#7F7F7F",
                    "#17becf",
                ]
            elif n == 10:
                colorlist = [
                    "#1f77b4",
                    "#ff7f0e",
                    "#367B7F",
                    "#ff9896",
                    "#7F7F7F",
                    "#d62728",
                    "#aa40fc",
                    "#e377c2",
                    "#375FD2",
                    "#17becf",
                ] 
            elif 10 < n <= 20:
                colorlist = cmap_20
            else:
                colorlist = cmap_28
            by = "start"
        elif is_known_cmap:
            colorlist = get_cmap(cmap_valid, n=n, reverse=reverse,alpha=alpha,return_list=True)

        elif any(["cub" in cmap.lower(), "sns" in cmap.lower()]):
            if kwargs:
                colorlist = sns.cubehelix_palette(n, **kwargs)
            else:
                colorlist = sns.cubehelix_palette(
                    n, start=0.5, rot=-0.75, light=0.85, dark=0.15, as_cmap=False
                )
            colorlist = [matplotlib.colors.rgb2hex(color) for color in colorlist]
        elif any(["hls" in cmap.lower(), "hsl" in cmap.lower()]):
            if kwargs:
                colorlist = sns.hls_palette(n, **kwargs)
            else:
                colorlist = sns.hls_palette(n)
            colorlist = [matplotlib.colors.rgb2hex(color) for color in colorlist]
        elif any(["col" in cmap.lower(), "pal" in cmap.lower()]):
            palette, desat, as_cmap = None, None, False
            if kwargs:
                for k, v in kwargs.items():
                    if "p" in k:
                        palette = v
                    elif "d" in k:
                        desat = v
                    elif "a" in k:
                        as_cmap = v
            colorlist = sns.color_palette(
                palette=palette, n_colors=n, desat=desat, as_cmap=as_cmap
            )
            colorlist = [matplotlib.colors.rgb2hex(color) for color in colorlist]
        else:
            if by == "start":
                by = "linspace"
            colorlist = cmap2hex(cmap)
    elif isinstance(cmap, list):
        colorlist = cmap
    else:
        warnings.warn(f"cmap: {cmap}")
    if verbose:
        print(f"colorlist: {colorlist}")
    # config 'by': start/begin/linspace
    if "st" in by.lower() or "be" in by.lower():
        clist = cycle2list(colorlist, n=n)
    if "l" in by.lower() or "p" in by.lower():
        clist = []
        [
            clist.append(colorlist[i])
            for i in [int(i) for i in np.linspace(0, len(colorlist) - 1, n)]
        ]

    if verbose:
        print(f"clist: {clist}")
    #  output
    if "rgb" in output.lower():
        return hue2rgb(clist, alpha)
    elif "h" in output.lower():
        hue_list = []
        [hue_list.append(color2hex(i,keep_alpha=True)) for i in clist]
        return hue_list
    else:
        raise ValueError("Invalid output type. Choose 'rgb' or 'hue'.")


def get_valid_cmap_list():
    import matplotlib
    import seaborn as sns

    # Matplotlib built-in colormaps
    mpl_maps = sorted(matplotlib.colormaps)

    # Seaborn palettes (only names that can be used as cmap)
    sns_maps = sorted(sns.palettes.SEABORN_PALETTES.keys())

    return mpl_maps + sns_maps

def get_cmap(
    colors: list = None,
    n: int = None,
    alpha: float = None,
    *,
    midpoint: float = None,
    reverse: bool = False,
    return_list: bool = False,
    verbose: bool = False,
):
    """
    Powerful and robust custom colormap generator.
    """

    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, ListedColormap
 
    if isinstance(colors, str):
        name = colors.lower()
        cmap_name_valid=get_valid_cmap_list()
        if name not in [i.lower() for i in cmap_name_valid]:
            raise ValueError(
            f"Invalid colormap name '{colors}'. Find it from these list: \n{cmap_name_valid}"
        )
        name=strcmp(name, cmap_name_valid)[0]
        try:
            if n is not None:
                cmap_ = plt.get_cmap(name, lut=n)
            else:
                cmap_ = plt.get_cmap(name)
            cmap_list = cmap_(np.linspace(0, 1, n if n else cmap_.N))
            if reverse:
                cmap_list = cmap_list[::-1]
            if alpha is not None:
                cmap_list[:, -1] = alpha
            cmap_list=cmap_list.tolist() if isinstance(cmap_list, np.ndarray) else cmap_list
            if verbose:
                print(f"1:return_list: {return_list}\n type(ListedColormap(cmap_list)):{type(cmap_list)}\ntype(ListedColormap(cmap_list)):{type(cmap_list)}")
            return  ListedColormap(cmap_list) if not return_list else cmap_list
        except Exception:
            pass

        # Try seaborn palette (converted to a colormap)
        try: 
            if n is None:
                n = 256  # default

            pal = sns.color_palette(colors, n)

            # Convert palette to RGBA
            cmap_list = []
            for rgb in pal:
                r, g, b = rgb
                a = alpha if alpha is not None else 1.0
                cmap_list.append((r, g, b, a))
            # Reverse
            if reverse:
                cmap_list = cmap_list[::-1]
            cmap_list=cmap_list.tolist() if isinstance(cmap_list, np.ndarray) else cmap_list
            if verbose:
                print(f"2:return_list: {return_list}\n type(ListedColormap(cmap_list)):{type(cmap_list)}\ntype(ListedColormap(cmap_list)):{type(cmap_list)}")
            return ListedColormap(cmap_list) if not return_list else cmap_list
        except Exception as e:
            print(e) 

        raise ValueError(
            f"Invalid colormap name '{colors}'. "
            "Not found in matplotlib or seaborn."
        ) 
    if colors is None:
        colors = ["#0f86a9", "white", "#ed8b10"]  
    if reverse:
        colors = list(colors[::-1]) 
    # convert to rgb
    colors_rgb = [color2rgb(c, alpha=alpha) for c in colors]
    if midpoint is not None:
        if midpoint<=0 or midpoint> 1:
            raise ValueError(f"'midpoint' should be 0< midpoint <1")
        n_colors = len(colors_rgb)

        # Generate positions but shift the middle index
        color_positions = np.linspace(0, 1, n_colors)
        mid_index = n_colors // 2
        color_positions[int(mid_index)] = midpoint

        # Sort by position to avoid monotonicity issues
        colors_rgb = sorted(zip(color_positions, colors_rgb), key=lambda x: x[0])

    n = n if n is not None else 512
    base_cmap = LinearSegmentedColormap.from_list("base", colors_rgb)
    colors_list = [base_cmap(i / n) for i in range(n)]

    if verbose:
        print(f"3:return_list: {return_list}\n type(ListedColormap(colors_list)):{type(colors_list)}\ntype(ListedColormap(colors_list)):{type(colors_list)}")
    return ListedColormap(colors_list) if not return_list else colors_list 


def figsets(*args, **kwargs):
    import matplotlib
    from cycler import cycler

    matplotlib.rc("text", usetex=False)

    fig = plt.gcf()
    fontsize = kwargs.get("fontsize", 11)
    plt.rcParams["font.size"] = fontsize
    fontname = kwargs.pop("fontname", "Arial")
    fontname = plt_font(fontname)  # 显示中文
    verbose=kwargs.pop("verbose",False)
    sns_themes = ["white", "whitegrid", "dark", "darkgrid", "ticks"]
    sns_contexts = ["notebook", "talk", "poster"]  # now available "paper"
    scienceplots_styles = [
        "science",
        "nature",
        "scatter",
        "ieee",
        "no-latex",
        "std-colors",
        "high-vis",
        "bright",
        "dark_background",
        "science",
        "high-vis",
        "vibrant",
        "muted",
        "retro",
        "grid",
        "high-contrast",
        "light",
        "cjk-tc-font",
        "cjk-kr-font",
    ]
    if verbose:
        print("""
        from py2ls.ips import *
        from py2ls.plot import *
        ax=plotxy(data=generate_test_data("mix",200),  hue="Cluster",kind_='box',x='Group',y='y')
        
        figsets(ax,
                # style="notebook", # set styles; need to re-run it to make it applied
                font_size=12, # set global fontsize
                label_loc="rt",# set axis label position: l:left; r:right; t:top; b: bottom
                xlabel="custom x-label",# set xlabel
                ylabel="custom y-label",# set ylabel
                tick_loc=["xnone"], # "xticklabelnont","xticknone","xtickoff","xticklabeloff","all"/"both","xnone"/"xoff"/"none"; "ynone"/"yoff"/"none"; 
                minor_tick="x",# minor ticks 'ON': ["both", ":", "all", "a", "b", "on"] or only 'x'/'y'
                tick_para=dict(which='major',length=10,width=3,direction="inout",ax='x',color='b',pad=25,label_size=30),  # which='major'/'minor'/'both'; direction='in'/'out'/'inout'; ax='x'/'y'/'both'
                xtick=[0,1,2,3, 4,5], # set xticks...
                ytick= range(-2,6,2), # set yticks...
                xangle=30, # or 'xrotation' set xlabel's rotation
                yangle=-90, # or 'yrotation' set ylabel's rotation 
                xlim=[-2,5], 
                ylim=[-5,5], 
                tit="titl=",# title
                suptitle="suptitle=",# super title
                # yscale="log",# "linear"/"log"/"logit"/"symlog"
                text=[
                        dict(
                            x=0,
                            y=1.8,
                            s="Wake",
                            c="k",
                            bbox=dict(facecolor="0.8", edgecolor="none", boxstyle="round,pad=0.1"),
                        ),
                        dict(
                            x=1,
                            y=1.4,
                            s="Sleep",
                            c="k",
                            bbox=dict(facecolor="0.8", edgecolor="none", boxstyle="round,pad=0.05"),
                        ),
                    ], # List: add mutiple custom text on the plot
                sp=5, # "spine", "adjust", "ad", "sp", "spi", "adj", "spines"
                sp_color="r",
                box=["l",'r','b'],# **** doesn't work
                grid=dict(which='major', color='k',ls="--",lw=1.2),
                legend=None,# remove legend,
                # colorbar_loc=[0.475, 0.15, 0.04, 0.25],# [left, bottom, width, height] [0.475, 0.15, 0.04, 0.25]
                verbose=1)
                
        plt.show()
    """)
    def set_step_1(ax, key, value):
        nonlocal fontsize, fontname
        if ("fo" in key) and (("size" in key) or ("sz" in key)):
            fontsize = value
            plt.rcParams.update(
                {
                    "font.size": fontsize,
                    "figure.titlesize": fontsize,
                    "axes.titlesize": fontsize,
                    "axes.labelsize": fontsize,
                    "xtick.labelsize": fontsize,
                    "ytick.labelsize": fontsize,
                    "legend.fontsize": fontsize,
                    "legend.title_fontsize": fontsize,
                }
            )

            # Customize tick labels
            ax.tick_params(axis="both", which="major", labelsize=fontsize)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontname(fontname)

            # Optionally adjust legend font properties if a legend is included
            if ax.get_legend():
                for text in ax.get_legend().get_texts():
                    text.set_fontsize(fontsize)
                    text.set_fontname(fontname)
        # style
        if "st" in key.lower() or "th" in key.lower():
            if isinstance(value, str):
                if (value in plt.style.available) or (value in scienceplots_styles):
                    plt.style.use(value)
                elif value in sns_themes:
                    sns.set_style(value)
                elif value in sns_contexts:
                    sns.set_context(value)
                else:
                    print(
                        f"\nWarning\n'{value}' is not a plt.style,select on below:\n{plt.style.available+sns_themes+sns_contexts+scienceplots_styles}"
                    )
            if isinstance(value, list):
                for i in value:
                    if (i in plt.style.available) or (i in scienceplots_styles):
                        plt.style.use(i)
                    elif i in sns_themes:
                        sns.set_style(i)
                    elif i in sns_contexts:
                        sns.set_context(i)
                    else:
                        print(
                            f"\nWarning\n'{i}' is not a plt.style,select on below:\n{plt.style.available+sns_themes+sns_contexts+scienceplots_styles}"
                        )
        # xlabel, ylabel
        if "la" in key.lower():
            if "loc" in key.lower() or "po" in key.lower():
                for i in value:
                    if "l" in i.lower() and not "g" in i.lower():
                        ax.yaxis.set_label_position("left")
                    if "r" in i.lower() and not "o" in i.lower():
                        ax.yaxis.set_label_position("right")
                    if "t" in i.lower() and not "l" in i.lower():
                        ax.xaxis.set_label_position("top")
                    if "b" in i.lower() and not "o" in i.lower():
                        ax.xaxis.set_label_position("bottom")
            if ("x" in key.lower()) and (
                "tic" not in key.lower() and "tk" not in key.lower()
            ):
                ax.set_xlabel(value, fontname=fontname, fontsize=fontsize)
            if ("y" in key.lower()) and (
                "tic" not in key.lower() and "tk" not in key.lower()
            ):
                ax.set_ylabel(value, fontname=fontname, fontsize=fontsize)
            if ("z" in key.lower()) and (
                "tic" not in key.lower() and "tk" not in key.lower()
            ):
                ax.set_zlabel(value, fontname=fontname, fontsize=fontsize)
        # xlabel=dict()
        if key == "xlabel" and isinstance(value, dict):
            ax.set_xlabel(**value)
        if key == "ylabel" and isinstance(value, dict):
            ax.set_ylabel(**value)
        # tick location
        if "tic" in key.lower() or "tk" in key.lower():
            if ("loc" in key.lower()) or ("po" in key.lower()):
                if verbose:
                    print("processing tick, position...")

                if isinstance(value, str):
                    value = [value]

                for i in value:
                    code = i.lower()

                    # --- hide ticks only, keep labels ---
                    if code in ["xticknone", "xtickoff"]:
                        if verbose: print("hide xticks")
                        ax.tick_params(axis="x", which="both",
                                    bottom=False, top=False)

                    if code in ["yticknone", "ytickoff"]:
                        if verbose: print("hide yticks")
                        ax.tick_params(axis="y", which="both",
                                    left=False, right=False)

                    if code in ["none", "off"]:
                        if verbose: print("hide x & y ticks")
                        ax.tick_params(axis="both", which="both",
                                    bottom=False, top=False,
                                    left=False, right=False)
                    # ----------Hide labels only------------------
                    if code in ["xticklabelnone", "xticklabeloff","xticklabelhide"]:
                        if verbose: print("hide x ticklabel")
                        ax.tick_params(axis="x", which="both",
                                    labelbottom=False)

                    if code in ["ylblhide", "ylabeloff","ylabelnone"]:
                        if verbose: print("hide yticklabel")
                        ax.tick_params(axis="y", which="both",
                                    labelleft=False)

                    # ----------Hide ticks + labels------------------
                    # X-axis OFF (ticks + labels)
                    if code in ["xnone", "xoff","none"]:
                        if verbose: print("hide xtick + xticklabel")
                        ax.tick_params(axis="x", which="both",
                                    bottom=False, top=False,
                                    labelbottom=False)
                    # Y-axis OFF (ticks + labels)
                    if code in ["ynone", "yoff","none"]:
                        if verbose: print("hide ytick + yticklabel")
                        ax.tick_params(axis="y", which="both",
                                    left=False, right=False,
                                    labelleft=False)

                    # Positions
                    if code == "l":
                        ax.yaxis.set_ticks_position("left")
                    if code == "r":
                        ax.yaxis.set_ticks_position("right")
                    if code == "t":
                        ax.xaxis.set_ticks_position("top")
                    if code == "b":
                        ax.xaxis.set_ticks_position("bottom")

                    # ALL → fully enable both ticks + labels
                    if code in ["a", "all", "both"]:
                        if verbose: print("fully enable both ticks + labels")
                        ax.tick_params(axis="both", which="both",
                                    bottom=True, top=True,
                                    left=True, right=True,
                                    labelbottom=True, labelleft=True)

            # ticks / labels
            elif "x" in key.lower():
                if value is None:
                    value = []
                if "la" not in key.lower():
                    ax.set_xticks(value)
                if "la" in key.lower():
                    ax.set_xticklabels(value)
            elif "y" in key.lower():
                if value is None:
                    value = []
                if "la" not in key.lower():
                    ax.set_yticks(value)
                if "la" in key.lower():
                    ax.set_yticklabels(value)
            elif "z" in key.lower():
                if value is None:
                    value = []
                if "la" not in key.lower():
                    ax.set_zticks(value)
                if "la" in key.lower():
                    ax.set_zticklabels(value)
        # rotation
        if "angle" in key.lower() or ("rot" in key.lower()):
            if "x" in key.lower():
                if value in [0, 90, 180, 270]:
                    ax.tick_params(axis="x", rotation=value)
                    for tick in ax.get_xticklabels():
                        tick.set_horizontalalignment("center")
                elif value > 0:
                    ax.tick_params(axis="x", rotation=value)
                    for tick in ax.get_xticklabels():
                        tick.set_horizontalalignment("right")
                elif value < 0:
                    ax.tick_params(axis="x", rotation=value)
                    for tick in ax.get_xticklabels():
                        tick.set_horizontalalignment("left")
            if "y" in key.lower():
                ax.tick_params(axis="y", rotation=value)
                for tick in ax.get_yticklabels():
                    tick.set_horizontalalignment("right")
        # box
        if "bo" in key in key:  # box setting, and ("p" in key or "l" in key):
            if isinstance(value, (str, list)): 
                locations = []
                for i in value:
                    if "l" in i.lower() and not "t" in i.lower():
                        locations.append("left")
                    if "r" in i.lower() and not "o" in i.lower():  # right
                        locations.append("right")
                    if "t" in i.lower() and not "r" in i.lower():  # top
                        locations.append("top")
                    if "b" in i.lower() and not "t" in i.lower():
                        locations.append("bottom")
                    if i.lower() in ["a", "both", "all", "al", ":"]:
                        [
                            locations.append(x)
                            for x in ["left", "right", "top", "bottom"]
                        ]
                locations=list(set(locations)) 
                if "none" in value:
                    locations = []  # hide all
                for spi in ax.spines.values():
                    spi.set_position(("outward", 0))  # force default outward
                    spi.set_color("black")

                # check spines 
                for loc, spi in ax.spines.items():  
                    if str(loc) in locations:
                        # spi.set_color("k")
                        spi.set_position(("outward", 0))
                    else:
                        spi.set_color("none")  # no spine
        # ticks
        if "tick" in key.lower():  # tick ticks tick_para ={}
            if isinstance(value, dict):
                if isinstance(value, dict) and any(
                        (k.lower().startswith("wh") and "mi" in str(val).lower()) for k, val in value.items()
                    ):
                        ax.minorticks_on() 
                for k, val in value.items(): 
                    if "wh" in k.lower():
                        ax.tick_params(
                            which=val
                        )  # {'major', 'minor', 'both'}, default: 'major'
                    elif "dir" in k.lower():
                        ax.tick_params(direction=val)  # {'in', 'out', 'inout'}
                    elif "len" in k.lower():  # length
                        ax.tick_params(length=val)
                    elif ("wid" in k.lower()) or ("wd" in k.lower()):  # width
                        ax.tick_params(width=val)
                    elif "ax" in k.lower():  # ax
                        ax.tick_params(axis=val)  # {'x', 'y', 'both'}, default: 'both'
                    elif ("c" in k.lower()) and ("ect" not in k.lower()):
                        ax.tick_params(colors=val)  # Tick color.
                    elif "pad" in k.lower() or "space" in k.lower():
                        ax.tick_params(
                            pad=val
                        )  # float, distance in points between tick and label
                    elif (
                        ("lab" in k.lower() or "text" in k.lower())
                        and ("s" in k.lower())
                        and ("z" in k.lower())
                    ):  # label_size
                        ax.tick_params(
                            labelsize=val
                        )  # float, distance in points between tick and label
        if "text" in key.lower():
            if isinstance(value, dict):
                ax.text(**value)
            elif isinstance(value, list):
                if all([isinstance(i, dict) for i in value]):
                    [ax.text(**value_) for value_ in value]

        # minorticks_on
        if "mi" in key.lower() and "tic" in key.lower():  # minor_ticks
            import matplotlib.ticker as tck

            if "x" in value.lower() or "x" in key.lower():
                ax.xaxis.set_minor_locator(tck.AutoMinorLocator())  # ax.minorticks_on()
            if "y" in value.lower() or "y" in key.lower():
                ax.yaxis.set_minor_locator(
                    tck.AutoMinorLocator()
                )  # ax.minorticks_off()
            if value.lower() in ["both", ":", "all", "a", "b", "on"]:
                ax.minorticks_on()
        if key == "colormap" or key == "cmap":
            plt.set_cmap(value)

    def set_step_2(ax, key, value):
        nonlocal fontsize, fontname
        
        if key == "figsize":
            print("not support param 'figsize'")
            pass
        if "xlim" in key.lower():
            ax.set_xlim(value)
        if "ylim" in key.lower():
            ax.set_ylim(value)
        if "zlim" in key.lower():
            ax.set_zlim(value)
        # https://matplotlib.org/stable/api/scale_api.html#builtin-scales
        if "scale" in key.lower():  # axis scale type: "linear"/"log"/"logit"/"symlog"
            
            if "x" in key.lower():
                ax.set_xscale(value)
            if "y" in key.lower():
                ax.set_yscale(value)
            if "z" in key.lower():
                ax.set_zscale(value)
        if any(i in key.lower() for i in ['percent','pct', 'perc']):
            import matplotlib.ticker as mtick
            if 'x' in key.lower():
                ax.xaxis.set_major_formatter(mtick.PercentFormatter(value)) 
            if "y" in key.lower():
                ax.yaxis.set_major_formatter(mtick.PercentFormatter(value)) 
            if "z" in key.lower():
                ax.zaxis.set_major_formatter(mtick.PercentFormatter(value)) 
        if key == "grid":
            if isinstance(value, dict):
                for k, val in value.items():
                    if "wh" in k.lower():  # which
                        ax.grid(
                            which=val
                        )  # {'major', 'minor', 'both'}, default: 'major'
                    elif "ax" in k.lower():  # ax
                        ax.grid(axis=val)  # {'x', 'y', 'both'}, default: 'both'
                    elif ("c" in k.lower()) and ("ect" not in k.lower()):  # c: color
                        ax.grid(color=val)  # Tick color.
                    elif "l" in k.lower() and ("s" in k.lower()):  # ls:line stype
                        ax.grid(linestyle=val)
                    elif "l" in k.lower() and ("w" in k.lower()):  # lw: line width
                        ax.grid(linewidth=val)
                    elif "al" in k.lower():  # alpha:
                        ax.grid(alpha=val)
            else:
                if value == "on" or value is True:
                    ax.grid(visible=True)
                elif value == "off" or value is False:
                    ax.grid(visible=False)
        if "tit" in key.lower():
            if "sup" in key.lower():
                plt.suptitle(value, fontname=fontname, fontsize=fontsize)
            else:
                ax.set_title(value, fontname=fontname, fontsize=fontsize)
        if key.lower() in ["spine", "adjust", "ad", "sp", "spi", "adj", "spines"]:
            if isinstance(value, bool) or (value in ["go", "do", "ja", "yes"]):
                if value:
                    adjust_spines(ax)  # dafault distance=2
            if isinstance(value, (float, int)):
                adjust_spines(ax=ax, distance=value)
        if "c" in key.lower() and (
            "sp" in key.lower() or "ax" in key.lower()
        ):  # spine color
            for loc, spi in ax.spines.items():
                spi.set_color(value)
        if "leg" in key.lower():  # legend
            legend_kws = kwargs.get("legend", None)
            if legend_kws:
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
                ax.legend(**legend_kws)
            else:
                legend = ax.get_legend()
                if legend is not None:
                    legend.remove()
        if (
            any(["colorbar" in key.lower(), "cbar" in key.lower()])
            and "loc" in key.lower()
        ):
            cbar = ax.collections[0].colorbar  # Access the colorbar from the plot
            cbar.ax.set_position(
                value
            )  # [left, bottom, width, height] [0.475, 0.15, 0.04, 0.25]

    for arg in args:
        if isinstance(arg, matplotlib.axes._axes.Axes):
            ax = arg
            args = args[1:]
    ax = kwargs.get("ax", plt.gca())
    if "ax" not in locals() or ax is None:
        ax = plt.gca()
    for key, value in kwargs.items():
        set_step_1(ax, key, value)
        set_step_2(ax, key, value)
    for arg in args:
        if isinstance(arg, dict):
            for k, val in arg.items():
                set_step_1(ax, k, val)
            for k, val in arg.items():
                set_step_2(ax, k, val)
        else:
            Nargin = len(args) // 2
            ax.labelFontSizeMultiplier = 1
            ax.titleFontSizeMultiplier = 1
            ax.set_facecolor("w")

            for ip in range(Nargin):
                key = args[ip * 2].lower()
                value = args[ip * 2 + 1]
                set_step_1(ax, key, value)
            for ip in range(Nargin):
                key = args[ip * 2].lower()
                value = args[ip * 2 + 1]
                set_step_2(ax, key, value)

    colors = get_color(8)
    matplotlib.rcParams["axes.prop_cycle"] = cycler(color=colors)
    if len(fig.get_axes()) > 1:
        try:
            fig.set_constrained_layout(True)# plt.tight_layout()
        except Exception as e:
            print(e)


def split_legend(ax, n=2, loc=None, title=None, bbox=None, ncol=1, **kwargs):
    """
    split_legend(
        ax,
        n=2,
        loc=["upper left", "lower right"],
        labelcolor="k",
        fontsize=6,
    )
    """
    # Retrieve all lines and labels from the axis
    handles, labels = ax.get_legend_handles_labels()
    num_labels = len(labels)

    # Calculate the number of labels per legend part
    labels_per_part = (num_labels + n - 1) // n  # Round up
    # Create a list to hold each legend object
    legends = []

    # Default locations and titles if not specified
    if loc is None:
        loc = ["best"] * n
    if title is None:
        title = [None] * n
    if bbox is None:
        bbox = [None] * n

    # Loop to create each split legend
    for i in range(n):
        # Calculate the range of labels for this part
        start_idx = i * labels_per_part
        end_idx = min(start_idx + labels_per_part, num_labels)

        # Skip if no labels in this range
        if start_idx >= end_idx:
            break

        # Subset handles and labels
        part_handles = handles[start_idx:end_idx]
        part_labels = labels[start_idx:end_idx]

        # Create the legend for this part
        legend = ax.legend(
            handles=part_handles,
            labels=part_labels,
            loc=loc[i],
            title=title[i],
            ncol=ncol,
            bbox_to_anchor=bbox[i],
            **kwargs,
        )

        # Add the legend to the axis and save it to the list
        (
            ax.add_artist(legend) if i != (n - 1) else None
        )  # the lastone will be added automaticaly
        legends.append(legend)
    return legends


def get_colors(
    n: int = 1,
    cmap: str = "auto",
    by: str = "start",
    alpha: float = 1.0,
    reverse: bool = False,
    output: str = "hue",
    *args,
    **kwargs,
):
    return get_color(n=n, cmap=cmap, alpha=alpha,reverse=reverse, output=output, *args, **kwargs)



def stdshade(ax=None, *args, **kwargs):
    """
    usage:
    plot.stdshade(data_array, c=clist[1], lw=2, ls="-.", alpha=0.2)
    """
    from scipy.signal import savgol_filter

    # Separate kws_line and kws_fill if necessary
    kws_line = kwargs.pop("kws_line", {})
    kws_fill = kwargs.pop("kws_fill", {})

    # Merge kws_line and kws_fill into kwargs
    kwargs.update(kws_line)
    kwargs.update(kws_fill)

    def str2list(str_):
        l = []
        [l.append(x) for x in str_]
        return l

    def hue2rgb(hex_colors):
        def hex_to_rgb(hex_color):
            """Converts a hexadecimal color code to RGB values."""
            if hex_colors.startswith("#"):
                hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

        if isinstance(hex_colors, str):
            return hex_to_rgb(hex_colors)
        elif isinstance(hex_colors, (list)):
            """Converts a list of hexadecimal color codes to a list of RGB values."""
            rgb_values = [hex_to_rgb(hex_color) for hex_color in hex_colors]
            return rgb_values

    if (
        isinstance(ax, np.ndarray)
        and ax.ndim == 2
        and min(ax.shape) > 1
        and max(ax.shape) > 1
    ):
        y = ax
        ax = plt.gca()
    if ax is None:
        ax = plt.gca()
    alpha = kwargs.get("alpha", 0.2)
    acolor = kwargs.get("color", "k")
    acolor = kwargs.get("c", "k")
    paraStdSem = "sem"
    plotStyle = "-"
    plotMarker = "none"
    smth = 1
    l_c_one = ["r", "g", "b", "m", "c", "y", "k", "w"]
    l_style2 = ["--", "-."]
    l_style1 = ["-", ":"]
    l_mark = ["o", "+", "*", ".", "x", "_", "|", "s", "d", "^", "v", ">", "<", "p", "h"]
    # Check each argument
    for iarg in range(len(args)):
        if (
            isinstance(args[iarg], np.ndarray)
            and args[iarg].ndim == 2
            and min(args[iarg].shape) > 1
            and max(args[iarg].shape) > 1
        ):
            y = args[iarg]
        # Except y, continuous data is 'F'
        if (isinstance(args[iarg], np.ndarray) and args[iarg].ndim == 1) or isinstance(
            args[iarg], range
        ):
            x = args[iarg]
            if isinstance(x, range):
                x = np.arange(start=x.start, stop=x.stop, step=x.step)
        # Only one number( 0~1), 'alpha' / color
        if isinstance(args[iarg], (int, float)):
            if np.size(args[iarg]) == 1 and 0 <= args[iarg] <= 1:
                alpha = args[iarg]
        if isinstance(args[iarg], (list, tuple)) and np.size(args[iarg]) == 3:
            acolor = args[iarg]
            acolor = tuple(acolor) if isinstance(acolor, list) else acolor
        # Color / plotStyle /
        if (
            isinstance(args[iarg], str)
            and len(args[iarg]) == 1
            and args[iarg] in l_c_one
        ):
            acolor = args[iarg]
        else:
            if isinstance(args[iarg], str):
                if args[iarg] in ["sem", "std"]:
                    paraStdSem = args[iarg]
                if args[iarg].startswith("#"):
                    acolor = hue2rgb(args[iarg])
                if str2list(args[iarg])[0] in l_c_one:
                    if len(args[iarg]) == 3:
                        k = [i for i in str2list(args[iarg]) if i in l_c_one]
                        if k != []:
                            acolor = k[0]
                        st = [i for i in l_style2 if i in args[iarg]]
                        if st != []:
                            plotStyle = st[0]
                    elif len(args[iarg]) == 2:
                        k = [i for i in str2list(args[iarg]) if i in l_c_one]
                        if k != []:
                            acolor = k[0]
                        mk = [i for i in str2list(args[iarg]) if i in l_mark]
                        if mk != []:
                            plotMarker = mk[0]
                        st = [i for i in l_style1 if i in args[iarg]]
                        if st != []:
                            plotStyle = st[0]
                if len(args[iarg]) == 1:
                    k = [i for i in str2list(args[iarg]) if i in l_c_one]
                    if k != []:
                        acolor = k[0]
                    mk = [i for i in str2list(args[iarg]) if i in l_mark]
                    if mk != []:
                        plotMarker = mk[0]
                    st = [i for i in l_style1 if i in args[iarg]]
                    if st != []:
                        plotStyle = st[0]
                if len(args[iarg]) == 2:
                    st = [i for i in l_style2 if i in args[iarg]]
                    if st != []:
                        plotStyle = st[0]
        # smth
        if (
            isinstance(args[iarg], (int, float))
            and np.size(args[iarg]) == 1
            and args[iarg] >= 1
        ):
            smth = args[iarg]
    smth = kwargs.get("smth", smth)
    if "x" not in locals() or x is None:
        x = np.arange(1, y.shape[1] + 1)
    elif len(x) < y.shape[1]:
        y = y[:, x]
        nRow = y.shape[0]
        nCol = y.shape[1]
        print(f"y was corrected, please confirm that {nRow} row, {nCol} col")
    else:
        x = np.arange(1, y.shape[1] + 1)

    if x.shape[0] != 1:
        x = x.T
    yMean = np.nanmean(y, axis=0)
    if smth > 1:
        yMean = savgol_filter(np.nanmean(y, axis=0), smth, 1)
    else:
        yMean = np.nanmean(y, axis=0)
    if paraStdSem == "sem":
        if smth > 1:
            wings = savgol_filter(
                np.nanstd(y, axis=0, ddof=1) / np.sqrt(y.shape[0]), smth, 1
            )
        else:
            wings = np.nanstd(y, axis=0, ddof=1) / np.sqrt(y.shape[0])
    elif paraStdSem == "std":
        if smth > 1:
            wings = savgol_filter(np.nanstd(y, axis=0, ddof=1), smth, 1)
        else:
            wings = np.nanstd(y, axis=0, ddof=1)

    # fill_kws = kwargs.get('fill_kws', {})
    # line_kws = kwargs.get('line_kws', {})

    # setting form kwargs
    lw = kwargs.get("lw", 0.5)
    ls = kwargs.get("ls", plotStyle)
    marker = kwargs.get("marker", plotMarker)
    label = kwargs.get("label", None)
    label_line = kwargs.get("label_line", None)
    label_fill = kwargs.get("label_fill", None)
    alpha = kwargs.get("alpha", alpha)
    color = kwargs.get("color", acolor)
    if not label_line and label:
        label_line = label
    kwargs["lw"] = lw
    kwargs["ls"] = ls
    kwargs["label_line"] = label_line
    kwargs["label_fill"] = label_fill

    # set kws_line
    if "color" not in kws_line:
        kws_line["color"] = color
    if "lw" not in kws_line:
        kws_line["lw"] = lw
    if "ls" not in kws_line:
        kws_line["ls"] = ls
    if "marker" not in kws_line:
        kws_line["marker"] = marker
    if "label" not in kws_line:
        kws_line["label"] = label_line

    # set kws_line
    if "color" not in kws_fill:
        kws_fill["color"] = color
    if "alpha" not in kws_fill:
        kws_fill["alpha"] = alpha
    if "lw" not in kws_fill:
        kws_fill["lw"] = 0
    if "label" not in kws_fill:
        kws_fill["label"] = label_fill

    fill = ax.fill_between(x, yMean + wings, yMean - wings, **kws_fill)
    line = ax.plot(x, yMean, **kws_line)

    # figsets
    kw_figsets = kwargs.get("figsets", None)
    if kw_figsets is not None:
        figsets(ax=ax, **kw_figsets)

    return line[0], fill


"""
########## Usage 1 ##########
plot.stdshade(data,
              'b',
              ':',
              'd',
              0.1,
              4,
              label='ddd',
              label_line='label_line',
              label_fill="label-fill")
plt.legend()

########## Usage 2 ##########
plot.stdshade(data,
              'm-',
              alpha=0.1,
              lw=2,
              ls=':',
              marker='d',
              color='b',
              smth=4,
              label='ddd',
              label_line='label_line',
              label_fill="label-fill")
plt.legend()

"""


def adjust_spines(ax=None, spines=["left", "bottom"], distance=2):
    if ax is None:
        ax = plt.gca()
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(("outward", distance))  # outward by 2 points
            # spine.set_smart_bounds(True)
        else:
            spine.set_color("none")  # don't draw spine
    # turn off ticks where there is no spine
    if "left" in spines:
        ax.yaxis.set_ticks_position("left")
    else:
        ax.yaxis.set_ticks([])
    if "bottom" in spines:
        ax.xaxis.set_ticks_position("bottom")
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])


# And then plot the data:


# def add_colorbar(im, width=None, pad=None, **kwargs):
#     # usage: add_colorbar(im, width=0.01, pad=0.005, label="PSD (dB)", shrink=0.8)
#     l, b, w, h = im.axes.get_position().bounds  # get boundaries
#     width = width or 0.1 * w  # get width of the colorbar
#     pad = pad or width  # get pad between im and cbar
#     fig = im.axes.figure  # get figure of image
#     cax = fig.add_axes([l + w + pad, b, width, h])  # define cbar Axes
#     return fig.colorbar(im, cax=cax, **kwargs)  # draw cbar


def add_colorbar(
    im,
    cmap="viridis",
    vmin=-1,
    vmax=1,
    orientation="vertical",
    width_ratio=0.05,
    pad_ratio=0.02,
    shrink=1.0,
    **kwargs,
):
    import matplotlib as mpl

    if all([cmap, vmin, vmax]):
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    else:
        norm = False
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    l, b, w, h = im.axes.get_position().bounds  # position: left, bottom, width, height
    if orientation == "vertical":
        width = width_ratio * w
        pad = pad_ratio * w
        cax = im.figure.add_axes(
            [l + w + pad, b, width, h * shrink]
        )  # Right of the image
    else:
        height = width_ratio * h
        pad = pad_ratio * h
        cax = im.figure.add_axes(
            [l, b - height - pad, w * shrink, height]
        )  # Below the image
    cbar = im.figure.colorbar(sm, cax=cax, orientation=orientation, **kwargs)
    return cbar


# Usage:
# add_colorbar(im, width_ratio=0.03, pad_ratio=0.01, orientation='horizontal', label="PSD (dB)")


def generate_xticks_with_gap(x_len, hue_len):
    """
    Generate a concatenated array based on x_len and hue_len,
    and return only the positive numbers.

    Parameters:
    - x_len: int, number of segments to generate
    - hue_len: int, length of each hue

    Returns:
    - numpy array: Concatenated array containing only positive numbers
    """

    arrays = [
        np.arange(1, hue_len + 1) + hue_len * (x_len - i) + (x_len - i)
        for i in range(max(x_len, hue_len), 0, -1)  # i iterates from 3 to 1
    ]
    concatenated_array = np.concatenate(arrays)
    positive_array = concatenated_array[concatenated_array > 0].tolist()

    return positive_array


def generate_xticks_x_labels(x_len, hue_len):
    arrays = [
        np.arange(1, hue_len + 1) + hue_len * (x_len - i) + (x_len - i)
        for i in range(max(x_len, hue_len), 0, -1)  # i iterates from 3 to 1
    ]
    return [np.mean(i) for i in arrays if np.mean(i) > 0]


def remove_colors_in_dict(
    data: dict, sections_to_remove_facecolor=["b", "e", "s", "bx", "v"]
):
    # Remove "FaceColor" from specified sections
    for section in sections_to_remove_facecolor:
        if section in data and ("FaceColor" in data[section]):
            del data[section]["FaceColor"]

    if "c" in data:
        del data["c"]
    if "loc" in data:
        del data["loc"]
    return data


def add_asterisks(ax, res, xticks_x_loc, xticklabels, **kwargs_funcstars):
    if len(xticklabels) > 2:
        if isinstance(res, dict):
            pval_groups = res["res_tab"]["p-unc"].tolist()[0]
        else:
            pval_groups = res["res_tab"]["PR(>F)"].tolist()[0]
        report_go = kwargs_funcstars.get("report_go", False)
        if pval_groups <= 0.05:
            A_list = res["res_posthoc"]["A"].tolist()
            B_list = res["res_posthoc"]["B"].tolist()
            xticklabels_array = np.array(xticklabels)
            yscal_ = 0.99
            for A, B, P in zip(
                res["res_posthoc"]["A"].tolist(),
                res["res_posthoc"]["B"].tolist(),
                res["res_posthoc"]["p-unc"].tolist(),
            ):
                index_A = np.where(xticklabels_array == A)[0][0]
                index_B = np.where(xticklabels_array == B)[0][0]
                FuncStars(
                    ax=ax,
                    x1=xticks_x_loc[index_A],
                    x2=xticks_x_loc[index_B],
                    pval=P,
                    yscale=yscal_,
                    **kwargs_funcstars,
                )
                if P <= 0.05:
                    yscal_ -= 0.075
        if report_go:
            try:
                if isinstance(res["APA"], list):
                    APA_str = res["APA"][0]
                else:
                    APA_str = res["APA"]
            except:
                pass

            FuncStars(
                ax=ax,
                x1=(
                    xticks_x_loc[0] - (xticks_x_loc[-1] - xticks_x_loc[0]) / 3
                    if xticks_x_loc[0] > 1
                    else xticks_x_loc[0]
                ),
                x2=(
                    xticks_x_loc[0] - (xticks_x_loc[-1] - xticks_x_loc[0]) / 3
                    if xticks_x_loc[0] > 1
                    else xticks_x_loc[0]
                ),
                pval=None,
                report_scale=np.random.uniform(0.7, 0.99),
                report=APA_str,
                fontsize_note=8,
            )
    else:
        if isinstance(res, tuple):
            res = res[1]
            pval_groups = res["pval"]
            FuncStars(
                ax=ax,
                x1=xticks_x_loc[0],
                x2=xticks_x_loc[1],
                pval=pval_groups,
                **kwargs_funcstars,
            )
        # else:
        #     pval_groups = res["pval"]
        #     FuncStars(
        #         ax=ax,
        #         x1=1,
        #         x2=2,
        #         pval=pval_groups,
        #         **kwargs_funcstars,
        #     )


def style_examples(
    dir_save="/Users/macjianfeng/Dropbox/github/python/py2ls/.venv/lib/python3.12/site-packages/py2ls/data/styles/example",
):
    f = listdir(
        "/Users/macjianfeng/Dropbox/github/python/py2ls/.venv/lib/python3.12/site-packages/py2ls/data/styles/",
        kind=".json",
        verbose=False,
    )
    display(f.sample(2))
    # def style_example(dir_save,)
    # Sample data creation
    np.random.seed(0)
    categories = ["A", "B", "C", "D", "E"]
    data = pd.DataFrame(
        {
            "value": np.concatenate(
                [np.random.normal(loc, 0.4, 100) for loc in range(5)]
            ),
            "category": np.repeat(categories, 100),
        }
    )
    for i in range(f.num[0]):
        plt.figure()
        _, _ = catplot(
            data=data,
            x="category",
            y="value",
            style=i,
            figsets=dict(title=f"style{i+1} or style idx={i}"),
        )
        figsave(
            dir_save,
            f"{f.name[i]}.pdf",
        )


import matplotlib.pyplot as plt
from PIL import Image


def thumbnail(dir_img_list: list, figsize=(10, 10), dpi=100, show=False, verbose=False):
    """
    Display a thumbnail figure of all images in the specified directory.

    Args:
        dir_img_list (list): List of image file paths to display.
        figsize (tuple): Size of the figure (width, height) in inches.
        dpi (int): Dots per inch for the figure.
    """
    if verbose:
        print(
            'thumbnail(listdir("./img-innere-medizin-ii", ["jpeg", "jpg", "png"]).fpath.tolist(),figsize=[5,5],dpi=200)'
        )
    num_images = len(dir_img_list)
    if num_images == 0:
        print("No images found to display.")
        return None

    # Calculate the number of rows and columns for the grid
    cols = int(num_images**0.5)
    rows = (num_images // cols) + (num_images % cols > 0)

    fig, axs = plt.subplots(rows, cols, figsize=figsize, dpi=dpi)
    axs = axs.flatten()  # Flatten the grid for easy iteration

    for ax, image_file in zip(axs, dir_img_list):
        try:
            img = Image.open(image_file)
            ax.imshow(img)
            ax.axis("off")  # Hide axes
        except (IOError, FileNotFoundError) as e:
            ax.axis("off")  # Still hide axes if image can't be loaded

    # Hide any remaining unused axes
    for ax in axs[len(dir_img_list) :]:
        ax.axis("off")

    plt.tight_layout()
    if show:
        plt.show()


def get_params_from_func_usage(function_signature):
    import re

    # Regular expression to match parameter names, ignoring '*' and '**kwargs'
    keys_pattern = r"(?<!\*\*)\b(\w+)="
    # Find all matches
    matches = re.findall(keys_pattern, function_signature)
    return matches

def generate_test_data(kind="all",n=5):

    import pandas as pd
    import numpy as np

    np.random.seed(1)

    # 1. numeric only
    df_numeric = pd.DataFrame(
        {
            "x": np.random.normal(0, 1, n),
            "y": np.random.normal(2, 1, n),
            "z": np.random.normal(-1, 1, n),
        }
    )

    # 2. mixed categorical + numeric
    df_mixed = pd.DataFrame(
        {
            "x": np.random.randn(n),
            "y": np.random.randn(n) * 2 + 1,
            "Cluster": np.random.choice(["A", "B", "C"], n),
            "Group": np.random.choice(["Control", "Treatment"], n),
        }
    )

    # 3. pure categorical
    df_cat = pd.DataFrame(
        {
            "Category": np.random.choice(["Apple", "Pear", "Banana"], n),
            "Group": np.random.choice(["G1", "G2"], n),
        }
    )

    # 4. long-format
    df_long = pd.melt(
        df_numeric.reset_index(),
        id_vars="index",
        value_vars=["x", "y", "z"],
        var_name="variable",
        value_name="value",
    )

    # 5. time-series
    dates = pd.date_range("2020-01-01", periods=n)
    df_time = pd.DataFrame(
        {
            "date": dates,
            "value": np.random.randn(n).cumsum(),
            "group": np.random.choice(["A", "B"], n),
        }
    )
    df_all = {
        "df_numeric": df_numeric,
        "df_mixed": df_mixed,
        "df_cat": df_cat,
        "df_long": df_long,
        "df_time": df_time,
    }
    if kind == "all":
        return df_all
    elif "num" in kind.lower():
        return df_numeric
    elif "cat" in kind.lower():
        return df_cat
    elif "long" in kind.lower():
        return df_long
    elif "mix" in kind.lower():
        return df_mixed
    elif "time" in kind.lower():
        return df_time
    else:
        return all
def plot_xy(
    data: pd.DataFrame = None,
    x=None,
    y=None,
    ax=None,
    kind_: Union[str, list] = None,  # Specify the kind of plot
    verbose=False,
    **kwargs,
):
    # You can call the original plotxy function if needed
    # or simply replicate the functionality here
    return plotxy(data, x=x, y=y, ax=ax, kind_=kind_, verbose=verbose, **kwargs)

@decorators.Timer()
def plotxy(
    data: pd.DataFrame = None,
    x=None,
    y=None,
    ax=None,
    kind_: Union[str, list] = "scatter",  # Specify the kind of plot
    verbose=False,
    **kwargs,
):
    """
    e.g., plotxy(data=data_log, x="Component_1", y="Component_2", hue="Cluster",kind='scater)
    Create a variety of plots based on the kind parameter.

    Parameters:
        data (pd.DataFrame): DataFrame containing the data.
        x (str): Column name for the x-axis.
        y (str): Column name for the y-axis.
        hue (str): Column name for the hue (color) grouping.
        ax: Matplotlib axes object for the plot.
        kind (str): Type of plot ('scatter', 'line', 'displot', 'kdeplot', etc.).
        verbose (bool): If True, print default settings instead of plotting.
        **kwargs: Additional keyword arguments for the plot functions.

    Returns:
        ax or FacetGrid: Matplotlib axes object or FacetGrid for displot.
    """ 

    if not "default_settings" in locals():
        default_settings = get_default_settings() #fload(current_directory / "data" / "usages_sns.json")
    if not "sns_info" in locals():
        sns_info = get_sns_info()#pd.DataFrame(fload(current_directory / "data" / "sns_info.json"))

    valid_kinds = list(default_settings.keys())
    valid_kinds.extend(["catplot_sns","stdshade"])
    if kind_:
        kind_ = [strcmp(i, valid_kinds)[0] for i in ([kind_] if isinstance(kind_, str) else kind_)]
    else:
        verbose = True

    if verbose:
        if kind_ is not None:
            for k in kind_:
                if k in valid_kinds:
                    print(f"{k}:\n\t{default_settings[k]}") if k in default_settings else None
        usage_str = """plotxy(data=ranked_genes,
        x="log2(fold_change)",
        y="-log10(p-value)",
        palette=get_color(3, cmap="coolwarm"),
        kind_=["scatter","rug"],
        kws_rug=dict(height=0.2),
        kws_scatter=dict(s=20, color=get_color(3)[2]),
        verbose=0)


        
        # catplot_sns
        plotxy(data=data,kind_="catplot_sns", verbose=1)
        
        # catplot
        plotxy(data=df_numeric,kind_="catplot", verbose=1,opt=dict(dict(l={"go":1})))
        """
        print(f"currently support to plot:\n{valid_kinds}\n\nusage:\n{usage_str}")
        # return  # Do not plot, just print the usage

    kws_figsets = kwargs.pop("figsets", {})
    kws_add_text = kwargs.pop("add_text", {})
    
    # ============ preprocess data ============
    try:
        data = df_preprocessing_(data, kind=kind_[0]) 
        if "variable" in data.columns and "value" in data.columns:
            x, y = "variable", "value"
    except Exception as e:
        print(e)
        
    sns_with_col = [
            "catplot",
            "histplot",
            "relplot",
            "lmplot",
            "pairplot",
            "displot",
            "kdeplot",
        ]

    # indicate 'col' features
    col = kwargs.get("col", None)
    if col and not any(k in sns_with_col for k in kind_):
        print(f"Warning: '{kind_}' has no 'col' param, try using {sns_with_col}")
    # Define plots that create their own figure
    plots_that_create_figure = ["jointplot", "lmplot", "catplot_sns", "displot"]
    if ax is None and not any(plot in kind_ for plot in plots_that_create_figure):
        ax = plt.gca()

    zorder = 0
    for k in kind_:
        zorder += 1
        # (1) return FcetGrid
        if k == "jointplot":
            if run_once_within(10):
                print("\n xample-data (mix):\n",generate_test_data("mix"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
            kws_joint = kwargs.pop("kws_joint", kwargs)
            kws_joint = {k: v for k, v in kws_joint.items() if not k.startswith("kws_")}
            hue = kwargs.get("hue", None)
            if (
                isinstance(kws_joint, dict) or hue is None
            ):  # Check if kws_ellipse is a dictionary
                kws_joint.pop("hue", None)  # Safely remove 'hue' if it exists

            palette = kwargs.get("palette", None)
            if palette is None:
                palette = kws_joint.pop(
                    "palette",
                    get_color(data[hue].nunique()) if hue is not None else None,
                )
            else:
                kws_joint.pop("palette", palette)
            stats = kwargs.pop("stats", None)
            if stats:
                stats = kws_joint.pop("stats", True)
            if stats:
                r, p_value = scipy_stats.pearsonr(data[x], data[y])
            for key in ["palette", "alpha", "hue", "stats"]:
                kws_joint.pop(key, None)
            g = sns.jointplot(
                data=data, x=x, y=y, hue=hue, palette=palette, **kws_joint
            )
            if stats:
                g.ax_joint.annotate(
                    f"pearsonr = {r:.2f} p = {p_value:.3f}",
                    xy=(0.6, 0.98),
                    xycoords="axes fraction",
                    fontsize=12,
                    color="black",
                    ha="center",
                )
        elif k == "lmplot":
            if run_once_within(10):
                print("\n xample-data (mix):\n",generate_test_data("mix"))
                print("""
        https://seaborn.pydata.org/generated/seaborn.lmplot.html
            This function combines regplot() and FacetGrid. It is intended as a convenient interface to fit regression models across conditional subsets of a dataset.

            Usage:
            plotxy(generate_test_data("mix",200).sort_values(["Cluster","Group"]),kind_="lm", x="x",y="y", hue="Group", col="Cluster")
            # Plot a regression fit over a scatter plot:
            sns.lmplot(data=penguins, x="bill_length_mm", y="bill_depth_mm")
            
            # Condition the regression fit on another variable and represent it using color:
            sns.lmplot(data=penguins, x="bill_length_mm", y="bill_depth_mm", hue="species")
            
            # Condition the regression fit on another variable and split across subplots:
            sns.lmplot(
                data=penguins, x="bill_length_mm", y="bill_depth_mm",
                hue="species", col="sex", height=4,
            )

            # Condition across two variables using both columns and rows:
            sns.lmplot(
                data=penguins, x="bill_length_mm", y="bill_depth_mm",
                col="species", row="sex", height=3,
            ) 

            # Allow axis limits to vary across subplots:
            sns.lmplot(
                data=penguins, x="bill_length_mm", y="bill_depth_mm",
                col="species", row="sex", height=3,
                facet_kws=dict(sharex=False, sharey=False),
            )

                      """)
            kws_lm = kwargs.pop("kws_lm", kwargs)
            stats = kwargs.pop("stats", True)  # Flag to calculate stats
            hue = kwargs.pop("hue", None)  # Get the hue argument (if any)
            col = kwargs.pop("col", None)  # Get the col argument (if any)
            row = kwargs.pop("row", None)  # Get the row argument (if any)

            # Create the linear model plot (lmplot)
            g = sns.lmplot(data=data, x=x, y=y, hue=hue, col=col, row=row, **kws_lm)

            # Compute Pearson correlation and p-value statistics
            if stats:
                stats_per_facet = {}
                stats_per_hue = {}

                # If no hue, col, or row, calculate stats for the entire dataset
                if all([hue is None, col is None, row is None]):
                    r, p_value = scipy_stats.pearsonr(data[x], data[y])
                    stats_per_facet[(None, None)] = (
                        r,
                        p_value,
                    )  # Store stats for the entire dataset

                else:
                    if hue is None and (col is not None or row is not None):
                        for ax in g.axes.flat:
                            facet_name = ax.get_title()
                            if "=" in facet_name:
                                # Assume facet_name is like 'Column = Value'
                                facet_column_name = facet_name.split("=")[
                                    0
                                ].strip()  # Column name before '='
                                facet_value_str = facet_name.split("=")[
                                    1
                                ].strip()  # Facet value after '='

                                # Try converting facet_value to match the data type of the DataFrame column
                                facet_column_dtype = data[facet_column_name].dtype
                                if (
                                    facet_column_dtype == "int"
                                    or facet_column_dtype == "float"
                                ):
                                    facet_value = pd.to_numeric(
                                        facet_value_str, errors="coerce"
                                    )  # Convert to numeric
                                else:
                                    facet_value = facet_value_str  # Treat as a string if not numeric
                            else:
                                facet_column_name = facet_name.split("=")[
                                    0
                                ].strip()  # Column name before '='
                                facet_value = facet_name.split("=")[1].strip()
                            facet_data = data[data[facet_column_name] == facet_value]
                            if not facet_data.empty:
                                r, p_value = scipy_stats.pearsonr(
                                    facet_data[x], facet_data[y]
                                )
                                stats_per_facet[facet_name] = (r, p_value)
                            else:
                                stats_per_facet[facet_name] = (
                                    None,
                                    None,
                                )  # Handle empty facets

            # Annotate the stats on the plot
            for ax in g.axes.flat:
                if stats:
                    # Adjust the position for each facet to avoid overlap
                    idx = 1
                    shift_factor = (
                        0.02 * idx
                    )  # Adjust this factor as needed to prevent overlap
                    y_position = (
                        0.98 - shift_factor
                    )  # Dynamic vertical shift for each facet

                    if all([hue is None, col is None, row is None]):
                        # Use stats for the entire dataset if no hue, col, or row
                        r, p_value = stats_per_facet.get((None, None), (None, None))
                        if r is not None and p_value is not None:
                            ax.annotate(
                                f"pearsonr = {r:.2f} p = {p_value:.3f}",
                                xy=(0.6, y_position),
                                xycoords="axes fraction",
                                fontsize=12,
                                color="black",
                                ha="center",
                            )
                        else:
                            ax.annotate(
                                "No stats available",
                                xy=(0.6, y_position),
                                xycoords="axes fraction",
                                fontsize=12,
                                color="black",
                                ha="center",
                            )
                    elif hue is not None:
                        if col is None and row is None:
                            hue_categories = sorted(flatten(data[hue], verbose=0))
                            idx = 1
                            for category in hue_categories:
                                subset_data = data[data[hue] == category]
                                r, p_value = scipy_stats.pearsonr(
                                    subset_data[x], subset_data[y]
                                )
                                stats_per_hue[category] = (r, p_value)
                                shift_factor = (
                                    0.05 * idx
                                )  # Adjust this factor as needed to prevent overlap
                                y_position = (
                                    0.98 - shift_factor
                                )  # Dynamic vertical shift for each facet
                                ax.annotate(
                                    f"{category}: pearsonr = {r:.2f} p = {p_value:.3f}",
                                    xy=(0.6, y_position),
                                    xycoords="axes fraction",
                                    fontsize=12,
                                    color="black",
                                    ha="center",
                                )
                                idx += 1
                        else:
                            for ax in g.axes.flat:
                                facet_name = ax.get_title()
                                if "=" in facet_name:
                                    # Assume facet_name is like 'Column = Value'
                                    facet_column_name = facet_name.split("=")[
                                        0
                                    ].strip()  # Column name before '='
                                    facet_value_str = facet_name.split("=")[
                                        1
                                    ].strip()  # Facet value after '='

                                    # Try converting facet_value to match the data type of the DataFrame column
                                    facet_column_dtype = data[facet_column_name].dtype
                                    if (
                                        facet_column_dtype == "int"
                                        or facet_column_dtype == "float"
                                    ):
                                        facet_value = pd.to_numeric(
                                            facet_value_str, errors="coerce"
                                        )  # Convert to numeric
                                    else:
                                        facet_value = facet_value_str  # Treat as a string if not numeric
                                else:
                                    facet_column_name = facet_name.split("=")[
                                        0
                                    ].strip()  # Column name before '='
                                    facet_value = facet_name.split("=")[1].strip()
                                facet_data = data[
                                    data[facet_column_name] == facet_value
                                ]
                                if not facet_data.empty:
                                    r, p_value = scipy_stats.pearsonr(
                                        facet_data[x], facet_data[y]
                                    )
                                    stats_per_facet[facet_name] = (r, p_value)
                                else:
                                    stats_per_facet[facet_name] = (
                                        None,
                                        None,
                                    )  # Handle empty facets

                                ax.annotate(
                                    f"pearsonr = {r:.2f} p = {p_value:.3f}",
                                    xy=(0.6, y_position),
                                    xycoords="axes fraction",
                                    fontsize=12,
                                    color="black",
                                    ha="center",
                                )
                    elif hue is None and (col is not None or row is not None):
                        # Annotate stats for each facet
                        facet_name = ax.get_title()
                        r, p_value = stats_per_facet.get(facet_name, (None, None))
                        if r is not None and p_value is not None:
                            ax.annotate(
                                f"pearsonr = {r:.2f} p = {p_value:.3f}",
                                xy=(0.6, y_position),
                                xycoords="axes fraction",
                                fontsize=12,
                                color="black",
                                ha="center",
                            )
                        else:
                            ax.annotate(
                                "No stats available",
                                xy=(0.6, y_position),
                                xycoords="axes fraction",
                                fontsize=12,
                                color="black",
                                ha="center",
                            )

        elif k == "catplot_sns":
            if run_once_within(10):
                print("\n xample-data (mix):\n",generate_test_data("mix"),"\nplotxy(data=data, kind_='catplot', x='Group', y='y', style=2, stats=1)")
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print("""
    https://seaborn.pydata.org/generated/seaborn.catplot.html
            Categorical scatterplots:
                stripplot() (with kind="strip"; the default)
                swarmplot() (with kind="swarm")

            Categorical distribution plots:
                boxplot() (with kind="box")
                violinplot() (with kind="violin")
                boxenplot() (with kind="boxen")

            Categorical estimate plots:
                pointplot() (with kind="point")
                barplot() (with kind="bar")
                countplot() (with kind="count")

    sns.catplot(
        data=df, x="age", y="class", hue="sex",
        kind="violin", bw_adjust=.5, cut=0, split=True,
    )

    sns.catplot(data=df, x="age", y="class", kind="violin", color=".9", inner=None)
    sns.swarmplot(data=df, x="age", y="class", size=3)
                      """)
            kws_cat = kwargs.pop("kws_cat", kwargs)
            g = sns.catplot(data=data, x=x, y=y, **kws_cat)
        elif k == "displot":
            if run_once_within(10): 
                print("\n xample-data (mix):\n",generate_test_data("mix"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print("""
        # While in histogram mode, it is also possible to add a KDE curve:
        sns.displot(data=penguins, x="flipper_length_mm", kde=True)

        # To draw a bivariate plot, assign both x and y:
        sns.displot(data=penguins, x="flipper_length_mm", y="bill_length_mm")

        # Currently, bivariate plots are available only for histograms and KDEs:
        sns.displot(data=penguins, x="flipper_length_mm", y="bill_length_mm", kind="kde")

        # For each kind of plot, you can also show individual observations with a marginal “rug”:
        g = sns.displot(data=penguins, x="flipper_length_mm", y="bill_length_mm", kind="kde", rug=True)

        # Each kind of plot can be drawn separately for subsets of data using hue mapping:
        sns.displot(data=penguins, x="flipper_length_mm", hue="species", kind="kde")

        # Additional keyword arguments are passed to the appropriate underlying plotting function, allowing for further customization:
        sns.displot(data=penguins, x="flipper_length_mm", hue="species", multiple="stack")
                      """)
            kws_dis = kwargs.pop("kws_dis", kwargs)
            # displot creates a new figure and returns a FacetGrid
            g = sns.displot(data=data, x=x, y=y, **kws_dis)

        if k == "catplot":
            if run_once_within(10):
                print("\n xample-data (mix):\n",generate_test_data("mix"),"\nplotxy(data=data, kind_='catplot', x='Group', y='y', style=2, stats=1)")
                print("\n xample-data (df_long):\n",generate_test_data("long"))
            kws_cat = kwargs.pop("kws_cat", kwargs)
            g = catplot(data=data, x=x, y=y, ax=ax, **kws_cat)
        elif k == "stdshade":
            kws_stdshade = kwargs.pop("kws_stdshade", kwargs)
            ax = stdshade(ax=ax, **kwargs)
        elif k == "ellipse":
            kws_ellipse = kwargs.pop("kws_ellipse", kwargs)
            kws_ellipse = {
                k: v for k, v in kws_ellipse.items() if not k.startswith("kws_")
            }
            hue = kwargs.get("hue", None)
            if (
                isinstance(kws_ellipse, dict) or hue is None
            ):  # Check if kws_ellipse is a dictionary
                kws_ellipse.pop("hue", None)  # Safely remove 'hue' if it exists

            palette = kwargs.get("palette", None)
            if palette is None:
                palette = kws_ellipse.pop(
                    "palette",
                    get_color(data[hue].nunique()) if hue is not None else None,
                )
            alpha = kws_ellipse.pop("alpha", 0.1)
            hue_order = kwargs.get("hue_order", None)
            if hue_order is None:
                hue_order = kws_ellipse.get("hue_order", None)
            if hue_order:
                data["hue"] = pd.Categorical(
                    data[hue], categories=hue_order, ordered=True
                )
                data = data.sort_values(by="hue")
            for key in ["palette", "alpha", "hue", "hue_order"]:
                kws_ellipse.pop(key, None)
            ax = ellipse(
                ax=ax,
                data=data,
                x=x,
                y=y,
                hue=hue,
                palette=palette,
                alpha=alpha,
                zorder=zorder,
                **kws_ellipse,
            )
        elif k == "scatterplot":
            if run_once_within(10):
                print("\n xample-data (df_numeric):\n",generate_test_data("num"))
                print("\n xample-data (mix):\n",generate_test_data("mix"))
                print("""
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="time")

# Assigning the same variable to style will also vary the markers and create a more accessible plot:
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="time", style="time")

# Assigning hue and style to different variables will vary colors and markers independently:
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="day", style="time")

# If the variable assigned to hue is numeric, the semantic mapping will be quantitative and use a different default palette:
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="size")

# Pass the name of a categorical palette or explicit colors (as a Python list of dictionary) to force categorical mapping of the hue variable:
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="size", palette="deep")

# If there are a large number of unique numeric values, the legend will show a representative, evenly-spaced set:
tip_rate = tips.eval("tip / total_bill").rename("tip_rate")
sns.scatterplot(data=tips, x="total_bill", y="tip", hue=tip_rate)

# A numeric variable can also be assigned to size to apply a semantic mapping to the areas of the points:
sns.scatterplot(data=tips, x="total_bill", y="tip", hue="size", size="size")

# Control the range of marker areas with sizes, and set legend="full" to force every unique value to appear in the legend:
sns.scatterplot(
    data=tips, x="total_bill", y="tip", hue="size", size="size",
    sizes=(20, 200), legend="full"
)

# Pass a tuple of values or a matplotlib.colors.Normalize object to hue_norm to control the quantitative hue mapping:
sns.scatterplot(
    data=tips, x="total_bill", y="tip", hue="size", size="size",
    sizes=(20, 200), hue_norm=(0, 7), legend="full"
)

# Control the specific markers used to map the style variable by passing a Python list or dictionary of marker codes:
markers = {"Lunch": "s", "Dinner": "X"}
sns.scatterplot(data=tips, x="total_bill", y="tip", style="time", markers=markers)

# Additional keyword arguments are passed to matplotlib.axes.Axes.scatter(), allowing you to directly set the attributes of the plot that are not semantically mapped:
sns.scatterplot(data=tips, x="total_bill", y="tip", s=100, color=".2", marker="+")

# The previous examples used a long-form dataset. When working with wide-form data, each column will be plotted against its index using both hue and style mapping:
index = pd.date_range("1 1 2000", periods=100, freq="m", name="date")
data = np.random.randn(100, 4).cumsum(axis=0)
wide_df = pd.DataFrame(data, index, ["a", "b", "c", "d"])
sns.scatterplot(data=wide_df)
                      """)
            kws_scatter = kwargs.pop("kws_scatter", kwargs)
            kws_scatter = {
                k: v for k, v in kws_scatter.items() if not k.startswith("kws_")
            }
            hue = kwargs.get("hue", None)
            if isinstance(kws_scatter, dict):  # Check if kws_scatter is a dictionary
                kws_scatter.pop("hue", None)  # Safely remove 'hue' if it exists
            palette = kws_scatter.get("palette", None)
            if palette is None:
                palette = kws_scatter.pop(
                    "palette",
                    get_color(data[hue].nunique()) if hue is not None else None,
                )
            s = kws_scatter.pop("s", 10)
            alpha = kws_scatter.pop("alpha", 0.7)
            for key in ["s", "palette", "alpha", "hue"]:
                kws_scatter.pop(key, None)
            ax = sns.scatterplot(
                ax=ax,
                data=data,
                x=x,
                y=y,
                hue=hue,
                palette=palette,
                s=s,
                alpha=alpha,
                zorder=zorder,
                **kws_scatter,
            )
        elif k == "histplot":
            if run_once_within(10):
                print("\n xample-data (df_numeric):\n",generate_test_data("num"))
                print("\n xample-data (df_mix):\n",generate_test_data("mix"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print(""" 
    https://seaborn.pydata.org/generated/seaborn.histplot.html#seaborn-histplot
    represents the distribution of one or more variables by counting the number of observations that fall within discrete bins.

    # Assign a variable to x to plot a univariate distribution along the x axis:
    penguins = sns.load_dataset("penguins")
    sns.histplot(data=penguins, x="flipper_length_mm")

    # Flip the plot by assigning the data variable to the y axis:
    sns.histplot(data=penguins, y="flipper_length_mm")

    # Check how well the histogram represents the data by specifying a different bin width:
    sns.histplot(data=penguins, x="flipper_length_mm", binwidth=3)

    # define the total number of bins to use:
    sns.histplot(data=penguins, x="flipper_length_mm", bins=30)

    # Add a kernel density estimate to smooth the histogram, providing complementary information about the shape of the distribution:
    sns.histplot(data=penguins, x="flipper_length_mm", kde=True)

    # If neither x nor y is assigned, the dataset is treated as wide-form, and a histogram is drawn for each numeric column:
    sns.histplot(data=penguins)
    # You can otherwise draw multiple histograms from a long-form dataset with hue mapping:
    sns.histplot(data=penguins, x="flipper_length_mm", hue="species")

    # The default approach to plotting multiple distributions is to “layer” them, but you can also “stack” them:
    sns.histplot(data=penguins, x="flipper_length_mm", hue="species", multiple="stack")

    # Overlapping bars can be hard to visually resolve. A different approach would be to draw a step function:
    sns.histplot(penguins, x="flipper_length_mm", hue="species", element="step")

    # You can move even farther away from bars by drawing a polygon with vertices in the center of each bin. This may make it easier to see the shape of the distribution, but use with caution: it will be less obvious to your audience that they are looking at a histogram:
    sns.histplot(penguins, x="flipper_length_mm", hue="species", element="poly")

    # To compare the distribution of subsets that differ substantially in size, use independent density normalization:
    sns.histplot(
        penguins, x="bill_length_mm", hue="island", element="step",
        stat="density", common_norm=False,
    )
    # It’s also possible to normalize so that each bar’s height shows a probability, proportion, or percent, which make more sense for discrete variables:
    tips = sns.load_dataset("tips")
    sns.histplot(data=tips, x="size", stat="percent", discrete=True)

    # You can even draw a histogram over categorical variables (although this is an experimental feature):
    sns.histplot(data=tips, x="day", shrink=.8)

    # When using a hue semantic with discrete data, it can make sense to “dodge” the levels:
    sns.histplot(data=tips, x="day", hue="sex", multiple="dodge", shrink=.8)
    # Real-world data is often skewed. For heavily skewed distributions, it’s better to define the bins in log space. Compare:
    planets = sns.load_dataset("planets")
    sns.histplot(data=planets, x="distance")

    # To the log-scale version:
    sns.histplot(data=planets, x="distance", log_scale=True)

    # There are also a number of options for how the histogram appears. You can show unfilled bars:
    sns.histplot(data=planets, x="distance", log_scale=True, fill=False)
    # Or an unfilled step function:
    sns.histplot(data=planets, x="distance", log_scale=True, element="step", fill=False)

    # Step functions, especially when unfilled, make it easy to compare cumulative histograms:
    sns.histplot(
        data=planets, x="distance", hue="method",
        hue_order=["Radial Velocity", "Transit"],
        log_scale=True, element="step", fill=False,
        cumulative=True, stat="density", common_norm=False,
    )

    # When both x and y are assigned, a bivariate histogram is computed and shown as a heatmap:
    sns.histplot(penguins, x="bill_depth_mm", y="body_mass_g")
    # It’s possible to assign a hue variable too, although this will not work well if data from the different levels have substantial overlap:
    sns.histplot(penguins, x="bill_depth_mm", y="body_mass_g", hue="species")
    # Multiple color maps can make sense when one of the variables is discrete:
    sns.histplot(
        penguins, x="bill_depth_mm", y="species", hue="species", legend=False
    )

    # The bivariate histogram accepts all of the same options for computation as its univariate counterpart, using tuples to parametrize x and y independently:
    sns.histplot(
        planets, x="year", y="distance",
        bins=30, discrete=(True, False), log_scale=(False, True),
    )

    # The default behavior makes cells with no observations transparent, although this can be disabled:
    sns.histplot(
        planets, x="year", y="distance",
        bins=30, discrete=(True, False), log_scale=(False, True),
        thresh=None,
    )

    # It’s also possible to set the threshold and colormap saturation point in terms of the proportion of cumulative counts:
    sns.histplot(
        planets, x="year", y="distance",
        bins=30, discrete=(True, False), log_scale=(False, True),
        pthresh=.05, pmax=.9,
    )

    # To annotate the colormap, add a colorbar:
    sns.histplot(
        planets, x="year", y="distance",
        bins=30, discrete=(True, False), log_scale=(False, True),
        cbar=True, cbar_kws=dict(shrink=.75),
    ) 
                """)
            kws_hist = kwargs.pop("kws_hist", kwargs)
            kws_hist = {k: v for k, v in kws_hist.items() if not k.startswith("kws_")}
            ax = sns.histplot(data=data, x=x, y=y, ax=ax, zorder=zorder, **kws_hist)
        elif k == "kdeplot":
            if run_once_within(10):
                print("\n xample-data (df_mix):\n",generate_test_data("mix"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print("""
                    https://seaborn.pydata.org/generated/seaborn.kdeplot.html
                    A kernel density estimate (KDE) plot is a method for visualizing the distribution of observations in a dataset, analogous to a histogram. KDE represents the data using a continuous probability density curve in one or more dimensions.

                    # Use less smoothing:
                    sns.kdeplot(data=tips, x="total_bill", bw_adjust=.2)
                    
                    # Use more smoothing, but don’t smooth past the extreme data points:
                    ax= sns.kdeplot(data=tips, x="total_bill", bw_adjust=5, cut=0)

                    # “Stack” the conditional distributions:
                    sns.kdeplot(data=tips, x="total_bill", hue="time", multiple="stack")

                    # Normalize the stacked distribution at each value in the grid:
                    sns.kdeplot(data=tips, x="total_bill", hue="time", multiple="fill")

                    # Use numeric hue mapping:
                    sns.kdeplot(data=tips, x="total_bill", hue="size")
                    # Modify the appearance of the plot:
                    sns.kdeplot(
                        data=tips, x="total_bill", hue="size",
                        fill=True, common_norm=False, palette="crest",
                        alpha=.5, linewidth=0,
                    )

                    # Plot a bivariate distribution:
                    sns.kdeplot(data=geyser, x="waiting", y="duration", hue="kind")
                    # filled
                    sns.kdeplot(
                        data=geyser, x="waiting", y="duration", hue="kind", fill=True,
                    )
                    # Show fewer contour levels, covering less of the distribution:
                    sns.kdeplot(
                        data=geyser, x="waiting", y="duration", hue="kind",
                        levels=5, thresh=.2,
                    )
                    # Fill the axes extent with a smooth distribution, using a different colormap:
                    sns.kdeplot(
                        data=geyser, x="waiting", y="duration",
                        fill=True, thresh=0, levels=100, cmap="mako",
                    ) 
                """)
            kws_kde = kwargs.pop("kws_kde", kwargs)
            kws_kde = {k: v for k, v in kws_kde.items() if not k.startswith("kws_")}
            hue = kwargs.get("hue", None)
            if (
                isinstance(kws_kde, dict) or hue is None
            ):  # Check if kws_kde is a dictionary
                kws_kde.pop("hue", None)  # Safely remove 'hue' if it exists

            palette = kwargs.get("palette", None)
            if palette is None:
                palette = kws_kde.pop(
                    "palette",
                    get_color(data[hue].nunique()) if hue is not None else None,
                )
            alpha = kws_kde.pop("alpha", 0.05)
            for key in ["palette", "alpha", "hue"]:
                kws_kde.pop(key, None)
            ax = sns.kdeplot(
                data=data,
                x=x,
                y=y,
                palette=palette,
                hue=hue,
                ax=ax,
                alpha=alpha,
                zorder=zorder,
                **kws_kde,
            )
        elif k == "ecdfplot":
            if run_once_within(10):  
                print("""
                    https://seaborn.pydata.org/generated/seaborn.ecdfplot.html#seaborn-ecdfplot
                    Plot empirical cumulative distribution functions.

                    An ECDF represents the proportion or count of observations falling below each unique value in a dataset. Compared to a histogram or density plot, it has the advantage that each observation is visualized directly, meaning that there are no binning or smoothing parameters that need to be adjusted. It also aids direct comparisons between multiple distributions. A downside is that the relationship between the appearance of the plot and the basic properties of the distribution (such as its central tendency, variance, and the presence of any bimodality) may not be as intuitive.

                    sns.ecdfplot(data=penguins, x="bill_length_mm", hue="species", stat="count")
                """)
            kws_ecdf = kwargs.pop("kws_ecdf", kwargs)
            kws_ecdf = {k: v for k, v in kws_ecdf.items() if not k.startswith("kws_")}
            ax = sns.ecdfplot(data=data, x=x, y=y, ax=ax, zorder=zorder, **kws_ecdf)
        elif k == "rugplot":
            if run_once_within(10): 
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print("""
                      https://seaborn.pydata.org/generated/seaborn.rugplot.html
                    This function is intended to complement other plots by showing the location of individual observations in an unobtrusive way.

                    sns.scatterplot(data=tips, x="total_bill", y="tip")
                    sns.rugplot(data=tips, x="total_bill", y="tip", height=.1)
                      """)
            kws_rug = kwargs.pop("kws_rug", kwargs)
            kws_rug = {k: v for k, v in kws_rug.items() if not k.startswith("kws_")}
            ax = sns.rugplot(data=data, x=x, y=y, ax=ax, zorder=zorder, **kws_rug)
        elif k == "stripplot":
            if run_once_within(10):
                print("\n xample-data (df_numeric):\n",generate_test_data("num"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print("""
                      A strip plot can be drawn on its own, but it is also a good complement to a box or violin plot in cases where you want to show all observations along with some representation of the underlying distribution.

                    sns.stripplot(data=tips, x="total_bill", y="day", hue="sex", dodge=True, jitter=False)
                    sns.stripplot(data=tips, orient="h")

                    sns.stripplot(
                        data=tips, x="total_bill", y="day", hue="time",
                        jitter=False, s=20, marker="D", linewidth=1, alpha=.1,
                    )
                    # Put the rug outside the axes:
                    sns.scatterplot(data=tips, x="total_bill", y="tip")
                    sns.rugplot(data=tips, x="total_bill", y="tip", height=-.02, clip_on=False)

                    # Show the density of a larger dataset using thinner lines and alpha blending:
                    diamonds = sns.load_dataset("diamonds")
                    sns.scatterplot(data=diamonds, x="carat", y="price", s=5)
                    sns.rugplot(data=diamonds, x="carat", y="price", lw=1, alpha=.005)
                      """)
            kws_strip = kwargs.pop("kws_strip", kwargs)
            kws_strip = {k: v for k, v in kws_strip.items() if not k.startswith("kws_")}
            dodge = kws_strip.pop("dodge", True)
            ax = sns.stripplot(
                data=data, x=x, y=y, ax=ax, zorder=zorder, dodge=dodge, **kws_strip
            )
        elif k == "swarmplot":
            if run_once_within(10):
                print("\n xample-data (df_numeric):\n",generate_test_data("num"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print("""
                    https://seaborn.pydata.org/generated/seaborn.swarmplot.html#seaborn-swarmplot 
                    This function is similar to stripplot(), but the points are adjusted (only along the categorical axis) so that they don’t overlap. This gives a better representation of the distribution of values, but it does not scale well to large numbers of observations. This style of plot is sometimes called a “beeswarm”.
                    A swarm plot can be drawn on its own, but it is also a good complement to a box or violin plot in cases where you want to show all observations along with some representation of the underlying distribution.

                    sns.swarmplot(data=tips, x="total_bill", y="day")
                    sns.swarmplot(data=tips, x="total_bill", y="day", hue="day", legend=False)
                    sns.swarmplot(data=tips, x="total_bill", y="day", hue="sex", dodge=True)

                    sns.swarmplot(
                        data=tips, x="total_bill", y="day",
                        marker="x", linewidth=1,
                    )
                    """
                    )
            kws_swarm = kwargs.pop("kws_swarm", kwargs)
            kws_swarm = {k: v for k, v in kws_swarm.items() if not k.startswith("kws_")}
            ax = sns.swarmplot(data=data, x=x, y=y, ax=ax, zorder=zorder, **kws_swarm)
        elif k == "boxplot":
            if run_once_within(10):
                print("\n xample-data (df_numeric):\n",generate_test_data("num"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
            kws_box = kwargs.pop("kws_box", kwargs)
            kws_box = {k: v for k, v in kws_box.items() if not k.startswith("kws_")}
            ax = sns.boxplot(data=data, x=x, y=y, ax=ax, zorder=zorder, **kws_box)
        elif k == "violinplot":
            if run_once_within(10):
                print("\n xample-data (df_numeric):\n",generate_test_data("num"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print("""
                    https://seaborn.pydata.org/generated/seaborn.violinplot.html#seaborn-violinplot
                     A violin plot plays a similar role as a box-and-whisker plot. It shows the distribution of data points after grouping by one (or more) variables. Unlike a box plot, each violin is drawn using a kernel density estimate of the underlying distribution.

                    sns.violinplot(data=df, x="class", y="age", hue="alive", split=True, gap=.1, inner="quart")
                    sns.violinplot(data=df, x="age", y="deck", inner="point", density_norm="count")
                    sns.violinplot(data=df, x="age", y="alive", cut=0, inner="stick")
                    sns.violinplot(data=df, x="age", inner_kws=dict(box_width=15, whis_width=2, color=".8"))
                    """
                    )
            kws_violin = kwargs.pop("kws_violin", kwargs)
            kws_violin = {
                k: v for k, v in kws_violin.items() if not k.startswith("kws_")
            }
            ax = sns.violinplot(data=data, x=x, y=y, ax=ax, zorder=zorder, **kws_violin)
        elif k == "boxenplot":
            if run_once_within(10):
                print("\n xample-data (df_numeric):\n",generate_test_data("num"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print("""
                    https://seaborn.pydata.org/generated/seaborn.boxenplot.html#seaborn-boxenplot
                    This style of plot was originally named a “letter value” plot because it shows a large number of quantiles that are defined as “letter values”. It is similar to a box plot in plotting a nonparametric representation of a distribution in which all features correspond to actual observations. By plotting more quantiles, it provides more information about the shape of the distribution, particularly in the tails.

                    sns.boxenplot(data=diamonds, x="price", y="clarity", width=.5)
                    sns.boxenplot(
                        data=diamonds, x="price", y="clarity",
                        linewidth=.5, linecolor=".7",
                        line_kws=dict(linewidth=1.5, color="#cde"),
                        flier_kws=dict(facecolor=".7", linewidth=.5),
                    )
                    sns.boxenplot(data=diamonds, x="price", y="clarity", hue="clarity", fill=False)
                    """
                    )
            kws_boxen = kwargs.pop("kws_boxen", kwargs)
            kws_boxen = {k: v for k, v in kws_boxen.items() if not k.startswith("kws_")}
            ax = sns.boxenplot(data=data, x=x, y=y, ax=ax, zorder=zorder, **kws_boxen)
        elif k == "pointplot":
            if run_once_within(10):
                print("\n xample-data (df_numeric):\n",generate_test_data("num"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
            kws_point = kwargs.pop("kws_point", kwargs)
            kws_point = {k: v for k, v in kws_point.items() if not k.startswith("kws_")}
            ax = sns.pointplot(data=data, x=x, y=y, ax=ax, zorder=zorder, **kws_point)
        elif k == "barplot":
            if run_once_within(10):
                print("\n xample-data (df_numeric):\n",generate_test_data("num"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print("""
                    https://seaborn.pydata.org/generated/seaborn.barplot.html#seaborn.barplot
                    sns.barplot(penguins, x="island", y="body_mass_g")

                    # assign the grouping variable to hue as wel
                    sns.barplot(penguins, x="body_mass_g", y="island", hue="island", legend=False)
                    
                    # When plotting a “wide-form” dataframe, each column will be aggregated and represented as a bar:
                    flights_wide = flights.pivot(index="year", columns="month", values="passengers")
                    sns.barplot(flights_wide)

                    # Add text labels with each bar’s value:
                    ax = sns.barplot(flights, x="year", y="passengers", estimator="sum", errorbar=None)
                    ax.bar_label(ax.containers[0], fontsize=10);

                    # Customize the appearance of the plot using matplotlib.patches.Rectangle and matplotlib.lines.Line2D
                    sns.barplot(
                        penguins, x="body_mass_g", y="island",
                        errorbar=("pi", 50), capsize=.4,
                        err_kws={"color": ".5", "linewidth": 2.5},
                        linewidth=2.5, edgecolor=".5", facecolor=(0, 0, 0, 0),
                    )
                    """
                    )
            kws_bar = kwargs.pop("kws_bar", kwargs)
            kws_bar = {k: v for k, v in kws_bar.items() if not k.startswith("kws_")}
            ax = sns.barplot(data=data, x=x, y=y, ax=ax, zorder=zorder, **kws_bar)
        elif k == "countplot":
            if run_once_within(10):
                print("https://seaborn.pydata.org/generated/seaborn.countplot.html#seaborn-countplot")
                print("\n xample-data (df_numeric):\n",generate_test_data("num"))
                print("""
                    sns.countplot(titanic, x="class")
                    sns.countplot(titanic, x="class", hue="survived")
                    sns.countplot(titanic, x="class", hue="survived", stat="percent")
                    """
                    )
            kws_count = kwargs.pop("kws_count", kwargs)
            kws_count = {k: v for k, v in kws_count.items() if not k.startswith("kws_")}
            if not kws_count.get("hue", None):
                kws_count.pop("palette", None)
            if y is None:
                ax = sns.countplot(data=data, x=x, ax=ax, zorder=zorder, **kws_count)
            else:
                ax = sns.countplot(data=data, y=y, ax=ax, zorder=zorder, **kws_count)

        elif k == "regplot":
            if run_once_within(10):
                print("https://seaborn.pydata.org/generated/seaborn.regplot.html#seaborn.regplot")
                print("\n xample-data (df_numeric):\n",generate_test_data("num")) 
                print("""
                    sns.regplot(
                        data=data, x="x", y="y", 
                        # order=2,
                        ci=95, marker="x", color=".3", line_kws=dict(color="r"),
                    )
                    """
                    )
            kws_reg = kwargs.pop("kws_reg", kwargs)
            kws_reg = {k: v for k, v in kws_reg.items() if not k.startswith("kws_")}
            stats = kwargs.pop("stats", True)  # Flag to calculate stats

            # Compute Pearson correlation if stats is True
            if stats:
                r, p_value = scipy_stats.pearsonr(data[x], data[y])
            ax = sns.regplot(data=data, x=x, y=y, ax=ax, **kws_reg)

            # Annotate the Pearson correlation and p-value
            ax.annotate(
                f"pearsonr = {r:.2f} p = {p_value:.3f}",
                xy=(0.6, 0.98),
                xycoords="axes fraction",
                fontsize=12,
                color="black",
                ha="center",
            )
        elif k == "residplot":
            if run_once_within(10):
                print("\n xample-data (df_numeric):\n",generate_test_data("num")) 
                print("""
                    sns.residplot(data=data, x="x", y="y", lowess=True, line_kws=dict(color="r"))
                    """
                    )
            kws_resid = kwargs.pop("kws_resid", kwargs)
            kws_resid = {k: v for k, v in kws_resid.items() if not k.startswith("kws_")}
            ax = sns.residplot(
                data=data, x=x, y=y, lowess=True, ax=ax, **kws_resid
            )
        elif k == "lineplot":
            if run_once_within(10):
                print("https://seaborn.pydata.org/generated/seaborn.lineplot.html#seaborn-lineplot")
                print("\n xample-data (df_numeric):\n",generate_test_data("num")) 
                print("\n xample-data (df_mix):\n",generate_test_data("mix"))
                print("\n xample-data (df_long):\n",generate_test_data("long"))
                print("\n xample-data (time):\n",generate_test_data("time"))
            kws_line = kwargs.pop("kws_line", kwargs)
            kws_line = {k: v for k, v in kws_line.items() if not k.startswith("kws_")} 
            ax = sns.lineplot(ax=ax, data=data, x=x, y=y, zorder=zorder, **kws_line)

        figsets(ax=ax, **kws_figsets) if kws_figsets else None
        if kws_add_text:
            add_text(ax=ax, **kws_add_text) if kws_add_text else None
    if run_once_within(10):
        for k in kind_:
            print(f"\n{k}⤵ {strcmp(k,list(default_settings.keys()))[0]}")
            print(default_settings[strcmp(k,list(default_settings.keys()))[0]])
    if "g" in locals():
        if ax is not None:
            return g, ax
    return ax

def df_preprocessing_(data, kind, verbose=False):
    """
    Automatically formats data for various seaborn plot types.

    Parameters:
    - data (pd.DataFrame): Original DataFrame.
    - kind (str): Type of seaborn plot, e.g., "heatmap", "boxplot", "violinplot", "lineplot", "scatterplot", "histplot", "kdeplot", "catplot", "barplot".
    - verbose (bool): If True, print detailed information about the data format conversion.

    Returns:
    - pd.DataFrame: Formatted DataFrame ready for the specified seaborn plot type.
    """
    # Determine data format: 'long', 'wide', or 'uncertain'
    df_format_ = get_df_format(data)

    # Correct plot type name
    kind = strcmp(
        kind,
        [
            "heatmap",
            "pairplot",
            "jointplot",  # Typically requires wide format for axis variables
            "facetgrid",  # Used for creating small multiples (can work with wide format)
            "barplot",  # Can be used with wide format
            "pointplot",  # Works well with wide format
            "pivot_table",  # Works with wide format (aggregated data)
            "boxplot",
            "violinplot",
            "stripplot",
            "swarmplot",
            "catplot",
            "lineplot",
            "scatterplot",
            "relplot",
            "barplot",  # Can also work with long format (aggregated data in long form)
            "boxenplot",  # Similar to boxplot, works with long format
            "countplot",  # Works best with long format (categorical data)
            "heatmap",  # Can work with long format after reshaping
            "lineplot",  # Can work with long format (time series, continuous)
            "histplot",  # Can be used with both wide and long formats
            "kdeplot",  # Works with both wide and long formats
            "ecdfplot",  # Works with both formats
            "scatterplot",  # Can work with both formats depending on data structure
            "lineplot",  # Can work with both wide and long formats
            "area plot",  # Can work with both formats, useful for stacked areas
            "violinplot",  # Can work with both formats depending on categorical vs continuous data
            "ellipse",  # ellipse plot, default confidence=0.95
        ],
    )[0]

    wide_kinds = [
        "pairplot",
        "countplot",  # Works best with long format (categorical data)
    ]

    # Define plot types that require 'long' format
    long_kinds = [
        "catplot",
    ]

    # Flexible kinds: distribution plots can use either format
    flexible_kinds = [
        "jointplot",  # Typically requires wide format for axis variables
        "lineplot",  # Can work with long format (time series, continuous)
        "lineplot",
        "scatterplot",
        "barplot",  # Can also work with long format (aggregated data in long form)
        "boxenplot",  # Similar to boxplot, works with long format
        "regplot",
        "violinplot",
        "stripplot",
        "swarmplot",
        "boxplot",
        "histplot",  # Can be used with both wide and long formats
        "kdeplot",  # Works with both wide and long formats
        "ecdfplot",  # Works with both formats
        "scatterplot",  # Can work with both formats depending on data structure
        "lineplot",  # Can work with both wide and long formats
        "area plot",  # Can work with both formats, useful for stacked areas
        "violinplot",  # Can work with both formats depending on categorical vs continuous data
        "relplot",
        "pointplot",  # Works well with wide format
        "ellipse",
    ]

    # Wide format (e.g., for heatmap and pairplot)
    if kind in wide_kinds:
        if df_format_ != "wide":
            if verbose:
                print("Converting to wide format for", kind)
            return data.corr() if kind == "heatmap" else data
        return data

    # Long format for categorical plots or time series
    elif kind in long_kinds:
        if df_format_ == "wide":
            if verbose:
                print("Converting wide data to long format for", kind)
            return pd.melt(data, var_name="variable", value_name="value")
        elif df_format_ == "uncertain":
            if verbose:
                print("Data format is uncertain, attempting to melt for", kind)
            return pd.melt(data, var_name="variable", value_name="value")
        return data

    # Flexible format: distribution plots can use either long or wide
    elif kind in flexible_kinds:
        if df_format_ == "wide" or df_format_ == "long":
            return data
        if verbose:
            print("Converting uncertain format to long format for distribution plots")
        return pd.melt(data, var_name="variable", value_name="value")

    else:
        if verbose:
            print("Unrecognized plot type; returning original data without conversion.")
        return data

def norm_cmap(data, cmap="coolwarm", min_max=[0, 1]):
    norm_ = plt.Normalize(min_max[0], min_max[1])
    colormap = plt.get_cmap(cmap)
    return colormap(norm_(data))

def volcano(
    data: pd.DataFrame,
    x: str,
    y: str,
    gene_col: str = None,
    top_genes=[5, 5],  # [down-regulated, up-regulated]
    score_power=[1,1],# (power_log2FC, power_padj)
    thr_x=np.log2(1.5),  # default: 0.585
    thr_y=-np.log10(0.05),
    sort_xy="x",  #'y', 'xy'
    colors=("#00BFFF", "#9d9a9a", "#FF3030"),
    s=20,
    fill=True,  # plot filled scatter
    facecolor="none",
    edgecolor="none",
    edgelinewidth=0.5,
    alpha=0.8,
    legend=False,
    ax=None,
    verbose=False,
    kws_text=dict(fontsize=10, color="k"),
    kws_bbox=dict(
        facecolor="none", alpha=0.5, edgecolor="black", boxstyle="round,pad=0.3"
    ),  # '{}' to hide
    kws_arrow=dict(color="k", lw=0.5),  # '{}' to hide
    **kwargs,
):
    """
    Generates a customizable scatter plot (e.g., volcano plot).

    Parameters:
    -----------
    data : pd.DataFrame
        The DataFrame containing the data to plot.
    x : str
        Column name for x-axis values (e.g., log2FoldChange).
    y : str
        Column name for y-axis values (e.g., -log10(FDR)).
    gene_col : str, optional
        Column name for gene names. If provided, gene names will be displayed. Default is None.
    top_genes : int, list, optional
        Number of top genes to label based on y-axis values. Default is 5.
    thr_x : float, optional
        Threshold for x-axis values. Default is 0.585.
    thr_y : float, optional
        Threshold for y-axis values (e.g., significance threshold). Default is -np.log10(0.05).
    colors : tuple, optional
        Colors for points above/below thresholds and neutral points. Default is ("red", "blue", "gray").
    figsize : tuple, optional
        Figure size. Default is (6, 4).
    s : int, optional
        Size of points in the plot. Default is 20.
    fontsize : int, optional
        Font size for gene labels. Default is 10.
    alpha : float, optional
        Transparency of the points. Default is 0.8.
    legend : bool, optional
        Whether to show a legend. Default is False.
    """
    usage_str = """
    _, axs = plt.subplots(1, 1, figsize=(4, 5))
    volcano(
        ax=axs,
        data=ranked_genes,
        x="log2(fold_change)",
        y="-log10(p-value)",
        gene_col="ID_REF",
        top_genes=6,
        thr_x=np.log2(1.2),
        # thr_y=-np.log10(0.05),
        colors=("#00BFFF", "#9d9a9a", "#FF3030"),
        fill=0,
        alpha=1,
        facecolor="none",
        s=20,
        edgelinewidth=0.5,
        edgecolor="0.5",
        kws_text=dict(fontsize=10, color="k"),
        kws_arrow=dict(style="-", color="k", lw=0.5),
        # verbose=True,
        figsets=dict(ylim=[0, 10], title="df"),
    )
    """
    if verbose:
        print(usage_str)
        return
    from adjustText import adjust_text

    kws_figsets = {}
    for k_arg, v_arg in kwargs.items():
        if "figset" in k_arg:
            kws_figsets = v_arg
            kwargs.pop(k_arg, None)
            break

    data = data.copy()
    # filter nan
    data = data.dropna(subset=[x, y])  # Drop rows with NaN in x or y
    data.loc[:, "color"] = np.where(
        (data[x] > thr_x) & (data[y] > thr_y),
        colors[2],
        np.where((data[x] < -thr_x) & (data[y] > thr_y), colors[0], colors[1]),
    )
    top_genes = [top_genes, top_genes] if isinstance(top_genes, int) else top_genes

    # could custom how to select the top genes, x: x has priority
    sort_by_x_y = [x, y] if sort_xy == "x" else [y, x]
    ascending_up = [True, True] if sort_xy == "x" else [False, True]
    ascending_down = [False, True] if sort_xy == "x" else [False, False]

    # ===========================
    # 原来的算法
    # ===========================
    # down_reg_genes = (
    #     data[(data["color"] == colors[0]) & (data[x].abs() > thr_x) & (data[y] > thr_y)]
    #     .sort_values(by=sort_by_x_y, ascending=ascending_up)
    #     .head(top_genes[0])
    # )
    # up_reg_genes = (
    #     data[(data["color"] == colors[2]) & (data[x].abs() > thr_x) & (data[y] > thr_y)]
    #     .sort_values(by=sort_by_x_y, ascending=ascending_down)
    #     .head(top_genes[1])
    # )
    # ===========================
    # 综合考虑显著性与fold change
    # ===========================
    data = data.copy()
    data["score"] = (data[x].abs() ** score_power[0]) * (data[y] ** score_power[1]) # 综合得分: |log2FC| × -log10(padj)
    # 分别选择上下调的 top 基因
    down_candidates = data[(data[x] < -thr_x) & (data[y] > thr_y)]
    up_candidates = data[(data[x] > thr_x) & (data[y] > thr_y)]

    down_reg_genes = down_candidates.sort_values("score", ascending=False).head(top_genes[0])
    up_reg_genes = up_candidates.sort_values("score", ascending=False).head(top_genes[1])
    
    sele_gene = pd.concat([down_reg_genes, up_reg_genes]) 

    palette = {colors[0]: colors[0], colors[1]: colors[1], colors[2]: colors[2]}
    # Plot setup
    if ax is None:
        ax = plt.gca()

    # Handle fill parameter
    if fill:
        facecolors = data["color"]  # Fill with colors
        edgecolors = edgecolor  # Set edgecolor
    else:
        facecolors = facecolor  # No fill, use edge color as the face color
        edgecolors = data["color"]

    ax = sns.scatterplot(
        ax=ax,
        data=data,
        x=x,
        y=y,
        hue="color",
        palette=palette,
        s=s,
        linewidths=edgelinewidth,
        color=facecolors,
        edgecolor=edgecolors,
        alpha=alpha,
        legend=legend,
        **kwargs,
    )

    # Add threshold lines for x and y axes
    ax.axhline(y=thr_y, color="black", linestyle="--", lw=1)
    ax.axvline(x=-thr_x, color="black", linestyle="--", lw=1)
    ax.axvline(x=thr_x, color="black", linestyle="--", lw=1)

    # Add gene labels for selected significant points
    if gene_col:
        texts = []
        # if kws_text:
        fontname = kws_text.pop("fontname", "Arial")
        textcolor = kws_text.pop("color", "k")
        fontsize = kws_text.pop("fontsize", 10)
        arrowstyles = [
            "->",
            "<-",
            "<->",
            "<|-",
            "-|>",
            "<|-|>",
            "-",
            "-[",
            "-[",
            "fancy",
            "simple",
            "wedge",
        ]
        arrowstyle = kws_arrow.pop("style", "<|-")
        arrowstyle = strcmp(arrowstyle, arrowstyles, scorer="strict")[0]
        expand = kws_arrow.pop("expand", (1.05, 1.1))
        arrowcolor = kws_arrow.pop("color", "0.4")
        arrowlinewidth = kws_arrow.pop("lw", 0.75)
        shrinkA = kws_arrow.pop("shrinkA", 0)
        shrinkB = kws_arrow.pop("shrinkB", 0)
        mutation_scale = kws_arrow.pop("head", 10)
        arrow_fill = kws_arrow.pop("fill", False)
        for i in range(sele_gene.shape[0]):
            if isinstance(textcolor, list):  # be consistant with dots's color
                textcolor = colors[0] if sele_gene[x].iloc[i] > 0 else colors[1]
            texts.append(
                ax.text(
                    x=sele_gene[x].iloc[i],
                    y=sele_gene[y].iloc[i],
                    s=sele_gene[gene_col].iloc[i],
                    bbox=kws_bbox if kws_bbox else None,
                    fontdict={
                        "fontsize": fontsize,
                        "color": textcolor,
                        "fontname": fontname,
                    },
                )
            )
        print(arrowstyle)
        adjust_text(
            texts,
            expand=expand,
            min_arrow_len=5,
            ax=ax,
            arrowprops=dict(
                arrowstyle=arrowstyle,
                fill=arrow_fill,
                color=arrowcolor,
                lw=arrowlinewidth,
                shrinkA=shrinkA,
                shrinkB=shrinkB,
                mutation_scale=mutation_scale,
                **kws_arrow,
            ),
        )

    figsets(**kws_figsets)


def sns_func_info(dir_save=None):
    sns_info = {
        "Functions": [
            "relplot",
            "scatterplot",
            "lineplot",
            "lmplot",
            "catplot",
            "stripplot",
            "boxplot",
            "violinplot",
            "boxenplot",
            "pointplot",
            "barplot",
            "countplot",
            "displot",
            "histplot",
            "kdeplot",
            "ecdfplot",
            "rugplot",
            "regplot",
            "residplot",
            "pairplot",
            "jointplot",
            "plotting_context",
        ],
        "Category": [
            "relational",
            "relational",
            "relational",
            "relational",
            "categorical",
            "categorical",
            "categorical",
            "categorical",
            "categorical",
            "categorical",
            "categorical",
            "categorical",
            "distribution",
            "distribution",
            "distribution",
            "distribution",
            "distribution",
            "regression",
            "regression",
            "grid-based(fig)",
            "grid-based(fig)",
            "context",
        ],
        "Detail": [
            "A figure-level function for creating scatter plots and line plots. It combines the functionality of scatterplot and lineplot.",
            "A function for creating scatter plots, useful for visualizing the relationship between two continuous variables.",
            "A function for drawing line plots, often used to visualize trends over time or ordered categories.",
            "A figure-level function for creating linear model plots, combining regression lines with scatter plots.",
            "A figure-level function for creating categorical plots, which can display various types of plots like box plots, violin plots, and bar plots in one function.",
            "A function for creating a scatter plot where one of the variables is categorical, helping visualize distribution along a categorical axis.",
            "A function for creating box plots, which summarize the distribution of a continuous variable based on a categorical variable.",
            "A function for creating violin plots, which combine box plots and KDEs to visualize the distribution of data.",
            "A function for creating boxen plots, an enhanced version of box plots that better represent data distributions with more quantiles.",
            "A function for creating point plots, which show the mean (or another estimator) of a variable for each level of a categorical variable.",
            "A function for creating bar plots, which represent the mean (or other estimators) of a variable with bars, typically used with categorical data.",
            "A function for creating count plots, which show the counts of observations in each categorical bin.",
            "A figure-level function that creates distribution plots. It can visualize histograms, KDEs, and ECDFs, making it versatile for analyzing the distribution of data.",
            "A function for creating histograms, useful for showing the frequency distribution of a continuous variable.",
            "A function for creating kernel density estimate (KDE) plots, which visualize the probability density function of a continuous variable.",
            "A function for creating empirical cumulative distribution function (ECDF) plots, which show the proportion of observations below a certain value.",
            "A function that adds a rug plot to the axes, representing individual data points along an axis.",
            "A function for creating regression plots, which fit and visualize a regression model on scatter data.",
            "A function for creating residual plots, useful for diagnosing the fit of a regression model.",
            "A figure-level function that creates a grid of scatter plots for each pair of variables in a dataset, often used for exploratory data analysis.",
            "A figure-level function that combines scatter plots and histograms (or KDEs) to visualize the relationship between two variables and their distributions.",
            "Not a plot itself, but a function that allows you to change the context (style and scaling) of your plots to fit different publication requirements or visual preferences.",
        ],
    }
    if dir_save is None:
        if "mac" in get_os():
            dir_save = "/Users/macjianfeng/Dropbox/github/python/py2ls/py2ls/data/"
        else:
            dir_save = "Z:\\Jianfeng\\temp\\"
    dir_save += "/" if not dir_save.endswith("/") else ""
    fsave(
        dir_save + "sns_info.json",
        sns_info,
    )


def get_color_overlap(*colors):
    import matplotlib.colors as mcolors

    """Blend multiple colors by averaging their RGB values."""
    rgbs = [mcolors.to_rgb(color) for color in colors]
    blended_rgb = [sum(channel) / len(channel) for channel in zip(*rgbs)]
    return mcolors.to_hex(blended_rgb)


def desaturate_color(color, saturation_factor=0.5):
    """Reduce the saturation of a color by a given factor (between 0 and 1)."""
    import matplotlib.colors as mcolors
    import colorsys

    # Convert the color to RGB
    rgb = mcolors.to_rgb(color)
    # Convert RGB to HLS (Hue, Lightness, Saturation)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    # Reduce the saturation
    s *= saturation_factor
    # Convert back to RGB
    return colorsys.hls_to_rgb(h, l, s)


def textsets(
    text,
    fontname="Arial",
    fontsize=11,
    fontweight="normal",
    fontstyle="normal",
    fontcolor="k",
    backgroundcolor=None,
    shadow=False,
    ha="center",
    va="center",
    shadow_linewidth=3,
    shadow_foreground_color="gray"
):
    from matplotlib import patheffects

    if text: # Ensure text exists
        if fontname:
            text.set_fontname(plt_font(fontname))
        if fontsize:
            text.set_fontsize(fontsize)
        if fontweight:
            text.set_fontweight(fontweight)
        if fontstyle:
            text.set_fontstyle(fontstyle)
        if fontcolor:
            text.set_color(fontcolor)
        if backgroundcolor:
            text.set_backgroundcolor(backgroundcolor)
        text.set_horizontalalignment(ha)
        text.set_verticalalignment(va)
        if shadow:
            text.set_path_effects([patheffects.withStroke(linewidth=shadow_linewidth, foreground=shadow_foreground_color)])

def venn(
    lists: list,
    labels: list = None,
    ax=None,
    verbose:bool = True,
    colors=None,
    edgecolor=None,
    alpha=0.5,
    saturation=0.75,
    linewidth=0,  # default no edge
    linestyle: str = "-",
    fontname: str ="Arial",
    fontsize=10,
    fontcolor="k",
    fontweight: str ="normal",
    fontstyle: str ="normal",
    ha: str ="center",
    va: str ="center",
    shadow: bool =False,
    subset_fontsize=10,
    subset_fontweight="normal",
    subset_fontstyle="normal",
    subset_fontcolor="k",
    backgroundcolor=None,
    custom_texts=None,
    show_percentages=True,  # display percentage
    fmt="{:.1%}",
    ellipse_shape=False,  # 椭圆形
    ellipse_scale=[1.5, 1],  # not perfect, 椭圆形的形状
    **kwargs,
):
    """
    Advanced Venn diagram plotting function with extensive customization options.
    Parameters:
        lists: list of sets, 2 or 3 sets
        labels: list of strings, labels for the sets
        ax: matplotlib axis, optional
        colors: list of colors, colors for the Venn diagram patches
        edgecolor: string, color of the circle edges
        alpha: float, transparency level for the patches
        linewidth: float, width of the circle edges
        linestyle: string, line style for the circles
        fontname: string, font for set labels
        fontsize: int, font size for set labels
        fontweight: string, weight of the set label font (e.g., 'bold', 'light')
        fontstyle: string, style of the set label font (e.g., 'italic')
        label_align: string, horizontal alignment of set labels ('left', 'center', 'right')
        label_baseline: string, vertical alignment of set labels ('top', 'center', 'bottom')
        subset_fontsize: int, font size for subset labels (the numbers)
        subset_fontweight: string, weight of subset label font
        subset_fontstyle: string, style of subset label font
        subset_label_format: string, format for subset labels (e.g., "{:.2f}" for floats)
        shadow: bool, add shadow effect to the patches
        custom_texts: list of custom texts to replace the subset labels
        **kwargs: additional keyword arguments passed to venn2 or venn3
    """
    if ax is None:
        ax = plt.gca()
    if isinstance(lists, dict):
        labels,lists = list(lists.keys()),list(lists.values())
    if isinstance(lists[0], set):
        lists = [list(i) for i in lists]

    lists = [set(flatten(i, verbose=False)) for i in lists]
    if verbose:
        ls_param(venn)
        print("""
    Usage:
        # Define the two sets
        set1 = [1, 2, 3, 4, 5]
        set2 = [4, 5, 6, 7, 8]
        set3 = [1, 2, 4, 7, 9, 10, 11, 6, 103]
        _, axs = plt.subplots(1, 2)
        venn(
            [set1, set2],
            ["Set A", "Set B"],
            colors=["r", "b"],
            edgecolor="r",
            linewidth=0,
            ax=axs[0],
        )
        venn(
            [set1, set2, set3],
            ["Set A", "Set B", "Set 3"],
            colors=["r", "g", "b"],
            saturation=0.8,
            linewidth=[3, 5, 7],
            linestyle=[":", "-", "--"],
            # edgecolor="r",
            # alpha=1,
            ax=axs[1],
        )
              """)
    # Function to apply text styles to labels
    if colors is None:
        colors = ["r", "b"] if len(lists) == 2 else ["r", "g", "b"]
    # if labels is None:
    #     if len(lists) == 2:
    #         labels = ["set1", "set2"]
    #     elif len(lists) == 3:
    #         labels = ["set1", "set2", "set3"]
    #     elif len(lists) == 4:
    #         labels = ["set1", "set2", "set3", "set4"]
    #     elif len(lists) == 5:
    #         labels = ["set1", "set2", "set3", "set4", "set55"]
    #     elif len(lists) == 6:
    #         labels = ["set1", "set2", "set3", "set4", "set5", "set6"]
    #     elif len(lists) == 7:
    #         labels = ["set1", "set2", "set3", "set4", "set5", "set6", "set7"]
    if labels is None:
        labels = [f"set{i+1}" for i in range(len(lists))]
    # if edgecolor is None:
    #     edgecolor = colors
    edgecolor = edgecolor or colors
    colors = [desaturate_color(color, saturation) for color in colors]
    universe = len(set.union(*lists))

    # Check colors and auto-calculate overlaps
    def get_count_and_percentage(set_count, subset_count):
        percent = subset_count / set_count if set_count > 0 else 0
        return (
            f"{subset_count}\n({fmt.format(percent)})"
            if show_percentages
            else f"{subset_count}"
        )

    if fmt is not None:
        if not fmt.startswith("{"):
            fmt = "{:" + fmt + "}"
    if len(lists) == 2:

        from matplotlib_venn import venn2, venn2_circles

        # Auto-calculate overlap color for 2-set Venn diagram
        overlap_color = get_color_overlap(colors[0], colors[1]) if colors else None

        # Draw the venn diagram
        v = venn2(subsets=lists, set_labels=labels, ax=ax, **kwargs)
        venn_circles = venn2_circles(subsets=lists, ax=ax)
        set1, set2 = lists[0], lists[1]
        v.get_patch_by_id("10").set_color(colors[0])
        v.get_patch_by_id("01").set_color(colors[1])
        try:
            v.get_patch_by_id("11").set_color(
                get_color_overlap(colors[0], colors[1]) if colors else None
            )
        except Exception as e:
            print(e)
        # v.get_label_by_id('10').set_text(len(set1 - set2))
        # v.get_label_by_id('01').set_text(len(set2 - set1))
        # v.get_label_by_id('11').set_text(len(set1 & set2))

        v.get_label_by_id("10").set_text(
            get_count_and_percentage(universe, len(set1 - set2))
        )
        v.get_label_by_id("01").set_text(
            get_count_and_percentage(universe, len(set2 - set1))
        )
        try:
            v.get_label_by_id("11").set_text(
                get_count_and_percentage(universe, len(set1 & set2))
            )
        except Exception as e:
            print(e)

        if not isinstance(linewidth, list):
            linewidth = [linewidth]
        if isinstance(linestyle, str):
            linestyle = [linestyle]
        if not isinstance(edgecolor, list):
            edgecolor = [edgecolor]
        linewidth = linewidth * 2 if len(linewidth) == 1 else linewidth
        linestyle = linestyle * 2 if len(linestyle) == 1 else linestyle
        edgecolor = edgecolor * 2 if len(edgecolor) == 1 else edgecolor
        for i in range(2):
            venn_circles[i].set_lw(linewidth[i])
            venn_circles[i].set_ls(linestyle[i])
            venn_circles[i].set_edgecolor(edgecolor[i])
        # 椭圆
        if ellipse_shape:
            import matplotlib.patches as patches

            for patch in v.patches:
                patch.set_visible(False)  # Hide original patches if using ellipses
            center1 = v.get_circle_center(0)
            center2 = v.get_circle_center(1)
            ellipse1 = patches.Ellipse(
                (center1.x, center1.y),
                width=ellipse_scale[0],
                height=ellipse_scale[1],
                edgecolor=edgecolor[0] if edgecolor else colors[0],
                facecolor=colors[0],
                lw=(
                    linewidth if isinstance(linewidth, (int, float)) else 1.0
                ),  # Ensure lw is a number
                ls=linestyle[0],
                alpha=(
                    alpha if isinstance(alpha, (int, float)) else 0.5
                ),  # Ensure alpha is a number
            )
            ellipse2 = patches.Ellipse(
                (center2.x, center2.y),
                width=ellipse_scale[0],
                height=ellipse_scale[1],
                edgecolor=edgecolor[1] if edgecolor else colors[1],
                facecolor=colors[1],
                lw=(
                    linewidth if isinstance(linewidth, (int, float)) else 1.0
                ),  # Ensure lw is a number
                ls=linestyle[0],
                alpha=(
                    alpha if isinstance(alpha, (int, float)) else 0.5
                ),  # Ensure alpha is a number
            )
            ax.add_patch(ellipse1)
            ax.add_patch(ellipse2)
        # Apply styles to set labels
        for i, text in enumerate(v.set_labels):
            textsets(
                text,
                fontname=fontname,
                fontsize=fontsize,
                fontweight=fontweight,
                fontstyle=fontstyle,
                fontcolor=fontcolor,
                ha=ha,
                va=va,
                shadow=shadow,
            )

        # Apply styles to subset labels
        for i, text in enumerate(v.subset_labels):
            if text:  # Ensure text exists
                if custom_texts:  # Custom text handling
                    text.set_text(custom_texts[i])
                textsets(
                    text,
                    fontname=fontname,
                    fontsize=subset_fontsize,
                    fontweight=subset_fontweight,
                    fontstyle=subset_fontstyle,
                    fontcolor=subset_fontcolor,
                    ha=ha,
                    va=va,
                    shadow=shadow,
                )
        # Set transparency level
        for patch in v.patches:
            if patch:
                patch.set_alpha(alpha)
                if "none" in edgecolor or 0 in linewidth:
                    patch.set_edgecolor("none")
        return ax
    elif len(lists) == 3:

        from matplotlib_venn import venn3, venn3_circles

        # Auto-calculate overlap colors for 3-set Venn diagram
        colorAB = get_color_overlap(colors[0], colors[1]) if colors else None
        colorAC = get_color_overlap(colors[0], colors[2]) if colors else None
        colorBC = get_color_overlap(colors[1], colors[2]) if colors else None
        colorABC = (
            get_color_overlap(colors[0], colors[1], colors[2]) if colors else None
        )
        set1, set2, set3 = lists[0], lists[1], lists[2]

        # Draw the venn diagram
        v = venn3(subsets=lists, set_labels=labels, ax=ax, **kwargs) 
        def safe_set_patch_and_label(v, region_id, color, text):
            patch = v.get_patch_by_id(region_id)
            label = v.get_label_by_id(region_id)

            if patch is not None:
                patch.set_color(color)
                patch.set_alpha(0.7)

            if label is not None:
                label.set_text(text)

 
        # All region metadata stored in one clean structure
        region_map = {
            "100": (colors[0], len(set1 - set2 - set3)),
            "010": (colors[1], len(set2 - set1 - set3)),
            "001": (colors[2], len(set3 - set1 - set2)),
            "110": (colorAB, len(set1 & set2 - set3)),
            "101": (colorAC, len(set1 & set3 - set2)),
            "011": (colorBC, len(set2 & set3 - set1)),
            "111": (colorABC, len(set1 & set2 & set3)),
        }

        # Loop cleanly through regions
        for region_id, (color, count) in region_map.items():
            text = get_count_and_percentage(universe, count)
            safe_set_patch_and_label(v, region_id, color, text)

        # Apply styles to set labels
        for i, text in enumerate(v.set_labels):
            textsets(
                text,
                fontname=fontname,
                fontsize=fontsize,
                fontweight=fontweight,
                fontstyle=fontstyle,
                fontcolor=fontcolor,
                ha=ha,
                va=va,
                shadow=shadow,
            )

        # Apply styles to subset labels
        for i, text in enumerate(v.subset_labels):
            if text:  # Ensure text exists
                if custom_texts:  # Custom text handling
                    text.set_text(custom_texts[i])
                textsets(
                    text,
                    fontname=fontname,
                    fontsize=subset_fontsize,
                    fontweight=subset_fontweight,
                    fontstyle=subset_fontstyle,
                    fontcolor=subset_fontcolor,
                    ha=ha,
                    va=va,
                    shadow=shadow,
                )

        venn_circles = venn3_circles(subsets=lists, ax=ax)
        if not isinstance(linewidth, list):
            linewidth = [linewidth]
        if isinstance(linestyle, str):
            linestyle = [linestyle]
        if not isinstance(edgecolor, list):
            edgecolor = [edgecolor]
        linewidth = linewidth * 3 if len(linewidth) == 1 else linewidth
        linestyle = linestyle * 3 if len(linestyle) == 1 else linestyle
        edgecolor = edgecolor * 3 if len(edgecolor) == 1 else edgecolor

        # edgecolor=[to_rgba(i) for i in edgecolor]

        for i in range(3):
            venn_circles[i].set_lw(linewidth[i])
            venn_circles[i].set_ls(linestyle[i])
            venn_circles[i].set_edgecolor(edgecolor[i])

        # 椭圆形
        if ellipse_shape:
            import matplotlib.patches as patches

            for patch in v.patches:
                patch.set_visible(False)  # Hide original patches if using ellipses
            center1 = v.get_circle_center(0)
            center2 = v.get_circle_center(1)
            center3 = v.get_circle_center(2)
            ellipse1 = patches.Ellipse(
                (center1.x, center1.y),
                width=ellipse_scale[0],
                height=ellipse_scale[1],
                edgecolor=edgecolor[0] if edgecolor else colors[0],
                facecolor=colors[0],
                lw=(
                    linewidth if isinstance(linewidth, (int, float)) else 1.0
                ),  # Ensure lw is a number
                ls=linestyle[0],
                alpha=(
                    alpha if isinstance(alpha, (int, float)) else 0.5
                ),  # Ensure alpha is a number
            )
            ellipse2 = patches.Ellipse(
                (center2.x, center2.y),
                width=ellipse_scale[0],
                height=ellipse_scale[1],
                edgecolor=edgecolor[1] if edgecolor else colors[1],
                facecolor=colors[1],
                lw=(
                    linewidth if isinstance(linewidth, (int, float)) else 1.0
                ),  # Ensure lw is a number
                ls=linestyle[0],
                alpha=(
                    alpha if isinstance(alpha, (int, float)) else 0.5
                ),  # Ensure alpha is a number
            )
            ellipse3 = patches.Ellipse(
                (center3.x, center3.y),
                width=ellipse_scale[0],
                height=ellipse_scale[1],
                edgecolor=edgecolor[1] if edgecolor else colors[1],
                facecolor=colors[1],
                lw=(
                    linewidth if isinstance(linewidth, (int, float)) else 1.0
                ),  # Ensure lw is a number
                ls=linestyle[0],
                alpha=(
                    alpha if isinstance(alpha, (int, float)) else 0.5
                ),  # Ensure alpha is a number
            )
            ax.add_patch(ellipse1)
            ax.add_patch(ellipse2)
            ax.add_patch(ellipse3)
        # Set transparency level
        for patch in v.patches:
            if patch:
                patch.set_alpha(alpha)
                if "none" in edgecolor or 0 in linewidth:
                    patch.set_edgecolor("none")
        return ax

    dict_data = {}
    for i_list, list_ in enumerate(lists):
        dict_data[labels[i_list]] = {*list_}

    if 3 < len(lists) < 6:
        from venn import venn as vn

        legend_loc = kwargs.pop("legend_loc", "upper right")
        ax = vn(dict_data, ax=ax, legend_loc=legend_loc, **kwargs)

        return ax
    else:
        from venn import pseudovenn

        cmap = kwargs.pop("cmap", "plasma")
        ax = pseudovenn(dict_data, cmap=cmap, ax=ax, **kwargs)

        return ax


#! subplots, support automatic extend new axis
def subplot(
    rows: int = 2,
    cols: int = 2,
    figsize: Union[tuple, list] = [8, 8],
    sharex=False,
    sharey=False,
    verbose=False,
    fig=None,
    **kwargs,
):
    """
    nexttile = subplot(
        8,
        2,
        figsize=(8, 9),
        sharey=True,
        sharex=True,
    )

    for i in range(8):
        ax = nexttile()
        x = np.linspace(0, 10, 100) + i
        ax.plot(x, np.sin(x + i) + i, label=f"Plot {i + 1}")
        ax.legend()
        ax.set_title(f"Tile {i + 1}")
        ax.set_ylabel(f"Tile {i + 1}")
        ax.set_xlabel(f"Tile {i + 1}")
    """
    from matplotlib.gridspec import GridSpec

    if verbose:
        print(
            f"usage:\n\tnexttile = subplot(2, 2, figsize=(5, 5), sharex=False, sharey=False)\n\tax = nexttile()"
        )

    figsize_recommend = f"subplot({rows}, {cols}, figsize={figsize})"
    if fig is None:
        fig = plt.figure(figsize=figsize, constrained_layout=True)
    grid_spec = GridSpec(rows, cols, figure=fig)
    occupied = set()
    row_first_axes = [None] * rows  # Track the first axis in each row (for sharey)
    col_first_axes = [None] * cols  # Track the first axis in each column (for sharex)

    def expand_ax():
        nonlocal rows, grid_spec, cols, row_first_axes, fig, figsize, figsize_recommend
        # fig_height = fig.get_figheight()
        # subplot_height = fig_height / rows
        rows += 1  # Expands by adding a row
        # figsize = (figsize[0], fig_height+subplot_height)
        fig.set_size_inches(figsize)
        grid_spec = GridSpec(rows, cols, figure=fig)
        row_first_axes.append(None)
        figsize_recommend = f"Warning: 建议设置 subplot({rows}, {cols})"
        print(figsize_recommend)

    def nexttile(rowspan=1, colspan=1, **kwargs):
        nonlocal rows, cols, occupied, grid_spec, fig, figsize_recommend
        for row in range(rows):
            for col in range(cols):
                if all(
                    (row + r, col + c) not in occupied
                    for r in range(rowspan)
                    for c in range(colspan)
                ):
                    break
            else:
                continue
            break

        else:
            expand_ax()
            return nexttile(rowspan=rowspan, colspan=colspan, **kwargs)

        sharex_ax, sharey_ax = None, None

        if sharex:
            sharex_ax = col_first_axes[col]
        if sharey:
            sharey_ax = row_first_axes[row]
        ax = fig.add_subplot(
            grid_spec[row : row + rowspan, col : col + colspan],
            sharex=sharex_ax,
            sharey=sharey_ax,
            **kwargs,
        )

        if row_first_axes[row] is None:
            row_first_axes[row] = ax
        if col_first_axes[col] is None:
            col_first_axes[col] = ax

        for r in range(row, row + rowspan):
            for c in range(col, col + colspan):
                occupied.add((r, c))

        return ax

    return nexttile


#! radar chart
def radar(
    data: pd.DataFrame,
    columns=None,
    ylim=(0, 100),
    facecolor=None,
    edgecolor="none",
    edge_linewidth=0.5,
    fontsize=10,
    fontcolor="k",
    size=6,
    linewidth=1,
    linestyle="-",
    alpha=0.3,
    fmt=".1f",
    marker="o",
    bg_color="0.8",
    bg_alpha=None,
    grid_interval_ratio=0.2,
    show_value=False,  # show text for each value
    cmap=None,
    legend_loc="upper right",
    legend_fontsize=10,
    grid_color="gray",
    grid_alpha=0.5,
    grid_linestyle="--",
    grid_linewidth=0.5,
    circular: bool = False,
    tick_fontsize=None,
    tick_fontcolor="0.65",
    tick_loc=None,  # label position
    turning=None,
    ax=None,
    sp=2,
    verbose=True,
    axis=0,
    **kwargs,
):
    """
    Example DATA:
        df = pd.DataFrame(
                data=[
                    [80, 90, 60],
                    [80, 20, 90],
                    [80, 95, 20],
                    [80, 95, 20],
                    [80, 30, 100],
                    [80, 30, 90],
                    [80, 80, 50],
                ],
                index=["HP", "MP", "ATK", "DEF", "SP.ATK", "SP.DEF", "SPD"],
                columns=["Hero", "Warrior", "Wizard"],
            )
        usage 1:
            radar(data=df)
        usage 2:
            radar(data=df["Wizard"])
        usage 3:
            radar(data=df, columns="Wizard")
        usage 4:
            nexttile = subplot(1, 2)
            radar(data=df, columns="Wizard", ax=nexttile(projection="polar"))
            pie(data=df, columns="Wizard", ax=nexttile(), width=0.5, pctdistance=0.7)
    Parameters:
        - data (pd.DataFrame): The data to plot. Each column corresponds to a variable, and each row represents a data point.
        - ylim (tuple): The limits of the radial axis (y-axis). Default is (0, 100).
        - color: The color(s) for the plot. Can be a single color or a list of colors.
        - fontsize (int): Font size for the angular labels (x-axis).
        - fontcolor (str): Color for the angular labels.
        - size (int): The size of the markers for each data point.
        - linewidth (int): Line width for the plot lines.
        - linestyle (str): Line style for the plot lines.
        - alpha (float): The transparency level for the filled area.
        - marker (str): The marker style for the data points.
        - value_offset=0.93,# offset of the text of each value
        - edgecolor (str): The color for the marker edges.
        - edge_linewidth (int): Line width for the marker edges.
        - bg_color (str): Background color for the radar chart.
        - grid_interval_ratio (float): Determines the intervals for the grid lines as a fraction of the y-limit.
        - cmap (str): The colormap to use if `color` is a list.
        - legend_loc (str): The location of the legend.
        - legend_fontsize (int): Font size for the legend.
        - grid_color (str): Color for the grid lines.
        - grid_alpha (float): Transparency of the grid lines.
        - grid_linestyle (str): Style of the grid lines.
        - grid_linewidth (int): Line width of the grid lines.
        - circular (bool): If True, use circular grid lines. If False, use spider-style grid lines (straight lines).
        - tick_fontsize (int): Font size for the radial (y-axis) labels.
        - tick_fontcolor (str): Font color for the radial (y-axis) labels.
        - tick_loc (float or None): The location of the radial tick labels (between 0 and 1). If None, it is automatically calculated.
        - turning (float or None): Rotation of the radar chart. If None, it is not applied.
        - ax (matplotlib.axes.Axes or None): The axis on which to plot the radar chart. If None, a new axis will be created.
        - sp (int): Padding for the ticks from the plot area.
        - **kwargs: Additional arguments for customization.
    """
    if run_once_within(20, reverse=True) and verbose:
        usage_ = """usage:
        radar(
            data: pd.DataFrame, #The data to plot. Each column corresponds to a variable, and each row represents a data point.
            ylim=(0, 100),# ylim (tuple): The limits of the radial axis (y-axis). Default is (0, 100).
            facecolor=get_color(5),#The color(s) for the plot. Can be a single color or a list of colors.
            edgecolor="none",#for the marker edges.
            edge_linewidth=0.5,#for the marker edges.
            fontsize=10,# Font size for the angular labels (x-axis).
            fontcolor="k",# Color for the angular labels.
            size=6,#The size of the markers for each data point.
            linewidth=1, 
            linestyle="-",
            alpha=0.5,#for the filled area.
            fmt=".1f",
            marker="o",# for the data points.
            bg_color="0.8",
            bg_alpha=None,
            grid_interval_ratio=0.2,#Determines the intervals for the grid lines as a fraction of the y-limit.
            show_value=False,# show text for each value
            cmap=None,
            legend_loc="upper right",
            legend_fontsize=10,
            grid_color="gray",
            grid_alpha=0.5,
            grid_linestyle="--",
            grid_linewidth=0.5,
            circular: bool = False,#If True, use circular grid lines. If False, use spider-style grid lines (straight lines)
            tick_fontsize=None,#for the radial (y-axis) labels.
            tick_fontcolor="0.65",#for the radial (y-axis) labels.
            tick_loc=None,  # label position
            turning=None,#Rotation of the radar chart
            ax=None,
            sp=2,#Padding for the ticks from the plot area.
            **kwargs,
        )"""
        print(usage_)
    if circular:
        from matplotlib.colors import to_rgba
    kws_figsets = {}
    for k_arg, v_arg in kwargs.items():
        if "figset" in k_arg:
            kws_figsets = v_arg
            kwargs.pop(k_arg, None)
            break
    if axis == 1:
        data = data.T
    if isinstance(data, dict):
        data = pd.DataFrame(pd.Series(data))
    if ~isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)
    if isinstance(data, pd.DataFrame):
        data = data.select_dtypes(include=np.number)
    if isinstance(columns, str):
        columns = [columns]
    if columns is None:
        columns = list(data.columns)
    data = data[columns]
    categories = list(data.index)
    num_vars = len(categories)

    # Set y-axis limits and grid intervals
    vmin, vmax = ylim

    # Set up angle for each category on radar chart
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Complete the loop to ensure straight-line connections

    # If no axis is provided, create a new one
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # bg_color
    if bg_alpha is None:
        bg_alpha = alpha
    (
        ax.set_facecolor(to_rgba(bg_color, alpha=bg_alpha))
        if circular
        else ax.set_facecolor("none")
    )
    # Set up the radar chart with straight-line connections
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axis per variable and add labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    if circular:
        # * cicular style
        ax.yaxis.set_ticks(np.arange(vmin, vmax + 1, vmax * grid_interval_ratio))
        ax.grid(
            axis="both",
            color=grid_color,
            linestyle=grid_linestyle,
            alpha=grid_alpha,
            linewidth=grid_linewidth,
            dash_capstyle="round",
            dash_joinstyle="round",
        )
        ax.spines["polar"].set_color(grid_color)
        ax.spines["polar"].set_linewidth(grid_linewidth)
        ax.spines["polar"].set_linestyle("-")
        ax.spines["polar"].set_alpha(grid_alpha)
        ax.spines["polar"].set_capstyle("round")
        ax.spines["polar"].set_joinstyle("round")

    else:
        # * spider style: spider-style grid (straight lines, not circles)
        # Create the spider-style grid (straight lines, not circles)
        for i in range(
            1, int((vmax - vmin) / ((vmax - vmin) * grid_interval_ratio)) + 1
        ):  # int(vmax * grid_interval_ratio) + 1):
            ax.plot(
                angles + [angles[0]],  # Closing the loop
                [i * vmax * grid_interval_ratio] * (num_vars + 1)
                + [i * vmax * grid_interval_ratio],
                color=grid_color,
                linestyle=grid_linestyle,
                alpha=grid_alpha,
                linewidth=grid_linewidth,
            )
        # set bg_color
        ax.fill(angles, [vmax] * (data.shape[0] + 1), color=bg_color, alpha=bg_alpha)
        ax.yaxis.grid(False)
    # Move radial labels away from plotted line
    if tick_loc is None:
        tick_loc = (
            np.mean([angles[0], angles[1]]) / (2 * np.pi) * 360 if circular else 0
        )

    ax.set_rlabel_position(tick_loc)
    ax.set_theta_offset(turning) if turning is not None else None
    ax.tick_params(
        axis="x", labelsize=fontsize, colors=fontcolor
    )  # Optional: for angular labels
    tick_fontsize = fontsize - 2 if fontsize is None else tick_fontsize
    ax.tick_params(
        axis="y", labelsize=tick_fontsize, colors=tick_fontcolor
    )  # For radial labels
    if not circular:
        ax.spines["polar"].set_visible(False)
    ax.tick_params(axis="x", pad=sp)  # move spines outward
    ax.tick_params(axis="y", pad=sp)  # move spines outward
    # colors
    if facecolor is not None:
        if not isinstance(facecolor, list):
            facecolor = [facecolor]
        colors = facecolor
    else:
        colors = (
            get_color(data.shape[1])
            if cmap is None
            else plt.get_cmap(cmap)(np.linspace(0, 1, data.shape[1]))
        )

    # Plot each row with straight lines
    for i, (col, val) in enumerate(data.items()):
        values = val.tolist()
        values += values[:1]  # Close the loop
        ax.plot(
            angles,
            values,
            color=colors[i],
            linewidth=linewidth,
            linestyle=linestyle,
            label=col,
            clip_on=False,
        )
        ax.fill(angles, values, color=colors[i], alpha=alpha)
        # Add text labels for each value at each angle
        labeled_points = set()  # 这样同一个点就不会标多次了
        if show_value:
            for angle, value in zip(angles, values):
                if (angle, value) not in labeled_points:
                    # offset_radius = value * value_offset
                    lim_ = np.max(values)
                    sep_in = lim_ / 5
                    sep_low = sep_in * 2
                    sep_med = sep_in * 3
                    sep_hig = sep_in * 4
                    sep_out = lim_ * 5
                    if value < sep_in:
                        offset_radius = value * 0.7
                    elif value < sep_low:
                        offset_radius = value * 0.8
                    elif sep_low <= value < sep_med:
                        offset_radius = value * 0.85
                    elif sep_med <= value < sep_hig:
                        offset_radius = value * 0.9
                    elif sep_hig <= value < sep_out:
                        offset_radius = value * 0.93
                    else:
                        offset_radius = value * 0.98
                    ax.text(
                        angle,
                        offset_radius,
                        f"{value:{fmt}}",
                        ha="center",
                        va="center",
                        fontsize=fontsize,
                        color=fontcolor,
                        zorder=11,
                    )
                    labeled_points.add((angle, value))

    ax.set_ylim(ylim)
    # Add markers for each data point
    for i, (col, val) in enumerate(data.items()):
        ax.plot(
            angles,
            list(val) + [val[0]],  # Close the loop for markers
            color=colors[i],
            marker=marker,
            markersize=size,
            markeredgecolor=edgecolor,
            markeredgewidth=edge_linewidth,
            zorder=10,
            clip_on=False,
        )
    # ax.tick_params(axis='y', labelleft=False, left=False)
    if "legend" in kws_figsets:
        figsets(ax=ax, **kws_figsets)
    else:

        figsets(
            ax=ax,
            legend=dict(
                loc=legend_loc,
                fontsize=legend_fontsize,
                bbox_to_anchor=[1.1, 1.4],
                ncols=2,
            ),
            **kws_figsets,
        )
    return ax


def pie(
    data: pd.Series,
    columns: list = None,
    facecolor=None,
    explode=[0.1],
    startangle=90,
    shadow=True,
    fontcolor="k",
    fmt=".2f",
    width=None,  # the center blank
    pctdistance=0.85,
    labeldistance=1.1,
    kws_wedge={},
    kws_text={},
    kws_arrow={},
    center=(0, 0),
    radius=1,
    frame=False,
    fontsize=10,
    edgecolor="white",
    edgewidth=1,
    cmap=None,
    show_value=False,
    show_label=True,  # False: only show the outer layer, if it is None, not show
    expand_label=(1.2, 1.2),
    kws_bbox={},  # dict(facecolor="none", alpha=0.5, edgecolor="black", boxstyle="round,pad=0.3"),  # '{}' to hide
    show_legend=True,
    legend_loc="upper right",
    bbox_to_anchor=[1.4, 1.1],
    legend_fontsize=10,
    rotation_correction=0,
    verbose=True,
    ax=None,
    **kwargs,
):
    from adjustText import adjust_text

    if run_once_within(20, reverse=True) and verbose:
        usage_ = """usage:
            pie(
            data:pd.Series,
            columns:list = None,
            facecolor=None,
            explode=[0.1],
            startangle=90,
            shadow=True,
            fontcolor="k",
            fmt=".2f", 
            width=None,# the center blank
            pctdistance=0.85,
            labeldistance=1.1,
            kws_wedge={},
            kws_text={}, 
            center=(0, 0),
            radius=1,
            frame=False,
            fontsize=10,
            edgecolor="white",
            edgewidth=1,
            cmap=None,
            show_value=False,
            show_label=True,# False: only show the outer layer, if it is None, not show
            show_legend=True,
            legend_loc="upper right",
            bbox_to_anchor=[1.4, 1.1],
            legend_fontsize=10,
            rotation_correction=0,
            verbose=True,
            ax=None,
            **kwargs
        )
        
    usage 1: 
    data = {"Segment A": 30, "Segment B": 50, "Segment C": 20}

    ax = pie(
        data=data,
        # columns="Segment A",
        explode=[0, 0.2, 0],
        # width=0.4,
        show_label=False,
        fontsize=10,
        # show_value=1,
        fmt=".3f",
    )

    # prepare dataset
    df = pd.DataFrame(
        data=[
                [80, 90, 60],
                [80, 20, 90],
                [80, 95, 20],
                [80, 95, 20],
                [80, 30, 100],
                [80, 30, 90],
                [80, 80, 50],
            ],
            index=["HP", "MP", "ATK", "DEF", "SP.ATK", "SP.DEF", "SPD"],
            columns=["Hero", "Warrior", "Wizard"],
        )
    usage 1: only plot one column
        pie(
            df,
            columns="Wizard",
            width=0.6,
            show_label=False,
            fmt=".0f",
        )
    usage 2: 
        pie(df,columns=["Hero", "Warrior"],show_label=False)
    usage 3: set different width
        pie(df,
            columns=["Hero", "Warrior", "Wizard"],
            width=[0.3, 0.2, 0.2],
            show_label=False,
            fmt=".0f",
            )
    usage 4: set width the same for all columns
        pie(df,
            columns=["Hero", "Warrior", "Wizard"],
            width=0.2,
            show_label=False,
            fmt=".0f",
            )
    usage 5: adjust the labels' offset
        pie(df, columns="Wizard", width=0.6, show_label=False, fmt=".6f", labeldistance=1.2)

    usage 6: 
        nexttile = subplot(1, 2)
        radar(data=df, columns="Wizard", ax=nexttile(projection="polar"))
        pie(data=df, columns="Wizard", ax=nexttile(), width=0.5, pctdistance=0.7)
    """
        print(usage_)
    # Convert data to a Pandas Series if needed
    if isinstance(data, dict):
        data = pd.DataFrame(pd.Series(data))
    if ~isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    if isinstance(data, pd.DataFrame):
        data = data.select_dtypes(include=np.number)
    if isinstance(columns, str):
        columns = [columns]
    if columns is None:
        columns = list(data.columns)
    # data=data[columns]
    # columns = list(data.columns)
    # print(columns)
    # 选择部分数据
    df = data[columns]

    if not isinstance(explode, list):
        explode = [explode]
    if explode == [None]:
        explode = [0]

    if width is None:
        if df.shape[1] > 1:
            width = 1 / (df.shape[1] + 2)
        else:
            width = 1
    if isinstance(width, (float, int)):
        width = [width]
    if len(width) < df.shape[1]:
        width = width * df.shape[1]
    if isinstance(radius, (float, int)):
        radius = [radius]
    radius_tile = [1] * df.shape[1]
    radius = radius_tile.copy()
    for i in range(1, df.shape[1]):
        radius[i] = radius_tile[i] - np.sum(width[:i])

    # colors
    if facecolor is not None:
        if not isinstance(facecolor, list):
            facecolor = [facecolor]
        colors = facecolor
    else:
        colors = (
            get_color(data.shape[0])
            if cmap is None
            else plt.get_cmap(cmap)(np.linspace(0, 1, data.shape[0]))
        )
    # to check if facecolor is nested list or not
    is_nested = True if any(isinstance(i, list) for i in colors) else False
    inested = 0
    for column_, width_, radius_ in zip(columns, width, radius):
        if column_ != columns[0]:
            labels = data.index if show_label else None
        else:
            labels = data.index if show_label is not None else None
        data = df[column_]
        labels_legend = data.index
        sizes = data.values

        # Set wedge and text properties if none are provided
        kws_wedge = kws_wedge or {"edgecolor": edgecolor, "linewidth": edgewidth}
        kws_wedge.update({"width": width_})
        fontcolor = kws_text.get("color", fontcolor)
        fontsize = kws_text.get("fontsize", fontsize)
        kws_text.update({"color": fontcolor, "fontsize": fontsize})

        if ax is None:
            ax = plt.gca()
        if len(explode) <= len(labels_legend):
            explode.extend([0] * (len(labels_legend) - len(explode)))
        if fmt:
            if not fmt.startswith("%"):
                autopct = f"%{fmt}%%"
        else:
            autopct = None

        if show_value is None:
            result = ax.pie(
                sizes,
                labels=labels,
                autopct=None,
                startangle=startangle + rotation_correction,
                explode=explode,
                colors=colors[inested] if is_nested else colors,
                shadow=shadow,
                pctdistance=pctdistance,
                labeldistance=labeldistance,
                wedgeprops=kws_wedge,
                textprops=kws_text,
                center=center,
                radius=radius_,
                frame=frame,
                **kwargs,
            )
        else:
            result = ax.pie(
                sizes,
                labels=labels,
                autopct=autopct if autopct else None,
                startangle=startangle + rotation_correction,
                explode=explode,
                colors=colors[inested] if is_nested else colors,
                shadow=shadow,  # shadow,
                pctdistance=pctdistance,
                labeldistance=labeldistance,
                wedgeprops=kws_wedge,
                textprops=kws_text,
                center=center,
                radius=radius_,
                frame=frame,
                **kwargs,
            )
        if len(result) == 3:
            wedges, texts, autotexts = result
        elif len(result) == 2:
            wedges, texts = result
            autotexts = None
        #! adjust_text
        if autotexts or texts:
            all_texts = []
            if autotexts and show_value:
                all_texts.extend(autotexts)
            if texts and show_label:
                all_texts.extend(texts)

            adjust_text(
                all_texts,
                ax=ax,
                arrowprops=kws_arrow,  # dict(arrowstyle="-", color="gray", lw=0.5),
                bbox=kws_bbox if kws_bbox else None,
                expand=expand_label,
                fontdict={
                    "fontsize": fontsize,
                    "color": fontcolor,
                },
            )
            # Show exact values on wedges if show_value is True
            if show_value:
                for i, (wedge, txt) in enumerate(zip(wedges, texts)):
                    angle = (wedge.theta2 - wedge.theta1) / 2 + wedge.theta1
                    x = np.cos(np.radians(angle)) * (pctdistance) * radius_
                    y = np.sin(np.radians(angle)) * (pctdistance) * radius_
                    if not fmt.startswith("{"):
                        value_text = f"{sizes[i]:{fmt}}"
                    else:
                        value_text = fmt.format(sizes[i])
                    ax.text(
                        x,
                        y,
                        value_text,
                        ha="center",
                        va="center",
                        fontsize=fontsize,
                        color=fontcolor,
                    )
            inested += 1
    # Customize the legend
    if show_legend:
        ax.legend(
            wedges,
            labels_legend,
            loc=legend_loc,
            bbox_to_anchor=bbox_to_anchor,
            fontsize=legend_fontsize,
            title_fontsize=legend_fontsize,
        )
    ax.set(aspect="equal")
    return ax


def ellipse(
    data,
    x=None,
    y=None,
    hue=None,
    n_std=1.5,
    ax=None,
    confidence=0.95,
    annotate_center=False,
    palette=None,
    facecolor=None,
    edgecolor=None,
    label: bool = True,
    **kwargs,
):
    """
    Plot advanced ellipses representing covariance for different groups
    # simulate data:
                control = np.random.multivariate_normal([0, 0], [[1, 0.5], [0.5, 1]], size=50)
                patient = np.random.multivariate_normal([2, 1], [[1, -0.3], [-0.3, 1]], size=50)
                df = pd.DataFrame(
                    {
                        "Dim1": np.concatenate([control[:, 0], patient[:, 0]]),
                        "Dim2": np.concatenate([control[:, 1], patient[:, 1]]),
                        "Group": ["Control"] * 50 + ["Patient"] * 50,
                    }
                )
                plotxy(
                    data=df,
                    x="Dim1",
                    y="Dim2",
                    hue="Group",
                    kind_="scatter",
                    palette=get_color(8),
                )
                ellipse(
                    data=df,
                    x="Dim1",
                    y="Dim2",
                    hue="Group",
                    palette=get_color(8),
                    alpha=0.1,
                    lw=2,
                )
    Parameters:
        data (DataFrame): Input DataFrame with columns for x, y, and hue.
        x (str): Column name for x-axis values.
        y (str): Column name for y-axis values.
        hue (str, optional): Column name for group labels.
        n_std (float): Number of standard deviations for the ellipse (overridden if confidence is provided).
        ax (matplotlib.axes.Axes, optional): Matplotlib Axes object to plot on. Defaults to current Axes.
        confidence (float, optional): Confidence level (e.g., 0.95 for 95% confidence interval).
        annotate_center (bool): Whether to annotate the ellipse center (mean).
        palette (dict or list, optional): A mapping of hues to colors or a list of colors.
        **kwargs: Additional keyword arguments for the Ellipse patch.

    Returns:
        list: List of Ellipse objects added to the Axes.
    """
    from matplotlib.patches import Ellipse
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    from scipy.stats import chi2

    if ax is None:
        ax = plt.gca()

    # Validate inputs
    if x is None or y is None:
        raise ValueError(
            "Both `x` and `y` must be specified as column names in the DataFrame."
        )
    if not isinstance(data, pd.DataFrame):
        raise ValueError("`data` must be a pandas DataFrame.")

    # Prepare data for hue-based grouping
    ellipses = []
    if hue is not None:
        groups = data[hue].unique()
        colors = sns.color_palette(palette or "husl", len(groups))
        color_map = dict(zip(groups, colors))
    else:
        groups = [None]
        color_map = {None: kwargs.get("edgecolor", "blue")}
    alpha = kwargs.pop("alpha", 0.2)
    edgecolor = kwargs.pop("edgecolor", None)
    facecolor = kwargs.pop("facecolor", None)
    for group in groups:
        group_data = data[data[hue] == group] if hue else data

        # Extract x and y columns for the group
        group_points = group_data[[x, y]].values

        # Compute mean and covariance matrix
        # # 标准化处理
        # group_points = group_data[[x, y]].values
        # group_points -= group_points.mean(axis=0)
        # group_points /= group_points.std(axis=0)

        cov = np.cov(group_points.T)
        mean = np.mean(group_points, axis=0)

        # Eigenvalues and eigenvectors
        eigvals, eigvecs = np.linalg.eigh(cov)
        order = eigvals.argsort()[::-1]
        eigvals, eigvecs = eigvals[order], eigvecs[:, order]

        # Rotation angle and ellipse dimensions
        angle = np.degrees(np.arctan2(*eigvecs[:, 0][::-1]))
        if confidence:
            n_std = np.sqrt(chi2.ppf(confidence, df=2))  # Chi-square quantile
        width, height = 2 * n_std * np.sqrt(eigvals)

        # Create and style the ellipse
        if facecolor is None:
            facecolor_ = color_map[group]
        if edgecolor is None:
            edgecolor_ = color_map[group]
        ellipse = Ellipse(
            xy=mean,
            width=width,
            height=height,
            angle=angle,
            edgecolor=edgecolor_,
            facecolor=(facecolor_, alpha),  # facecolor_, # only work on facecolor
            # alpha=alpha,
            label=group if (hue and label) else None,
            **kwargs,
        )
        ax.add_patch(ellipse)
        ellipses.append(ellipse)

        # Annotate center
        if annotate_center:
            ax.annotate(
                f"Mean\n({mean[0]:.2f}, {mean[1]:.2f})",
                xy=mean,
                xycoords="data",
                fontsize=10,
                ha="center",
                color=ellipse_color,
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    edgecolor="gray",
                    facecolor="white",
                    alpha=0.8,
                ),
            )

    return ax

def ppi(
    df: pd.DataFrame,
    player1 = "preferredName_A",
    player2 = "preferredName_B",
    weight = "score",
    n_layers = None,  # Number of concentric layers
    n_rank = [5, 10],  # Nodes in each rank for the concentric layout
    dist_node = 10,  # Distance between each rank of circles
    layout = "auto", 
    size = None,  # 700,
    sizes = (50, 500),  # min and max of size
    facecolor = "skyblue",# only works when cmap is None,otherwise it would be set up based on degree(node num)
    cmap = "coolwarm", # indicating degree(node num)
    edgecolor = "k",
    edgelinewidth = 1.5,
    alpha = 0.5,
    alphas = (0.1, 1.0),  # min and max of alpha
    marker = "o",
    node_hideticks = True,
    linecolor = "gray",
    line_cmap = "coolwarm",
    linewidth = 1.5,
    linewidths = (0.5, 5),  # min and max of linewidth
    linealpha = 1.0,
    linealphas = (0.1, 1.0),  # min and max of linealpha
    linestyle = "-",
    line_arrowstyle = "-",
    fontsize = 10,
    fontcolor = "k",
    ha: str = "center",
    va: str = "center",
    figsize = (12, 10),
    k_value = 0.3,
    bgcolor = "w",
    dir_save = "./ppi_network.html",
    physics = True,
    notebook = False,
    scale = 1,
    ax = None,
    layout_params = None,# for umap or pca...
    # 3D specific parameters
    elev = 30,
    azim = 45,
    edge_alpha_3d = 0.3,
    node_edgecolor_3d = "darkgray",
    node_linewidth_3d = 0.5,
    show_edges_3d = True,
    edge_width_3d = 1.0,
    edge_linestyle_3d = "-",
    # Preprocessing parameters
    drop_na=True,
    remove_self_loops=True,
    remove_duplicates=False,
    min_weight=None,
    max_weight=None,
    verbose: bool=True,
    **kwargs,
):
    """
    Author: Jianfeng.Liu (Jianfeng.Liu0413@gmail.com)
    Date created: 2019-03-20
    
    Plot Protein-Protein Interaction (PPI) networks with extensive customization options.
    
    it creates interactive network visualizations from interaction data,
    supporting both 2D and 3D layouts with customizable node/edge appearance.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing interaction data with at least three columns:
        source nodes, target nodes, and interaction weights.
    
    player1, player2 : str, default="preferredName_A", "preferredName_B"
        Column names in df DataFrame for source and target nodes.
        
    weight : str, default="score"
        Column name for interaction weights/strengths.
    
    # Layout Parameters
    layout : str, default="auto"
        Network layout algorithm. Options:
        - "auto": Automatically choose based on network size
        - "spring": Force-directed layout (Fruchterman-Reingold)
        - "circular": Nodes arranged in a circle
        - "kamada_kawai": Force-directed with optimal distances
        - "spectral": Spectral layout using eigenvectors
        - "random": Random node positions
        - "shell": Concentric circles
        - "planar": Planar layout if graph is planar
        - "spiral": Spiral layout
        - "degree": Nodes arranged by degree in concentric circles
        - "community": Community detection with Louvain algorithm
        - "hierarchical": Hierarchical layout (requires graphviz)
        - "umap": UMAP dimensionality reduction
        - "pca": PCA dimensionality reduction
    
    n_layers : int, optional
        Number of concentric layers for "degree" layout.
    
    n_rank : list, default=[5, 10]
        Number of nodes in each rank for concentric "degree" layout.
    
    dist_node : float, default=10
        Distance between concentric circles in "degree" layout.
    
    layout_params : dict, optional
        Additional parameters for specific layouts:
        - For UMAP: n_neighbors, min_dist, metric, n_components
        - For PCA: n_components
    
    k_value : float, default=0.3
        Optimal distance between nodes for spring layout.
    
    scale : float, default=1
        Scale factor for node positions.
    
    # Node Appearance Parameters
    size : int, float, or list, optional
        Node sizes. If None, sizes are scaled by node degree.
        Example: size=100 (all nodes same size) or size=[100, 150, 200] (per-node sizes)
    
    sizes : tuple, default=(50, 500)
        Minimum and maximum node size range for automatic scaling.
    
    facecolor : str or list, default="skyblue"
        only works when cmap is None,otherwise it would be set up based on degree(node num)
        Node colors. Can be single color or list of colors per node.
        Example: "red", ["red", "blue", "green"], or based on degree
    
    cmap : str, default="coolwarm"
        Colormap for node colors when colored by degree.
    
    alpha : float or list, default=0.5
        Node transparency (0=transparent, 1=opaque).
    
    alphas : tuple, default=(0.1, 1.0)
        Minimum and maximum alpha range for automatic scaling.
    
    marker : str, default="o"
        Node marker shape. Options: "o", "s", "^", "D", "v", etc.
    
    node_hideticks : bool, default=True
        Hide node axis ticks.
    
    # Edge Appearance Parameters  
    linecolor : str or list, default="gray"
        if linecolor is None, then it would be auto-setup based on degrees.
        Edge colors. Can be single color or list of colors per edge.
    
    line_cmap : str, default="coolwarm"
        only works when linecolor is None;
        Colormap for edge colors when colored by weight.
    
    linewidth : float or list, default=1.5
        Edge widths. Can be single value or list per edge.
    
    linewidths : tuple, default=(0.5, 5)
        Minimum and maximum edge width range for automatic scaling.
    
    linealpha : float or list, default=1.0
        Edge transparency.
    
    linealphas : tuple, default=(0.1, 1.0)
        Minimum and maximum edge alpha range for automatic scaling.
    
    linestyle : str, default="-"
        Edge line style. Options: "-", "--", "-.", ":".
    
    line_arrowstyle : str, default="-"
        Edge arrow style (for directed graphs).
    
    # Label Parameters
    fontsize : int, default=10
        Node label font size.
    
    fontcolor : str, default="k"
        Node label color.
    
    ha, va : str, default="center", "center"
        Horizontal and vertical alignment of node labels.
    
    # Figure & Output Parameters
    figsize : tuple, default=(12, 10)
        Figure size (width, height) in inches.
    
    bgcolor : str, default="w"
        Background color.
    
    dir_save : str, default="./ppi_network.html"
        Output path for saving interactive HTML and GraphML files.
    
    physics : bool, default=True
        Enable physics simulation in interactive plot.
    
    notebook : bool, default=False
        Optimize for Jupyter notebook display.
    
    ax : matplotlib.axes.Axes, optional
        Existing axes to plot on.
    
    # 3D Plotting Parameters
    elev : float, default=30
        Elevation angle for 3D plots.
    
    azim : float, default=45
        Azimuth angle for 3D plots.
    
    edge_alpha_3d : float, default=0.3
        Edge transparency in 3D plots.
    
    node_edgecolor_3d : str, default="darkgray"
        Node border color in 3D plots.
    
    node_linewidth_3d : float, default=0.5
        Node border width in 3D plots.
    
    show_edges_3d : bool, default=True
        Show edges in 3D plots.
    
    edge_width_3d : float, default=1.0
        Edge width in 3D plots.
    
    edge_linestyle_3d : str, default="-"
        Edge line style in 3D plots.
    
    **kwargs : dict
        Additional keyword arguments passed to matplotlib.

    Returns
    -------
    G : networkx.Graph
        The created graph object.
    
    ax : matplotlib.axes.Axes or tuple
        Axes object for 2D plots, or (fig, ax) tuple for 3D plots.
    """
    usage_str="""
        Examples
        --------
        >>> # Basic usage with default parameters
        >>> G, ax = ppi(df)
        
        >>> # Customize node appearance by degree
        >>> G, ax = ppi(
        ...     df,
        ...     layout="spring",
        ...     facecolor="degree",  # Color by degree
        ...     size=None,  # Size by degree
        ...     cmap="viridis",
        ...     sizes=(30, 300)
        ... )
        
        >>> # Concentric layout by degree
        >>> G, ax = ppi(
        ...     df,
        ...     layout="degree",
        ...     n_layers=4,
        ...     n_rank=[5, 10, 15, 20],
        ...     dist_node=15
        ... )
        
        >>> # Community detection layout
        >>> G, ax = ppi(
        ...     df,
        ...     layout="community",
        ...     facecolor="degree",
        ...     cmap="Set3"
        ... )
        
        >>> # 3D UMAP layout
        >>> G, (fig, ax) = ppi(
        ...     df,
        ...     layout="umap",
        ...     layout_params={"n_components": 3},  # Force 3D
        ...     elev=20,
        ...     azim=60,
        ...     node_edgecolor_3d="black"
        ... )
        
        >>> # Custom edge styling by weight
        >>> G, ax = ppi(
        ...     df,
        ...     linecolor="weight",  # Color edges by weight
        ...     line_cmap="plasma",
        ...     linewidth="weight",  # Width by weight
        ...     linewidths=(0.5, 3)
        ... )
        
        >>> # Save with custom filename
        >>> G, ax = ppi(
        ...     df,
        ...     dir_save="./my_network.html",
        ...     bgcolor="black",
        ...     fontcolor="white"
        ... )
        
        >>> # Advanced: Custom column names and filtering
        >>> filtered_df = df[df['score'] > 0.5]
        >>> G, ax = ppi(
        ...     filtered_df,
        ...     player1="gene_A",
        ...     player2="gene_B", 
        ...     weight="interaction_strength",
        ...     layout="kamada_kawai"
        ... )
        
        Notes
        -----
        - The function automatically detects 3D coordinates and switches to 3D plotting
        - For large networks (>1000 nodes), consider using "spring" or "umap" layouts
        - Interactive HTML output can be opened in web browsers and edited in Cytoscape
        - Node degrees are calculated automatically for coloring and sizing
        - The function returns both the graph object and axes for further customization
    """
    from pyvis.network import Network
    import networkx as nx
    from IPython.display import IFrame
    from matplotlib.colors import Normalize
    from matplotlib import cm
    from . import ips
    from sklearn.decomposition import PCA
    try:
        import umap
        has_umap = True
    except ImportError:
        has_umap = False
        print("UMAP not installed — skipping UMAP layout.")
    try:
        import community as community_louvain
    except ImportError:
        community_louvain = None
    VERBOSE = True if verbose else False
    #==========to handle pca/umap: n_components >2
    def _reduce_to_2d(coords):
        """Reduce any coordinate matrix to 2D for plotting."""
        if coords.shape[1] > 2:
            coords_2d = coords[:, :2]  # keep only first two dimensions
        else:
            coords_2d = coords
        return coords_2d
    
    def plot_graph_3d(
        G, 
        pos, 
        node_color="skyblue", 
        edge_color="gray", 
        node_size=100,
        edge_alpha=0.3,
        figsize=(10, 8),
        elev=30,
        azim=45,
        axis_off=True,
        fontsize=10,
        fontcolor="k",
        ha="center",
        va="center",
        **plot_kwargs
    ):
        """
        Optimized 3D network visualization with node labels.
        """
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")
        
        # Extract coordinates efficiently
        nodes = list(G.nodes())
        xs = np.array([pos[n][0] for n in nodes])
        ys = np.array([pos[n][1] for n in nodes])
        zs = np.array([pos[n][2] for n in nodes])
        
        # Handle node colors and sizes
        if isinstance(node_color, str):
            node_color = [node_color] * len(nodes)
        if isinstance(node_size, (int, float)):
            node_size = [node_size] * len(nodes)
        
        # Plot nodes with vectorized operations
        scatter = ax.scatter(
            xs, ys, zs, 
            s=node_size, 
            c=node_color,
            alpha=plot_kwargs.get('node_alpha', 1.0),
            edgecolors=plot_kwargs.get('node_edgecolor', 'darkgray'),
            linewidth=plot_kwargs.get('node_linewidth', 0.5),
            marker=plot_kwargs.get('node_marker', 'o')
        )
        
        # Add node labels
        label_offset = plot_kwargs.get('label_offset', 0.1)  # Offset to prevent overlapping
        for i, node in enumerate(nodes):
            ax.text(
                xs[i] + label_offset, 
                ys[i] + label_offset, 
                zs[i] + label_offset,
                node,
                fontsize=fontsize,
                color=fontcolor,
                ha=ha,
                va=va,
                bbox=dict(
                    boxstyle='round,pad=0.2',
                    facecolor='white',
                    alpha=0.7,
                    edgecolor='none'
                )
            )
        
        # Plot edges efficiently
        if plot_kwargs.get('show_edges', True):
            edge_colors = [edge_color] * G.number_of_edges() if isinstance(edge_color, str) else edge_color
            
            for i, (u, v) in enumerate(G.edges()):
                x = [pos[u][0], pos[v][0]]
                y = [pos[u][1], pos[v][1]] 
                z = [pos[u][2], pos[v][2]]
                
                ax.plot(
                    x, y, z, 
                    color=edge_colors[i] if i < len(edge_colors) else edge_color,
                    alpha=edge_alpha,
                    linewidth=plot_kwargs.get('edge_width', 1.0),
                    linestyle=plot_kwargs.get('edge_linestyle', '-')
                )
        
        # Styling
        ax.set_xlabel(plot_kwargs.get('xlabel', 'X'))
        ax.set_ylabel(plot_kwargs.get('ylabel', 'Y')) 
        ax.set_zlabel(plot_kwargs.get('zlabel', 'Z'))
        
        # Set equal aspect ratio
        max_range = max(np.ptp(xs), np.ptp(ys), np.ptp(zs))
        mid_x, mid_y, mid_z = np.mean(xs), np.mean(ys), np.mean(zs)
        ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
        ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2) 
        ax.set_zlim(mid_z - max_range/2, mid_z + max_range/2)
        
        # Viewing angle
        ax.view_init(elev=elev, azim=azim)
        
        if axis_off:
            ax.set_axis_off()
        
        # Add colorbar if colormapped
        if hasattr(scatter, 'set_array') and scatter.get_array() is not None:
            plt.colorbar(scatter, ax=ax, shrink=0.6, aspect=20, 
                        label=plot_kwargs.get('colorbar_label', ''))
        
        plt.tight_layout()
        return fig, ax

    if run_once_within():
        print(usage_str)
    # ===== DATA PREPROCESSING =====
    print("data preprocessing...") if VERBOSE else None
    original_count = len(df)
    df_clean = df.copy()

    # 1. Check required columns exist
    required_cols = [player1, player2, weight]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    print(f"Original dataset: shape: {df.shape}") if VERBOSE else None

    # 2. Drop NA values in key columns
    if drop_na:
        na_mask = df_clean[required_cols].isna().any(axis=1)
        na_count = na_mask.sum()
        if na_count > 0:
            df_clean = df_clean[~na_mask]
            print(f"Removed {na_count} df with missing values") if VERBOSE else None
    # 2. Smart NA handling with granular control
    if drop_na:
        # Check each column separately
        na_player1 = df_clean[player1].isna().sum()
        na_player2 = df_clean[player2].isna().sum()
        na_weight = df_clean[weight].isna().sum()
        
        total_na = na_player1 + na_player2 + na_weight
        
        if total_na > 0:
            # Remove rows with missing node names (critical)
            node_na_mask = df_clean[[player1, player2]].isna().any(axis=1)
            critical_na_count = node_na_mask.sum()
            
            if critical_na_count > 0:
                df_clean = df_clean[~node_na_mask]
                print(f"Removed {critical_na_count} interactions with missing node names") if VERBOSE else None
            
            # Handle missing weights separately (less critical)
            weight_na_mask = df_clean[weight].isna()
            weight_na_count = weight_na_mask.sum()
            
            if weight_na_count > 0:
                # Option A: Remove weight-missing rows
                df_clean = df_clean[~weight_na_mask]
                print(f"Removed {weight_na_count} interactions with missing weights") if VERBOSE else None
                
                # Option B: Fill with default weight (alternative)
                # df_clean[weight] = df_clean[weight].fillna(1.0)
                # print(f"Filled {weight_na_count} missing weights with default value 1.0") if VERBOSE else None
                
    # 3. Remove self-loops
    if remove_self_loops:
        self_loop_mask = df_clean[player1] == df_clean[player2]
        self_loop_count = self_loop_mask.sum()
        if self_loop_count > 0:
            df_clean = df_clean[~self_loop_mask]
            print(f"Removed {self_loop_count} self-loops") if VERBOSE else None

    # 4. Remove duplicates (keep highest weight)
    if remove_duplicates:
        original_count = len(df_clean)
        
        # Safer temporary column name
        temp_key = '__edge_key_temp__'
        
        # More efficient key creation without apply
        nodes_sorted = np.sort(df_clean[[player1, player2]].values, axis=1)
        df_clean[temp_key] = nodes_sorted[:, 0] + '|' + nodes_sorted[:, 1]
        
        # Sort by weight (descending) and keep first occurrence
        df_clean = df_clean.sort_values(weight, ascending=False)
        
        # Check if we have any duplicates to remove
        duplicate_mask = df_clean.duplicated(subset=[temp_key], keep='first')
        duplicates_removed = duplicate_mask.sum()
        
        if duplicates_removed > 0:
            df_clean = df_clean[~duplicate_mask]
            print(f"Removed {duplicates_removed} duplicate interactions (kept highest weight)") if VERBOSE else None
            
            # Additional info about what was kept
            if VERBOSE and duplicates_removed > 0:
                kept_count = len(df_clean)
                print(f"   • Kept {kept_count} unique interactions")
                
        # Clean up temporary column
        df_clean = df_clean.drop(temp_key, axis=1)
    
    # 5. Filter by weight thresholds
    if min_weight is not None:
        below_threshold = df_clean[weight] < min_weight
        below_count = below_threshold.sum()
        if below_count > 0:
            df_clean = df_clean[~below_threshold]
            print(f"Removed {below_count} df below weight threshold {min_weight}") if VERBOSE else None

    if max_weight is not None:
        above_threshold = df_clean[weight] > max_weight
        above_count = above_threshold.sum()
        if above_count > 0:
            df_clean = df_clean[~above_threshold]
            print(f"Removed {above_count} df above weight threshold {max_weight}") if VERBOSE else None

    # 6. Check for empty dataset after preprocessing
    if len(df_clean) == 0:
        raise ValueError("No df remaining after preprocessing! Check your filters.")

    # 7. Final statistics
    final_count = len(df_clean)
    removed_count = original_count - final_count
    removal_percentage = (removed_count / original_count) * 100 if original_count > 0 else 0

    print(f"Preprocessing complete:") if VERBOSE else None
    print(f"   • Removed {removed_count} df ({removal_percentage:.1f}%)") if VERBOSE else None
    print(f"   • Final dataset: {final_count} df") if VERBOSE else None
    print(f"   • Unique nodes: {len(set(df_clean[player1].tolist() + df_clean[player2].tolist()))}") if VERBOSE else None
    print(f"cleanded dataset: shape: {df_clean.shape}") if VERBOSE else None
    
    # Replace original df with cleaned version
    df = df_clean.sort_values(by=weight, ascending=False)
    
    # Initialize Pyvis network
    net = Network(height="750px", width="100%", bgcolor=bgcolor, font_color=fontcolor)
    net.force_atlas_2based(
        gravity=-50, central_gravity=0.01, spring_length=100, spring_strength=0.1
    )
    net.toggle_physics(physics)

    kws_figsets = {}
    for k_arg, v_arg in kwargs.items():
        if "figset" in k_arg:
            kws_figsets = v_arg
            kwargs.pop(k_arg, None)
            break

    # Create a NetworkX graph from the interaction data
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row[player1], row[player2], weight=row[weight])
    # G = nx.from_pandas_edgelist(df, source=player1, target=player2, edge_attr=weight)

    # Calculate node degrees
    degrees = dict(G.degree())
    norm = Normalize(vmin=min(degrees.values()), vmax=max(degrees.values()))
    colormap = cm.get_cmap(cmap)  # Get the 'coolwarm' colormap

    if not isa(facecolor, "color"):
        print("facecolor: based on degrees") if VERBOSE else None
        facecolor = [colormap(norm(deg)) for deg in degrees.values()]  # Use colormap
    num_nodes = G.number_of_nodes()
    # * size
    # Set properties based on degrees
    if not isinstance(size, (int, float, list)):
        print("size: based on degrees") if VERBOSE else None
        size = [deg * 50 for deg in degrees.values()]  # Scale sizes
    size = (
        (size[:num_nodes] if len(size) > num_nodes else size)
        if isinstance(size, list)
        else [size] * num_nodes
    )
    if isinstance(size, list) and len(ips.flatten(size, verbose=False)) != 1:
        # Normalize sizes
        min_size, max_size = sizes  # Use sizes tuple for min and max values
        min_degree, max_degree = min(size), max(size)
        if max_degree > min_degree:  # Avoid division by zero
            size = [
                min_size
                + (max_size - min_size) * (sz - min_degree) / (max_degree - min_degree)
                for sz in size
            ]
        else:
            # If all values are the same, set them to a default of the midpoint
            size = [(min_size + max_size) / 2] * len(size)

    # * facecolor
    facecolor = (
        (facecolor[:num_nodes] if len(facecolor) > num_nodes else facecolor)
        if isinstance(facecolor, list)
        else [facecolor] * num_nodes
    )
    # * facealpha
    if isinstance(alpha, list):
        alpha = (
            alpha[:num_nodes]
            if len(alpha) > num_nodes
            else alpha + [alpha[-1]] * (num_nodes - len(alpha))
        )
        min_alphas, max_alphas = alphas  # Use alphas tuple for min and max values
        if len(alpha) > 0:
            # Normalize alpha based on the specified min and max
            min_alpha, max_alpha = min(alpha), max(alpha)
            if max_alpha > min_alpha:  # Avoid division by zero
                alpha = [
                    min_alphas
                    + (max_alphas - min_alphas)
                    * (ea - min_alpha)
                    / (max_alpha - min_alpha)
                    for ea in alpha
                ]
            else:
                # If all alpha values are the same, set them to the average of min and max
                alpha = [(min_alphas + max_alphas) / 2] * len(alpha)
        else:
            # Default to a full opacity if no edges are provided
            alpha = [1.0] * num_nodes
    else:
        # If alpha is a single value, convert it to a list and normalize it
        alpha = [alpha] * num_nodes  # Adjust based on alphas

    for i, node in enumerate(G.nodes()):
        net.add_node(
            node,
            label=node,
            size=size[i],
            color=facecolor[i],
            alpha=alpha[i],
            font={"size": fontsize, "color": fontcolor},
        )
    print(f"nodes number: {i+1}") if VERBOSE else None

    for edge in G.edges(data=True):
        net.add_edge(
            edge[0],
            edge[1],
            weight=edge[2]["weight"],
            color=edgecolor,
            width=edgelinewidth * edge[2]["weight"],
        )
    # ===== Layout selection =====
    if "auto" in layout.lower():
        if G.number_of_nodes() <= 50:
            layout = "spring"
        elif community_louvain:
            layout = "community"
        else:
            layout = "spectral"
        print(f"Auto-selected layout: {layout}") if VERBOSE else None
    layouts = [
        "auto","community","spectral","fruchterman_reingold","hierarchical",
        "umap","pca","spring","circular","kamada_kawai","random","shell",
        "planar","spiral","degree",]
    layout = ips.strcmp(layout, layouts)[0]
    print(f"layout:{layout}, or select one in {layouts}") if VERBOSE else None

    # load the layout params
    layout_params = layout_params or {}

    # compute dimensional embeddings
    def _get_pos_from_embedding(embedding, nodes):
        """Convert embedding array to node position dict."""
        if embedding.shape[1] == 2:
            pos = {node: embedding[i, :2] for i, node in enumerate(nodes)}
        elif embedding.shape[1] == 3:
            pos = {node: embedding[i, :3] for i, node in enumerate(nodes)}
        else:
            print(f":warning: embedding with {embedding.shape[1]} dims — using first 2 for plot.")
            pos = {node: embedding[i, :2] for i, node in enumerate(nodes)}
        return pos
    
    # Choose layout
    if layout == "spring":
        pos = nx.spring_layout(G, k=k_value)
    elif layout == "fruchterman_reingold":
        pos = nx.fruchterman_reingold_layout(G)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    elif layout == "spectral":
        pos = nx.spectral_layout(G)
    elif layout == "random":
        pos = nx.random_layout(G)
    elif layout == "shell":
        pos = nx.shell_layout(G)
    elif layout == "planar":
        if nx.check_planarity(G)[0]:
            pos = nx.planar_layout(G)
        else:
            print("Graph is not planar; switching to spring layout.") if VERBOSE else None
            pos = nx.spring_layout(G, k=k_value)
    elif layout == "spiral":
        pos = nx.spiral_layout(G)
    elif layout == "degree":
        # Calculate node degrees and sort nodes by degree
        degrees = dict(G.degree())
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        norm = Normalize(vmin=min(degrees.values()), vmax=max(degrees.values()))
        colormap = cm.get_cmap(cmap)

        # Create positions for concentric circles based on n_layers and n_rank
        pos = {}
        n_layers = len(n_rank) + 1 if n_layers is None else n_layers
        for rank_index in range(n_layers):
            if rank_index < len(n_rank):
                nodes_per_rank = n_rank[rank_index]
                rank_nodes = sorted_nodes[
                    sum(n_rank[:rank_index]) : sum(n_rank[: rank_index + 1])
                ]
            else:
                # 随机打乱剩余节点的顺序
                remaining_nodes = sorted_nodes[sum(n_rank[:rank_index]) :]
                random_indices = np.random.permutation(len(remaining_nodes))
                rank_nodes = [remaining_nodes[i] for i in random_indices]

            radius = (rank_index + 1) * dist_node  # Radius for this rank

            # Arrange nodes in a circle for the current rank
            for i, (node, degree) in enumerate(rank_nodes):
                angle = (i / len(rank_nodes)) * 2 * np.pi  # Distribute around circle
                pos[node] = (radius * np.cos(angle), radius * np.sin(angle))
    elif layout == "community" and community_louvain:
        partition = community_louvain.best_partition(G)
        pos = nx.spring_layout(G, k=k_value, seed=0)
        for node, cluster in partition.items():
            pos[node] = (pos[node][0] + cluster * 2, pos[node][1] + cluster * 2)
    elif layout == "hierarchical":
        try:
            from networkx.drawing.nx_agraph import graphviz_layout
            pos = graphviz_layout(G, prog="dot")
        except Exception:
            print("graphviz not available — fallback to spring layout")
            pos = nx.spring_layout(G, k=k_value)
    elif layout == "umap" and has_umap:
        adj = nx.to_numpy_array(G)
        n_neighbors = layout_params.get("n_neighbors", 10)
        min_dist = layout_params.get("min_dist", 0.3)
        metric = layout_params.get("metric", "cosine")
        n_comp = layout_params.get("n_components", 2)
        umap_embed = umap.UMAP(
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            metric=metric,
            n_components=n_comp,random_state=0
        ).fit_transform(adj)
        pos = _get_pos_from_embedding(umap_embed, list(G.nodes()))
    elif layout == "pca":
        adj = nx.to_numpy_array(G)
        n_comp = layout_params.get("n_components", 2)
        pca_embed = PCA(n_components=n_comp).fit_transform(adj)
        pos = _get_pos_from_embedding(pca_embed, list(G.nodes()))

    else:
        print(
            f"Unknown layout '{layout}', defaulting to 'spring',or可以用这些: {layouts}"
        )
        pos = nx.spring_layout(G, k=k_value)

    # Check for 3D positions and use optimized 3D plotting
    any_3d = any(len(v) == 3 for v in pos.values())
    if any_3d:
        print("Detected 3D embedding — rendering optimized 3D plot.") if VERBOSE else None
        fig_3d, ax_3d = plot_graph_3d(
            G, 
            pos, 
            node_color=facecolor, 
            edge_color=linecolor, 
            node_size=size,
            edge_alpha=edge_alpha_3d,
            figsize=figsize,
            elev=elev,
            azim=azim,
            node_edgecolor=node_edgecolor_3d,
            node_linewidth=node_linewidth_3d,
            show_edges=show_edges_3d,
            edge_width=edge_width_3d,
            edge_linestyle=edge_linestyle_3d,
            **kwargs
        )
        
        # Save 3D plot if requested
        if dir_save:
            
            plt.savefig(dir_save.replace('.html', '_3d.png'), dpi=300, bbox_inches='tight')
            print(f"3D plot saved as {dir_save.replace('.html', '_3d.png')}") if VERBOSE else None
            
        return G, (fig_3d, ax_3d)  
 
    for node, (x, y) in pos.items():
        net.get_node(node)["x"] = x * scale
        net.get_node(node)["y"] = y * scale

    # If ax is None, use plt.gca()
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)

    # Draw nodes, edges, and labels with customization options
    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_size=size,
        node_color=facecolor,
        linewidths=edgelinewidth,
        edgecolors=edgecolor,
        alpha=alpha,
        hide_ticks=node_hideticks,
        node_shape=marker,
    )

    # * linewidth
    if isinstance(linewidth, str) and linewidth in df.columns:
        # linewidth is a column name - use those values for edge widths
        print(f"Setting edge widths based on '{linewidth}' column") if VERBOSE else None
        
        # Create a mapping from edges to the linewidth values
        edge_to_weight = {}
        for _, row in df.iterrows():
            node1, node2 = row[player1], row[player2]
            # Create both possible edge directions since graph is undirected
            edge_to_weight[(node1, node2)] = row[linewidth]
            edge_to_weight[(node2, node1)] = row[linewidth]
        
        # Get linewidth values for each edge in the graph
        linewidth_values = []
        for u, v in G.edges():
            weight_val = edge_to_weight.get((u, v), 1.0)
            linewidth_values.append(weight_val)
        
        # Normalize to the specified linewidths range
        min_lw, max_lw = linewidths
        if len(set(linewidth_values)) > 1:
            min_val = min(linewidth_values)
            max_val = max(linewidth_values)
            linewidth = [
                min_lw + (max_lw - min_lw) * (w - min_val) / (max_val - min_val)
                for w in linewidth_values
            ]
        else:
            # If all values are the same, use midpoint
            linewidth = [(min_lw + max_lw) / 2] * len(linewidth_values)
    elif not isinstance(linewidth, (list, np.ndarray)):
        linewidth = [float(linewidth)] * G.number_of_edges()
    else:
        linewidth = (
            linewidth[: G.number_of_edges()]
            if len(linewidth) > G.number_of_edges()
            else linewidth + [linewidth[-1]] * (G.number_of_edges() - len(linewidth))
        )
        # Normalize linewidth if it is a list
        if isinstance(linewidth, list):
            min_linewidth, max_linewidth = min(linewidth), max(linewidth)
            vmin, vmax = linewidths  # Use linewidths tuple for min and max values
            if max_linewidth > min_linewidth:  # Avoid division by zero
                # Scale between vmin and vmax
                linewidth = [
                    vmin
                    + (vmax - vmin)
                    * (lw - min_linewidth)
                    / (max_linewidth - min_linewidth)
                    for lw in linewidth
                ]
            else:
                # If all values are the same, set them to a default of the midpoint
                linewidth = [(vmin + vmax) / 2] * len(linewidth)
        else:
            # If linewidth is a single value, convert it to a list of that value
            linewidth = [linewidth] * G.number_of_edges()

    # * linecolor
    if not isinstance(linecolor, str):
        weights = [G[u][v]["weight"] for u, v in G.edges()]
        norm = Normalize(vmin=min(weights), vmax=max(weights))
        colormap = cm.get_cmap(line_cmap)
        linecolor = [colormap(norm(weight)) for weight in weights]
    else:
        linecolor = [linecolor] * G.number_of_edges()

    # * linealpha
    if isinstance(linealpha, list):
        linealpha = (
            linealpha[: G.number_of_edges()]
            if len(linealpha) > G.number_of_edges()
            else linealpha + [linealpha[-1]] * (G.number_of_edges() - len(linealpha))
        )
        min_alpha, max_alpha = linealphas  # Use linealphas tuple for min and max values
        if len(linealpha) > 0:
            min_linealpha, max_linealpha = min(linealpha), max(linealpha)
            if max_linealpha > min_linealpha:  # Avoid division by zero
                linealpha = [
                    min_alpha
                    + (max_alpha - min_alpha)
                    * (ea - min_linealpha)
                    / (max_linealpha - min_linealpha)
                    for ea in linealpha
                ]
            else:
                linealpha = [(min_alpha + max_alpha) / 2] * len(linealpha)
        else:
            linealpha = [1.0] * G.number_of_edges()  # 如果设置有误,则将它设置成1.0
    else:
        linealpha = [linealpha] * G.number_of_edges()  # Convert to list if single value

    nx.draw_networkx_edges(
        G,
        pos,
        ax=ax,
        edge_color=linecolor,
        width=linewidth,
        style=linestyle,
        arrows=True if line_arrowstyle else False, # only works if arrows=True and with the proper connectionstyle.
        arrowstyle=line_arrowstyle,
        alpha=linealpha,
    )

    nx.draw_networkx_labels(
        G,
        pos,
        ax=ax,
        font_size=fontsize,
        font_color=fontcolor,
        horizontalalignment=ha,
        verticalalignment=va,
    )
    figsets(ax=ax, **kws_figsets)
    ax.axis("off")
    if dir_save:
        if not os.path.basename(dir_save):
            dir_save = "_.html"
        net.write_html(dir_save)
        nx.write_graphml(G, dir_save.replace(".html", "_CytoscapeEditable.graphml"))  # Export to GraphML
        print(f"could be edited in Cytoscape \n{dir_save.replace(".html",".graphml")}")
        ips.figsave(dir_save.replace(".html", ".pdf"))
    return G, ax

def plot_map(
    location=[39.949610, -75.150282],  # Default center of the map
    zoom_start=16,  # Default zoom level
    tiles="OpenStreetMap",  # Tile style for Folium
    markers=None,  # List of marker dictionaries for Folium
    overlays=None,  # List of overlays (e.g., GeoJson, PolyLine, Circle) for Folium
    custom_layers=None,  # List of custom Folium layers
    fit_bounds=None,  # Coordinates to fit map bounds
    plugins=None,  # List of Folium plugins to add
    scroll_wheel_zoom=True,  # Enable/disable scroll wheel zoom
    map_width=725,  # Map display width for Streamlit
    map_height=None,  # Map display height for Streamlit
    output="normale",  # "streamlit" or "offline" rendering
    save_path=None,  # Path to save the map in offline mode
    pydeck_map=False,  # Whether to use pydeck for rendering (True for pydeck)
    pydeck_style="mapbox://styles/mapbox/streets-v11",  # Map style for pydeck
    verbose=True,  # show usage
    **kwargs,  # Additional arguments for Folium Map
):
    """
    Creates a customizable Folium or pydeck map and renders it in Streamlit or saves offline.

    # get all built-in tiles
    from py2ls import netfinder as nt
    sp = nt.get_soup(url, driver="se")
    url = "https://leaflet-extras.github.io/leaflet-providers/preview/"
    tiles_support = nt.fetch(sp,"span",class_="leaflet-minimap-label")
    df_tiles = pd.DataFrame({"tiles": tiles_support})
    fsave("....tiles.csv",df_tiles)
    """
    config_markers = """from folium import Icon
    # https://github.com/lennardv2/Leaflet.awesome-markers?tab=readme-ov-file
    markers = [
        {
            "location": [loc[0], loc[1]],
            "popup": "Center City",
            "tooltip": "Philadelphia",
            "icon": Icon(color="red", icon="flag"),
        },
        {
            "location": [loc[0], loc[1] + 0.05],
            "popup": "Rittenhouse Square",
            "tooltip": "A lovely park",
            "icon": Icon(
                color="purple", icon="flag", prefix="fa"
            ),  # Purple marker with "star" icon (Font Awesome)
        },
    ]"""
    config_overlay = """
    from folium import Circle

    circle = Circle(
        location=loc,
        radius=300,  # In meters
        color="#EB686C",
        fill=True,
        fill_opacity=0.2,
    )
    markers = [
        {
            "location": [loc[0], loc[1]],
            "popup": "Center City",
            "tooltip": "Philadelphia",
        },
        {
            "location": [loc[0], loc[1] + 0.05],
            "popup": "Rittenhouse Square",
            "tooltip": "A lovely park",
        },
    ]
    plot_map(loc, overlays=[circle], zoom_start=14)
    """
    config_plugin = """
    from folium.plugins import HeatMap
    heat_data = [
        [48.54440975, 9.060237673391708, 1],
        [48.5421456, 9.057464182487431, 1],
        [48.54539175, 9.059915422200906, 1],
    ]
    heatmap = HeatMap(
        heat_data,
        radius=5,  # Increase the radius of each point
        blur=5,  # Adjust the blurring effect
        min_opacity=0.4,  # Make the heatmap semi-transparent
        max_zoom=16,  # Zoom level at which points appear
        gradient={  # Define a custom gradient
            0.2: "blue",
            0.4: "lime",
            0.6: "yellow",
            1.0: "#A34B00",
        },
    )

    plot_map(loc, plugins=[heatmap])
    """
    from pathlib import Path

    # Get the current script's directory as a Path object
    current_directory = Path(__file__).resolve().parent
    if not "tiles_support" in locals():
        tiles_support = (
            fload(current_directory / "data" / "tiles.csv", verbose=0)
            .iloc[:, 1]
            .tolist()
        )
    tiles = strcmp(tiles, tiles_support)[0]
    import folium
    import streamlit as st
    import pydeck as pdk
    from streamlit_folium import st_folium
    from folium.plugins import HeatMap

    if pydeck_map:
        view = pdk.ViewState(
            latitude=location[0],
            longitude=location[1],
            zoom=zoom_start,
            pitch=0,
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=[{"lat": location[0], "lon": location[1]}],
            get_position="[lon, lat]",
            get_color="[200, 30, 0, 160]",
            get_radius=1000,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            map_style=pydeck_style,
        )
        st.pydeck_chart(deck)

        return deck  # Return the pydeck map

    else:
        m = folium.Map(
            location=location,
            zoom_start=zoom_start,
            tiles=tiles,
            scrollWheelZoom=scroll_wheel_zoom,
            **kwargs,
        )
        if markers:
            if verbose:
                print(config_markers)
            for marker in markers:
                folium.Marker(
                    location=marker.get("location"),
                    popup=marker.get("popup"),
                    tooltip=marker.get("tooltip"),
                    icon=marker.get(
                        "icon", folium.Icon()
                    ),  # Default icon if none specified
                ).add_to(m)

        if overlays:
            if verbose:
                print(config_overlay)
            for overlay in overlays:
                overlay.add_to(m)

        if custom_layers:
            for layer in custom_layers:
                layer.add_to(m)

        if plugins:
            if verbose:
                print(config_plugin)
            for plugin in plugins:
                plugin.add_to(m)

        if fit_bounds:
            m.fit_bounds(fit_bounds)

        if output == "streamlit":
            st_data = st_folium(m, width=map_width, height=map_height)
            return st_data
        elif output == "offline":
            if save_path:
                m.save(save_path)
            return m
        else:
            return m

#!####### plot SHAP ######### 

# ==============================
# Global style
# ============================== 
COLOR_PALETTE = {
    "background": "white",
    "main": "#1f77b4",
    "positive": "#1f77b4",  # blue
    "negative": "#d62728",  # red
    "zero_line": "#444444",
    "violin": "#8c564b",
}
def plot_shap(
    kind,
    shap_values,
    X,
    feature_names,
    top_n=20,
    sample_index=None,
    figsize=(8, 6),
    ax=None,
    cmap="coolwarm",
    signed=False,  # if False, show absolute importance for bar
    expected_value=None,  # for waterfall baseline
):
    """
    Ultimate SHAP plotting function (publication-ready).

    Parameters
    ----------
    kind : str
        bar | dot | violin | dependence | waterfall
    shap_values : np.ndarray or list
        SHAP values (n_samples, n_features)
    X : np.ndarray or DataFrame
        Feature matrix
    feature_names : list
        Feature names
    signed : bool
        Whether bar plot shows signed values (default False -> absolute)
    expected_value : float
        Model expected value (for waterfall)
    """

    import matplotlib.pyplot as plt
    # ----------------------------
    # Prepare data
    # ----------------------------
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # positive class

    shap_df = pd.DataFrame(shap_values, columns=feature_names)
    X_df = pd.DataFrame(X, columns=feature_names)

    mean_abs = shap_df.abs().mean()
    mean_signed = shap_df.mean()

    order = mean_abs.sort_values(ascending=False).head(top_n).index
    shap_top = shap_df[order]
    X_top = X_df[order]

    if ax is None: fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor(COLOR_PALETTE["background"])

    # ----------------------------
    # BAR: mean SHAP
    # ----------------------------
    if kind == "bar":
        vals = mean_signed[order] if signed else mean_abs[order]
        vals = vals.sort_values()
        offset = (vals.max() - vals.min()) * 0.01

        if signed:
            df = pd.DataFrame({
                "feature": vals.index,
                "value": vals.values,
                "sign": ["positive" if v>0 else "negative" for v in vals.values]
            })
            ax = sns.barplot(
                data=df,
                y="feature",
                x="value",
                palette={"positive": COLOR_PALETTE["positive"], "negative": COLOR_PALETTE["negative"]},
                hue="sign",
                dodge=False
            )
            ax.legend_.remove()
        else:
            df = pd.DataFrame({"feature": vals.index, "value": vals.values})
            ax = sns.barplot(data=df, y="feature", x="value", color=COLOR_PALETTE["main"])

        # numeric labels
        for i, v in enumerate(vals.values):
            ax.text(v + np.sign(v) * offset, i, f"{v:+.2f}" if signed else f"{v:.2f}",
                    va="center", ha="left" if v>0 else "right", fontsize=10)

        ax.invert_yaxis()
        ax.axvline(0, color=COLOR_PALETTE["zero_line"], lw=1.5)
        ax.set_xlabel("Mean SHAP value" + (" (signed)" if signed else " (absolute)"))
        ax.set_ylabel("Feature")

    # ----------------------------
    # DOT / beeswarm
    # ----------------------------
    elif kind == "dot":
        for i, f in enumerate(order):
            y = np.ones(len(shap_top)) * i
            sc = ax.scatter(
                shap_top[f],
                y,
                c=X_top[f],
                cmap=cmap,
                s=30,
                alpha=0.7,
                marker='o'
            )
        ax.axvline(0, color=COLOR_PALETTE["zero_line"], lw=1)
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels(order)
        ax.set_xlabel("SHAP value")
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label("Feature value", rotation=270, labelpad=15)

    # ----------------------------
    # VIOLIN 
    # ----------------------------
    elif kind == "violin":
        import matplotlib.cm as cm
        from matplotlib.collections import PolyCollection
        import numpy as np

        # Sort features by mean absolute SHAP
        feature_order = mean_abs[order].sort_values(ascending=True).index
        shap_top_ordered = shap_top[feature_order]
        X_top_ordered = X_top[feature_order]
        
        # Get global min/max for consistent coloring
        global_min = X_top_ordered.values.min()
        global_max = X_top_ordered.values.max()
        
        # Create colormap
        norm = plt.Normalize(global_min, global_max)

        for i, f in enumerate(feature_order):
            # Get data for this feature
            shap_vals = shap_top_ordered[f].values
            feat_vals = X_top_ordered[f].values
            
            # Create violin plot (without filling initially)
            vp = ax.violinplot(
                shap_vals,
                positions=[i],
                vert=False,
                widths=0.8,
                showmeans=False,
                showmedians=False,
                showextrema=False
            )
            
            # Remove default fill
            vp['bodies'][0].set_facecolor('none')
            vp['bodies'][0].set_edgecolor('none')
            
            # Get the vertices of the violin polygon
            path = vp['bodies'][0].get_paths()[0]
            vertices = path.vertices
            
            # Create gradient-filled violin
            # We'll create multiple segments with different colors
            num_segments = 50
            violin_vertices = vertices.copy()
            
            # Sort vertices for proper gradient application
            # For horizontal violin plots, x is shap value, y is density
            left_side = violin_vertices[violin_vertices[:, 1] <= i]
            right_side = violin_vertices[violin_vertices[:, 1] > i]
            
            # Sort sides
            left_side = left_side[left_side[:, 0].argsort()]  # sort by shap value
            right_side = right_side[right_side[:, 0].argsort()[::-1]]  # reverse sort
            
            # Create gradient colors based on feature value distribution
            # Map feature values to colors
            sorted_feat_vals = np.sort(feat_vals)
            colors = cmap(norm(sorted_feat_vals))
            
            # Alternative approach: Create gradient violin using PolyCollection
            # This creates a smooth gradient across the violin
            
            # Create a grid for the violin fill
            x_grid = np.linspace(violin_vertices[:, 0].min(), violin_vertices[:, 0].max(), 100)
            
            # For each x position, find corresponding y bounds
            polygons = []
            poly_colors = []
            
            # Create interpolated gradient
            for j in range(len(x_grid) - 1):
                x1, x2 = x_grid[j], x_grid[j+1]
                
                # Find vertices in this x range
                mask = (violin_vertices[:, 0] >= x1) & (violin_vertices[:, 0] <= x2)
                if mask.any():
                    # Get y values for this segment
                    segment_verts = violin_vertices[mask]
                    y_min = segment_verts[:, 1].min()
                    y_max = segment_verts[:, 1].max()
                    
                    # Create polygon for this segment
                    polygon = [
                        [x1, y_min],
                        [x2, y_min],
                        [x2, y_max],
                        [x1, y_max]
                    ]
                    polygons.append(polygon)
                    
                    # Determine color based on x position (mapped to feature value percentile)
                    # Map x position to a feature value using linear interpolation
                    x_pos = (x1 + x2) / 2
                    x_norm = (x_pos - violin_vertices[:, 0].min()) / (violin_vertices[:, 0].max() - violin_vertices[:, 0].min())
                    
                    # Get corresponding feature value (use percentile)
                    feat_percentile = np.percentile(sorted_feat_vals, x_norm * 100)
                    poly_colors.append(cmap(norm(feat_percentile)))
            
            # Add gradient-filled violin using PolyCollection
            if polygons:
                poly_collection = PolyCollection(
                    polygons,
                    facecolors=poly_colors,
                    edgecolors='none',
                    alpha=0.8,
                    linewidths=0
                )
                ax.add_collection(poly_collection)
            
            # Add median line
            median = np.median(shap_vals)
            ax.plot([median, median], [i-0.4, i+0.4], 
                    color='white', linewidth=1.5, alpha=0.8, zorder=3)
            
            # Overlay scatter points with jitter
            # y_jitter = np.random.normal(i, 0.05, size=len(feat_vals))
            # scatter = ax.scatter(
            #     shap_vals, 
            #     y_jitter, 
            #     c=feat_vals, 
            #     cmap=cmap, 
            #     norm=norm,
            #     s=14, 
            #     alpha=0.7, 
            #     edgecolor='white',
            #     linewidth=0.5,
            #     zorder=4
            # )

        # Formatting
        ax.set_yticks(range(len(feature_order)))
        ax.set_yticklabels(feature_order)
        ax.axvline(0, color=COLOR_PALETTE["zero_line"], lw=1.5, alpha=0.8, zorder=1)
        ax.set_xlabel("SHAP value (impact on SP)")
        
        # Set nice axis limits
        y_padding = 0.8
        ax.set_ylim(-y_padding, len(feature_order) - 1 + y_padding)
        
        # Add grid for better readability
        ax.grid(True, axis='x', alpha=0.2, linestyle='--', linewidth=0.5)

        # Colorbar with improved styling
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, pad=0.01)
        cbar.set_label("Feature value", rotation=270, labelpad=20)
        
        # # Add title
        # ax.set_title(f"Violin Plot of Top {order} Features\n(Colored by Feature Value)", 
        #             fontweight="bold", pad=15)
        
        # Adjust layout
        plt.tight_layout()

    elif kind == "violin2":
        import matplotlib.cm as cm
        import numpy as np
        from matplotlib.colors import LinearSegmentedColormap
        
        # Sort features by mean absolute SHAP
        feature_order = mean_abs[order].sort_values(ascending=True).index
        shap_top_ordered = shap_top[feature_order]
        X_top_ordered = X_top[feature_order]
        
        # Create colormap

        global_min = X_top_ordered.values.min()
        global_max = X_top_ordered.values.max()
        norm = plt.Normalize(global_min, global_max)
        
        for i, f in enumerate(feature_order):
            shap_vals = shap_top_ordered[f].values
            feat_vals = X_top_ordered[f].values
            
            # Create violin with gradient fill using a simpler approach
            # Create multiple transparent violins with different colors
            num_layers = 20
            sorted_idx = np.argsort(feat_vals)
            sorted_shap = shap_vals[sorted_idx]
            sorted_feat = feat_vals[sorted_idx]
            
            # Split data into layers for gradient effect
            chunk_size = max(1, len(sorted_shap) // num_layers)
            
            for layer in range(num_layers):
                start_idx = layer * chunk_size
                end_idx = min((layer + 1) * chunk_size, len(sorted_shap))
                
                if end_idx <= start_idx:
                    continue
                    
                layer_shap = sorted_shap[start_idx:end_idx]
                layer_feat_mean = sorted_feat[start_idx:end_idx].mean()
                
                # Create partial violin for this layer
                vp = ax.violinplot(
                    layer_shap,
                    positions=[i],
                    vert=False,
                    widths=0.7 * (layer + 1) / num_layers,  # Nested violins
                    showmeans=False,
                    showmedians=False,
                    showextrema=False
                )
                
                # Color based on average feature value in this layer
                color = cmap(norm(layer_feat_mean))
                vp['bodies'][0].set_facecolor(color)
                vp['bodies'][0].set_alpha(0.5 / np.sqrt(num_layers))
                vp['bodies'][0].set_edgecolor('none')
            
            # Add median line
            median = np.median(shap_vals)
            ax.plot([median, median], [i-0.3, i+0.3], 
                    color='black', linewidth=1.5, alpha=0.9, zorder=3)
            
            # Overlay scatter points
            y_jitter = np.random.normal(i, 0.04, size=len(shap_vals))
            ax.scatter(shap_vals, y_jitter, c=feat_vals, 
                    cmap=cmap, norm=norm, s=10, alpha=0.6, 
                    edgecolors='white', linewidth=0.3, zorder=4)
        
        # Formatting
        ax.set_yticks(range(len(feature_order)))
        ax.set_yticklabels(feature_order)
        ax.axvline(0, color=COLOR_PALETTE["zero_line"], lw=1.5, alpha=0.8)
        ax.set_xlabel("SHAP value (impact on SP)", fontweight="bold")
        
        # Colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label("Feature value", rotation=270, labelpad=15)

    elif kind == "violin3":
        import matplotlib.cm as cm
        import numpy as np
        from matplotlib.collections import PolyCollection
        
        # Sort features by mean absolute SHAP
        feature_order = mean_abs[order].sort_values(ascending=True).index
        shap_top_ordered = shap_top[feature_order]
        X_top_ordered = X_top[feature_order]
        
        # Get global min/max for consistent coloring
        global_min = X_top_ordered.values.min()
        global_max = X_top_ordered.values.max()
        
        # Create colormap (coolwarm: blue=low, red=high)
        norm = plt.Normalize(global_min, global_max)
        
        for i, f in enumerate(feature_order):
            shap_vals = shap_top_ordered[f].values
            feat_vals = X_top_ordered[f].values
            
            # Create base violin plot
            vp = ax.violinplot(
                shap_vals,
                positions=[i],
                vert=False,
                widths=0.8,
                showmeans=False,
                showmedians=False,
                showextrema=False
            )
            
            # Get violin polygon vertices
            path = vp['bodies'][0].get_paths()[0]
            vertices = path.vertices
            
            # Remove the default violin body
            vp['bodies'][0].remove()
            
            # Create gradient fill for the violin
            # Split violin into left and right sides
            center_y = i
            left_mask = vertices[:, 1] <= center_y
            right_mask = vertices[:, 1] > center_y
            
            left_vertices = vertices[left_mask]
            right_vertices = vertices[right_mask]
            
            # Sort vertices for each side
            left_vertices = left_vertices[left_vertices[:, 0].argsort()]  # sort by x (SHAP value)
            right_vertices = right_vertices[right_vertices[:, 0].argsort()[::-1]]  # reverse sort
            
            # Combine vertices to form full polygon
            all_vertices = np.vstack([left_vertices, right_vertices])
            
            # Create color gradient across the violin width
            # Map x-position (SHAP value) to color through feature values
            # We'll sample feature values across the SHAP distribution
            
            # Create interpolated x positions across violin
            x_min, x_max = all_vertices[:, 0].min(), all_vertices[:, 0].max()
            x_range = np.linspace(x_min, x_max, 100)
            
            # For each x position, find corresponding y bounds
            polygons = []
            facecolors = []
            
            for j in range(len(x_range) - 1):
                x1, x2 = x_range[j], x_range[j+1]
                
                # Find vertices in this x range for top and bottom
                mask_x = (all_vertices[:, 0] >= x1) & (all_vertices[:, 0] <= x2)
                if np.any(mask_x):
                    segment_verts = all_vertices[mask_x]
                    y_bottom = segment_verts[:, 1].min()
                    y_top = segment_verts[:, 1].max()
                    
                    # Create polygon rectangle for this segment
                    polygon = [
                        [x1, y_bottom],
                        [x2, y_bottom],
                        [x2, y_top],
                        [x1, y_top]
                    ]
                    polygons.append(polygon)
                    
                    # Determine color based on x position
                    # Map x to feature value percentile
                    x_pos = (x1 + x2) / 2
                    x_normalized = (x_pos - x_min) / (x_max - x_min)
                    
                    # Get corresponding feature value (use quantile)
                    # We assume feature values are roughly correlated with SHAP values
                    feat_value = np.percentile(feat_vals, x_normalized * 100)
                    facecolors.append(cmap(norm(feat_value)))
            
            # Create gradient-filled violin using PolyCollection
            if polygons:
                poly_collection = PolyCollection(
                    polygons,
                    facecolors=facecolors,
                    edgecolors='none',
                    alpha=0.7,
                    linewidths=0,
                    zorder=2
                )
                ax.add_collection(poly_collection)
            
            # Add median line (white line in the middle)
            median_val = np.median(shap_vals)
            ax.plot([median_val, median_val], [i-0.4, i+0.4], 
                    color='white', linewidth=1.5, alpha=0.9, zorder=3)
            
            # Add scatter points with jitter (colored by actual feature values)
            y_jitter = np.random.normal(i, 0.05, size=len(shap_vals))
            ax.scatter(
                shap_vals,
                y_jitter,
                c=feat_vals,
                cmap=cmap,
                norm=norm,
                s=20,
                alpha=0.7,
                edgecolors='white',
                linewidth=0.5,
                zorder=4
            )
        
        # Formatting to match your example
        ax.set_yticks(range(len(feature_order)))
        ax.set_yticklabels(feature_order, fontsize=10)
        ax.axvline(0, color=COLOR_PALETTE["zero_line"], lw=1.5, alpha=0.8, zorder=1)
        ax.set_xlabel("SHAP value (impact on SP)", fontweight="bold")
        
        # Set y-axis limits with padding
        ax.set_ylim(-0.5, len(feature_order) - 0.5)
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add colorbar on the right
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, pad=0.02)
        cbar.set_label("Feature value", rotation=270, labelpad=20, fontweight="bold")
        
        # Optional: Add grid for better readability
        ax.grid(True, axis='x', alpha=0.1, linestyle='-', linewidth=0.5)
        
        # Adjust layout
        plt.tight_layout()

    # DEPENDENCE
    # ----------------------------
    elif kind == "dependence":
        from statsmodels.nonparametric.smoothers_lowess import lowess
        f = order[0]
        x = X_top[f]
        y = shap_top[f]
        ax.scatter(x, y, s=30, alpha=0.6, marker='o')
        smoothed = lowess(y, x, frac=0.3)
        ax.plot(smoothed[:,0], smoothed[:,1], color="black", lw=2)
        ax.axhline(0, color=COLOR_PALETTE["zero_line"], lw=1)
        ax.set_xlabel(f"{f}")
        ax.set_ylabel("SHAP value")

    # ----------------------------
    # WATERFALL
    # ----------------------------
    elif kind == "waterfall":
        if sample_index is None:
            raise ValueError("sample_index required for waterfall")

        v = shap_df.iloc[sample_index][order]
        v = v.sort_values(key=np.abs)
        base_value = expected_value if expected_value is not None else shap_df.values.mean()
        cumulative = base_value + np.cumsum(v.values)
        starts = np.concatenate([[base_value], cumulative[:-1]])
        colors = [COLOR_PALETTE["positive"] if x>0 else COLOR_PALETTE["negative"] for x in v.values]
        markers = ['o' if x>0 else 's' for x in v.values]  # circle for positive, square for negative

        for i, (feature, val, start, m) in enumerate(zip(v.index, v.values, starts, markers)):
            ax.barh(feature, val, left=start, color=colors[i], edgecolor="black", height=0.6)
            # add numeric label
            offset = abs(v.values).max() * 0.03
            ax.text(start + val + np.sign(val)*offset, i, f"{val:+.2f}",
                    va="center", ha="left" if val>0 else "right", fontsize=10)

            # add marker
            ax.scatter(start + val, i, color=colors[i], marker=m, s=60, zorder=3)

        # baseline & final prediction
        ax.axvline(base_value, color="black", linestyle="--", lw=1.5)
        ax.axvline(cumulative[-1], color="black", lw=2)
        ax.set_xlabel("Model output")
        ax.set_ylabel("Feature")

    else:
        raise ValueError(f"Unknown kind: {kind}")

    # ----------------------------
    # Final polish
    # ----------------------------
    for spine in ax.spines.values():
        spine.set_linewidth(1.8)

    plt.tight_layout()
    return ax

def plot_shap_from_results(results_dict, model_name, plot_types=['bar', 'dot', 'violin'], save_dir=None):
    """
    Re-plot SHAP visualizations from stored SHAP data.
    
    Parameters:
    -----------
    results_dict : dict
        Results dictionary containing SHAP data
    model_name : str
        Name of the model to plot
    plot_types : list
        Types of plots to generate
    save_dir : str, optional
        Directory to save plots
    """
    if model_name not in results_dict or 'shap_data' not in results_dict[model_name]:
        print(f"No SHAP data found for model: {model_name}")
        return
    
    shap_data = results_dict[model_name]['shap_data']
    
    # Extract data for plotting
    shap_values = shap_data.get('shap_values_array')
    X_values = shap_data.get('X_values')
    feature_names = shap_data.get('feature_names')
    
    if shap_values is None:
        print(f"SHAP values not available for {model_name}")
        return
    
    # Now you can call your plot_shap function with the stored data
    if 'bar' in plot_types:
        plot_shap(kind="bar", shap_values=shap_values, X=X_values, 
                 feature_names=feature_names, title=f"SHAP - {model_name}")
    
    if 'dot' in plot_types:
        plot_shap(kind="dot", shap_values=shap_values, X=X_values,
                 feature_names=feature_names, title=f"SHAP Summary - {model_name}")
    
    # 3. Violin plot (distribution of SHAP values)
        plot_shap(
            kind="violin",
            shap_values=shap_values,
            X=X_values,
            feature_names=feature_names,
            top_n=shap_top_n 
        )
    # 4. Density plot
    ax = plot_shap(
                            kind="density",
                            shap_values=shap_values,
                            X=X_values,
                            feature_names=feature_names,
                            top_n=min(5, shap_top_n),
                            scientific=True,
                            figsize=(10, 6)
                        )
    # 5. Dependence plots for top 3 features (using your function)
    top_3_features = shap_importance_df.head(3)['feature'].tolist()
    for i, feature in enumerate(top_3_features):
        if feature in feature_names:
            ax = plot_shap(
                kind="dependence",
                shap_values=shap_values,
                X=X_values,
                feature_names=feature_names,
                top_n=3,
                scientific=True,
                figsize=(10, 6)
            )
    # 6. Waterfall plot for a sample
    if len(shap_values_array) > 0:
        # Choose a representative sample
        predictions = model_obj.predict_proba(X_shap_sample)[:, 1]
        sample_idx = np.argmax(np.abs(predictions - 0.5))  # Most confident
        
        ax = plot_shap(
            kind="waterfall",
            shap_values=shap_values,
            X=X_values,
            feature_names=feature_names,
            top_n=shap_top_n,
            sample_index=sample_idx,
            scientific=True,
            figsize=(12, 8)
        )
