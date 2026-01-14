from math import isfinite

import matplotlib.pyplot as plt
from typing import List, Dict
import numpy as np
from pathlib import Path
import astropy.units as u

import inspect

from matplotlib import ticker

from hwo_disra.DRMinator import YieldSample


class Plotinator(object):

    def __init__(self,
                 file_prefix: str | None = None,
                 output_dir: Path | None = None,
                 show_plots: bool = False):
        self.output_dir = output_dir
        self.file_prefix = file_prefix
        self.show_plots = show_plots

    def contour_plot(self, samples: List[List[YieldSample]],
                     x_key: str, y_key: str, z_key: str,
                     num_color_levels=20,
                     contour_levels=None,
                     contour_color='white',
                     color_label = None,
                     titles=None,
                     units: dict[str, u.UnitBase | str] = {},
                     filename='',
                     transforms: Dict[str, callable] = None,
                     axis_labels: Dict[str, str] = None,
                     file_prefix: str = "", figsize = None):
        """
        Makes a contour plot from dictionary data

        Args:
            data: Tuple containing any value and a list of dictionaries with float values
            x_key: Key for x-axis values in the dictionaries
            y_key: Key for y-axis values in the dictionaries
            z_key: Key for z-axis values (colors) in the dictionaries
            num_color_levels (optional): number of contour levels (default = 20)
            contour_levels (optional): values for overplotted countour lines
            contour_color (optional): color of contour lines (default = 'white')
            color_label (optional): text label for colorbar (default = z_key)
            title (optional): text title overlaid on plotted image (default = ' ')
            filename (optional): if provided, saves plot to this filename
            transforms: (optional): if provided should be a dictionary mapping
                        one or more of the *_key values to a function from
                        values of that key to new values.  These transform(s)
                        will be applied prior to plotting.
            axis_labels: (optional) dictionary mapping *_key values to the
                        text that should be used as the axis label for that
                        key axis.

        Returns:
            Produces plot with contours and returns the contour levels
        """
        if transforms is None:
            transforms = {}
        if axis_labels is None:
            axis_labels = {}
        if titles is None:
            titles = []

        transforms = {x_key: transforms.get(x_key) or (lambda x: x),
                      y_key: transforms.get(y_key) or (lambda y: y),
                      z_key: transforms.get(z_key) or (lambda z: z)}

        samples = [self.apply_transforms(s, x_key, y_key, z_key, transforms) for s in samples]

        plot_count = len(samples)
        cols = min(plot_count, 3)
        nrows = max(1, (int) (plot_count / cols))

        fig, axs = plt.subplots(nrows, cols,
                                figsize=figsize,
                                squeeze=False)

        all_z_values = [d[z_key] for s in samples for d in s if isfinite(d[z_key])]
        z_min, z_max = min(all_z_values), max(all_z_values)
        consistent_levels = np.linspace(z_min, z_max, num_color_levels)

        # fig.suptitle(title)
        axs = axs.ravel()
        def smart_formatter(x, pos):
            if x == int(x):  # Check if it's effectively an integer
                return f'{int(x)}'
            else:
                return f'{x:.3f}'.rstrip('0').rstrip('.')

        for i,sample in enumerate(samples):
            # Extract unique x and y values and sort them
            x_values = sorted(set(d[x_key] for d in sample))
            y_values = sorted(set(d[y_key] for d in sample))

            # Create 2D matrix of z values
            matrix = np.zeros((len(y_values), len(x_values)))
            x_idx = {x: i for i, x in enumerate(x_values)}
            y_idx = {y: i for i, y in enumerate(y_values)}

            for d in sample:
                ix = y_idx[d[y_key]]
                jx = x_idx[d[x_key]]
                matrix[ix][jx] = d[z_key]

            ax = axs[i]

            ax.xaxis.set_major_formatter(ticker.FuncFormatter(smart_formatter))
            ax.set_xlabel(axis_labels.get(x_key) or f"{x_key} ({units.get(x_key, 'unknown units')})")
            ax.set_ylabel(axis_labels.get(y_key) or f"{y_key} ({units.get(y_key, 'unknown units')})")

            cont = ax.contourf(x_values, y_values, matrix, levels=consistent_levels)

            x = np.max(x_values) - (np.max(x_values) - np.min(x_values))*0.05
            y = np.max(y_values) - (np.max(y_values) - np.min(y_values))*0.05
            ax.text(x, y, titles[i] if i < len(titles) else '', color='white', horizontalalignment='right', verticalalignment='top', fontsize='medium', fontweight='semibold')

            if contour_levels is not None:
                cont_lines = ax.contour(x_values, y_values, matrix, levels=contour_levels, colors=contour_color)
                ax.clabel(cont_lines, inline=True, fontsize='medium')

            if i == len(samples) - 1:
                fig.colorbar(cont, ax=ax, label=color_label or axis_labels.get(z_key) or f"{z_key} ({units.get(z_key) or 'unknown units'})")



        # fig.colorbar(cont, label=color_label or axis_labels.get(z_key) or z_key)
        # fig.subplots_adjust(right=0.8)
        # cbar_ax = fig.add_axes((0.83, 0.15, 0.03, 0.7))
        # if cont is not None:
        #     cbar = fig.colorbar(cont, cax=cbar_ax)
        #     cb = plt.colorbar(cont, cax=cbar_ax)
        #     cb.set_label(label=color_label or axis_labels.get(z_key) or z_key)
        # plt.savefig("kbo_panel2_plot2.pdf", bbox_inches='tight')
        # files.download("kbo_panel2_plot2.pdf")
        self.write_plot(f"{file_prefix}-{filename}")
        self.show_plot()

    @staticmethod
    def plot_args(*args, **kwargs):
        return args, kwargs

    def region_bar_plot(self, bar_regions,
        line_plots, title = None, scale = None,
        ylim = None, xlim = None, ylabel = None,
        xlabel = None, filename = None):
        fig=plt.figure()
        plt.style.use('default')
        ax=fig.add_subplot(111)

        if scale is not None:
            ax.set_yscale(scale)
        if title is not None:
            plt.title(title)
        for args, kwargs in line_plots:
            plt.plot(*args, **kwargs)

        for args, kwargs in bar_regions:
            plt.bar(*args, **kwargs)

        if ylim is not None:
            plt.ylim(*ylim)
        if xlim is not None:
            plt.xlim(*xlim)
        if ylabel is not None:
            plt.ylabel(ylabel)
        if xlabel is not None:
            plt.xlabel(xlabel)

        plt.legend(loc='best')
        self.write_plot(filename)
        self.show_plot()

    def barplot(self, x_values, y_values, z_values,
                    x_key: str, y_key: str, z_key: str,
                    title="", filename="",
                    transforms: Dict[str, callable] = {},
                    axis_labels: Dict[str, str] = {},
                    file_prefix: str = ""):
        fig = plt.figure()

        print(x_values)

        ax = fig.add_subplot(111)
        ax.bar(x_values, y_values)
        ax.set_xlabel(x_key)
        ax.set_ylabel(y_key)
        ax.set_title(title)

        self.write_plot(filename)

    def apply_transforms(self, dict_list, x_key, y_key, z_key, transforms):
        def apply_transform(key, d):
            f = transforms[key]
            sig = inspect.signature(f)

            if len(sig.parameters) == 1:
                return f(d[key])
            else:
                params = { name: d[name]
                           for name in sig.parameters
                           if name in d}
                return f(**params)

        return [{key: apply_transform(key, d)
                     for key in [x_key, y_key, z_key]}
                     for d in dict_list]

    def show_plot(self):
        """
        If `self.show_plots = True` show the current plot with `plt.show()`
        """
        if self.show_plots:
            plt.show()

    def write_plot(self, filename: str):
        """
        Write the current plot to `self.output_dir / filename`
        with plt.savefig.  If output_dir is not specified, do nothing.
        """
        if self.output_dir is not None and self.file_prefix is not None:
            plt.savefig(self.output_dir / f"{self.file_prefix}-{filename}",
                        bbox_inches = 'tight')
