#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core shape classes for easyshapey.

Provides 2D shape manipulation for data selection in plots.
Supports Box, RotatedBox, Oval, and arbitrary N-sided Polygons.

Author: caganze
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.patches import Ellipse
from abc import ABCMeta, abstractproperty
import math


class BadVerticesFormatError(Exception):
    """Raised when vertices format is invalid for a shape."""
    pass


class Shape(object):
    """
    Abstract base class for 2D shapes.

    Provides common interface for shape manipulation, data selection,
    and visualization on matplotlib axes.

    Parameters
    ----------
    xrange : list, optional
        X-axis range [min, max].
    yrange : list, optional
        Y-axis range [min, max].
    color : str, optional
        Fill color for the shape.
    alpha : float, optional
        Transparency (0-1). Default 0.3.
    lw : float, optional
        Line width. Default 2.
    linestyle : str, optional
        Line style. Default '--'.
    """
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        self.xrange = kwargs.get('xrange', [])
        self.yrange = kwargs.get('yrange', [])
        self._color = kwargs.get('color', None)
        self.alpha = kwargs.get('alpha', 0.3)
        self.linewidth = kwargs.get('lw', 2)
        self.linestyle = kwargs.get('linestyle', '--')
        self.edgecolor = kwargs.get('color', 'k')
        self.codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
        self._shapetype = None
        self._coeffs = None

    def __repr__(self):
        return 'shape'

    @abstractproperty
    def shapetype(self):
        """str: Type identifier for the shape."""
        return self._shapetype

    @shapetype.setter
    def shapetype(self, s_type):
        self._shapetype = s_type

    @abstractproperty
    def color(self):
        """str: Fill color for the shape."""
        return self._color

    @color.setter
    def color(self, new_color):
        self._color = new_color

    @abstractproperty
    def spath(self):
        """matplotlib.path.Path: Path object for rendering."""
        return Path(self.vertices, self.codes)

    def _select(self, data):
        """
        Internal selection using path containment.

        Parameters
        ----------
        data : ndarray
            2D array with shape (2, n_points).

        Returns
        -------
        tuple
            (selected_data, boolean_mask)
        """
        if self.__repr__() == 'oval':
            bools = self.ellipse.contains_points(list(zip(data[0], data[1])))
        else:
            bools = self.spath.contains_points(list(zip(data[0], data[1])))
        return np.array([data[0][bools], data[1][bools]]), bools

    def select(self, data):
        """
        Select data points inside the shape.

        Parameters
        ----------
        data : ndarray or DataFrame
            2D array (2, n) or DataFrame with x, y columns.

        Returns
        -------
        ndarray or DataFrame
            Points contained within the shape.

        Raises
        ------
        ValueError
            If data is empty.
        """
        if len(data) == 0:
            raise ValueError('Data cannot be empty')

        if isinstance(data, pd.DataFrame):
            data.columns = ['x', 'y']
            bools = self._select(np.array([data['x'].values, data['y'].values]))[1]
            return data[bools]
        return self._select(data)[0]


class Box(Shape):
    """
    Rectangular/parallelogram shape fitted to data.

    Fits a linear trend to data and creates a box around it.
    Supports rotation and data selection.

    Parameters
    ----------
    shapetype : str, optional
        'box' (fitted to trend) or 'rectangle' (horizontal). Default 'box'.
    sigma : float, optional
        Width multiplier for scatter. Default 1.
    xshift : float, optional
        X-axis padding fraction. Default 0.1.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shapetype = kwargs.get('shapetype', 'box')
        self.completeness = kwargs.get('completeness', 0.85)
        self.contamination = np.nan
        self._data = None
        self._data_type = None
        self._scatter = None
        self._pol = None
        self._vertices = None
        self._angle = None
        self._coeffs = None
        self.sigma = kwargs.get('sigma', 1)
        self.xshift = kwargs.get('xshift', 0.1)

    def __repr__(self):
        return 'box'

    def __len__(self):
        return 0 if self._data is None else len(self.data[0])

    @property
    def center(self):
        """tuple: (x, y) center of the box."""
        vs = np.array(self.vertices)
        return (np.nanmean(vs[:, 0]), np.nanmean(vs[:, 1]))

    @property
    def angle(self):
        """float: Angle of first edge in radians."""
        x1, y1 = self.vertices[0]
        x2, y2 = self.vertices[1]
        dist = math.hypot(x2 - x1, y2 - y1)
        return np.arccos(abs(x2 - x1) / dist) if dist > 0 else 0.0

    @property
    def vertices(self):
        """list: Vertices as [(x1,y1), (x2,y2), ...] closed polygon."""
        return self._vertices

    @vertices.setter
    def vertices(self, vertices):
        vs = np.array(vertices)
        if not np.allclose(vs[0], vs[-1], rtol=1e-4):
            raise BadVerticesFormatError(
                f'First vertex {vertices[0]} must equal last {vertices[-1]}'
            )
        self.xrange = [vs[:, 0].min(), vs[:, 0].max()]
        self.yrange = [vs[:, 1].min(), vs[:, 1].max()]
        self._vertices = vertices

    @property
    def area(self):
        """float: Area of the bounding box."""
        return abs(np.ptp(self.xrange) * np.ptp(self.yrange))

    @property
    def data(self):
        """ndarray: Data array used to fit the box."""
        return np.array(self._data)

    @data.setter
    def data(self, input_data):
        if self._data_type == 'contam':
            self._data = input_data
            return

        if isinstance(input_data, pd.DataFrame):
            input_data = input_data.values.T

        x, y = input_data[0], input_data[1]
        x_min, x_max = np.nanmin(x), np.nanmax(x)
        dx = x_max - x_min
        x_min -= self.xshift * dx
        x_max += self.xshift * dx

        y_med, y_std = np.nanmedian(y), np.nanstd(y)
        mask = np.abs(y - y_med) < self.sigma * y_std

        if self.shapetype == 'rectangle':
            pol = np.poly1d([0, y_med])
        else:
            pol = np.poly1d(np.polyfit(x[mask], y[mask], 1))

        ys = pol([x_min, x_max])
        scatter = self.sigma * np.sqrt(np.mean((y[mask] - pol(x[mask]))**2))

        v1, v2 = (x_min, ys[0] + scatter), (x_max, ys[1] + scatter)
        v3, v4 = (x_max, ys[1] - scatter), (x_min, ys[0] - scatter)

        self._vertices = [v1, v2, v3, v4, v1]
        self._data = np.array([x, y])
        self._scatter = scatter
        self._pol = pol
        self._coeffs = pol.coefficients

    @property
    def datatype(self):
        """str: Data type label ('contam' or None)."""
        return self._data_type

    @datatype.setter
    def datatype(self, new_type):
        self._data_type = new_type

    @property
    def efficiency(self):
        """float: Fraction of data points inside the box."""
        return len(self.select(self.data)[0]) / len(self.data[0])

    @property
    def scatter(self):
        """float: Scatter from the center line."""
        return self._scatter

    @property
    def coeffs(self):
        """ndarray: Polynomial coefficients [slope, intercept]."""
        return self._coeffs

    def contains(self, points):
        """
        Check if points are inside the box.

        Parameters
        ----------
        points : list of tuples
            Points as [(x1, y1), (x2, y2), ...].

        Returns
        -------
        list of bool
            True for each point inside.
        """
        return [self.spath.contains_point(p) for p in points]

    def rotate(self, ang, **kwargs):
        """
        Rotate the box around its center.

        Parameters
        ----------
        ang : float
            Rotation angle in radians.
        center : tuple, optional
            Custom rotation center (x, y).
        set_vertices : bool, optional
            If True, update in place. Default True.

        Returns
        -------
        ndarray or None
            New vertices if set_vertices=False.
        """
        vs = np.array(self.vertices)
        c = np.array(kwargs.get('center', self.center))
        cos_a, sin_a = np.cos(ang), np.sin(ang)
        rot = np.array([[cos_a, -sin_a], [sin_a, cos_a]])

        rotated = (vs[:, :2] - c) @ rot.T + c
        new_vs = [(r[0], r[1]) for r in rotated]

        if kwargs.get('set_vertices', True):
            self._vertices = new_vs
        else:
            return np.array(new_vs)

    def plot(self, **kwargs):
        """
        Plot the box on matplotlib axes.

        Parameters
        ----------
        ax : Axes, optional
            Matplotlib axes. Default current axes.
        highlight : bool, optional
            Use thicker lines if True.
        label : str, optional
            Text label at center.
        only_shape : bool, optional
            If False, also plot data points.
        """
        ax = kwargs.get('ax', plt.gca())

        if kwargs.get('highlight', False):
            self.linewidth, self.linestyle = 3.5, '-'
            self.edgecolor = '#111111'

        if not kwargs.get('only_shape', True):
            ax.plot(self.data[0], self.data[1], 'k.', ms=0.1)

        patch = patches.PathPatch(
            self.spath, facecolor=self.color, alpha=self.alpha,
            edgecolor=self.edgecolor, linewidth=self.linewidth,
            linestyle=self.linestyle
        )
        ax.add_patch(patch)

        if kwargs.get('label'):
            ax.text(self.center[0], self.center[1] + (self._scatter or 0),
                    kwargs['label'], fontsize=15, color='#111111')


class RotatedBox(Box):
    """
    Box that finds optimal rotation to minimize bounding area.

    Automatically rotates to find the smallest enclosing rectangle.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @Box.data.setter
    def data(self, df):
        if self._data_type == 'contam':
            self._data = df
            return

        x, y = np.array(df.x), np.array(df.y)
        v1 = (x.min(), y.max())
        v2 = (x.max(), y.max())
        v3 = (x.max(), y.min())
        v4 = (x.min(), y.min())

        self._data = df
        self._vertices = [v1, v2, v3, v4, v1]

        # Find optimal rotation (minimal area)
        best_area, best_vs = float('inf'), None
        for alpha in np.linspace(0, np.pi / 2, 100):
            vs = self.rotate(alpha, set_vertices=False)
            area = np.ptp(vs[:, 0]) * np.ptp(vs[:, 1])
            if area < best_area:
                best_area, best_vs = area, vs

        if best_vs is not None:
            self._vertices = [(v[0], v[1]) for v in best_vs]


class Oval(Shape):
    """
    Elliptical shape fitted to data.

    Creates an ellipse based on a Box fitted to the data.

    Parameters
    ----------
    completeness : float, optional
        Target completeness. Default 0.85.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shapetype = 'oval'
        self.completeness = kwargs.get('completeness', 0.85)
        self.contamination = np.nan
        self._data = None
        self._data_type = None
        self._vertices = None
        self._center = None
        self._height = None
        self._width = None
        self._box = None
        self._ellipse = None
        self._angle = 0

    def __repr__(self):
        return 'oval'

    def __len__(self):
        return 0 if self._data is None else len(self._data)

    @property
    def angle(self):
        """float: Rotation angle in radians."""
        return self._angle

    @property
    def center(self):
        """tuple: (x, y) center of the ellipse."""
        return self._center

    @property
    def height(self):
        """float: Height of the ellipse."""
        return self._height

    @property
    def width(self):
        """float: Width of the ellipse."""
        return self._width

    @property
    def vertices(self):
        """list: Bounding vertices from underlying box."""
        return self._vertices

    @property
    def box(self):
        """Box: Underlying box used to create the ellipse."""
        return self._box

    @property
    def ellipse(self):
        """Ellipse: Matplotlib Ellipse patch."""
        if self._ellipse is not None:
            self._ellipse.set_alpha(self.alpha)
            self._ellipse.set_facecolor(self.color)
        return self._ellipse

    @property
    def data(self):
        """ndarray: Data used to fit the ellipse."""
        return self._data

    @data.setter
    def data(self, df):
        b = Box()
        b.data = df
        vs = np.array(b.vertices)
        self._vertices = vs
        self._center = [np.mean(vs[:, 0]), np.mean(vs[:, 1])]
        self._angle = b.angle
        self._box = b
        self._height = np.linalg.norm(vs[1] - vs[2])
        self._width = np.linalg.norm(vs[0] - vs[1])
        self._ellipse = Ellipse(self._center, self._width, self._height, np.degrees(self._angle))
        self._data = df

    def plot(self, **kwargs):
        """
        Plot the ellipse on matplotlib axes.

        Parameters
        ----------
        ax : Axes, optional
            Matplotlib axes.
        set_limits : bool, optional
            If True, set axis limits.
        """
        ax = kwargs.get('ax', plt.gca())
        ax.add_patch(self.ellipse)

        if kwargs.get('set_limits', False):
            ax.set_xlim(kwargs.get('plot_xlim', []))
            ax.set_ylim(kwargs.get('plot_ylim', []))


class Polygon(Shape):
    """
    Arbitrary N-sided 2D polygon.

    Supports any polygon from triangles (N=3) to complex shapes.
    Can be created from vertices or interactively via clicking.

    Parameters
    ----------
    vertices : list of tuples, optional
        Polygon vertices as [(x1, y1), (x2, y2), ...].
        Auto-closes if last != first.

    Examples
    --------
    >>> tri = Polygon(vertices=[(0, 0), (1, 0), (0.5, 1)])
    >>> print(tri.n_sides)  # 3
    >>> print(tri.area)     # 0.5
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._shapetype = kwargs.get('shapetype', 'polygon')
        self._vertices = None
        if 'vertices' in kwargs and kwargs['vertices'] is not None:
            self.vertices = kwargs['vertices']

    def __repr__(self):
        return 'polygon'

    def __len__(self):
        return 0 if self._vertices is None else self.n_sides

    @property
    def n_sides(self):
        """int: Number of sides."""
        return 0 if self._vertices is None else len(self._vertices) - 1

    @property
    def shapetype(self):
        """str: Shape type identifier."""
        return self._shapetype

    @shapetype.setter
    def shapetype(self, s_type):
        self._shapetype = s_type

    @property
    def color(self):
        """str: Fill color."""
        return self._color

    @color.setter
    def color(self, new_color):
        self._color = new_color

    @property
    def vertices(self):
        """list: Vertices as [(x, y), ...], closed polygon."""
        return self._vertices

    @vertices.setter
    def vertices(self, vertices):
        if vertices is None or len(vertices) < 3:
            raise BadVerticesFormatError('Polygon requires >= 3 vertices')

        vs = np.array(vertices, dtype=float)
        if vs.ndim != 2 or vs.shape[1] != 2:
            raise BadVerticesFormatError('Vertices must be [(x, y), ...]')

        # Auto-close if needed
        if not np.allclose(vs[0], vs[-1], rtol=1e-4):
            vs = np.vstack([vs, vs[0]])

        self.xrange = [vs[:, 0].min(), vs[:, 0].max()]
        self.yrange = [vs[:, 1].min(), vs[:, 1].max()]
        n = len(vs)
        self.codes = [Path.MOVETO] + [Path.LINETO] * (n - 2) + [Path.CLOSEPOLY]
        self._vertices = [tuple(v) for v in vs]

    @property
    def spath(self):
        """matplotlib.path.Path: Path for rendering."""
        if self._vertices is None:
            raise ValueError('No vertices set')
        return Path(self._vertices, self.codes)

    @property
    def center(self):
        """tuple: Centroid (x, y)."""
        if self._vertices is None:
            return (0, 0)
        vs = np.array(self._vertices[:-1])
        return (vs[:, 0].mean(), vs[:, 1].mean())

    @property
    def area(self):
        """float: Area using shoelace formula."""
        if self._vertices is None or len(self._vertices) < 3:
            return 0.0
        vs = np.array(self._vertices[:-1])
        x, y = vs[:, 0], vs[:, 1]
        return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    @property
    def angle(self):
        """float: Angle of first edge in radians."""
        if self._vertices is None or len(self._vertices) < 3:
            return 0.0
        v1, v2 = np.array(self._vertices[0]), np.array(self._vertices[1])
        d = v2 - v1
        dist = np.linalg.norm(d)
        if dist == 0:
            return 0.0
        return np.arctan2(d[1], d[0])

    def contains(self, points):
        """
        Check if points are inside the polygon.

        Parameters
        ----------
        points : list of tuples
            Points as [(x1, y1), ...].

        Returns
        -------
        list of bool
        """
        return [self.spath.contains_point(p) for p in points]

    def rotate(self, ang, **kwargs):
        """
        Rotate polygon around center.

        Parameters
        ----------
        ang : float
            Angle in radians.
        center : tuple, optional
            Custom rotation center.
        set_vertices : bool, optional
            Update in place if True (default).

        Returns
        -------
        ndarray or None
            New vertices if set_vertices=False.
        """
        if self._vertices is None:
            return

        vs = np.array(self._vertices[:-1])
        c = np.array(kwargs.get('center', self.center))
        cos_a, sin_a = np.cos(ang), np.sin(ang)
        rot = np.array([[cos_a, -sin_a], [sin_a, cos_a]])

        rotated = (vs - c) @ rot.T + c
        new_vs = [tuple(v) for v in rotated] + [tuple(rotated[0])]

        if kwargs.get('set_vertices', True):
            self.vertices = new_vs
        else:
            return np.array(new_vs)

    def plot(self, **kwargs):
        """
        Plot polygon on matplotlib axes.

        Parameters
        ----------
        ax : Axes, optional
            Matplotlib axes.
        highlight : bool, optional
            Use thicker lines.
        label : str, optional
            Text label at center.
        """
        if self._vertices is None:
            raise ValueError('No vertices set')

        ax = kwargs.get('ax', plt.gca())

        if kwargs.get('highlight', False):
            self.linewidth, self.linestyle = 3.5, '-'
            self.edgecolor = '#111111'

        patch = patches.PathPatch(
            self.spath, facecolor=self.color, alpha=self.alpha,
            edgecolor=self.edgecolor, linewidth=self.linewidth,
            linestyle=self.linestyle
        )
        ax.add_patch(patch)

        if kwargs.get('label'):
            c = self.center
            ax.text(c[0], c[1], kwargs['label'], fontsize=15,
                    ha='center', va='center', color='#111111')

    @staticmethod
    def from_clicks(ax=None, min_points=3, max_points=None):
        """
        Create polygon interactively by clicking.

        Parameters
        ----------
        ax : Axes, optional
            Axes to click on. Creates new figure if None.
        min_points : int, optional
            Minimum vertices. Default 3.
        max_points : int, optional
            Maximum vertices. None for unlimited.

        Returns
        -------
        Polygon
            New polygon from clicked points.

        Notes
        -----
        Press 'q' or close window when done.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.set_title("Click points, press 'q' when done")
            ax.grid(True, alpha=0.3)
            ax.set_xlim(-10, 10)
            ax.set_ylim(-10, 10)
        else:
            fig = ax.figure

        points = []

        def onclick(event):
            if event.inaxes != ax or event.button != 1:
                return
            if max_points and len(points) >= max_points:
                return
            points.append((event.xdata, event.ydata))
            ax.plot(event.xdata, event.ydata, 'ro', ms=8)

            if len(points) >= 2:
                xs, ys = zip(*points)
                ax.plot(xs, ys, 'b-', lw=2, alpha=0.5)

            fig.canvas.draw()

        def onkey(event):
            if event.key in ('q', 'Q') and len(points) >= min_points:
                plt.close(fig)

        fig.canvas.mpl_connect('button_press_event', onclick)
        fig.canvas.mpl_connect('key_press_event', onkey)
        plt.show(block=True)

        if len(points) < min_points:
            raise ValueError(f'Need {min_points} points, got {len(points)}')

        return Polygon(vertices=points)

    @staticmethod
    def from_data(data, method='convex_hull', **kwargs):
        """
        Create polygon from data points.

        Parameters
        ----------
        data : ndarray or DataFrame
            Data points.
        method : str
            'convex_hull' or 'bounding_box'.
        **kwargs
            Passed to Polygon constructor.

        Returns
        -------
        Polygon
        """
        if isinstance(data, pd.DataFrame):
            pts = data[['x', 'y']].values if 'x' in data.columns else data.values
        else:
            pts = data.T if data.shape[0] == 2 else data

        if method == 'bounding_box':
            x_min, x_max = pts[:, 0].min(), pts[:, 0].max()
            y_min, y_max = pts[:, 1].min(), pts[:, 1].max()
            verts = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        elif method == 'convex_hull':
            from scipy.spatial import ConvexHull
            hull = ConvexHull(pts)
            verts = pts[hull.vertices].tolist()
        else:
            raise ValueError(f"Unknown method: {method}")

        return Polygon(vertices=verts, **kwargs)
