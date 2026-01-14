import numpy as np
import matplotlib.pyplot as plt


def plot_spectrum(shifts, peak=1, width=2, padding=0, res=1000,
                  x_min=None, x_max=None, x_label=None,
                  y_label=None, y2_label=None, y_legend=None, y2_legend=None):
    if x_min is None:
        x_min = min(shifts) - padding
    if x_max is None:
        x_max = max(shifts) + padding
    if isinstance(peak, (int, float)):
        peak = np.ones_like(shifts) * peak
    if isinstance(width, (int, float)):
        width = np.ones_like(shifts) * width
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.linspace(x_min, x_max, res)
    y = np.zeros_like(x)
    y2 = np.zeros_like(x)
    gamma = width / 2.0
    for s, p, w in zip(shifts, peak, width):
        g = w / 2.0
        y += p * (1.0 / np.pi) * (g / ((x - s)**2 + g**2))
    ax.plot(x, y, color='black', lw=1.5, label=y_legend)
    if x_label is not None:
        ax.set_xlabel(x_label)
    if y_label is not None:
        ax.set_ylabel(y_label)
    if y_legend is not None:
        ax.legend(loc="upper left")
    ax2 = ax.twinx()
    if y2_label is not None:
        ax2.set_ylabel(y2_label)
    bin_width = 0.01
    bins = np.arange(x_min, x_max + bin_width, bin_width)
    counts, bin_edges = np.histogram(shifts, bins=bins, weights=peak)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    mask = counts > 0
    markerline, stemlines, baseline = ax2.stem(bin_centers[mask], counts[mask],
                                               linefmt='C2-', markerfmt=' ',
                                               basefmt=' ', label=y2_legend)
    if y2_legend is not None:
        ax2.legend(loc="upper right")
    fig.tight_layout()
    ax.grid()
    return fig, ax, ax2
