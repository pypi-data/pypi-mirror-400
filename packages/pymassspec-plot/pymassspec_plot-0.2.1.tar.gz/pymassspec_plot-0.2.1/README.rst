################
PyMassSpec-Plot
################

.. start short_desc

**Plotting extension for PyMassSpec.**

.. end short_desc


.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |actions_linux| |actions_windows| |actions_macos| |coveralls|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy|
	* - Other
	  - |license| |language| |requires|

.. |docs| image:: https://img.shields.io/readthedocs/pymassspec-plot/latest?logo=read-the-docs
	:target: https://pymassspec-plot.readthedocs.io/en/latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/PyMassSpec/PyMassSpec-Plot/workflows/Docs%20Check/badge.svg
	:target: https://github.com/PyMassSpec/PyMassSpec-Plot/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |actions_linux| image:: https://github.com/PyMassSpec/PyMassSpec-Plot/workflows/Linux/badge.svg
	:target: https://github.com/PyMassSpec/PyMassSpec-Plot/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/PyMassSpec/PyMassSpec-Plot/workflows/Windows/badge.svg
	:target: https://github.com/PyMassSpec/PyMassSpec-Plot/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/PyMassSpec/PyMassSpec-Plot/workflows/macOS/badge.svg
	:target: https://github.com/PyMassSpec/PyMassSpec-Plot/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status

.. |actions_flake8| image:: https://github.com/PyMassSpec/PyMassSpec-Plot/workflows/Flake8/badge.svg
	:target: https://github.com/PyMassSpec/PyMassSpec-Plot/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/PyMassSpec/PyMassSpec-Plot/workflows/mypy/badge.svg
	:target: https://github.com/PyMassSpec/PyMassSpec-Plot/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://dependency-dash.repo-helper.uk/github/PyMassSpec/PyMassSpec-Plot/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/PyMassSpec/PyMassSpec-Plot/
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/PyMassSpec/PyMassSpec-Plot/master?logo=coveralls
	:target: https://coveralls.io/github/PyMassSpec/PyMassSpec-Plot?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/PyMassSpec/PyMassSpec-Plot?logo=codefactor
	:target: https://www.codefactor.io/repository/github/PyMassSpec/PyMassSpec-Plot
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/PyMassSpec-Plot
	:target: https://pypi.org/project/PyMassSpec-Plot/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/PyMassSpec-Plot?logo=python&logoColor=white
	:target: https://pypi.org/project/PyMassSpec-Plot/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/PyMassSpec-Plot
	:target: https://pypi.org/project/PyMassSpec-Plot/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/PyMassSpec-Plot
	:target: https://pypi.org/project/PyMassSpec-Plot/
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/PyMassSpec-Plot?logo=anaconda
	:target: https://anaconda.org/domdfcoding/PyMassSpec-Plot
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/PyMassSpec-Plot?label=conda%7Cplatform
	:target: https://anaconda.org/domdfcoding/PyMassSpec-Plot
	:alt: Conda - Platform

.. |license| image:: https://img.shields.io/github/license/PyMassSpec/PyMassSpec-Plot
	:target: https://github.com/PyMassSpec/PyMassSpec-Plot/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/PyMassSpec/PyMassSpec-Plot
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/PyMassSpec/PyMassSpec-Plot/v0.2.1
	:target: https://github.com/PyMassSpec/PyMassSpec-Plot/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/PyMassSpec/PyMassSpec-Plot
	:target: https://github.com/PyMassSpec/PyMassSpec-Plot/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2026
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/PyMassSpec-Plot
	:target: https://pypi.org/project/PyMassSpec-Plot/
	:alt: PyPI - Downloads

.. end shields

Installation
--------------

.. start installation

``PyMassSpec-Plot`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install PyMassSpec-Plot

To install with ``conda``:

	* First add the required channels

	.. code-block:: bash

		$ conda config --add channels https://conda.anaconda.org/bioconda
		$ conda config --add channels https://conda.anaconda.org/conda-forge
		$ conda config --add channels https://conda.anaconda.org/domdfcoding

	* Then install

	.. code-block:: bash

		$ conda install PyMassSpec-Plot

.. end installation
