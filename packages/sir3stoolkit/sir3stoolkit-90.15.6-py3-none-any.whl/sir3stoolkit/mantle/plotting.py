# -*- coding: utf-8 -*-
"""
Created on Thu Okt 7 13:39:13 2025

This module implements general plotting functions for SIR 3S applications. TODO: AGSN, Time Curves, Network Color Diagram

@author: Jablonski

"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

import re
from typing import Dict, Tuple, Optional

import logging

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

from sir3stoolkit.core.wrapper import SIR3S_Model

class SIR3S_Model_Plotting(SIR3S_Model):
    
    def plot_pipe_layer(
        self,
        ax=None,
        gdf=None,
        *,
        width_scaling_col: str | None = None,
        color_mixing_col: str | None = None,
        attribute: str | None = None,
        # visual params
        colors=('darkgreen', 'magenta'),
        legend_fmt: str | None = None,
        legend_values: list[float] | None = None,
        # independent norms
        width_vmin: float | None = None,
        width_vmax: float | None = None,
        color_vmin: float | None = None,
        color_vmax: float | None = None,
        # filtering & styling
        query: str | None = None,
        line_width_factor: float = 10.0,
        zorder: float | None = None,
    ):
        """
        Plot line geometries with separate width and color scaling.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axis to plot into. If None, uses current axes (plt.gca()).
        gdf : pandas.DataFrame or geopandas.GeoDataFrame
            Input with a 'geometry' column of shapely LineString/MultiLineString.
        width_scaling_col : str, optional
            Column used to scale line widths (numeric). If None, uses `attribute`
            if provided; otherwise constant width.
        color_mixing_col : str, optional
            Column used to color lines (numeric). If None, uses `attribute`
            if provided; otherwise a constant color.
        attribute : str, optional
            Legacy single column used for both width and color if the specific
            columns are not provided.
        colors : tuple[str, str], optional
            Two colors to build a linear segmented colormap.
        legend_fmt : str, optional
            Legend label format, default: f"{color_col} {{:.4f}}".
        legend_values : list[float], optional
            Explicit legend tick values; default: 5 linear steps.
        width_vmin, width_vmin : float, optional
            Bounds for width normalization; defaults to data min/max.
        color_vmin, color_vmax : float, optional
            Bounds for color normalization; defaults to data min/max.
        query : str, optional
            Pandas query string to filter rows before plotting.
        line_width_factor : float, optional
            Factor applied after width normalization, default 10.0.
        zorder : float, optional
            Z-order for drawing.

        Returns
        -------
        list[matplotlib.patches.Patch] or None
            Legend patches based on the color scaling column; None if constant color.
        """
        logger.info(f"[plot] Plotting pipes (width='{width_scaling_col}', color='{color_mixing_col}', attr='{attribute}')")

        ax = ax or plt.gca()
        if gdf is None or getattr(gdf, 'empty', True) or 'geometry' not in gdf.columns:
            logger.warning("[plot] Pipes: missing data or geometry column.")
            return None

        df = gdf.query(query) if query else gdf
        if df.empty:
            logger.warning("[plot] Pipes: filtered dataframe is empty.")
            return None

        # --- WIDTH SCALING ---
        width_col = width_scaling_col or attribute
        if width_col is not None:
            try:
                a_w = df[width_col].astype(float).to_numpy()
            except Exception as e:
                logger.error(f"[plot] Pipes: width column '{width_col}' not numeric or missing. {e}")
                return None
            vmin_w = float(width_vmin) if width_vmin is not None else float(np.nanmin(a_w))
            vmax_w = float(width_vmax) if width_vmax is not None else float(np.nanmax(a_w))
            if not np.isfinite(vmin_w) or not np.isfinite(vmax_w) or vmin_w == vmax_w:
                vmax_w = vmin_w + 1e-12
            norm_w = plt.Normalize(vmin=vmin_w, vmax=vmax_w)
            widths_full = norm_w(a_w) * float(line_width_factor)
        else:
            widths_full = None  # will use constant width later

        # --- COLOR SCALING ---
        color_col = color_mixing_col or attribute
        cmap = mcolors.LinearSegmentedColormap.from_list('cmap', list(colors), N=256)
        patches = None
        if color_col is not None:
            try:
                a_c = df[color_col].astype(float).to_numpy()
            except Exception as e:
                logger.error(f"[plot] Pipes: color column '{color_col}' not numeric or missing. {e}")
                return None
            vmin_c = float(color_vmin) if color_vmin is not None else float(np.nanmin(a_c))
            vmax_c = float(color_vmax) if color_vmax is not None else float(np.nanmax(a_c))
            if not np.isfinite(vmin_c) or not np.isfinite(vmax_c) or vmin_c == vmax_c:
                vmax_c = vmin_c + 1e-12
            norm_c = plt.Normalize(vmin=vmin_c, vmax=vmax_c)
            colors_full = cmap(norm_c(a_c))
            legend_fmt = legend_fmt or f"{color_col} {{:.4f}}"
            vals = legend_values if legend_values is not None else np.linspace(vmin_c, vmax_c, 5)
            patches = [mpatches.Patch(color=cmap(norm_c(float(v))), label=legend_fmt.format(float(v))) for v in vals]
        else:
            colors_full = None  # will use constant color later

        # --- BUILD SEGMENTS ---
        segs, cols, lw = [], [], []
        count = 0
        for i, geom in enumerate(df['geometry']):
            if geom is None:
                continue
            gt = getattr(geom, 'geom_type', None)
            col = colors_full[i] if colors_full is not None else mcolors.to_rgba(colors[0])
            w = widths_full[i] if widths_full is not None else float(line_width_factor) * 0.5
            if gt == 'LineString':
                segs.append(np.asarray(geom.coords)); cols.append(col); lw.append(w); count += 1
            elif gt == 'MultiLineString':
                for part in getattr(geom, 'geoms', []):
                    segs.append(np.asarray(part.coords)); cols.append(col); lw.append(w); count += 1

        if not segs:
            logger.warning("[plot] Pipes: no line geometries found.")
            return None

        lc = LineCollection(segs, colors=cols, linewidths=lw, zorder=zorder)
        ax.add_collection(lc); ax.autoscale_view()

        logger.info(f"[plot] Pipes: plotted {count} segments.")
        return patches

    def plot_node_layer(
        self,
        ax=None,
        gdf=None,
        *,
        size_scaling_col: str | None = None,
        color_mixing_col: str | None = None,
        attribute: str | None = None,
        # visual params
        colors=('darkgreen', 'magenta'),
        legend_fmt: str | None = None,
        legend_values: list[float] | None = None,
        # independent norms
        size_vmin: float | None = None,
        size_vmax: float | None = None,
        color_vmin: float | None = None,
        color_vmax: float | None = None,
        # filtering & styling
        query: str | None = None,
        marker_style: str = 'o',
        marker_size_factor: float = 1000.0,
        zorder: float | None = None,
    ):
        """
        Plot point nodes with separate size and color scaling.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Axis to plot into. If None, uses current axes (plt.gca()).
        gdf : pandas.DataFrame or geopandas.GeoDataFrame
            Input with a 'geometry' column of shapely geometries.
        size_scaling_col : str, optional
            Column used to scale marker sizes (numeric). If None, uses `attribute`
            if provided; otherwise constant size.
        color_mixing_col : str, optional
            Column used to color markers (numeric). If None, uses `attribute`
            if provided; otherwise a constant color.
        attribute : str, optional
            Legacy single column used for both size and color if the specific
            columns are not provided.
        colors : tuple[str, str], optional
            Two colors to build a linear segmented colormap.
        legend_fmt : str, optional
            Legend label format, default: f"{color_col} {{:.4f}}".
        legend_values : list[float], optional
            Explicit legend tick values; default: 5 linear steps.
        size_vmin, size_vmax : float, optional
            Bounds for size normalization; defaults to data min/max.
        color_vmin, color_vmax : float, optional
            Bounds for color normalization; defaults to data min/max.
        query : str, optional
            Pandas query string to filter rows before plotting.
        marker_style : str, optional
            Matplotlib marker style, default 'o'.
        marker_size_factor : float, optional
            Factor applied after size normalization, default 1000.0.
        zorder : float, optional
            Z-order for drawing.

        Returns
        -------
        list[matplotlib.patches.Patch] or None
            Legend patches based on the color scaling column; None if constant color.
        """
        logger.info(f"[plot] Plotting nodes (size='{size_scaling_col}', color='{color_mixing_col}', attr='{attribute}')")

        ax = ax or plt.gca()
        if gdf is None or getattr(gdf, 'empty', True) or 'geometry' not in gdf.columns:
            logger.warning("[plot] Nodes: missing data or geometry column.")
            return None

        df = gdf.query(query) if query else gdf
        if df.empty:
            logger.warning("[plot] Nodes: filtered dataframe is empty.")
            return None

        geoms = df['geometry']
        is_point = geoms.apply(lambda g: getattr(g, 'geom_type', None) == 'Point')
        if not is_point.any():
            logger.warning("[plot] Nodes: no Point geometries found.")
            return None

        # --- SIZE SCALING ---
        size_col = size_scaling_col or attribute
        if size_col is not None:
            try:
                a_size = df.loc[is_point, size_col].astype(float).to_numpy()
            except Exception as e:
                logger.error(f"[plot] Nodes: size column '{size_col}' not numeric or missing. {e}")
                return None
            vmin_s = float(size_vmin) if size_vmin is not None else float(np.nanmin(a_size))
            vmax_s = float(size_vmax) if size_vmax is not None else float(np.nanmax(a_size))
            if not np.isfinite(vmin_s) or not np.isfinite(vmax_s) or vmin_s == vmax_s:
                vmax_s = vmin_s + 1e-12
            norm_s = plt.Normalize(vmin=vmin_s, vmax=vmax_s)
            sizes = norm_s(a_size) * float(marker_size_factor)
        else:
            sizes = np.full(is_point.sum(), float(marker_size_factor) * 0.5)

        # --- COLOR SCALING ---
        color_col = color_mixing_col or attribute
        cmap = mcolors.LinearSegmentedColormap.from_list('cmap', list(colors), N=256)
        patches = None
        if color_col is not None:
            try:
                a_col = df.loc[is_point, color_col].astype(float).to_numpy()
            except Exception as e:
                logger.error(f"[plot] Nodes: color column '{color_col}' not numeric or missing. {e}")
                return None
            vmin_c = float(color_vmin) if color_vmin is not None else float(np.nanmin(a_col))
            vmax_c = float(color_vmax) if color_vmax is not None else float(np.nanmax(a_col))
            if not np.isfinite(vmin_c) or not np.isfinite(vmax_c) or vmin_c == vmax_c:
                vmax_c = vmin_c + 1e-12
            norm_c = plt.Normalize(vmin=vmin_c, vmax=vmax_c)
            colors_arr = cmap(norm_c(a_col))
            # Legend only for color scaling
            legend_fmt = legend_fmt or f"{color_col} {{:.4f}}"
            vals = legend_values if legend_values is not None else np.linspace(vmin_c, vmax_c, 5)
            patches = [mpatches.Patch(color=cmap(norm_c(float(v))), label=legend_fmt.format(float(v))) for v in vals]
        else:
            # Constant color (first color provided)
            colors_arr = np.tile(mcolors.to_rgba(colors[0]), (is_point.sum(), 1))

        # --- PLOT ---
        coords = np.array([(g.x, g.y) for g in geoms[is_point]])
        ax.scatter(coords[:, 0], coords[:, 1], s=sizes, c=colors_arr, marker=marker_style, zorder=zorder)

        logger.info(f"[plot] Nodes: plotted {is_point.sum()} points.")
        return patches
