#!/usr/bin/env python3
#
#  __init__.py
"""
Plotting extension for PyMassSpec.
"""
################################################################################
#                                                                              #
#    PyMassSpec software for processing of mass-spectrometry data              #
#    Copyright (C) 2005-2012 Vladimir Likic                                    #
#    Copyright (C) 2019-2021 Dominic Davis-Foster                              #
#                                                                              #
#    This program is free software; you can redistribute it and/or modify      #
#    it under the terms of the GNU General Public License version 2 as         #
#    published by the Free Software Foundation.                                #
#                                                                              #
#    This program is distributed in the hope that it will be useful,           #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#    GNU General Public License for more details.                              #
#                                                                              #
#    You should have received a copy of the GNU General Public License         #
#    along with this program; if not, write to the Free Software               #
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.                 #
#                                                                              #
################################################################################

# stdlib
from typing import List, Mapping, Optional, Sequence, Tuple

# 3rd party
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
from matplotlib.container import BarContainer
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from pyms import Peak
from pyms.IonChromatogram import IonChromatogram
from pyms.Peak.List.Function import is_peak_list
from pyms.Spectrum import MassSpectrum, normalize_mass_spec

# this package
from pymassspec_plot.utils import invert_mass_spec

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020-2021 Dominic Davis-Foster"
__license__: str = "GNU General Public License v2 (GPLv2)"
__version__: str = "0.2.1"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["plot_ic", "plot_mass_spec", "plot_peaks", "plot_head2tail", "ClickEventHandler"]

default_filetypes = ["png", "pdf", "svg"]

# Ensure that the intersphinx links are correct.
Axes.__module__ = "matplotlib.axes"
Figure.__module__ = "matplotlib.figure"


def plot_ic(  # noqa: PRM002
		ax: matplotlib.axes.Axes,
		ic: IonChromatogram,
		minutes: bool = False,
		**kwargs,
		) -> List[Line2D]:
	"""
	Plots an Ion Chromatogram.

	:param ax: The axes to plot the IonChromatogram on.
	:param ic: Ion chromatogram m/z channels for plotting.
	:param minutes: Whether the x-axis should be plotted in minutes. Default :py:obj:`False` (plotted in seconds)
	:no-default minutes:

	:Other Parameters: :class:`matplotlib.lines.Line2D` properties.
		Used to specify properties like a line label (for auto legends),
		linewidth, antialiasing, marker face color.

		.. code-block:: python

			>>> plot_ic(im.get_ic_at_index(5), label='IC @ Index 5', linewidth=2)

		See :class:`matplotlib.lines.Line2D` for the list of possible keyword arguments.

	:return: A list of Line2D objects representing the plotted data.
	"""

	if not isinstance(ic, IonChromatogram):
		raise TypeError("'ic' must be an IonChromatogram")

	time_list = ic.time_list

	if minutes:
		time_list = [time / 60 for time in time_list]

	plot = ax.plot(time_list, ic.intensity_array, **kwargs)

	# Set axis ranges
	ax.set_xlim(min(time_list), max(time_list))
	ax.set_ylim(bottom=0)

	return plot


def plot_mass_spec(ax: Axes, mass_spec: MassSpectrum, **kwargs) -> BarContainer:  # noqa: PRM002
	"""
	Plots a Mass Spectrum.

	:param ax: The axes to plot the :class:`~pyms.Spectrum.MassSpectrum` on.
	:param mass_spec: The mass spectrum to plot.

	:Other Parameters: :class:`matplotlib.lines.Line2D` properties.
		Used to specify properties like a line label (for auto legends),
		linewidth, antialiasing, marker face color.

		Example::

		>>> plot_mass_spec(im.get_ms_at_index(5), linewidth=2)
		>>>	ax.set_title(f"Mass spec for peak at time {im.get_time_at_index(5):5.2f}")

	See :class:`matplotlib.lines.Line2D` for the list of possible keyword arguments.

	:return: Container with all the bars, and optionally errorbars.
	"""

	if not isinstance(mass_spec, MassSpectrum):
		raise TypeError("'mass_spec' must be a MassSpectrum")

	mass_list = mass_spec.mass_list
	intensity_list = mass_spec.mass_spec

	if "width" not in kwargs:
		kwargs["width"] = 0.5

	# to set x axis range find minimum and maximum m/z channels
	min_mz = mass_list[0]
	max_mz = mass_list[-1]

	for idx, mass in enumerate(mass_list):
		if mass_list[idx] > max_mz:
			max_mz = mass_list[idx]

	for idx, mass in enumerate(mass_list):
		if mass_list[idx] < min_mz:
			min_mz = mass_list[idx]

	plot = ax.bar(mass_list, intensity_list, **kwargs)

	# Set axis ranges
	ax.set_xlim(min_mz - 1, max_mz + 1)
	ax.set_ylim(bottom=0)

	return plot


_spec_quargs_t = "'{0}_spec_kwargs' must be a mapping of keyword arguments for the {0} mass spectrum."


def plot_head2tail(
		ax: Axes,
		top_mass_spec: MassSpectrum,
		bottom_mass_spec: MassSpectrum,
		top_spec_kwargs: Optional[Mapping] = None,
		bottom_spec_kwargs: Optional[Mapping] = None,
		) -> Tuple[BarContainer, BarContainer]:
	"""
	Plots two mass spectra head to tail.

	:param ax: The axes to plot the MassSpectra on.
	:param top_mass_spec: The mass spectrum to plot on top.
	:param bottom_mass_spec: The mass spectrum to plot on the bottom.
	:param top_spec_kwargs: A dictionary of keyword arguments for the top mass spectrum.
		Defaults to red with a line width of ``0.5``.
	:no-default top_spec_kwargs:
	:param bottom_spec_kwargs: A dictionary of keyword arguments for the bottom mass spectrum.
		Defaults to blue with a line width of ``0.5``.
	:no-default bottom_spec_kwargs:

	``top_spec_kwargs`` and ``bottom_spec_kwargs`` are used to specify properties like a line label
	(for auto legends), linewidth, antialiasing, and marker face color.
	See :class:`matplotlib.lines.Line2D` for the list of possible keyword arguments.

	:return: A tuple of containers with all the bars, and optionally errorbars, for the top and bottom spectra.

	.. clearpage::
	"""

	if not isinstance(top_mass_spec, MassSpectrum):
		raise TypeError("'top_mass_spec' must be a MassSpectrum")

	if not isinstance(bottom_mass_spec, MassSpectrum):
		raise TypeError("'bottom_mass_spec' must be a MassSpectrum")

	if top_spec_kwargs is None:
		top_spec_kwargs = dict(color="red", width=0.5)
	elif not isinstance(top_spec_kwargs, Mapping):
		raise TypeError(_spec_quargs_t.format("top"))

	if bottom_spec_kwargs is None:
		bottom_spec_kwargs = dict(color="blue", width=0.5)
	elif not isinstance(bottom_spec_kwargs, Mapping):
		raise TypeError(_spec_quargs_t.format("bottom"))

	# Plot a line at y=0 with same width and colour as Spines
	ax.axhline(
			y=0,
			color=ax.spines["bottom"].get_edgecolor(),
			linewidth=ax.spines["bottom"].get_linewidth(),
			)

	# Normalize the mass spectra
	top_mass_spec = normalize_mass_spec(top_mass_spec)
	bottom_mass_spec = normalize_mass_spec(bottom_mass_spec)

	# Invert bottom mass spec
	invert_mass_spec(bottom_mass_spec, inplace=True)

	top_plot = plot_mass_spec(ax, top_mass_spec, **top_spec_kwargs)
	bottom_plot = plot_mass_spec(ax, bottom_mass_spec, **bottom_spec_kwargs)

	# Set ylim to 1.1 times max/min values
	ax.set_ylim(
			bottom=min(bottom_mass_spec.intensity_list) * 1.1,
			top=max(top_mass_spec.intensity_list) * 1.1,
			)

	# ax.spines['bottom'].set_position('zero')

	return top_plot, bottom_plot


def plot_peaks(
		ax: Axes,
		peak_list: Sequence[Peak.Peak],
		label: str = "Peaks",
		style: str = 'o',
		) -> List[Line2D]:
	"""
	Plots the locations of peaks as found by PyMassSpec.

	:param ax: The axes to plot the peaks on.
	:param peak_list: List of peaks to plot.
	:param label: label for plot legend.
	:param style: The marker style. See :mod:`matplotlib.markers` for a complete list

	:return: A list of Line2D objects representing the plotted data.
	"""

	if not is_peak_list(peak_list):
		raise TypeError("'peak_list' must be a list of Peak objects")

	time_list = []
	height_list = []

	if "line" in style.lower():
		lines = []
		for peak in peak_list:
			lines.append(ax.axvline(x=peak.rt, color="lightgrey", alpha=0.8, linewidth=0.3))

		return lines

	else:
		for peak in peak_list:
			time_list.append(peak.rt)
			height_list.append(sum(peak.mass_spectrum.intensity_list))
			# height_list.append(peak.height)
			# print(peak.height - sum(peak.mass_spectrum.intensity_list))
			# print(sum(peak.mass_spectrum.intensity_list))

		return ax.plot(time_list, height_list, style, label=label)


# TODO: Change order of arguments and use plt.gca() a la pyplot


class ClickEventHandler:
	"""
	Class to enable clicking of a chromatogram to view the intensities top ``n_intensities``
	most intense ions at that peak, and viewing of the mass spectrum with a right click.

	:param peak_list: The list of peaks identified in the chromatogram.
	:param fig: The figure to associate the event handler with.
		Defaults to the current figure. (see :func:`plt.gcf() <matplotlib.pyplot.gcf>`.
	:no-default fig:
	:param ax: The axes to associate the event handler with.
		Defaults to the current axes. (see :func:`plt.gca() <matplotlib.pyplot.gca>`.
	:no-default ax:
	:param tolerance:
	:param n_intensities:
	"""  # noqa: D400

	#: The figure to associate the event handler with.
	fig: Figure
	#: The axes to associate the event handler with.
	ax: Axes

	#: The figure to plot mass spectra on after right clicking the plot.
	ms_fig: Optional[Figure]
	#: The axes to plot mass spectra on after right clicking the plot.
	ms_ax: Optional[Axes]

	#: The number of top intensities to show in the terminal when left clicking the plot.
	n_intensities: int

	#: The callback ID for the button press event.
	cid: Optional[int]

	def __init__(
			self,
			peak_list: Sequence[Peak.Peak],
			fig: Optional[Figure] = None,
			ax: Optional[Axes] = None,
			tolerance: float = 0.005,
			n_intensities: int = 5,
			):

		if fig is None:
			self.fig = plt.gcf()
		else:
			self.fig = fig

		if ax is None:
			self.ax = plt.gca()
		else:
			self.ax = ax

		self.peak_list = peak_list

		self.ms_fig = None
		self.ms_ax = None

		self._min = 1 - tolerance
		self._max = 1 + tolerance
		self.n_intensities = n_intensities

		# If no peak list plot, no mouse click event
		if len(self.peak_list):
			self.cid = self.fig.canvas.mpl_connect("button_press_event", self.onclick)  # type: ignore[arg-type]
		else:
			self.cid = None

	def onclick(self, event: MouseEvent) -> None:
		"""
		Finds the n highest intensity m/z channels for the selected peak.
		The peak is selected by clicking on it.
		If a button other than the left one is clicked, a new plot of the mass spectrum is displayed.

		:param event: a mouse click by the user
		"""

		for peak in self.peak_list:
			# if event.xdata > 0.9999*peak.rt and event.xdata < 1.0001*peak.rt:
			assert event.xdata is not None
			if self._min * peak.rt < event.xdata < self._max * peak.rt:
				intensity_list = peak.mass_spectrum.mass_spec
				mass_list = peak.mass_spectrum.mass_list

				largest = self.get_n_largest(intensity_list)

				print(f"RT: {peak.rt}")
				print("Mass\t Intensity")
				for i in range(self.n_intensities):
					print(f"{mass_list[largest[i]]}\t {intensity_list[largest[i]]:0.6f}")

				# Check if right mouse button pressed, if so plot mass spectrum
				# Also check that a peak was selected, not just whitespace
				if event.button == 3 and len(intensity_list):

					if self.ms_fig is None or self.ms_ax is None:
						self.ms_fig, self.ms_ax = plt.subplots(1, 1)
					else:
						self.ms_ax.clear()

					plot_mass_spec(self.ms_ax, peak.mass_spectrum)
					self.ms_ax.set_title(f"Mass Spectrum at RT {peak.rt}")
					self.ms_fig.show()

				# TODO: Add multiple MS to same plot window and add option to close one of them
				# TODO: Allow more interaction with MS, e.g. adjusting mass range?
				return

		# if the selected point is not close enough to peak
		print("No Peak at this point")

	def get_n_largest(self, intensity_list: List[float]) -> List[int]:
		"""
		Computes the indices of the largest n ion intensities for writing to console.

		:param intensity_list: List of ion intensities.

		:return: Indices of largest :attr:`~.n_intensities` ion intensities.
		"""

		largest = [0] * self.n_intensities

		# Find out largest value
		for idx, intensity in enumerate(intensity_list):
			if intensity > intensity_list[largest[0]]:
				largest[0] = idx

		# Now find next four largest values
		for j in list(range(1, self.n_intensities)):
			for idx, intensity in enumerate(intensity_list):
				# if intensity_list[i] > intensity_list[largest[j]] and intensity_list[i] < intensity_list[largest[j-1]]:
				if intensity_list[largest[j]] < intensity < intensity_list[largest[j - 1]]:
					largest[j] = idx

		return largest
