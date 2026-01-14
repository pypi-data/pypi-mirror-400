import os
import json
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd

from .extractor import SB3Extractor
from .analyzer import ProjectAnalyzer
from .exporter import ExcelExporter

class Scratch3Analyzer:
    """
    Scratch3 文件分析器主类
    """
    
    def __init__(self):
        self.extractor = SB3Extractor()
        self.analyzer = ProjectAnalyzer()
        self.exporter = ExcelExporter()
    
    def analyze_file(self, sb3_path: str, output_excel: str = None) -> Dict[str, Any]:
        """
        分析单个.sb3文件
        
        Args:
            sb3_path: .sb3文件路径
            output_excel: 输出Excel文件路径（可选）
            
        Returns:
            分析结果字典
        """
        # 提取项目数据
        project_data = self.extractor.extract_sb3(sb3_path)
        
        if not project_data:
            raise ValueError(f"无法提取文件: {sb3_path}")
        
        # 分析项目
        analysis_results = self.analyzer.analyze_project(project_data)
        
        # 添加文件信息
        analysis_results['file_info'] = {
            'filename': os.path.basename(sb3_path),
            'filepath': sb3_path,
            'filesize': os.path.getsize(sb3_path)
        }
        
        # 导出到Excel
        if output_excel:
            self.exporter.export_to_excel(analysis_results, output_excel)
        
        return analysis_results
    
    def analyze_directory(self, directory: str, output_excel: str = None) -> List[Dict[str, Any]]:
        """
        分析目录中的所有.sb3文件
        
        Args:
            directory: 目录路径
            output_excel: 输出Excel文件路径（可选）
            
        Returns:
            所有文件的分析结果列表
        """
        all_results = []
        
        # 查找所有.sb3文件
        sb3_files = list(Path(directory).glob("*.sb3"))
        
        if not sb3_files:
            print(f"在目录 {directory} 中未找到.sb3文件")
            return all_results
        
        for sb3_file in sb3_files:
            try:
                print(f"正在分析: {sb3_file.name}")
                result = self.analyze_file(str(sb3_file))
                result['file_info']['filename'] = sb3_file.name
                all_results.append(result)
            except Exception as e:
                print(f"分析文件 {sb3_file} 时出错: {e}")
                continue
        
        # 导出到Excel
        if output_excel and all_results:
            self.exporter.export_multiple_to_excel(all_results, output_excel)
        
        return all_results