import json
from typing import Dict, List, Any, Set
from collections import defaultdict, Counter

class ProjectAnalyzer:
    """
    分析Scratch项目数据的类
    """
    
    def analyze_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析项目数据
        
        Args:
            project_data: 项目数据字典
            
        Returns:
            分析结果字典
        """
        project = project_data.get('project', {})
        targets = project.get('targets', [])
        
        results = {
            'project_info': self._extract_project_info(project),
            'sprites': self._analyze_sprites(targets),
            'blocks': self._analyze_blocks(targets),
            'variables': self._analyze_variables(targets),
            'lists': self._analyze_lists(targets),
            'costumes': self._analyze_costumes(targets),
            'sounds': self._analyze_sounds(targets),
            'events': self._analyze_events(targets),
            'complexity': self._calculate_complexity(targets)
        }
        
        return results
    
    def _extract_project_info(self, project: Dict) -> Dict:
        """提取项目基本信息"""
        return {
            'scratch_version': project.get('meta', {}).get('semver', '3.0.0'),
            'monitor_names': project.get('monitors', []),
            'extensions': project.get('extensions', []),
            'has_cloud_variables': self._has_cloud_variables(project)
        }
    
    def _analyze_sprites(self, targets: List[Dict]) -> List[Dict]:
        """分析所有角色"""
        sprites = []
        
        for target in targets:
            if target.get('isStage', False):
                sprite_type = 'stage'
            else:
                sprite_type = 'sprite'
            
            sprite_info = {
                'name': target.get('name', 'unknown'),
                'type': sprite_type,
                'visible': target.get('visible', True),
                'x': target.get('x', 0),
                'y': target.get('y', 0),
                'size': target.get('size', 100),
                'direction': target.get('direction', 90),
                'draggable': target.get('draggable', False),
                'rotation_style': target.get('rotationStyle', 'all around'),
                'layer_order': target.get('layerOrder', 0),
                'costume_count': len(target.get('costumes', [])),
                'sound_count': len(target.get('sounds', [])),
                'variable_count': len(target.get('variables', {})),
                'list_count': len(target.get('lists', {})),
                'block_count': len(target.get('blocks', {}))
            }
            sprites.append(sprite_info)
        
        return sprites
    
    def _analyze_blocks(self, targets: List[Dict]) -> Dict[str, Any]:
        """分析代码块使用情况"""
        all_blocks = {}
        block_counts = Counter()
        category_counts = Counter()
        
        for target in targets:
            blocks = target.get('blocks', {})
            for block_id, block_data in blocks.items():
                if isinstance(block_data, dict):
                    opcode = block_data.get('opcode', 'unknown')
                    category = self._get_block_category(opcode)
                    
                    block_counts[opcode] += 1
                    category_counts[category] += 1
        
        return {
            'total_blocks': sum(block_counts.values()),
            'unique_block_types': len(block_counts),
            'block_counts': dict(block_counts),
            'category_counts': dict(category_counts),
            'top_blocks': block_counts.most_common(10)
        }
    
    def _analyze_variables(self, targets: List[Dict]) -> Dict[str, Any]:
        """分析变量使用情况"""
        variables = []
        variable_count = 0
        
        for target in targets:
            target_vars = target.get('variables', {})
            for var_id, var_data in target_vars.items():
                if isinstance(var_data, list) and len(var_data) >= 2:
                    variables.append({
                        'name': var_data[0],
                        'value': var_data[1],
                        'sprite': target.get('name', 'unknown'),
                        'is_cloud': var_data[2] if len(var_data) > 2 else False
                    })
                    variable_count += 1
        
        return {
            'total_variables': variable_count,
            'variables': variables
        }
    
    def _analyze_lists(self, targets: List[Dict]) -> Dict[str, Any]:
        """分析列表使用情况"""
        lists = []
        list_count = 0
        
        for target in targets:
            target_lists = target.get('lists', {})
            for list_id, list_data in target_lists.items():
                if isinstance(list_data, list) and len(list_data) >= 2:
                    lists.append({
                        'name': list_data[0],
                        'items': list_data[1],
                        'item_count': len(list_data[1]) if isinstance(list_data[1], list) else 0,
                        'sprite': target.get('name', 'unknown')
                    })
                    list_count += 1
        
        return {
            'total_lists': list_count,
            'lists': lists
        }
    
    def _analyze_costumes(self, targets: List[Dict]) -> Dict[str, Any]:
        """分析造型使用情况"""
        costumes = []
        total_costumes = 0
        
        for target in targets:
            target_costumes = target.get('costumes', [])
            for costume in target_costumes:
                costumes.append({
                    'name': costume.get('name', 'unknown'),
                    'bitmap_resolution': costume.get('bitmapResolution', 1),
                    'data_format': costume.get('dataFormat', ''),
                    'sprite': target.get('name', 'unknown')
                })
            total_costumes += len(target_costumes)
        
        return {
            'total_costumes': total_costumes,
            'costumes': costumes
        }
    
    def _analyze_sounds(self, targets: List[Dict]) -> Dict[str, Any]:
        """分析声音使用情况"""
        sounds = []
        total_sounds = 0
        
        for target in targets:
            target_sounds = target.get('sounds', [])
            for sound in target_sounds:
                sounds.append({
                    'name': sound.get('name', 'unknown'),
                    'data_format': sound.get('dataFormat', ''),
                    'rate': sound.get('rate', 0),
                    'sample_count': sound.get('sampleCount', 0),
                    'sprite': target.get('name', 'unknown')
                })
            total_sounds += len(target_sounds)
        
        return {
            'total_sounds': total_sounds,
            'sounds': sounds
        }
    
    def _analyze_events(self, targets: List[Dict]) -> Dict[str, Any]:
        """分析事件使用情况"""
        event_blocks = [
            'event_whenflagclicked',
            'event_whenkeypressed',
            'event_whenthisspriteclicked',
            'event_whenbackdropswitchesto',
            'event_whengreaterthan',
            'event_whenbroadcastreceived',
            'event_broadcast',
            'event_broadcastandwait'
        ]
        
        event_counts = Counter()
        
        for target in targets:
            blocks = target.get('blocks', {})
            for block_id, block_data in blocks.items():
                if isinstance(block_data, dict):
                    opcode = block_data.get('opcode', '')
                    if opcode in event_blocks:
                        event_counts[opcode] += 1
        
        return {
            'total_events': sum(event_counts.values()),
            'event_counts': dict(event_counts)
        }
    
    def _calculate_complexity(self, targets: List[Dict]) -> Dict[str, Any]:
        """计算项目复杂度"""
        total_blocks = 0
        total_sprites = 0
        total_variables = 0
        total_lists = 0
        
        for target in targets:
            if not target.get('isStage', False):
                total_sprites += 1
            
            total_blocks += len(target.get('blocks', {}))
            total_variables += len(target.get('variables', {}))
            total_lists += len(target.get('lists', {}))
        
        return {
            'total_sprites': total_sprites,
            'total_blocks': total_blocks,
            'total_variables': total_variables,
            'total_lists': total_lists,
            'blocks_per_sprite': total_blocks / max(total_sprites, 1),
            'complexity_score': total_blocks + (total_variables * 2) + (total_lists * 3)
        }
    
    def _get_block_category(self, opcode: str) -> str:
        """获取代码块类别"""
        categories = {
            'motion': ['motion_'],
            'looks': ['looks_'],
            'sound': ['sound_'],
            'event': ['event_'],
            'control': ['control_'],
            'sensing': ['sensing_'],
            'operator': ['operator_'],
            'variables': ['data_'],
            'myblocks': ['procedures_']
        }
        
        for category, prefixes in categories.items():
            for prefix in prefixes:
                if opcode.startswith(prefix):
                    return category
        
        return 'other'
    
    def _has_cloud_variables(self, project: Dict) -> bool:
        """检查是否有云变量"""
        for target in project.get('targets', []):
            for var_data in target.get('variables', {}).values():
                if isinstance(var_data, list) and len(var_data) > 2:
                    if var_data[2]:  # 云变量标志位
                        return True
        return False