# -*- coding: utf-8 -*-
import re
import textwrap
import difflib
from typing import Dict, Set, List, Tuple, Optional

class CodeMerger:
    """
    一个最终版的、用于智能合并 RN 和 Harmony 代码的工具。
    它集成了作用域感知解析、依赖分析和基于规则的差异合并引擎。
    """
    JS_KEYWORDS = {
        'if', 'for', 'while', 'switch', 'case', 'catch', 'throw', 'try', 'finally', 'return', 'yield', 'await', 'async', 'function', 'class', 'const', 'let', 'var', 'import', 'export', 'default', 'from', 'in', 'of', 'new', 'delete', 'typeof', 'instanceof', 'void', 'with', 'debugger', 'super', 'this', 'get', 'set', 'console', 'Math', 'JSON', 'Promise', 'Object', 'Array', 'String', 'Number', 'Boolean', 'Date', 'RegExp', 'Map', 'Set', 'WeakMap', 'WeakSet', 'Symbol', 'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'encodeURI', 'decodeURI', 'encodeURIComponent', 'decodeURIComponent', 'require'
    }

    def _get_brace_level_at(self, content: str, pos: int) -> int:
        """通过逐字符扫描，准确计算在特定位置的括号嵌套层级，会忽略字符串和注释内的括号。"""
        level, in_string, in_line_comment, in_block_comment, i = 0, None, False, False, 0
        while i < pos:
            char = content[i]
            prev_char = content[i-1] if i > 0 else ''
            if in_line_comment:
                if char == '\n': in_line_comment = False
            elif in_block_comment:
                if char == '*' and content[i-1:i+1] == '*/': in_block_comment = False
            elif in_string:
                if char == in_string and prev_char != '\\': in_string = None
            else:
                if char in ['"', "'", "`"]: in_string = char
                elif char == '/' and content[i-1:i+1] == '//': in_line_comment = True
                elif char == '*' and content[i-1:i+1] == '/*': in_block_comment = True
                elif char == '{': level += 1
                elif char == '}': level -= 1
            i += 1
        return level

    def _extract_top_level_blocks(self, content: str) -> Tuple[List[Tuple[str, str]], Dict[str, str]]:
        """使用作用域感知的方法，只提取顶层的代码块。"""
        ordered_blocks, blocks_dict = [], {}
        block_start_pattern = re.compile(r"(?:export\s+)?(?:const|let|var|function|class)\s+(\w+)")
        
        current_pos = 0
        while current_pos < len(content):
            match = block_start_pattern.search(content, pos=current_pos)
            if not match: break

            if self._get_brace_level_at(content, match.start()) == 0:
                block_name = match.group(1)
                if block_name in blocks_dict:
                    current_pos = match.end()
                    continue
                start_pos, end_pos = match.start(), self._find_block_end(content, match.end())
                block_content = content[start_pos:end_pos]
                ordered_blocks.append((block_name, block_content))
                blocks_dict[block_name] = block_content
                current_pos = end_pos
            else:
                current_pos = match.end()
        return ordered_blocks, blocks_dict
    
    def _find_function_calls(self, content: str) -> Set[str]:
        pattern = re.compile(r"(?<!\.)\b([a-zA-Z_$][\w$]*)\s*\(")
        return set(pattern.findall(content)) - self.JS_KEYWORDS

    def _find_identifier_usages(self, content: str) -> Set[str]:
        pattern = re.compile(r"\b([a-zA-Z_$][\w$]*)\b")
        return set(pattern.findall(content)) - self.JS_KEYWORDS

    def _contains_harmony_code(self, content: str) -> bool:
        """检测是否包含鸿蒙相关代码"""
        # 简单检测harmony关键字
        return 'harmony' in content.lower() or 'Platform.OS' in content

    def _is_local_import(self, import_path: str) -> bool:
        """判断是否为本地模块导入"""
        # 相对路径导入
        if import_path.startswith(('./', '../', '/')):
            return True
        # 项目内部路径（根据实际项目结构调整）
        if import_path.startswith(('src/', 'bundles/', '@/')):
            return True
        return False

    def _get_block_name_from_import(self, import_path: str) -> str:
        """从import路径中提取组件名"""
        # 移除路径前缀和扩展名
        path_parts = import_path.replace('./', '').replace('../', '').split('/')
        filename = path_parts[-1].replace('.tsx', '').replace('.ts', '')
        # 将kebab-case转换为PascalCase
        return ''.join(word.capitalize() for word in filename.split('-'))

    def _find_real_dependencies(self, content: str, all_blocks: Dict[str, str]) -> Set[str]:
        """只收集真正的依赖，排除误报"""
        dependencies = set()
        
        # 检查import语句
        import_matches = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content)
        for import_path in import_matches:
            # 只处理来自同一模块的import
            if self._is_local_import(import_path):
                block_name = self._get_block_name_from_import(import_path)
                if block_name in all_blocks:
                    dependencies.add(block_name)
        
        # 检查函数调用，但排除误报
        function_calls = self._find_function_calls(content)
        for call in function_calls:
            if (call in all_blocks and 
                self._is_actual_dependency(call, content, all_blocks[call])):
                dependencies.add(call)
        
        return dependencies

    def _is_actual_dependency(self, block_name: str, content: str, block_content: str) -> bool:
        """判断是否为真实的依赖关系"""
        # 检查是否真的调用了该函数/组件
        call_pattern = rf'\b{re.escape(block_name)}\s*\('
        if not re.search(call_pattern, content):
            return False
        
        # 检查是否导入了该组件
        import_pattern = rf'import.*\b{re.escape(block_name)}\b'
        if re.search(import_pattern, content):
            return True
        
        # 如果没有显式导入，检查是否在同一文件中定义（可能是内部函数）
        definition_pattern = rf'(?:function|const|let|var)\s+{re.escape(block_name)}\s*[:=(]'
        if re.search(definition_pattern, block_content):
            return True
        
        return False

    def _should_skip_block(self, block_name: str, content: str, backup_content: str) -> bool:
        """判断是否应该跳过这个代码块"""
        # 基于语义分析判断是否为独立的业务组件
        if self._is_standalone_business_component(block_name, backup_content):
            # 检查当前文件是否包含相关的业务上下文
            return not self._has_related_business_context(block_name, content, backup_content)
        return False

    def _get_function_from_content(self, function_name: str, content: str) -> Optional[str]:
        """从内容中提取指定函数的代码"""
        # 查找函数定义
        function_pattern = rf'(?:function\s+{re.escape(function_name)}|const\s+{re.escape(function_name)}\s*=)\s*[^{{]*\{{[\s\S]*?\}}'
        match = re.search(function_pattern, content, re.IGNORECASE)
        return match.group(0) if match else None

    def _calculate_change_ratio(self, current: str, backup: str) -> float:
        """计算两个代码块的改动比例"""
        import difflib
        
        current_lines = current.strip().split('\n')
        backup_lines = backup.strip().split('\n')
        
        # 使用difflib计算相似度
        matcher = difflib.SequenceMatcher(None, current_lines, backup_lines)
        similarity = matcher.ratio()
        
        return 1.0 - similarity

    def _apply_merges(self, current_content: str, blocks_to_merge: Dict[str, str]) -> str:
        """应用合并结果"""
        result = current_content
        
        for block_name, new_content in blocks_to_merge.items():
            # 查找并替换函数
            function_pattern = rf'(?:function\s+{re.escape(block_name)}|const\s+{re.escape(block_name)}\s*=)\s*[^{{]*\{{[\s\S]*?\}}'
            result = re.sub(function_pattern, new_content, result, flags=re.IGNORECASE)
        
        return result

    def _record_conflicts(self, conflicts: List[Dict]):
        """记录冲突信息"""
        print("冲突记录:")
        for conflict in conflicts:
            print(f"  - {conflict['block_name']}: {conflict['change_ratio']:.2%} 改动")

    def _find_block_end(self, content: str, start_pos: int) -> int:
        try:
            first_brace_pos = content.index('{', start_pos)
        except ValueError:
            try: return content.index(';', start_pos) + 1
            except ValueError:
                try: return content.index('\n', start_pos) + 1
                except ValueError: return len(content)
        brace_level, search_pos = 1, first_brace_pos + 1
        while brace_level > 0 and search_pos < len(content):
            char = content[search_pos]
            if char == '{': brace_level += 1
            elif char == '}': brace_level -= 1
            search_pos += 1
        try:
            semicolon_after_brace = content.index(';', search_pos - 1)
            if all(c.isspace() for c in content[search_pos:semicolon_after_brace]): return semicolon_after_brace + 1
        except ValueError: pass
        return search_pos

    def _extract_imports(self, content: str) -> Dict[str, str]:
        imports_map = {}
        import_lines = re.findall(r"^\s*(?:import|from)\s+.*?(?:;|$)", content, re.MULTILINE)
        for line in import_lines:
            normalized_line = line.strip().rstrip(';')
            if ' from ' in normalized_line and normalized_line.startswith('import'):
                match = re.search(r"import\s+(.*?)\s+from", normalized_line)
                if not match: continue
                imports_str = match.group(1).strip()
                if imports_str.startswith('{') and imports_str.endswith('}'):
                    imports_str = imports_str[1:-1]
                    components = [c.strip().split(' as ')[0] for c in imports_str.split(',')]
                    for component in filter(None, components): imports_map[component] = normalized_line
                elif '*' in imports_str:
                    ns_match = re.search(r"\*\s+as\s+(\w+)", imports_str)
                    if ns_match: imports_map[ns_match.group(1)] = normalized_line
                else:
                    default_import = imports_str.split(',')[0].strip()
                    if default_import and '{' not in default_import: imports_map[default_import] = normalized_line
                    if '{' in imports_str and '}' in imports_str:
                        named_match = re.search(r"\{(.*?)\}", imports_str)
                        if named_match:
                            named_str = named_match.group(1)
                            components = [c.strip().split(' as ')[0] for c in named_str.split(',')]
                            for component in filter(None, components): imports_map[component] = normalized_line
            elif ' import ' in normalized_line and normalized_line.startswith('from'):
                match = re.search(r"import\s+(.*)", normalized_line)
                if not match: continue
                imports_str = match.group(1).strip()
                if imports_str.startswith('{') and imports_str.endswith('}'): imports_str = imports_str[1:-1]
                components = [c.strip().split(' as ')[0] for c in imports_str.split(',')]
                for component in filter(None, components): imports_map[component] = normalized_line
        return imports_map
    
    def merge_code(self, current_content: str, backup_content: str) -> str:
        """
        主函数：使用简化的合并策略，基于改动量决定是否自动合并。
        """
        ordered_backup_blocks, all_backup_blocks = self._extract_top_level_blocks(backup_content)
        
        # 筛选出包含harmony相关代码的function级别代码块
        harmony_blocks = {
            name: content for name, content in all_backup_blocks.items()
            if self._contains_harmony_code(content)
        }
        
        if not harmony_blocks:
            print("INFO: 在 backup_content 中未发现鸿蒙相关代码，无需合并。")
            return current_content

        # 尝试合并每个harmony代码块
        final_blocks_to_restore = {}
        conflicts = []
        
        for block_name, block_content in harmony_blocks.items():
            # 检查当前文件中是否已有同名函数
            current_block = self._get_function_from_content(block_name, current_content)
            
            if current_block is None:
                # 如果当前文件中没有这个函数，直接添加
                final_blocks_to_restore[block_name] = block_content
            else:
                # 计算改动量
                change_ratio = self._calculate_change_ratio(current_block, block_content)
                
                if change_ratio <= 0.3:  # 改动量小于30%，自动合并
                    final_blocks_to_restore[block_name] = block_content
                    print(f"自动合并 {block_name} (改动量: {change_ratio:.2%})")
                else:  # 改动量过大，标记为冲突
                    conflicts.append({
                        'block_name': block_name,
                        'current': current_block,
                        'backup': block_content,
                        'change_ratio': change_ratio
                    })
                    print(f"冲突: {block_name} (改动量: {change_ratio:.2%})，跳过自动合并")
        
        if conflicts:
            print(f"发现 {len(conflicts)} 个冲突，需要手动处理")
            self._record_conflicts(conflicts)
        
        return self._apply_merges(current_content, final_blocks_to_restore)
        
