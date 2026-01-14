# HTML模板说明

## 模板系统

HTMLReportGenerator 支持将HTML、CSS、JavaScript和Python代码完全分离，您可以在 `templates` 目录中放置自定义的模板文件。

## 文件结构

```
templates/
├── README.md                    # 本说明文件
├── table_report.html            # 表格视图报告HTML模板
├── validation_report.html       # 校验结果报告HTML模板
├── styles.css                   # CSS样式文件
└── script.js                    # JavaScript代码文件
```

## 模板文件说明

### HTML模板文件

- **table_report.html** - 表格视图报告模板
- **validation_report.html** - 校验结果报告模板

在HTML模板文件中，您可以使用以下方式引用CSS和JS：
```html
<link rel="stylesheet" href="styles.css">
<script src="script.js"></script>
```

这些引用在生成HTML时会自动转换为内联的 `<style>` 和 `<script>` 标签，确保生成的HTML文件是独立的，不依赖外部文件。

### CSS样式文件

- **styles.css** - 所有CSS样式代码

### JavaScript代码文件

- **script.js** - 所有JavaScript交互代码

## 模板变量

在HTML模板文件中，您可以使用以下变量（使用 `{变量名}` 格式）：

### 表格视图模板变量

- `{css_styles}` - CSS样式代码（自动从styles.css加载）
- `{generation_time}` - 报告生成时间
- `{total_cases}` - 测试用例总数
- `{summary_html}` - 摘要部分HTML
- `{table_rows}` - 表格行数据HTML
- `{javascript_code}` - JavaScript代码（自动从script.js加载）

### 校验报告模板变量

- `{css_styles}` - CSS样式代码（自动从styles.css加载）
- `{generation_time}` - 报告生成时间
- `{total_cases}` - 测试用例总数
- `{summary_html}` - 摘要部分HTML
- `{table_rows}` - 表格行数据HTML
- `{javascript_code}` - JavaScript代码（自动从script.js加载）

## 使用方式

### 方式1：使用外部模板文件（推荐）

1. 在 `templates` 目录中放置您的模板文件
2. HTMLReportGenerator 会自动检测并使用外部模板文件
3. 修改HTML、CSS或JS时，直接编辑对应的模板文件即可

### 方式2：使用内置模板（默认）

如果模板文件不存在，会自动使用Python代码中的内置模板。

## 优势

1. **完全分离**：HTML、CSS、JS和Python代码完全分离，各司其职
2. **易于维护**：修改样式和交互不需要改动Python代码
3. **独立生成**：生成的HTML文件是独立的，不依赖外部文件
4. **版本控制友好**：HTML、CSS、JS文件可以单独进行版本控制

