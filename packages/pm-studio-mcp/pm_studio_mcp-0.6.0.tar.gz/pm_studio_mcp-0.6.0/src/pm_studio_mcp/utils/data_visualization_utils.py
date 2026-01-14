"""
全新数据可视化工具 - 大幅度增强版本，支持中文和鲁棒时间处理，并且极大程度提高实用性与美观性（包括图表类型选择、配色、坐标轴和标签自动化判断等）

🎯 图表类型选择指南:

⭐ **优先级原则**: 当折线图和柱状图都适用时，**优先选择折线图**
折线图更适合展示数据的连续性和趋势变化，视觉效果更佳

📈 折线图(LINE) - 🥇 **优先推荐**
✅ 时间序列数据(趋势变化) - **首选**
✅ 多个指标随时间变化 - **首选**
✅ 显示变化趋势和模式 - **首选**
✅ 浏览器使用量、DAU/MAU趋势等 - **首选**
✅ 任何有序数据的连续展示 - **优先考虑**

📊 柱状图(BAR) - 🥈 备选方案:
✅ 比较不同类别的数值（当折线图不合适时）
✅ 对项目进行排名比较（离散分类）
✅ 类别名称较长时
✅ 纯分类数据比较（无时间序列特征）

📊 饼图(PIE) - 特定场景，尤其是份额类、组成部分类:
✅ 显示整体的组成部分(市场份额、百分比分解)
✅ 比较类别间的比例关系
✅ 类别数量为2-7个时效果最佳

⚠️ 散点图(SCATTER) - 仅限特定场景:
✅ 分析两个连续变量间的相关性
✅ 发现测量数据间的关系(身高vs体重、价格vs销量)
❌ 绝不用于时间序列数据!
❌ 绝不用于分类比较!
❌ 绝不用于显示时间趋势!
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import re
from typing import Dict, Any, Union
from matplotlib.ticker import FuncFormatter

# 简单配置 - 修正工作目录路径
WORKING_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "working_dir")

# 现代化专业配色方案
ENHANCED_COLORS = [
    "#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#6A994E",
    "#577590", "#F8961E", "#90E0EF", "#9B59B6", "#E74C3C",
    "#1ABC9C", "#F39C12", "#8E44AD", "#27AE60", "#E67E22"
]

# 日期匹配模式
DATE_PATTERN = re.compile(r'\d{4}-\d{2}-\d{2}')

def parse_date_robust(date_str):
    """鲁棒的日期解析函数 - 支持多种日期格式"""
    if not date_str or not isinstance(date_str, str):
        return None
    
    date_str = date_str.strip().strip('"\'')
    
    # 跳过明显不是日期的数字
    if date_str.isdigit() and len(date_str) < 6:
        return None
    
    # 常见日期格式按优先级排序
    formats = [
        "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ",
        "%m/%d/%Y", "%d/%m/%Y", "%d-%m-%Y", "%m-%d-%Y", "%Y%m%d", 
        "%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%d %B %Y",
        "%Y-%m", "%Y/%m", "%m/%Y", "%m-%Y"
    ]
    
    # 首先尝试提取YYYY-MM-DD模式
    date_match = DATE_PATTERN.search(date_str)
    if date_match:
        try:
            return datetime.datetime.strptime(date_match.group(0), "%Y-%m-%d")
        except ValueError:
            pass
    
    # 尝试各种预定义格式
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # 使用dateutil作为后备
    try:
        from dateutil import parser
        return parser.parse(date_str, fuzzy=True, default=datetime.datetime(2020, 1, 1))
    except:
        pass
    
    # 尝试pandas的to_datetime作为最后后备
    try:
        result = pd.to_datetime(date_str, errors='coerce', infer_datetime_format=True)
        if pd.notna(result):
            return result.to_pydatetime()
    except:
        pass
    
    return None

def identify_time_field(headers):
    """识别时间字段"""
    time_fields = [
        "__timestamp", "timestamp", "Timestamp", "TIMESTAMP",
        "date", "Date", "DATE", "time", "Time", "TIME",
        "datetime", "DateTime", "DATETIME", "created_at", "updated_at"
    ]
    
    # 精确匹配
    for field in time_fields:
        if field in headers:
            return field
    
    # 模糊匹配 - 查找包含时间关键词的列
    for header in headers:
        if any(keyword in header.lower() for keyword in ['time', 'date', 'day', '时间', '日期']):
            return header
    
    # 检查第一列是否像时间
    return headers[0] if headers else None

def format_time_label(date_obj):
    """格式化时间标签"""
    if not isinstance(date_obj, datetime.datetime):
        return str(date_obj)
    
    current_year = datetime.datetime.now().year
    return date_obj.strftime('%m-%d' if date_obj.year == current_year else '%Y-%m-%d')

def format_number_smart(value):
    """数值格式化函数"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return str(value)
    
    abs_value = abs(value)
    
    if abs_value >= 1_000_000_000_000:
        return f'{value/1_000_000_000_000:.1f}T'
    elif abs_value >= 100_000_000_000:
        return f'{value/1_000_000_000:.0f}B'
    elif abs_value >= 1_000_000_000:
        return f'{value/1_000_000_000:.1f}B'
    elif abs_value >= 10_000_000:
        return f'{value/1_000_000:.0f}M'
    elif abs_value >= 1_000_000:
        return f'{value/1_000_000:.1f}M'
    elif abs_value >= 100_000:
        return f'{value/1_000:.0f}K'
    elif abs_value >= 1_000:
        return f'{value/1_000:.1f}K'
    elif abs_value >= 10:
        return f'{value:.0f}'
    elif abs_value >= 1:
        return f'{value:.1f}'
    elif abs_value >= 0.001:
        return f'{value:.3f}'
    else:
        return f'{value:.2e}'

def create_smart_formatter():
    """创建数值格式化器"""
    def formatter(x, pos):
        return format_number_smart(x)
    return FuncFormatter(formatter)

def _determine_chart_type(df, string_cols, numeric_cols, has_time_data):
    """确定最适合的图表类型"""
    # 1. 首先检查是否是市场份额/占比类数据 - 优先饼图
    if len(string_cols) > 0 and len(numeric_cols) == 1:
        # 检查列名是否包含份额、占比、比例等关键词
        col_names_lower = ' '.join([str(col).lower() for col in df.columns])
        share_keywords = ['share', 'market', 'percent', 'ratio', '份额', '占比', '比例', '市场', '百分比']
        if any(keyword in col_names_lower for keyword in share_keywords) and len(df) <= 10:
            return 'pie', 'market_share_composition'
        # 检查数据是否像百分比或份额数据
        elif len(df) <= 10 and len(numeric_cols) == 1:
            values = df[numeric_cols[0]].dropna()
            if len(values) > 0:
                # 如果数值总和接近100或1，可能是百分比数据
                total = values.sum()
                if 90 <= total <= 110 or 0.9 <= total <= 1.1:
                    return 'pie', 'percentage_composition'
                else:
                    return 'bar', 'categorical_comparison'
        else:
            return 'bar', 'categorical_comparison'
    
    # 2. 时间序列数据 - 优先折线图
    elif has_time_data and len(numeric_cols) >= 1:
        return 'line', 'time_series_trending'
    
    # 3. 多个数值列且有序数据 - 折线图展示趋势
    elif len(numeric_cols) > 1 and len(df) > 2:
        return 'line', 'sequential_trending'
    
    # 4. 单个数值列，多行数据 - 根据数据特征选择
    elif len(numeric_cols) == 1 and len(df) > 1:
        if len(df) <= 15:  # 数据点不多时，可以用柱状图清晰对比
            return 'bar', 'discrete_comparison'
        else:  # 数据点较多时，用折线图展示趋势
            return 'line', 'trending_data'
    
    # 5. 默认情况
    else:
        return 'line', 'general'

def _analyze_time_range(df, time_col):
    """分析时间范围并格式化"""
    if not time_col or time_col not in df.columns:
        return ''
    
    time_values = []
    for val in df[time_col].dropna():
        parsed = parse_date_robust(str(val))
        if parsed:
            time_values.append(parsed)
    
    if not time_values:
        return ''
    
    time_values.sort()
    start_date = time_values[0]
    end_date = time_values[-1]
    
    # 计算时间跨度
    days_diff = (end_date - start_date).days
    if days_diff <= 7:
        return f"{start_date.strftime('%m-%d')} 至 {end_date.strftime('%m-%d')} (周数据)"
    elif days_diff <= 31:
        return f"{start_date.strftime('%m-%d')} 至 {end_date.strftime('%m-%d')} (月数据)"
    elif days_diff <= 365:
        return f"{start_date.strftime('%Y-%m')} 至 {end_date.strftime('%Y-%m')} (年内数据)"
    else:
        return f"{start_date.strftime('%Y-%m')} 至 {end_date.strftime('%Y-%m')} (多年数据)"

def _analyze_metrics(numeric_cols):
    """分析数值列含义"""
    metrics = []
    for col in numeric_cols:
        col_lower = col.lower()
        if 'dau' in col_lower or 'active' in col_lower:
            metrics.append(f"{col} (活跃用户)")
        elif 'revenue' in col_lower or '收入' in col_lower:
            metrics.append(f"{col} (收入)")
        elif 'count' in col_lower or '数量' in col_lower:
            metrics.append(f"{col} (数量)")
        elif 'rate' in col_lower or 'ratio' in col_lower or '率' in col_lower:
            metrics.append(f"{col} (比率)")
        elif 'share' in col_lower or '份额' in col_lower:
            metrics.append(f"{col} (市场份额)")
        else:
            metrics.append(col)
    return metrics

def _generate_title(metrics, time_range, string_cols, numeric_cols, df):
    """生成合适的标题"""
    if metrics and time_range:
        main_metric = metrics[0].split(' ')[0]  # 取第一个指标的名称部分
        return f"{main_metric} 趋势分析 ({time_range})"
    elif metrics:
        return f"{metrics[0]} 数据分析"
    elif string_cols and numeric_cols:
        return f"{string_cols[0]} vs {numeric_cols[0]} 对比分析"
    else:
        return "数据可视化分析"

def analyze_data_content(df):
    """分析数据内容，生成标题和描述 - 重构版本"""
    # 检测列类型
    string_cols = df.select_dtypes(include=['object']).columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # 识别时间列和有序数据
    time_col = identify_time_field(df.columns.tolist())
    has_time_data = time_col is not None
    
    # 确定图表类型
    chart_preference, data_type = _determine_chart_type(df, string_cols, numeric_cols, has_time_data)
    
    # 分析时间范围
    time_range = _analyze_time_range(df, time_col)
    
    # 分析指标含义
    metrics = _analyze_metrics(numeric_cols)
    
    # 生成标题
    suggested_title = _generate_title(metrics, time_range, string_cols, numeric_cols, df)
    
    # 时间序列数据总是推荐折线图
    if time_range:
        chart_preference = 'line'
    elif len(df) > 3 and metrics:
        chart_preference = 'line'
    
    return {
        'suggested_title': suggested_title,
        'data_type': data_type,
        'time_range': time_range,
        'metrics': metrics,
        'chart_preference': chart_preference
    }

def setup_chinese_fonts():
    """设置中文字体支持"""
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Arial', 'Helvetica']
    plt.rcParams['axes.unicode_minus'] = False

def detect_time_series(df, column):
    """检测是否是时间序列数据"""
    if column not in df.columns:
        return False, None
    
    # 尝试解析前几行
    sample_size = min(len(df), 5)
    success_count = sum(1 for value in df[column].head(sample_size) 
                       if parse_date_robust(str(value)) is not None)
    
    is_time_series = success_count >= sample_size * 0.6
    
    if is_time_series:
        # 创建排序索引
        parsed_dates = []
        for idx, value in enumerate(df[column]):
            parsed_date = parse_date_robust(str(value))
            parsed_dates.append((idx, parsed_date or datetime.datetime(1900, 1, 1)))
        
        parsed_dates.sort(key=lambda x: x[1])
        return True, [x[0] for x in parsed_dates]
    
    return False, None

class SimpleDataViz:
    """极简数据可视化类 - 支持中文和鲁棒时间处理"""
    
    def __init__(self):
        os.makedirs(WORKING_PATH, exist_ok=True)
        setup_chinese_fonts()
    
    def _apply_professional_style(self):
        """应用现代化专业样式"""
        setup_chinese_fonts()
        plt.style.use('default')
        
        # 设置现代化配色循环
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=ENHANCED_COLORS)
        
        # 字体和样式设置
        font_config = {
            'font.family': 'sans-serif',
            'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'Segoe UI', 'Roboto', 'Helvetica'],
            'font.weight': '500',
            'axes.titleweight': 'bold',
            'axes.titlesize': 16,
            'axes.labelweight': '600',
            'axes.labelsize': 11,
            'axes.unicode_minus': False,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'xtick.major.pad': 10,
            'ytick.major.pad': 8
        }
        plt.rcParams.update(font_config)
        
        # 网格和边框设置
        grid_config = {
            'axes.grid': True,
            'axes.grid.axis': 'y',
            'axes.axisbelow': True,
            'grid.color': '#E8E8E8',
            'grid.linestyle': '-',
            'grid.alpha': 0.3,
            'grid.linewidth': 0.8,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'axes.spines.left': True,
            'axes.spines.bottom': True,
            'axes.linewidth': 1.2
        }
        plt.rcParams.update(grid_config)
        
        # 背景和布局设置
        layout_config = {
            'figure.facecolor': '#FAFAFA',
            'axes.facecolor': 'white',
            'figure.subplot.bottom': 0.15,
            'figure.subplot.left': 0.12,
            'figure.subplot.right': 0.85,
            'figure.subplot.top': 0.88
        }
        plt.rcParams.update(layout_config)
    
    def _apply_common_axis_styling(self, ax, time_col, string_cols, numeric_cols):
        """应用通用的坐标轴样式设置 - 消除重复代码"""
        # 设置X轴标签
        if time_col:
            ax.set_xlabel('时间', fontweight='bold', fontfamily='Microsoft YaHei')
        elif len(string_cols) > 0:
            ax.set_xlabel(string_cols[0], fontweight='bold', fontfamily='Microsoft YaHei')
        
        # 设置Y轴标签
        if len(numeric_cols) == 1:
            ax.set_ylabel(numeric_cols[0], fontweight='bold', fontfamily='Microsoft YaHei')
        elif len(numeric_cols) > 1:
            ax.set_ylabel('数值', fontweight='bold', fontfamily='Microsoft YaHei')
        
        # 应用Y轴格式化器
        ax.yaxis.set_major_formatter(create_smart_formatter())
        
        # 设置x轴标签字体
        for label in ax.get_xticklabels():
            label.set_fontfamily('Microsoft YaHei')
            label.set_fontsize(9)
    
    def _add_data_labels(self, ax, bars, values, max_count=20):
        """为柱状图添加数据标签 - 统一方法"""
        if len(values) <= max_count:
            max_height = max([bar.get_height() for bar in bars])
            
            for i, bar in enumerate(bars):
                height = bar.get_height()
                if not np.isnan(height):
                    label = format_number_smart(height)
                    ax.text(bar.get_x() + bar.get_width()/2., height + max_height * 0.01,
                           label, ha='center', va='bottom', 
                           fontweight='bold', fontfamily='Microsoft YaHei', fontsize=8)
    
    def _add_line_annotations(self, ax, x_values, y_values, max_count=10):
        """为折线图添加数据点标注 - 统一方法"""
        if len(x_values) <= max_count:
            for i, (x, y) in enumerate(zip(x_values, y_values)):
                if not np.isnan(y):
                    label = format_number_smart(y)
                    ax.annotate(label, (x, y), color=ENHANCED_COLORS[0],
                               xytext=(0, 10), textcoords='offset points',
                               ha='center', va='bottom', fontsize=8,
                               fontweight='bold', fontfamily='Microsoft YaHei')
    
    def _create_legend(self, ax, numeric_cols):
        """创建统一的图例样式"""
        if len(numeric_cols) > 1:
            ax.legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=True,
                     fancybox=True, shadow=True, prop={'family': 'Microsoft YaHei'})
    
    def _process_data(self, data_source):
        """处理数据源"""
        if isinstance(data_source, str):
            encodings = ['utf-8', 'gbk', 'latin-1']
            for encoding in encodings:
                try:
                    df = pd.read_csv(data_source, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
        elif isinstance(data_source, dict):
            df = pd.DataFrame(data_source)
        else:
            df = data_source.copy()
        
        # 基本数据清理
        if df.columns.duplicated().any():
            df = df.loc[:, ~df.columns.duplicated()]
        
        df.columns = df.columns.str.strip()
        
        # 尝试转换数值类型
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    cleaned_series = df[col].astype(str).str.replace(',', '').str.replace('$', '').str.replace('¥', '')
                    numeric_series = pd.to_numeric(cleaned_series, errors='coerce')
                    if numeric_series.notna().sum() / len(df) > 0.8:
                        df[col] = numeric_series
                except:
                    pass
        
        return df
    
    def _sort_data_by_time(self, df, time_col):
        """按时间正确排序数据"""
        if time_col not in df.columns:
            return df, []
        
        # 解析所有时间值
        time_data = []
        for idx, val in enumerate(df[time_col]):
            parsed_time = parse_date_robust(str(val))
            time_data.append((idx, parsed_time or datetime.datetime(1900, 1, 1), val))
        
        time_data.sort(key=lambda x: x[1])
        
        # 获取排序后的索引和格式化标签
        sorted_indices = [x[0] for x in time_data]
        sorted_df = df.iloc[sorted_indices].reset_index(drop=True)
        formatted_labels = [format_time_label(x[1]) for x in time_data]
        
        return sorted_df, formatted_labels
    
    def _detect_columns(self, df):
        """检测列类型"""
        string_cols = df.select_dtypes(include=['object']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 识别时间列
        time_col = identify_time_field(df.columns.tolist())
        
        # 验证时间列是否真的包含时间数据
        is_time_valid = False
        if time_col and time_col in df.columns:
            sample_size = min(10, len(df))
            valid_dates = sum(1 for val in df[time_col].head(sample_size) 
                            if parse_date_robust(str(val)))
            is_time_valid = valid_dates >= sample_size * 0.6
            
            if is_time_valid and time_col in string_cols:
                string_cols.remove(time_col)
        
        # 检测可能的分类列
        categorical_cols = []
        for col in numeric_cols.copy():
            unique_count = df[col].nunique()
            total_count = len(df)
            
            if (unique_count <= 10 and unique_count < total_count * 0.5 and
                df[col].dtype in ['int64', 'int32'] or (df[col] == df[col].astype(int)).all()):
                categorical_cols.append(col)
        
        return string_cols, numeric_cols, time_col if is_time_valid else None
    
    def generate_chart(self, chart_type: str, data_source, **options) -> Dict[str, Any]:
        """生成图表"""
        try:
            # 处理数据
            df = self._process_data(data_source)
            
            # 分析数据内容
            data_analysis = analyze_data_content(df)
            
            # 应用专业样式
            self._apply_professional_style()
            
            # 检测列类型
            string_cols, numeric_cols, time_col = self._detect_columns(df)
            
            # 如果有时间列，先按时间排序
            if time_col:
                df, formatted_time_labels = self._sort_data_by_time(df, time_col)
            else:
                formatted_time_labels = []
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 根据图表类型生成
            if chart_type == 'pie':
                self._generate_pie_chart(ax, df, string_cols, numeric_cols, options, data_analysis)
                
            elif chart_type == 'bar':
                self._generate_bar_chart(ax, df, string_cols, numeric_cols, time_col, 
                                       formatted_time_labels, options, data_analysis)
                
            elif chart_type == 'line':
                self._generate_line_chart(ax, df, string_cols, numeric_cols, time_col,
                                        formatted_time_labels, options, data_analysis)
                
            elif chart_type == 'scatter':
                self._generate_scatter_chart(ax, df, numeric_cols, options, data_analysis)
                
            else:
                raise ValueError(f"不支持的图表类型: {chart_type}")
            
            # 设置标题
            title = options.get('title', data_analysis['suggested_title'])
            
            # 设置标题样式
            if data_analysis['time_range']:
                fig.suptitle(title, 
                           fontsize=18, 
                           fontweight='700', 
                           fontfamily='Microsoft YaHei', 
                           y=0.92,
                           color='#2C3E50')
                
                ax.set_title(data_analysis['time_range'], 
                           fontsize=12, 
                           fontweight='500', 
                           fontfamily='Microsoft YaHei', 
                           color='#7F8C8D',
                           pad=15)
            else:
                ax.set_title(title, 
                           fontsize=18, 
                           fontweight='700', 
                           fontfamily='Microsoft YaHei', 
                           pad=25,
                           color='#2C3E50')
            
            # 保存图片
            filename = options.get('filename', f'{chart_type}_chart.png')
            output_path = os.path.join(WORKING_PATH, filename)
            
            plt.tight_layout(rect=[0, 0, 1, 0.90] if data_analysis['time_range'] else [0, 0, 1, 0.92])
            
            plt.savefig(output_path, 
                       dpi=300,
                       bbox_inches='tight', 
                       facecolor='#FAFAFA',
                       edgecolor='none',
                       pad_inches=0.4,
                       format='png')
            plt.close()
            
            return {
                "success": True,
                "output_path": output_path,
                "message": f"成功生成 {chart_type} 图表: {output_path}",
                "chart_type": chart_type,
                "data_analysis": data_analysis,
                "recommended_chart": data_analysis.get('chart_preference', 'line'),
                "preference_note": "系统推荐: 优先使用最适合数据特征的图表类型",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            plt.close()
            return {
                "success": False,
                "output_path": None,
                "message": f"生成图表失败: {str(e)}",
                "chart_type": chart_type,
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _generate_bar_chart(self, ax, df, string_cols, numeric_cols, time_col, 
                          formatted_time_labels, options, data_analysis):
        """生成柱状图"""
        
        if len(numeric_cols) < 1:
            raise ValueError("柱状图需要至少一个数字列")
        
        # 确定x轴和y轴
        if time_col:
            x_values = formatted_time_labels
            y_col = numeric_cols[0]
            y_values = df[y_col].values
            
            bars = ax.bar(range(len(x_values)), y_values, 
                         color=ENHANCED_COLORS[0], 
                         edgecolor='white', 
                         linewidth=1.5,
                         alpha=0.8,
                         width=0.7)
            
            # 添加渐变效果
            for i, bar in enumerate(bars):
                intensity = y_values[i] / max(y_values) if max(y_values) > 0 else 0.5
                color = plt.matplotlib.colors.to_rgba(ENHANCED_COLORS[0], alpha=0.6 + intensity * 0.4)
                bar.set_facecolor(color)
            
            # 设置x轴标签
            ax.set_xticks(range(len(x_values)))
            ax.set_xticklabels(x_values, rotation=45, ha='right')
            
        elif len(string_cols) > 0:
            x_col = string_cols[0]
            y_col = numeric_cols[0]
            y_values = df[y_col].values
            
            bars = ax.bar(df[x_col], df[y_col], 
                         color=ENHANCED_COLORS[0],
                         edgecolor='white', 
                         linewidth=1.5,
                         alpha=0.8,
                         width=0.7)
            
            # 添加渐变效果
            for i, bar in enumerate(bars):
                intensity = y_values[i] / max(y_values) if max(y_values) > 0 else 0.5
                color = plt.matplotlib.colors.to_rgba(ENHANCED_COLORS[0], alpha=0.6 + intensity * 0.4)
                bar.set_facecolor(color)
            
            # 处理x轴标签旋转
            if len(df) > 8:
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        else:
            # 使用索引作为x轴
            y_col = numeric_cols[0]
            y_values = df[y_col].values
            bars = ax.bar(range(len(df)), df[y_col], 
                         color=ENHANCED_COLORS[0],
                         edgecolor='white', 
                         linewidth=1.5,
                         alpha=0.8,
                         width=0.7)
        
        # 添加数值标签
        self._add_data_labels(ax, bars, y_values)
        
        # 多系列数据支持
        if len(numeric_cols) > 1:
            bar_width = 0.8 / len(numeric_cols)
            x_positions = np.arange(len(df))
            
            # 清除之前的柱子
            ax.clear()
            
            # 重新应用样式
            self._apply_professional_style()
            
            for i, col in enumerate(numeric_cols[:5]):  # 最多显示5个系列
                offset = (i - len(numeric_cols)/2 + 0.5) * bar_width
                bars = ax.bar(x_positions + offset, df[col], bar_width, 
                             label=col, color=ENHANCED_COLORS[i % len(ENHANCED_COLORS)],
                             edgecolor='white', linewidth=0.5)
            
            # 设置x轴
            if time_col and formatted_time_labels:
                ax.set_xticks(x_positions)
                ax.set_xticklabels(formatted_time_labels, rotation=45, ha='right')
            elif len(string_cols) > 0:
                ax.set_xticks(x_positions)
                ax.set_xticklabels(df[string_cols[0]], rotation=45, ha='right')
        
        # 应用统一的坐标轴样式和图例
        self._apply_common_axis_styling(ax, time_col, string_cols, numeric_cols)
        self._create_legend(ax, numeric_cols)
    
    def _generate_line_chart(self, ax, df, string_cols, numeric_cols, time_col,
                           formatted_time_labels, options, data_analysis):
        """生成折线图"""
        
        if len(numeric_cols) < 1:
            raise ValueError("折线图需要至少一个数字列")
        
        # 确定x轴数据
        if time_col and formatted_time_labels:
            x_values = range(len(formatted_time_labels))
            x_labels = formatted_time_labels
        elif len(string_cols) > 0:
            x_values = range(len(df))
            x_labels = df[string_cols[0]].tolist()
        else:
            x_values = range(len(df))
            x_labels = [str(i) for i in x_values]
        
        # 多系列支持 - 同时显示多个指标
        if len(numeric_cols) == 1:
            # 单系列 - 现代化设计
            y_col = numeric_cols[0]
            line = ax.plot(x_values, df[y_col], 
                          marker='o', 
                          linewidth=3.5, 
                          markersize=8,
                          color=ENHANCED_COLORS[0], 
                          label=y_col, 
                          markerfacecolor='white',
                          markeredgewidth=2.5, 
                          markeredgecolor=ENHANCED_COLORS[0],
                          alpha=0.9,
                          linestyle='-')
            
            # 添加阴影效果
            ax.fill_between(x_values, df[y_col], alpha=0.15, color=ENHANCED_COLORS[0])
            
        else:
            # 多系列 - 最多显示5条线，现代化设计
            for i, col in enumerate(numeric_cols[:5]):
                ax.plot(x_values, df[col], 
                       marker='o', 
                       linewidth=3, 
                       markersize=7,
                       color=ENHANCED_COLORS[i % len(ENHANCED_COLORS)], 
                       label=col,
                       markerfacecolor='white', 
                       markeredgewidth=2, 
                       markeredgecolor=ENHANCED_COLORS[i % len(ENHANCED_COLORS)],
                       alpha=0.9,
                       linestyle='-')
        
        # 设置x轴标签
        ax.set_xticks(x_values)
        
        # 智能处理x轴标签密度
        if len(x_labels) > 15:
            # 太多标签时，只显示部分
            step = len(x_labels) // 10
            selected_indices = range(0, len(x_labels), step)
            selected_labels = [x_labels[i] if i < len(x_labels) else '' for i in selected_indices]
            ax.set_xticks([x_values[i] for i in selected_indices])
            ax.set_xticklabels(selected_labels, rotation=45, ha='right')
        elif len(x_labels) > 8:
            # 中等数量时旋转标签
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
        else:
            # 少量标签时正常显示
            ax.set_xticklabels(x_labels)
        
        # 添加数据点标注（单系列且数据点较少时）
        if len(numeric_cols) == 1:
            self._add_line_annotations(ax, x_values, df[numeric_cols[0]])
        
        # 应用统一的坐标轴样式和图例
        self._apply_common_axis_styling(ax, time_col, string_cols, numeric_cols)
        self._create_legend(ax, numeric_cols)
    
    def _generate_pie_chart(self, ax, df, string_cols, numeric_cols, options, data_analysis):
        """生成现代化饼图 - 清晰简洁的设计"""
        if len(string_cols) > 0 and len(numeric_cols) > 0:
            # 选择数据
            labels = df[string_cols[0]]
            values = df[numeric_cols[0]]
            
            # 数据预处理 - 合并小份额项目
            total = values.sum()
            threshold = total * 0.02  # 小于2%的项目合并为"其他"
            
            large_items = values >= threshold
            if large_items.sum() < len(values):  # 如果有小项目需要合并
                large_labels = labels[large_items].tolist()
                large_values = values[large_items].tolist()
                
                small_sum = values[~large_items].sum()
                if small_sum > 0:
                    large_labels.append('其他')
                    large_values.append(small_sum)
                
                labels = large_labels
                values = large_values
            
            # 清晰配色方案
            # 使用更饱和度适中的颜色，提高可读性
            clean_colors = [
                "#2E86AB",  # 深蓝色
                "#A23B72",  # 紫红色  
                "#F18F01",  # 橙色
                "#C73E1D",  # 红色
                "#6A994E",  # 绿色
                "#577590",  # 蓝灰色
                "#F8961E",  # 黄橙色
                "#8E44AD",  # 紫色
                "#27AE60",  # 翠绿色
                "#E67E22"   # 橘色
            ]
            colors = clean_colors[:len(labels)]
            
            # 简化爆炸效果 - 只突出最大项，其他保持整齐
            max_index = values.index(max(values))
            explode = [0.05 if i == max_index else 0 for i in range(len(values))]
            
            # 生成清晰饼图 - 去掉阴影和透明度
            wedges, texts, autotexts = ax.pie(
                values, 
                labels=labels, 
                autopct=lambda pct: f'{pct:.1f}%' if pct > 2 else '',  # 小于2%不显示百分比
                colors=colors,
                startangle=90,
                wedgeprops={
                    'edgecolor': '#FFFFFF',  # 纯白色边框
                    'linewidth': 2.5,       # 适中的边框宽度
                    'alpha': 1.0            # 完全不透明，颜色更清晰
                },
                explode=explode,
                shadow=False,              # 去掉阴影效果
                textprops={'fontsize': 11, 'fontweight': '600'}
            )
            
            # 清晰的文字样式
            for text in texts:
                text.set_fontfamily('Microsoft YaHei')
                text.set_fontsize(12)           # 略微增大字体
                text.set_fontweight('700')      # 更粗的字体
                text.set_color('#2C3E50')       # 深色文字更清晰
            
            # 清晰的百分比标签 - 去掉背景框，使用对比色
            for i, autotext in enumerate(autotexts):
                autotext.set_fontfamily('Microsoft YaHei')
                autotext.set_fontsize(11)
                autotext.set_fontweight('bold')
                autotext.set_color('#FFFFFF')   # 纯白色文字
                # 不使用背景框，直接显示在饼块上，更清晰
            
            # 📊 简洁的数值图例
            legend_labels = []
            for i, (label, value) in enumerate(zip(labels, values)):
                percentage = (value / total) * 100
                formatted_value = format_number_smart(value)
                legend_labels.append(f'{label}: {formatted_value} ({percentage:.1f}%)')
            
            # 创建清晰简洁的图例
            legend = ax.legend(
                legend_labels, 
                loc='center left', 
                bbox_to_anchor=(1.05, 0.5),    # 稍微调整位置
                frameon=True, 
                fancybox=False,                 # 使用简单矩形框
                shadow=False,                   # 去掉阴影
                prop={'family': 'Microsoft YaHei', 'size': 10, 'weight': '600'},
                borderpad=1.0,
                columnspacing=1.0,
                handlelength=1.2
            )
            
            # 简洁的图例框样式
            legend.get_frame().set_facecolor('#FFFFFF')    # 纯白背景
            legend.get_frame().set_edgecolor('#D5D5D5')    # 浅灰边框
            legend.get_frame().set_linewidth(1.0)          # 细边框
            legend.get_frame().set_alpha(1.0)              # 完全不透明
            
            # 设置饼图为完美圆形
            ax.set_aspect('equal')
            
        else:
            raise ValueError("饼图需要至少一个字符串列和一个数字列")
    
    def _generate_scatter_chart(self, ax, df, numeric_cols, options, data_analysis):
        """生成散点图 - 仅用于相关性分析，增强版本"""
        if len(numeric_cols) >= 2:
            x_col, y_col = numeric_cols[0], numeric_cols[1]
            
            # 🎨 创建散点图
            scatter = ax.scatter(df[x_col], df[y_col], 
                               color=ENHANCED_COLORS[0], alpha=0.7, s=60, 
                               edgecolors='white', linewidth=1)
            
            # 📈 添加趋势线
            try:
                z = np.polyfit(df[x_col].dropna(), df[y_col].dropna(), 1)
                p = np.poly1d(z)
                ax.plot(df[x_col], p(df[x_col]), "--", alpha=0.8, 
                       color=ENHANCED_COLORS[1], linewidth=2, label='趋势线')
                
                # 计算相关系数
                correlation = np.corrcoef(df[x_col].dropna(), df[y_col].dropna())[0,1]
                ax.text(0.05, 0.95, f'相关系数: {correlation:.3f}', 
                       transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                       fontfamily='Microsoft YaHei', fontweight='bold')
                
                ax.legend(prop={'family': 'Microsoft YaHei'})
            except:
                pass  # 如果无法计算趋势线，继续
            
            # 设置轴标签 - 散点图特殊处理，不使用通用方法
            ax.set_xlabel(x_col, fontweight='bold', fontfamily='Microsoft YaHei')
            ax.set_ylabel(y_col, fontweight='bold', fontfamily='Microsoft YaHei')
            
            # 应用轴格式化器
            ax.xaxis.set_major_formatter(create_smart_formatter())
            ax.yaxis.set_major_formatter(create_smart_formatter())
            
        else:
            raise ValueError("散点图需要至少两个数字列用于相关性分析")

# 保持向后兼容的类名
DataVisualizationUtils = SimpleDataViz
