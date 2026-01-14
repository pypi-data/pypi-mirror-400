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

* **Extract and analyze** Scratch 3.0 project files (.sb3)
* **Analyze sprites**, blocks, variables, lists, costumes, sounds, and events
* **Calculate project complexity** scores
* **Export analysis results** to Excel with multiple sheets
* **Batch process** multiple .sb3 files
* **Command-line interface** for easy use
* **Python API** for programmatic access

Installation
------------

Install from PyPI:

.. code-block:: bash

   pip install scratch3_analyzer

Requirements
------------

* Python 3.7 or higher
* pandas >= 1.3.0
* openpyxl >= 3.0.0

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

Analysis Output
---------------

The analyzer provides detailed information in these categories:

================================  ==============================================================
Category                          Description
================================  ==============================================================
**Project Info**                  Scratch version, extensions, cloud variables
**Sprites**                       All sprites with properties (position, size, visibility, etc.)
**Blocks**                        Block usage statistics by category and type
**Variables**                     All variables with values and cloud variable status
**Lists**                         All lists with item counts
**Costumes**                      Costume details and formats
**Sounds**                        Sound file details
**Events**                        Event block usage statistics
**Complexity**                    Project complexity metrics and scores
================================  ==============================================================

Advanced Usage
--------------

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

   from scratch3_analyzer import Scratch3Analyzer
   
   analyzer = Scratch3Analyzer()
   
   # Analyze all .sb3 files in a directory
   results = analyzer.analyze_directory(
       directory="./projects",
       output_excel="batch_analysis.xlsx"  # Optional: export summary to Excel
   )
   
   print(f"Analyzed {len(results)} projects")

Using Individual Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from scratch3_analyzer import SB3Extractor, ProjectAnalyzer, ExcelExporter
   
   # Use individual components
   extractor = SB3Extractor()
   analyzer = ProjectAnalyzer()
   exporter = ExcelExporter()
   
   # Extract project data
   project_data = extractor.extract_sb3("project.sb3")
   
   # Analyze the data
   analysis_results = analyzer.analyze_project(project_data)
   
   # Export to Excel
   exporter.export_to_excel(analysis_results, "detailed_analysis.xlsx")

Extract Specific Resources
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from scratch3_analyzer import SB3Extractor
   
   extractor = SB3Extractor()
   
   # Extract a specific costume or sound file
   costume_data = extractor.extract_specific_resource(
       sb3_path="project.sb3",
       resource_name="e0f5cf8c57f04f2e7c4a6e8d5c7b9a1f.png",
       output_path="costume.png"
   )

API Reference
-------------

Scratch3Analyzer
~~~~~~~~~~~~~~~~

.. code-block:: python

   class Scratch3Analyzer:
       def __init__(self):
           """Initialize the analyzer with extractor, analyzer, and exporter."""
       
       def analyze_file(self, sb3_path: str, output_excel: str = None) -> Dict[str, Any]:
           """
           Analyze a single .sb3 file.
           
           Args:
               sb3_path: Path to the .sb3 file
               output_excel: Optional path to export Excel results
               
           Returns:
               Dictionary containing all analysis results
           """
       
       def analyze_directory(self, directory: str, output_excel: str = None) -> List[Dict[str, Any]]:
           """
           Analyze all .sb3 files in a directory.
           
           Args:
               directory: Path to directory containing .sb3 files
               output_excel: Optional path to export Excel results
               
           Returns:
               List of analysis results for each file
           """

SB3Extractor
~~~~~~~~~~~~

.. code-block:: python

   class SB3Extractor:
       def extract_sb3(self, sb3_path: str) -> Optional[Dict[str, Any]]:
           """
           Extract project data from .sb3 file.
           
           Args:
               sb3_path: Path to the .sb3 file
               
           Returns:
               Dictionary containing project data and resources
           """
       
       def extract_specific_resource(self, sb3_path: str, resource_name: str, 
                                    output_path: str = None) -> Optional[bytes]:
           """
           Extract specific resource file from .sb3 file.
           
           Args:
               sb3_path: Path to the .sb3 file
               resource_name: Name of the resource file to extract
               output_path: Optional path to save the extracted file
               
           Returns:
               Binary data of the resource file
           """

ProjectAnalyzer
~~~~~~~~~~~~~~~

.. code-block:: python

   class ProjectAnalyzer:
       def analyze_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
           """
           Analyze project data and generate statistics.
           
           Args:
               project_data: Dictionary containing project data
               
           Returns:
               Dictionary containing analysis results
           """

ExcelExporter
~~~~~~~~~~~~~

.. code-block:: python

   class ExcelExporter:
       def export_to_excel(self, analysis_results: Dict[str, Any], output_path: str):
           """
           Export single project analysis to Excel.
           
           Args:
               analysis_results: Analysis results dictionary
               output_path: Path to save Excel file
           """
       
       def export_multiple_to_excel(self, all_results: List[Dict[str, Any]], output_path: str):
           """
           Export multiple project analyses to Excel.
           
           Args:
               all_results: List of analysis results dictionaries
               output_path: Path to save Excel file
           """

Command Line Interface
----------------------

Available Commands
~~~~~~~~~~~~~~~~~~

Analyze a Single File
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   scratch3-analyzer analyze <sb3_file> [options]
   
   Options:
       -o, --output OUTPUT    Output Excel file path
       --no-excel             Don't export to Excel

Analyze Multiple Files
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   scratch3-analyzer batch <directory> [options]
   
   Options:
       -o, --output OUTPUT    Output Excel file path
       -r, --recursive        Recursively search for .sb3 files

Show Version
^^^^^^^^^^^^

.. code-block:: bash

   scratch3-analyzer --version

Show Help
^^^^^^^^^

.. code-block:: bash

   scratch3-analyzer --help

Development
-----------

Setting Up Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/jzm3/scratch3_analyzer.git
   cd scratch3_analyzer
   
   # Create virtual environment
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   
   # Install in development mode
   pip install -e .

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Install test dependencies
   pip install pytest pytest-cov
   
   # Run tests
   pytest
   
   # Run tests with coverage
   pytest --cov=scratch3_analyzer

Code Style
~~~~~~~~~~

.. code-block:: bash

   # Install formatting tools
   pip install black flake8
   
   # Format code
   black .
   
   # Check code style
   flake8

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

This project is licensed under the MIT License - see the `LICENSE <LICENSE>`_ file for details.

Author
------

jzm (939370014@qq.com)

Project Home
------------

* GitHub: https://github.com/jzm3/scratch3_analyzer
* PyPI: https://pypi.org/project/scratch3_analyzer/
* Issues: https://github.com/jzm3/scratch3_analyzer/issues

Support
-------

If you encounter any issues or have questions:

1. Check the `GitHub Issues <https://github.com/jzm3/scratch3_analyzer/issues>`_
2. Email: 939370014@qq.com
3. Create a new issue on GitHub

Changelog
---------

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