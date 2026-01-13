#!/usr/bin/env python3
#
#  utils.py
"""
Utility functions.
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

# 3rd party
from pyms.Spectrum import MassSpectrum

__all__ = ["invert_mass_spec"]


def invert_mass_spec(mass_spec: MassSpectrum, inplace: bool = False) -> MassSpectrum:
	"""
	Invert the mass spectrum for display in a head2tail plot.

	:param mass_spec: The Mass Spectrum to normalize
	:param inplace: Whether the inversion should be applied to the
		:class:`~pyms.Spectrum.MassSpectrum` object given (:py:obj:`True`),
		or to a copy (:py:obj:`False`).

	:return: The normalized mass spectrum.
	"""

	inverted_intensity_list = [-x for x in mass_spec.intensity_list]

	if inplace:
		mass_spec.intensity_list = inverted_intensity_list
		return mass_spec
	else:
		return MassSpectrum(mass_spec.mass_list, inverted_intensity_list)
