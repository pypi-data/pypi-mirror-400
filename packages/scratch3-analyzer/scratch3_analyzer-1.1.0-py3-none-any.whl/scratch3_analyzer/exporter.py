import pandas as pd
from typing import Dict, List, Any
import os

class ExcelExporter:
    """
    导出分析结果到Excel的类
    """
    
    def export_to_excel(self, analysis_results: Dict[str, Any], output_path: str):
        """
        导出单个项目的分析结果到Excel
        
        Args:
            analysis_results: 分析结果字典
            output_path: 输出Excel文件路径
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 1. 项目信息
            project_info = analysis_results.get('project_info', {})
            project_info_df = pd.DataFrame([project_info])
            project_info_df.to_excel(writer, sheet_name='项目信息', index=False)
            
            # 2. 角色信息
            sprites = analysis_results.get('sprites', [])
            if sprites:
                sprites_df = pd.DataFrame(sprites)
                sprites_df.to_excel(writer, sheet_name='角色信息', index=False)
            
            # 3. 代码块分析
            blocks = analysis_results.get('blocks', {})
            if blocks:
                # 代码块类型统计
                block_counts_df = pd.DataFrame(
                    list(blocks.get('block_counts', {}).items()),
                    columns=['代码块类型', '数量']
                )
                block_counts_df.to_excel(writer, sheet_name='代码块统计', index=False)
                
                # 代码块类别统计
                category_counts_df = pd.DataFrame(
                    list(blocks.get('category_counts', {}).items()),
                    columns=['代码块类别', '数量']
                )
                category_counts_df.to_excel(writer, sheet_name='类别统计', index=False)
            
            # 4. 变量信息
            variables = analysis_results.get('variables', {})
            if variables.get('variables'):
                variables_df = pd.DataFrame(variables['variables'])
                variables_df.to_excel(writer, sheet_name='变量信息', index=False)
            
            # 5. 列表信息
            lists = analysis_results.get('lists', {})
            if lists.get('lists'):
                lists_df = pd.DataFrame(lists['lists'])
                lists_df.to_excel(writer, sheet_name='列表信息', index=False)
            
            # 6. 造型信息
            costumes = analysis_results.get('costumes', {})
            if costumes.get('costumes'):
                costumes_df = pd.DataFrame(costumes['costumes'])
                costumes_df.to_excel(writer, sheet_name='造型信息', index=False)
            
            # 7. 声音信息
            sounds = analysis_results.get('sounds', {})
            if sounds.get('sounds'):
                sounds_df = pd.DataFrame(sounds['sounds'])
                sounds_df.to_excel(writer, sheet_name='声音信息', index=False)
            
            # 8. 事件分析
            events = analysis_results.get('events', {})
            if events:
                events_df = pd.DataFrame(
                    list(events.get('event_counts', {}).items()),
                    columns=['事件类型', '数量']
                )
                events_df.to_excel(writer, sheet_name='事件分析', index=False)
            
            # 9. 复杂度分析
            complexity = analysis_results.get('complexity', {})
            if complexity:
                complexity_df = pd.DataFrame([complexity])
                complexity_df.to_excel(writer, sheet_name='复杂度分析', index=False)
            
            # 10. 文件信息
            file_info = analysis_results.get('file_info', {})
            if file_info:
                file_info_df = pd.DataFrame([file_info])
                file_info_df.to_excel(writer, sheet_name='文件信息', index=False)
            
            print(f"分析结果已导出到: {output_path}")
    
    def export_multiple_to_excel(self, all_results: List[Dict[str, Any]], output_path: str):
        """
        导出多个项目的分析结果到Excel
        
        Args:
            all_results: 多个项目的分析结果列表
            output_path: 输出Excel文件路径
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 汇总表格：所有项目的基本信息
            summary_data = []
            
            for result in all_results:
                file_info = result.get('file_info', {})
                complexity = result.get('complexity', {})
                blocks = result.get('blocks', {})
                variables = result.get('variables', {})
                lists = result.get('lists', {})
                
                summary_data.append({
                    '文件名': file_info.get('filename', ''),
                    '文件大小(KB)': file_info.get('filesize', 0) / 1024,
                    '角色数量': complexity.get('total_sprites', 0),
                    '代码块总数': complexity.get('total_blocks', 0),
                    '变量数量': complexity.get('total_variables', 0),
                    '列表数量': complexity.get('total_lists', 0),
                    '造型数量': result.get('costumes', {}).get('total_costumes', 0),
                    '声音数量': result.get('sounds', {}).get('total_sounds', 0),
                    '事件数量': result.get('events', {}).get('total_events', 0),
                    '复杂度得分': complexity.get('complexity_score', 0)
                })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='项目汇总', index=False)
            
            # 为每个项目创建单独的工作表
            for result in all_results:
                filename = result.get('file_info', {}).get('filename', 'unknown')
                # 简化工作表名称（Excel工作表名称最多31个字符）
                sheet_name = filename[:28] if len(filename) > 28 else filename
                
                # 提取关键信息
                project_data = []
                
                # 基本信息
                project_data.append({
                    '类别': '基本信息',
                    '项目名称': filename,
                    '角色数量': result.get('complexity', {}).get('total_sprites', 0),
                    '代码块总数': result.get('complexity', {}).get('total_blocks', 0),
                    '变量数量': result.get('complexity', {}).get('total_variables', 0),
                    '列表数量': result.get('complexity', {}).get('total_lists', 0)
                })
                
                # 代码块类别
                blocks = result.get('blocks', {})
                if blocks.get('category_counts'):
                    for category, count in blocks['category_counts'].items():
                        project_data.append({
                            '类别': '代码块类别',
                            '类别名称': category,
                            '数量': count
                        })
                
                # 事件统计
                events = result.get('events', {})
                if events.get('event_counts'):
                    for event_type, count in events['event_counts'].items():
                        project_data.append({
                            '类别': '事件统计',
                            '事件类型': event_type,
                            '数量': count
                        })
                
                if project_data:
                    project_df = pd.DataFrame(project_data)
                    try:
                        project_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    except:
                        # 如果工作表名称有问题，使用默认名称
                        alt_name = f"项目_{all_results.index(result) + 1}"
                        project_df.to_excel(writer, sheet_name=alt_name, index=False)
            
            print(f"批量分析结果已导出到: {output_path}")