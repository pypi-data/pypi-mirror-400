Scratch3 Analyzer
=================

A comprehensive Python library to extract, analyze, and export detailed statistics from Scratch 3.0 (.sb3) project files.

.. image:: https://img.shields.io/pypi/v/scratch3_analyzer.svg
   :target: https://pypi.org/project/scratch3_analyzer/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/scratch3_analyzer.svg
   :target: https://pypi.org/project/scratch3_analyzer/
   :alt: Python Versions

.. image:: https://img.shields.io/pypi/l/scratch3_analyzer.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

Features
--------

* Extract and analyze Scratch 3.0 project files (.sb3)
* Analyze sprites, blocks, variables, lists, costumes, sounds, and events
* Calculate project complexity scores
* Export analysis results to Excel with multiple sheets
* Batch process multiple .sb3 files
* Command-line interface for easy use
* Graphical user interface (GUI) for intuitive interaction
* Python API for programmatic access

Installation
------------

Install from PyPI::

   pip install scratch3_analyzer

Requirements
------------

* Python 3.7 or higher
* pandas >= 1.3.0
* openpyxl >= 3.0.0

For GUI functionality (optional):
* tkinter (usually included with Python on Windows and macOS)

Quick Start
-----------

Using Python API
~~~~~~~~~~~~~~~~

.. code-block:: python

   from scratch3_analyzer import Scratch3Analyzer

   # Create analyzer instance
   analyzer = Scratch3Analyzer()

   # Analyze a single .sb3 file
   result = analyzer.analyze_file(
       sb3_path="my_project.sb3",
       output_excel="analysis_results.xlsx"  # Optional: export to Excel
   )

   # Print some statistics
   print(f"Total blocks: {result['complexity']['total_blocks']}")
   print(f"Total sprites: {result['complexity']['total_sprites']}")
   print(f"Complexity score: {result['complexity']['complexity_score']}")

Using Command Line
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Analyze a single file
   scratch3-analyzer analyze my_project.sb3 --output results.xlsx

   # Analyze all files in a directory
   scratch3-analyzer batch ./projects --output summary.xlsx

   # Show version
   scratch3-analyzer --version

   # Show help
   scratch3-analyzer --help

Graphical User Interface (GUI)
------------------------------

Starting from version 1.1.0, Scratch3 Analyzer includes a graphical user interface.

Launch GUI::

   scratch3-analyzer --gui

GUI Features::

   * Single file analysis: Select and analyze individual .sb3 files
   * Batch processing: Analyze all .sb3 files in a directory
   * Recursive search: Option to search subdirectories for .sb3 files
   * Excel export: Export results to Excel with customizable output path
   * Progress tracking: Real-time progress display during analysis
   * Results display: View analysis results directly in the application

Development
-----------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/jzm3/scratch3_analyzer.git
   cd scratch3_analyzer

   # Install in development mode
   pip install -e .

Building and Publishing
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Build package
   python -m build

   # Upload to PyPI
   python -m twine upload dist/*

Contributing
------------

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: ``git checkout -b feature/amazing-feature``
3. Commit your changes: ``git commit -m 'Add amazing feature'``
4. Push to the branch: ``git push origin feature/amazing-feature``
5. Open a Pull Request

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.

Author
------

jzm (939370014@qq.com)

Project Home
------------

* GitHub: https://github.com/jzm3/scratch3_analyzer
* PyPI: https://pypi.org/project/scratch3_analyzer/
* Issues: https://github.com/jzm3/scratch3_analyzer/issues

Changelog
---------

Version 1.1.0 (2024-01-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Added**

* Added graphical user interface (GUI) with tkinter
* New ``--gui`` command-line option to launch the GUI
* GUI features include file selection, batch processing, and results display
* Progress tracking during analysis
* Recursive directory search option in GUI

**Changed**

* Updated CLI to support GUI mode
* Enhanced user experience with better error messages

**Fixed**

* Improved error handling in file extraction
* Fixed compatibility issues with different Python versions

Version 1.0.1 (2024-01-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Added**

* Added comprehensive documentation
* Improved README with detailed examples
* Enhanced API documentation

**Changed**

* Updated README format to reStructuredText (RST)
* Enhanced command-line help messages

**Fixed**

* Fixed documentation formatting
* Improved compatibility with different Python versions

Version 1.0.0 (2024-01-07)
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Added**

* Initial release of Scratch3 Analyzer
* Core functionality for analyzing Scratch 3.0 (.sb3) files
* Support for extracting sprites, blocks, variables, lists, costumes, sounds, and events
* Excel export functionality with multiple sheets
* Command-line interface
* Batch processing of multiple .sb3 files
* Project complexity scoring system