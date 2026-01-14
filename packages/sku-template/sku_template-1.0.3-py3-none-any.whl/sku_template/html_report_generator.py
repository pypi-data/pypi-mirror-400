"""
HTML报告生成器 - 用于替代Excel输出，生成更美观清晰的HTML格式报告
HTML Report Generator - Replace Excel output with beautiful and clear HTML format

功能特性：
- 表格视图展示测试用例数据
- 支持动态列配置
- 预期值 vs 实际值对比表格
- 状态筛选和标记
- 状态持久化（localStorage）
- 导出修改后的HTML文件
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union


class ComparisonItem:
    """对比项配置类"""
    
    def __init__(self, expected_key: str, actual_key: str, label: str):
        """
        初始化对比项
        
        Args:
            expected_key: 预期值字段名
            actual_key: 实际值字段名
            label: 显示标签
        
        注意：tolerance 不在初始化时设置，而是在每个case数据中通过 tolerance_overrides 字段设置
        """
        self.expected_key = expected_key
        self.actual_key = actual_key
        self.label = label
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "expected_key": self.expected_key,
            "actual_key": self.actual_key,
            "label": self.label,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComparisonItem':
        """从字典创建对比项"""
        return cls(
            expected_key=data.get("expected_key", ""),
            actual_key=data.get("actual_key", ""),
            label=data.get("label", "")
        )
    
    def __repr__(self) -> str:
        return f"ComparisonItem(expected_key='{self.expected_key}', actual_key='{self.actual_key}', label='{self.label}')"


class ComparisonConfig:
    """对比配置类（管理多个对比项）"""
    
    def __init__(self, items: Optional[List[Union[ComparisonItem, Dict[str, Any]]]] = None):
        """
        初始化对比配置
        
        Args:
            items: 对比项列表，可以是 ComparisonItem 对象或字典
        """
        self.items: List[ComparisonItem] = []
        if items:
            for item in items:
                if isinstance(item, ComparisonItem):
                    self.items.append(item)
                elif isinstance(item, dict):
                    self.items.append(ComparisonItem.from_dict(item))
                else:
                    raise ValueError(f"不支持的对比项类型: {type(item)}")
    
    def add(self, expected_key: str, actual_key: str, label: str) -> 'ComparisonConfig':
        """
        添加对比项
        
        Args:
            expected_key: 预期值字段名
            actual_key: 实际值字段名
            label: 显示标签
        
        注意：tolerance 不在初始化时设置，而是在每个case数据中通过 tolerance_overrides 字段设置
        
        Returns:
            self，支持链式调用
        """
        self.items.append(ComparisonItem(expected_key, actual_key, label))
        return self
    
    def to_list(self) -> List[Dict[str, Any]]:
        """转换为列表格式（用于向后兼容）"""
        return [item.to_dict() for item in self.items]
    
    def __iter__(self):
        """支持迭代"""
        return iter(self.items)
    
    def __len__(self) -> int:
        """支持 len()"""
        return len(self.items)
    
    def __getitem__(self, index: int) -> ComparisonItem:
        """支持索引访问"""
        return self.items[index]
    
    def __repr__(self) -> str:
        return f"ComparisonConfig(items={len(self.items)})"


class HTMLReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self, output_dir: str = "", 
                 custom_columns: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
                 comparison_config: Optional[Union[ComparisonConfig, List[Union[ComparisonItem, Dict[str, Any]]]]] = None):
        """
        初始化HTML报告生成器
        
        Args:
            output_dir: 输出目录，默认为项目根目录下的 report/billing 目录
            custom_columns: 自定义列配置，有两种使用方式：
                方式1：完全自定义（列表），提供完整的列配置列表，会完全替换默认列
                方式2：增量修改（字典），格式为：
                    {
                        "add": [  # 添加新列
                            {"key": "appid", "label": "AppID", "extractor": lambda idx, data: data.get("appid", "")},
                            ...
                        ],
                        "remove": ["vid", "cname"],  # 删除列（通过key）
                        "modify": {  # 修改现有列
                            "case": {"label": "用例名", "extractor": lambda idx, data: data.get("case", "")},
                            ...
                        },
                        "insert_before": {  # 在指定列之前插入
                            "status": [{"key": "new_col", "label": "新列", "extractor": lambda idx, data: "..."}],
                            ...
                        },
                        "insert_after": {  # 在指定列之后插入
                            "vid": [{"key": "appid", "label": "AppID", "extractor": lambda idx, data: data.get("appid", "")}],
                            ...
                        }
                    }
                如果不提供，使用默认列（idx, case, vid, cname, status, details）
            comparison_config: 对比表配置，支持三种格式：
                格式1：ComparisonConfig对象（推荐）
                    comparison_config = ComparisonConfig()
                    comparison_config.add("Language Detection Duration", "detectTime", "语言检测时长")
                    comparison_config.add("Actual Transcribing Duration", "actualTime", "实际转录时长")
                格式2：列表（字典格式）
                    [
                        {"expected_key": "Language Detection Duration", "actual_key": "detectTime", "label": "语言检测时长"},
                        {"expected_key": "Actual Transcribing Duration", "actual_key": "actualTime", "label": "实际转录时长"},
                    ]
                格式3：列表（ComparisonItem对象）
                    [
                        ComparisonItem("Language Detection Duration", "detectTime", "语言检测时长"),
                        ComparisonItem("Actual Transcribing Duration", "actualTime", "实际转录时长"),
                    ]
                此配置用于：
                1. 判断差异（检查每个字段是否超过case数据中tolerance设置的tolerance值）
                2. 展示对比表格（在详细信息中显示）
                注意：tolerance不在初始化时设置，而是在每个case数据中通过tolerance字段设置
                例如：case_data["tolerance"] = {"Effective Transcribing Duration": 0.5, "Actual Transcribing Duration": 1.0}
                注意：case数据必须使用分组结构：
                {
                    "expected": {"Effective Transcribing Duration": 59.0, ...},
                    "actual": {"effectiveTime": 59.3, ...},
                    "tolerance": {"Effective Transcribing Duration": 0.5, ...}
                }
                如果不提供，不进行差异检查且对比表为空
        """
        if output_dir == "":
            # 默认使用当前工作目录下的 report/billing 目录
            # 优先检查环境变量 REPORT_OUTPUT_DIR
            import os
            env_output_dir = os.environ.get('REPORT_OUTPUT_DIR')
            if env_output_dir:
                output_dir = env_output_dir
            else:
                # 使用当前工作目录
                current_dir = Path(os.getcwd())
                output_dir = str(current_dir / "report" / "billing")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 模板目录（可选，用于存放外部模板文件）
        self.template_dir = Path(__file__).parent / "templates"
        self.fragments_dir = self.template_dir / "fragments"
        
        # 自定义列配置（支持列表完全替换或字典增量修改）
        if custom_columns is None:
            self.custom_columns = self._get_default_columns_config()
        elif isinstance(custom_columns, list):
            # 完全自定义模式
            self.custom_columns = custom_columns
        elif isinstance(custom_columns, dict):
            # 增量修改模式
            self.custom_columns = self._apply_column_modifications(custom_columns)
        else:
            raise ValueError("custom_columns 必须是列表或字典")
        
        # 对比表配置
        # 此配置同时用于：1. 判断差异 2. 展示对比表格
        # 支持 ComparisonConfig 对象、列表（字典）或列表（ComparisonItem）
        if comparison_config is None:
            self.comparison_config = []
        elif isinstance(comparison_config, ComparisonConfig):
            self.comparison_config = comparison_config.to_list()
        elif isinstance(comparison_config, list):
            # 如果是列表，转换为字典列表格式
            self.comparison_config = []
            for item in comparison_config:
                if isinstance(item, ComparisonItem):
                    self.comparison_config.append(item.to_dict())
                elif isinstance(item, dict):
                    self.comparison_config.append(item)
                else:
                    raise ValueError(f"不支持的对比项类型: {type(item)}")
        else:
            raise ValueError(f"comparison_config 必须是 ComparisonConfig 对象、列表或 None")
    
    def generate_report(self, billing_datas: List[Dict[str, Any]], output_file: Optional[str] = None) -> str:
        """
        生成HTML报告（表格视图）
        
        Args:
            billing_datas: 计费数据列表
            output_file: 输出文件路径（可选）
                - 如果为 None，使用默认路径：{output_dir}/billing_report_{timestamp}.html
                - 如果指定为目录路径，在该目录下生成默认文件名
                - 如果指定为完整文件路径，使用该路径（会自动创建父目录）
            
        Returns:
            生成的HTML文件路径
        """
        if output_file:
            output_path = Path(output_file)
            # 如果指定的是目录，在该目录下生成默认文件名
            if output_path.is_dir() or (not output_path.suffix and not output_path.exists()):
                timestamp = str(int(time.time()))
                html_file = output_path / f"billing_report_{timestamp}.html"
            else:
                # 指定的是完整文件路径
                html_file = output_path
                # 确保父目录存在
                html_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            # 使用默认路径
            timestamp = str(int(time.time()))
            html_file = self.output_dir / f"billing_report_{timestamp}.html"
        
        html_content = self._build_table_html(billing_datas)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_file)
    
    def _get_css_styles(self) -> str:
        """获取CSS样式文件内容"""
        css_file = self.template_dir / "styles.css"
        if not css_file.exists():
            raise FileNotFoundError(f"CSS模板文件不存在: {css_file}")
        with open(css_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _get_default_columns_config(self) -> List[Dict[str, Any]]:
        """获取默认的列配置"""
        return [
            {
                "key": "idx",
                "label": "用例序号",
                "extractor": lambda idx, data: idx
            },
            {
                "key": "case",
                "label": "测试用例名称",
                "extractor": lambda idx, data: data.get("case", f"用例 {idx}")
            },
            {
                "key": "vid",
                "label": "VID",
                "extractor": lambda idx, data: data.get("vid", "N/A")
            },
            {
                "key": "cname",
                "label": "频道名",
                "extractor": lambda idx, data: data.get("cname", "N/A")
            },
            {
                "key": "status",
                "label": "结果状态",
                "extractor": None  # 特殊处理，由_build_status_select处理
            },
            {
                "key": "details",
                "label": "详细信息",
                "extractor": None  # 特殊处理，由_build_case_details处理
            },
        ]
    
    def _apply_column_modifications(self, modifications: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        应用列修改（增删改）
        
        Args:
            modifications: 修改配置字典，包含:
                - add: 添加新列（列表）
                - remove: 删除列（列表，通过key）
                - modify: 修改列（字典，key为列key，value为新的配置）
                - insert_before: 在指定列之前插入（字典，key为列key，value为要插入的列列表）
                - insert_after: 在指定列之后插入（字典，key为列key，value为要插入的列列表）
        
        Returns:
            修改后的列配置列表
        """
        # 从默认列开始
        columns = self._get_default_columns_config().copy()
        
        # 深拷贝，避免修改原始列表中的字典
        columns = [col.copy() for col in columns]
        
        # 1. 删除列
        if "remove" in modifications:
            remove_keys = set(modifications["remove"])
            columns = [col for col in columns if col["key"] not in remove_keys]
        
        # 2. 修改列
        if "modify" in modifications:
            modify_dict = modifications["modify"]
            for col in columns:
                if col["key"] in modify_dict:
                    mod = modify_dict[col["key"]]
                    if "label" in mod:
                        col["label"] = mod["label"]
                    if "extractor" in mod:
                        col["extractor"] = mod["extractor"]
        
        # 3. 在指定列之前插入
        if "insert_before" in modifications:
            insert_before = modifications["insert_before"]
            new_columns = []
            for col in columns:
                if col["key"] in insert_before:
                    # 在当前位置之前插入新列
                    new_columns.extend([c.copy() for c in insert_before[col["key"]]])
                new_columns.append(col)
            columns = new_columns
        
        # 4. 在指定列之后插入
        if "insert_after" in modifications:
            insert_after = modifications["insert_after"]
            new_columns = []
            for col in columns:
                new_columns.append(col)
                if col["key"] in insert_after:
                    # 在当前位置之后插入新列
                    new_columns.extend([c.copy() for c in insert_after[col["key"]]])
            columns = new_columns
        
        # 5. 添加新列（添加到末尾，但在status和details之前）
        if "add" in modifications:
            add_columns = modifications["add"]
            # 找到status和details的位置
            status_idx = None
            details_idx = None
            for i, col in enumerate(columns):
                if col["key"] == "status":
                    status_idx = i
                elif col["key"] == "details":
                    details_idx = i
            
            # 在status之前插入，如果没有status则在details之前插入
            insert_idx = status_idx if status_idx is not None else (details_idx if details_idx is not None else len(columns))
            for add_col in reversed(add_columns):  # 反向插入以保持顺序
                columns.insert(insert_idx, add_col.copy())
        
        return columns
    
    def _load_fragment(self, fragment_name: str) -> str:
        """
        加载模板片段
        
        Args:
            fragment_name: 片段文件名（不含.html扩展名）
            
        Returns:
            模板片段内容
            
        Raises:
            FileNotFoundError: 如果模板文件不存在
        """
        fragment_file = self.fragments_dir / f"{fragment_name}.html"
        if not fragment_file.exists():
            raise FileNotFoundError(f"模板片段文件不存在: {fragment_file}")
        with open(fragment_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _build_summary(self, billing_datas: List[Dict[str, Any]]) -> str:
        """构建摘要部分（使用配置的差值范围）"""
        total_cases = len(billing_datas)
        passed_cases = 0
        
        for data in billing_datas:
            # 使用配置的差值范围检查
            if not self._has_differences(data):
                passed_cases += 1
        
        failed_cases = total_cases - passed_cases
        pass_rate = (passed_cases/total_cases*100 if total_cases > 0 else 0)
        
        # 加载模板片段
        template = self._load_fragment("summary")
        return template.format(
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            pass_rate=f"{pass_rate:.1f}"
        )
    
    def _is_data_missing(self, data: Dict[str, Any]) -> bool:
        """检查数据是否丢失"""
        if not self.comparison_config:
            return False
        
        # 获取实际值（必须使用分组结构）
        actual = data.get("actual", {})
        
        # 检查是否有任何实际值不为None
        has_data = False
        for comparison_item in self.comparison_config:
            # 支持字典格式
            if isinstance(comparison_item, dict):
                actual_key = comparison_item.get("actual_key", "")
            # 支持 ComparisonItem 对象
            elif isinstance(comparison_item, ComparisonItem):
                actual_key = comparison_item.actual_key
            else:
                continue
            
            if not actual_key:
                continue
            
            # 获取实际值（使用分组结构）
            actual_val = actual.get(actual_key)
            
            # 如果实际值不为None，说明有数据
            if actual_val is not None:
                has_data = True
                break
        
        # 如果所有对比项的实际值都是None，认为是数据丢失
        return not has_data
    
    def _is_numeric(self, value: Any) -> bool:
        """
        判断值是否为数值类型或可以转换为数值
        
        Args:
            value: 要检查的值
            
        Returns:
            bool: 如果是数值类型或可转换为数值返回True，否则返回False
        """
        # 如果已经是数值类型
        if isinstance(value, (int, float)):
            return True
        
        # 如果是字符串，尝试转换
        if isinstance(value, str):
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False
        
        return False
    
    def _has_differences(self, data: Dict[str, Any]) -> bool:
        """
        检查是否有差异（使用comparison_config）
        
        每个case必须提供 tolerance 字段来设置tolerance：
        - tolerance 格式：{"expected_key": tolerance_value}，只使用expected_key作为key
        - 如果某个字段在 tolerance 中没有设置，则使用默认值 0（不允许有任何差异）
        """
        if not self.comparison_config:
            return False
        
        # 如果数据丢失，返回True（表示有差异，需要标记为失败）
        if self._is_data_missing(data):
            return True
        
        # 获取case级别的tolerance配置（必须提供）
        tolerance_config = data.get("tolerance", {})
        
        # 获取预期值和实际值（必须使用分组结构）
        expected = data.get("expected", {})
        actual = data.get("actual", {})
        
        for comparison_item in self.comparison_config:
            # 支持字典格式
            if isinstance(comparison_item, dict):
                expected_key = comparison_item.get("expected_key", "")
                actual_key = comparison_item.get("actual_key", "")
            # 支持 ComparisonItem 对象
            elif isinstance(comparison_item, ComparisonItem):
                expected_key = comparison_item.expected_key
                actual_key = comparison_item.actual_key
            else:
                continue
            
            if not expected_key or not actual_key:
                continue
            
            # 从case数据中获取tolerance（只使用expected_key）
            tolerance = tolerance_config.get(expected_key)
            
            # 如果case中没有设置tolerance，使用默认值0（不允许有任何差异）
            if tolerance is None:
                tolerance = 0
            
            # 获取预期值和实际值（使用分组结构）
            expected_val = expected.get(expected_key, 0)
            actual_val = actual.get(actual_key)
            
            # 如果实际值为None，认为有差异（数据丢失）
            if actual_val is None:
                return True
            
            # 判断是否都为数值类型
            expected_is_numeric = self._is_numeric(expected_val)
            actual_is_numeric = self._is_numeric(actual_val)
            
            # 如果都不是数值类型，进行字符串比较
            if not expected_is_numeric and not actual_is_numeric:
                # 转换为字符串进行比较
                expected_str = str(expected_val) if expected_val is not None else ""
                actual_str = str(actual_val)
                if expected_str != actual_str:
                    return True
            # 如果类型不匹配（一个是数值一个不是），直接判定为有差异
            elif expected_is_numeric != actual_is_numeric:
                return True
            else:
                # 两个都是数值类型，进行数值比较
                # 将值转换为数值（如果是字符串数值则转换）
                expected_val_num = float(expected_val) if isinstance(expected_val, str) else expected_val
                actual_val_num = float(actual_val) if isinstance(actual_val, str) else actual_val
                
                diff = abs(expected_val_num - actual_val_num)
                # tolerance=0 表示不允许有任何差异，tolerance>0 表示允许的差值范围
                if diff > tolerance:
                    return True
        
        return False
    
    
    def _build_comparison_table(self, data: Dict[str, Any]) -> str:
        """
        构建对比表格（使用配置的对比表配置和差值范围）
        
        每个case必须提供 tolerance 字段来设置tolerance：
        - tolerance 格式：{"expected_key": tolerance_value}，只使用expected_key作为key
        - 如果某个字段在 tolerance 中没有设置，则使用默认值 0（不允许有任何差异）
        """
        # 如果没有配置对比表，返回空
        if not self.comparison_config:
            return ""
        
        # 获取case级别的tolerance配置（必须提供）
        tolerance_config = data.get("tolerance", {})
        
        # 获取预期值和实际值（必须使用分组结构）
        expected = data.get("expected", {})
        actual = data.get("actual", {})
        
        # 加载行模板
        row_template = self._load_fragment("comparison_row")
        rows_html = []
        
        for comparison_item in self.comparison_config:
            # 支持字典格式
            if isinstance(comparison_item, dict):
                expected_key = comparison_item.get("expected_key", "")
                actual_key = comparison_item.get("actual_key", "")
                label = comparison_item.get("label", f"{expected_key} vs {actual_key}")
            # 支持 ComparisonItem 对象
            elif isinstance(comparison_item, ComparisonItem):
                expected_key = comparison_item.expected_key
                actual_key = comparison_item.actual_key
                label = comparison_item.label
            else:
                continue
            
            # 从case数据中获取tolerance（只使用expected_key）
            tolerance = tolerance_config.get(expected_key)
            
            # 如果case中没有设置tolerance，使用默认值0（不允许有任何差异）
            if tolerance is None:
                tolerance = 0
            
            # 格式化容差值显示
            tolerance_value_str = self._format_number(tolerance)
            
            # 获取预期值和实际值（使用分组结构）
            expected_val = expected.get(expected_key)
            actual_val = actual.get(actual_key)
            
            # 处理预期值显示：如果为None，显示"None"，否则格式化
            if expected_val is None:
                expected_value_str = "None"
            else:
                expected_value_str = self._format_number(expected_val)
            
            # 处理实际值显示和差值计算
            if actual_val is None:
                actual_value_str = "None"
                diff_str = "N/A"
                diff_class = "diff-warning"
            else:
                # 如果实际值不为None，进行数值比较
                actual_value_str = self._format_number(actual_val)
                
                # 如果预期值或实际值为None，无法计算差值
                if expected_val is None:
                    diff_str = "N/A"
                    diff_class = "diff-warning"
                else:
                    # 两个值都不为None，判断是否都为数值类型
                    expected_is_numeric = self._is_numeric(expected_val)
                    actual_is_numeric = self._is_numeric(actual_val)
                    
                    # 如果都不是数值类型，进行字符串比较
                    if not expected_is_numeric and not actual_is_numeric:
                        # 转换为字符串进行比较
                        expected_str = str(expected_val)
                        actual_str = str(actual_val)
                        
                        if expected_str == actual_str:
                            diff_class = "diff-pass"
                            diff_str = "Match"
                        else:
                            diff_class = "diff-warning"
                            diff_str = "Not Match"
                    # 如果类型不匹配（一个是数值一个不是），显示类型不匹配
                    elif expected_is_numeric != actual_is_numeric:
                        diff_class = "diff-warning"
                        diff_str = "Type Mismatch"
                    else:
                        # 两个都是数值类型，进行数值比较
                        # 将值转换为数值（如果是字符串数值则转换）
                        expected_val_num = float(expected_val) if isinstance(expected_val, str) else expected_val
                        actual_val_num = float(actual_val) if isinstance(actual_val, str) else actual_val
                        
                        diff = expected_val_num - actual_val_num
                        
                        # 如果tolerance为None，当作tolerance=0处理（不允许有任何差异）
                        if tolerance is None:
                            tolerance = 0
                        
                        # 差值颜色和显示逻辑：
                        # - 在容差范围内（abs(diff) <= tolerance）：使用绿色（diff-pass）表示通过
                        # - 超出容差范围：使用红色（diff-warning）表示警告，不分正负
                        if abs(diff) <= tolerance:
                            diff_class = "diff-pass"
                            # 差值小于0.001时显示为0.00，否则显示实际差值
                            diff_str = f"{diff:+.2f}" if abs(diff) > 0.001 else "0.00"
                        else:
                            diff_class = "diff-warning"
                            diff_str = f"{diff:+.2f}"
            
            rows_html.append(row_template.format(
                label=label,
                expected_value=expected_value_str,
                actual_value=actual_value_str,
                tolerance_value=tolerance_value_str,
                diff_class=diff_class,
                diff_str=diff_str
            ))
        
        rows = ''.join(rows_html)
        
        # 加载表格模板
        table_template = self._load_fragment("comparison_table")
        return table_template.format(rows=rows)
    
    
    def _format_number(self, value: Any) -> str:
        """格式化数字（整数保持整数格式，浮点数保留两位小数）"""
        if isinstance(value, bool):
            # 布尔值不应该被格式化为数字
            return str(value)
        if isinstance(value, int):
            # 整数不添加小数点
            return str(value)
        if isinstance(value, float):
            # 浮点数：如果是整数值则不显示小数，否则保留两位小数
            if value == int(value):
                return str(int(value))
            else:
                return f"{value:.2f}"
        return str(value)
    
    def _format_timestamp(self, timestamp: int) -> str:
        """格式化时间戳（支持秒级和毫秒级）"""
        if not timestamp:
            return "N/A"
        try:
            # 判断是秒级还是毫秒级时间戳
            # 如果时间戳 > 10000000000，认为是毫秒级（2286年以前的毫秒时间戳都会大于这个值）
            # 否则认为是秒级
            if timestamp > 10000000000:
                dt = datetime.fromtimestamp(timestamp / 1000)
            else:
                dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return str(timestamp)
    
    def _get_javascript(self) -> str:
        """获取JavaScript代码"""
        js_file = self.template_dir / "script.js"
        if not js_file.exists():
            raise FileNotFoundError(f"JavaScript模板文件不存在: {js_file}")
        with open(js_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _get_html_template(self) -> str:
        """
        获取HTML模板
        
        Returns:
            HTML模板字符串
        """
        return self._get_table_template()
    
    def _get_table_template(self) -> str:
        """获取表格视图模板"""
        template_file = self.template_dir / "table_report.html"
        if not template_file.exists():
            raise FileNotFoundError(f"表格报告模板文件不存在: {template_file}")
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
            # 替换外部引用为内联（如果模板中使用外部文件）
            template_content = template_content.replace(
                '<link rel="stylesheet" href="styles.css">',
                '<style>\n{css_styles}\n</style>'
            )
            template_content = template_content.replace(
                '<script src="script.js"></script>',
                '<script>\n{javascript_code}\n</script>'
            )
            return template_content
    
    def _build_table_html(self, billing_datas: List[Dict[str, Any]]) -> str:
        """构建表格视图的HTML（支持动态列）"""
        # 构建表头
        table_headers = self._build_table_headers()
        
        # 准备模板数据
        template_data = {
            'css_styles': self._get_css_styles(),
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_cases': len(billing_datas),
            'summary_html': self._build_summary(billing_datas),
            'table_headers': table_headers,
            'table_rows': self._build_table_rows(billing_datas),
            'javascript_code': self._get_javascript()
        }
        
        # 获取模板并填充数据
        template = self._get_html_template()
        return template.format(**template_data)
    
    def _build_table_headers(self) -> str:
        """构建表格表头（根据列配置）"""
        headers_html = []
        for col_config in self.custom_columns:
            col_key = col_config.get('key', '')
            # 为每列添加对应的class以设置宽度
            col_class = self._get_column_class(col_key)
            if col_class:
                headers_html.append(f"<th class='{col_class}'>{col_config['label']}</th>")
            else:
                headers_html.append(f"<th class='col-custom'>{col_config['label']}</th>")
        return ''.join(headers_html)
    
    def _get_column_class(self, col_key: str) -> str:
        """
        根据列key获取对应的CSS class
        
        Args:
            col_key: 列的key
            
        Returns:
            CSS class名称，如果没有匹配则返回空字符串
        """
        class_mapping = {
            'idx': 'col-idx',
            'case': 'col-case',
            'vid': 'col-vid',
            'cname': 'col-cname',
            'status': 'col-status',
            'details': 'col-details',
        }
        return class_mapping.get(col_key, 'col-custom')
    
    def _build_table_rows(self, billing_datas: List[Dict[str, Any]]) -> str:
        """构建表格行数据（根据列配置动态生成）"""
        rows_html = []
        
        for idx, data in enumerate(billing_datas, 1):
            # 检查是否有错误信息（数据格式错误或查询失败）
            has_error = data.get("error") is not None
            
            # 先根据数据差异判断内部状态
            has_diff = self._has_differences(data)
            is_missing = self._is_data_missing(data)
            
            if has_error:
                # 有错误（数据格式错误或查询失败），直接标记为失败
                internal_status = "fail"
            elif is_missing:
                # 数据丢失，标记为失败
                internal_status = "fail"
            elif has_diff:
                # 有差异，标记为有差异
                internal_status = "diff"
            else:
                # 无差异，标记为通过
                internal_status = "pass"
            
            # 获取外部设置的状态（如果存在）
            external_status = data.get("external_status")
            
            # 合并判断：取更严格（更差）的状态
            # 状态优先级：fail > diff > pass
            if external_status and external_status in ["pass", "diff", "fail"]:
                # 状态优先级：fail > diff > pass
                status_priority = {"fail": 3, "diff": 2, "pass": 1}
                internal_priority = status_priority.get(internal_status, 0)
                external_priority = status_priority.get(external_status, 0)
                
                # 取优先级更高的（更严格的状态）
                if external_priority > internal_priority:
                    initial_status = external_status
                else:
                    initial_status = internal_status
            else:
                # 没有外部状态，使用内部判断的结果
                initial_status = internal_status
            
            # 设置状态对应的CSS类
            if initial_status == "pass":
                initial_status_class = "status-pass"
            elif initial_status == "diff":
                initial_status_class = "status-diff"
            else:
                initial_status_class = "status-fail"
            
            # 获取外部设置的备注（如果存在）
            external_note = data.get("external_note", "")
            
            # 构建行的所有单元格
            cells_html = []
            for col_config in self.custom_columns:
                key = col_config['key']
                extractor = col_config.get('extractor')
                
                # 为每列添加对应的class以设置宽度
                cell_class = self._get_column_class(key)
                
                # 特殊处理状态和详细信息列
                if key == "status":
                    cell_content = self._build_status_select(idx, initial_status, initial_status_class, external_note)
                elif key == "details":
                    cell_content = self._build_case_details(idx, data)
                elif extractor:
                    cell_content = str(extractor(idx, data))
                else:
                    cell_content = str(data.get(key, ""))
                
                # 为单元格添加class以设置宽度
                cells_html.append(f"<td class='{cell_class}'>{cell_content}</td>")
            
            # 为每行添加data-status属性，用于状态过滤
            cells_content = ''.join(cells_html)
            rows_html.append(f'<tr data-status="{initial_status}" data-row-index="{idx}">{cells_content}</tr>')
        
        return ''.join(rows_html)
    
    def _build_status_select(self, idx: int, initial_status: str, status_class: str, initial_note: str = "") -> str:
        """
        构建状态选择框
        
        Args:
            idx: 用例序号
            initial_status: 初始状态 (pass, diff, fail)
            status_class: 状态CSS类
            initial_note: 初始备注（外部设置的备注）
        """
        pass_selected = 'selected' if initial_status == 'pass' else ''
        diff_selected = 'selected' if initial_status == 'diff' else ''
        fail_selected = 'selected' if initial_status == 'fail' else ''
        
        # 转义备注内容，防止HTML注入
        if initial_note:
            import html
            escaped_note = html.escape(initial_note)
        else:
            escaped_note = ""
        
        # 加载模板片段
        template = self._load_fragment("status_select")
        return template.format(
            idx=idx,
            status_class=status_class,
            pass_selected=pass_selected,
            diff_selected=diff_selected,
            fail_selected=fail_selected,
            initial_note=escaped_note
        )
    
    def _build_case_details(self, idx: int, data: Dict[str, Any]) -> str:
        """构建用例详细信息"""
        start_time = self._format_timestamp(data.get("startTime", 0))
        stop_time = self._format_timestamp(data.get("stopTime", 0))
        
        # 检查是否有错误信息
        error_msg = data.get("error")
        if error_msg:
            # 如果有错误，显示错误信息而不是对比表格
            comparison_table = f'<div class="error-message" style="color: red; padding: 10px; background: #fff0f0; border: 1px solid #ffcccc; border-radius: 4px; margin: 10px 0;">❌ {error_msg}</div>'
        else:
            # 正常情况，显示对比表格
            comparison_table = self._build_comparison_table(data)
        
        # 加载模板片段
        template = self._load_fragment("case_details")
        return template.format(
            idx=idx,
            start_time=start_time,
            stop_time=stop_time,
            comparison_table=comparison_table
        )
    

def load_report_config_from_business(business: str) -> Dict[str, Any]:
    """
    从业务配置文件中加载报告配置（comparison_config 和 custom_columns）
    
    Args:
        business: 业务名称（如 "speech-to-text"）
        
    Returns:
        包含 comparison_config、custom_columns 和 detail_fields 的字典，格式：
        {
            "comparison_config": ComparisonConfig 对象或 None,
            "custom_columns": 字典或列表或 None,
            "detail_fields": 列表，包含所有 detail. 开头的 actual_key 对应的字段路径
        }
        
    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 配置格式错误
    """
    from .sku_query_framework import SkuQueryFactory
    
    # 获取业务配置
    configs = SkuQueryFactory._get_business_configs()
    
    if business not in configs:
        raise ValueError(f"Unknown business: {business}. Available: {list(configs.keys())}")
    
    config = configs[business]
    report_config = config.get("report", {})
    
    result: Dict[str, Any] = {
        "comparison_config": None,
        "custom_columns": None,
        "detail_fields": []
    }
    
    # 加载 comparison_config
    comparison_config_data = report_config.get("comparison_config")
    if comparison_config_data:
        if isinstance(comparison_config_data, list):
            # 从列表创建 ComparisonConfig（数组格式：[expected_key, actual_key, label]）
            comparison_config = ComparisonConfig()
            for item in comparison_config_data:
                if isinstance(item, list) and len(item) >= 3:
                    # 数组格式：[expected_key, actual_key, label]
                    expected_key = str(item[0])
                    actual_key = str(item[1])
                    label = str(item[2])
                    if expected_key and actual_key and label:
                        comparison_config.add(expected_key, actual_key, label)
                else:
                    raise ValueError(f"comparison_config 中的每个元素必须是三元组数组 [expected_key, actual_key, label]，但收到了 {type(item)}: {item}")
            result["comparison_config"] = comparison_config
            
            # 从 comparison_config 中提取所有 detail. 开头的 actual_key
            for item in comparison_config.items:
                actual_key = item.actual_key
                if actual_key.startswith("detail."):
                    # 提取 detail. 后面的字段路径
                    field_path = actual_key[7:]  # 去掉 "detail." 前缀
                    if field_path and field_path not in result["detail_fields"]:
                        result["detail_fields"].append(field_path)
        else:
            raise ValueError(f"comparison_config 必须是列表格式，但收到了 {type(comparison_config_data)}")
    
    # 加载 custom_columns
    custom_columns_data = report_config.get("custom_columns")
    if custom_columns_data:
        if isinstance(custom_columns_data, list):
            # 完全自定义模式（列表）
            result["custom_columns"] = _process_custom_columns_list(custom_columns_data)
        elif isinstance(custom_columns_data, dict):
            # 增量修改模式（字典）
            result["custom_columns"] = _process_custom_columns_dict(custom_columns_data)
        else:
            raise ValueError(f"custom_columns 必须是列表或字典格式，但收到了 {type(custom_columns_data)}")
    
    return result


def _process_custom_columns_list(columns_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    处理完全自定义的列配置列表
    
    Args:
        columns_data: 列配置列表
        
    Returns:
        处理后的列配置列表，extractor 已转换为函数
    """
    processed = []
    for col in columns_data:
        col_copy = col.copy()
        # 处理 extractor
        if "extractor" in col_copy:
            extractor_str = col_copy["extractor"]
            if isinstance(extractor_str, str):
                col_copy["extractor"] = _create_extractor_from_string(extractor_str, col_copy.get("key", ""))
            # 如果已经是函数，保持不变
        elif "key" in col_copy:
            # 如果没有指定 extractor，默认使用 data.get(key, '')
            key = col_copy["key"]
            col_copy["extractor"] = lambda idx, data, k=key: data.get(k, "")
        processed.append(col_copy)
    return processed


def _process_custom_columns_dict(columns_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理增量修改的列配置字典
    
    Args:
        columns_data: 列配置字典
        
    Returns:
        处理后的列配置字典，extractor 已转换为函数
    """
    processed = {}
    
    for key, value in columns_data.items():
        if key in ["add", "insert_before", "insert_after"]:
            # 这些键的值是字典，key 是列名，value 是列配置列表
            processed[key] = {}
            for col_key, col_list in value.items():
                processed[key][col_key] = _process_custom_columns_list(col_list)
        elif key == "remove":
            # remove 是列表，直接复制
            processed[key] = value.copy() if isinstance(value, list) else value
        elif key == "modify":
            # modify 是字典，key 是列名，value 是列配置
            processed[key] = {}
            for col_key, col_config in value.items():
                col_config_copy = col_config.copy()
                # 处理 extractor
                if "extractor" in col_config_copy:
                    extractor_str = col_config_copy["extractor"]
                    if isinstance(extractor_str, str):
                        col_config_copy["extractor"] = _create_extractor_from_string(
                            extractor_str, col_key
                        )
                elif "key" in col_config_copy:
                    # 如果没有指定 extractor，默认使用 data.get(key, '')
                    key_name = col_config_copy.get("key", col_key)
                    col_config_copy["extractor"] = lambda idx, data, k=key_name: data.get(k, "")
                processed[key][col_key] = col_config_copy
        else:
            # 其他键直接复制
            processed[key] = value
    
    return processed


def _create_extractor_from_string(extractor_str: str, default_key: str = ""):
    """
    从字符串创建 extractor 函数
    
    支持的格式：
    1. "data.get('key', '')" - 简单的 data.get 调用
    2. "data.get('key')" - 不带默认值的 data.get
    3. "key" - 直接使用 key，等同于 data.get('key', '')
    
    Args:
        extractor_str: extractor 字符串表达式
        default_key: 默认的 key（如果 extractor_str 是简单的 key）
        
    Returns:
        extractor 函数
    """
    import re
    
    extractor_str = extractor_str.strip()
    
    # 如果只是简单的 key，使用 data.get(key, '')
    if not extractor_str.startswith("data.") and not extractor_str.startswith("lambda"):
        # 可能是简单的 key 名称
        key = extractor_str if extractor_str else default_key
        if key:
            return lambda idx, data, k=key: data.get(k, "")
        else:
            return lambda idx, data: ""
    
    # 处理 "data.get('key', '')" 格式
    match = re.match(r"data\.get\(['\"]([^'\"]+)['\"](?:,\s*['\"]?([^'\"]*)['\"]?)?\)", extractor_str)
    if match:
        key = match.group(1)
        default_value = match.group(2) if match.group(2) else ""
        return lambda idx, data, k=key, d=default_value: data.get(k, d)
    
    # 处理 lambda 表达式（如果将来需要支持）
    if extractor_str.startswith("lambda"):
        try:
            # 使用 eval 执行 lambda 表达式（注意安全性）
            return eval(extractor_str)
        except Exception as e:
            raise ValueError(f"无法解析 extractor 表达式: {extractor_str}, 错误: {e}")
    
    # 默认情况：尝试作为简单的 key
    if default_key:
        return lambda idx, data, k=default_key: data.get(k, "")
    else:
        return lambda idx, data: ""
