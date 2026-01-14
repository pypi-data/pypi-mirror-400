import zipfile
import json
import os
from typing import Dict, Any, Optional
import tempfile

class SB3Extractor:
    """
    用于提取.sb3文件内容的类
    """
    
    def extract_sb3(self, sb3_path: str) -> Optional[Dict[str, Any]]:
        """
        从.sb3文件中提取项目数据
        
        Args:
            sb3_path: .sb3文件路径
            
        Returns:
            项目数据字典
        """
        if not os.path.exists(sb3_path):
            raise FileNotFoundError(f"文件不存在: {sb3_path}")
        
        try:
            with zipfile.ZipFile(sb3_path, 'r') as zip_ref:
                # 提取project.json
                if 'project.json' in zip_ref.namelist():
                    with zip_ref.open('project.json') as f:
                        project_data = json.load(f)
                    
                    # 提取所有资源文件信息
                    resources = {}
                    for file_info in zip_ref.infolist():
                        if file_info.filename != 'project.json':
                            resources[file_info.filename] = {
                                'size': file_info.file_size,
                                'compressed_size': file_info.compress_size
                            }
                    
                    return {
                        'project': project_data,
                        'resources': resources,
                        'file_count': len(zip_ref.namelist())
                    }
                else:
                    raise ValueError("无效的.sb3文件：缺少project.json")
                    
        except (zipfile.BadZipFile, json.JSONDecodeError) as e:
            raise ValueError(f"文件格式错误: {e}")
    
    def extract_specific_resource(self, sb3_path: str, resource_name: str, 
                                 output_path: str = None) -> Optional[bytes]:
        """
        提取特定的资源文件
        
        Args:
            sb3_path: .sb3文件路径
            resource_name: 资源文件名
            output_path: 输出路径（可选）
            
        Returns:
            资源文件的二进制数据
        """
        try:
            with zipfile.ZipFile(sb3_path, 'r') as zip_ref:
                if resource_name in zip_ref.namelist():
                    data = zip_ref.read(resource_name)
                    
                    if output_path:
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(data)
                    
                    return data
        except Exception as e:
            print(f"提取资源时出错: {e}")
            return None