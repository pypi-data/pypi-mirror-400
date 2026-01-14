"""
Scratch3 Analyzer - A Python library for analyzing Scratch 3.0 (.sb3) project files

This library provides tools to extract, analyze, and export statistics from 
Scratch 3.0 project files. It can analyze sprites, blocks, variables, lists, 
costumes, sounds, events, and calculate project complexity.
"""

__version__ = "1.1.0"  # 更新版本号
__author__ = "jzm"
__email__ = "939370014@qq.com"

from .core import Scratch3Analyzer
from .extractor import SB3Extractor
from .analyzer import ProjectAnalyzer
from .exporter import ExcelExporter
from .gui import Scratch3AnalyzerGUI

__all__ = [
    'Scratch3Analyzer',
    'SB3Extractor', 
    'ProjectAnalyzer',
    'ExcelExporter',
    'Scratch3AnalyzerGUI',
]