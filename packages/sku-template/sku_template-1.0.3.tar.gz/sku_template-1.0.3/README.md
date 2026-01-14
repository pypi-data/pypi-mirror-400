# SKU Template

SKU Template 是一个用于计费测试的完整解决方案，提供了 AppID 管理、SKU 查询框架和 HTML 报告生成等功能。

## 功能特性

### 1. AppID管理服务
- **HTTP服务**：独立的AppID管理服务，支持并发获取
- **智能分配**：自动管理AppID的使用状态，避免冲突
- **等待机制**：当所有AppID都不可用时，智能等待到下个小时
- **轮询重试**：客户端支持轮询重试，解决HTTP超时问题

### 2. 统一SKU查询框架
- **配置化**：不同业务只需配置sku_ids和base_url
- **统一接口**：所有业务使用相同的查询接口
- **并发查询**：支持并发查询多个SKU
- **JSON输出**：Detail数据统一返回JSON格式

### 3. HTML报告生成器
- **美观界面**：响应式设计，支持移动端
- **交互功能**：可折叠的测试用例详情，点击展开/收起
- **对比可视化**：预期值vs实际值对比表，差值高亮显示
- **状态筛选**：支持按状态（全部/通过/有差异/失败）筛选用例
- **状态标记**：可手动标记每个用例的状态，状态持久化保存
- **状态联动**：汇总信息实时更新，反映当前状态统计
- **导出功能**：支持导出修改后的HTML文件，保存状态修改

## 文件说明

```
sku-template/
├── sku_template/                   # Python包目录
│   ├── __init__.py                 # 包初始化
│   ├── client.py                   # AppID客户端SDK
│   ├── appid_manager_service.py    # AppID管理HTTP服务
│   ├── sku_query_framework.py      # 统一SKU查询框架
│   ├── html_report_generator.py    # HTML报告生成器
│   ├── config_init.py              # 配置初始化模块
│   └── templates/                  # HTML模板目录
│       ├── table_report.html       # 表格报告模板
│       ├── styles.css              # 样式文件
│       ├── script.js               # JavaScript交互代码
│       └── fragments/              # 模板片段
│           ├── summary.html        # 摘要片段
│           ├── status_select.html  # 状态选择框片段
│           ├── case_details.html   # 用例详情片段
│           ├── comparison_table.html # 对比表格片段
│           └── comparison_row.html # 对比行片段
└── README.md                       # 本说明文件
```

## 配置初始化

### 方式1: 通过API初始化（推荐，全新功能）⭐

**新功能**：可以通过API动态初始化任务调度器，无需依赖配置文件查找。

```bash
# 最简单的初始化
curl -X POST "http://localhost:8888/api/task/init" \
  -H "X-API-Key: <your-token>" \
  -F "config_dir=/path/to/sku-config"

# 上传配置文件
curl -X POST "http://localhost:8888/api/task/init" \
  -H "X-API-Key: <your-token>" \
  -F "config_dir=/path/to/sku-config" \
  -F "common_config_file=@common.json" \
  -F "business_config_file=@sip_duration.json" \
  -F "business_name=sip_duration"
```

**优势**：
- ✅ 不需要预先准备配置文件
- ✅ 配置目录自动创建
- ✅ 支持动态上传配置文件
- ✅ 简化部署流程

详细说明请参考 [USAGE_GUIDE.md](USAGE_GUIDE.md) 和 [API_REFERENCE.md](API_REFERENCE.md)

### 方式2: 传统配置文件方式

在使用模块前，需要先初始化配置文件：

```bash
# 运行初始化命令（会自动创建 sku-config 目录和 common.json 文件）
sku-config-init

# 检查配置文件是否存在
sku-config-init --check
```

**注意**：初始化命令会自动创建 `sku-config` 目录和默认的 `common.json` 文件，请根据实际需求修改配置文件。

配置文件会按以下优先级查找：
1. 命令行参数 `--config-dir`
2. 环境变量 `SKU_CONFIG_DIR`
3. 系统目录 `/etc/sku-template/config/`（生产环境推荐）
4. 用户目录 `~/.sku-template/config/`（开发环境）
5. 当前工作目录 `./sku-config/`（向后兼容）

详细配置说明请参考 [USAGE_GUIDE.md](USAGE_GUIDE.md) 和 [CONFIG_DESIGN.md](CONFIG_DESIGN.md)

## 使用方法

### 1. 启动AppID管理服务

```bash
# 默认端口8888
python -m sku_template.appid_manager_service

# 自定义端口
python -m sku_template.appid_manager_service --port 9999

# 查看帮助
python -m sku_template.appid_manager_service --help
```

### 2. 运行示例测试

```bash
# 运行集成示例（在测试目录中）
python test/billing_new_features/test_stt_billing_improve.py
```

### 3. 单独使用各个组件

```python
# 使用AppID客户端
from sku_template import AppIdClient

client = AppIdClient("http://localhost:8888")

# 1. 首先初始化产品配置
appids = {"appid1": "12345", "appid2": "67890"}
client.init_product("stt_billing", appids)

# 2. 然后才能获取AppID
appid, vid, starttime, product_name = client.acquire_appid("stt_billing")
# ... 执行测试 ...
client.release_appid(appid, product_name)

# 3. 重新初始化产品配置（会重置所有数据）
new_appids = {"new_appid_1": "11111", "new_appid_2": "22222"}
client.init_product("stt_billing", new_appids)

# 使用SKU查询框架
from sku_template import SkuQueryFactory

# 自动查找当前工作目录下的 sku-config 配置
sku_client = SkuQueryFactory.get_client("speech-to-text", environment="staging")

# 查询数据
sku_data = sku_client.query_sku(vid, from_ts, ["30331", "30332"])
detail_data = sku_client.query_detail(vid, from_ts)

# 使用HTML报告生成器
from sku_template import HTMLReportGenerator

generator = HTMLReportGenerator()
html_file = generator.generate_report(billing_datas)
```

## API接口

### 任务调度器（新功能）⭐

```
POST /api/task/init
  通过API初始化任务调度器（类似 /api/appid/init）
  Form: config_dir=/path/to/sku-config, common_config_file=@common.json, business_config_file=@business.json, business_name=xxx
  Response: {"success": true, "message": "任务调度器初始化成功", "config_dir": "...", "data_dir": "..."}

POST /api/task/add
  添加一次性任务
  Form: business=xxx, environment=staging, start_delay_minutes=0, expected_values_file=@file.jsonl
  Response: {"success": true, "task_id": "xxx", "message": "..."}
```

详细说明请参考 [USAGE_GUIDE.md](USAGE_GUIDE.md)、[API_REFERENCE.md](API_REFERENCE.md) 和 [TASK_WORKFLOW.md](TASK_WORKFLOW.md)

### AppID管理服务

```
POST /api/appid/init
  初始化或重置产品AppID配置
  Body: {"productName": "stt_billing", "appids": {"appid1": "12345", "appid2": "67890"}}
  Response: {"success": true, "productName": "stt_billing", "removed_count": 0, "added_count": 2, "message": "Product 'stt_billing' initialized: removed 0, added 2 appids"}

POST /api/appid/acquire
  获取可用的AppID（自动标记为使用中）
  Body: {"productName": "stt_billing"}
  Response: {"appid": "xxx", "vid": 1057686, "productName": "stt_billing", "starttime": 1699000000000}

POST /api/appid/release
  释放AppID
  Body: {"appid": "xxx", "productName": "stt_billing"}
  Response: {"success": true, "stoptime": 1699000001000, "productName": "stt_billing"}

GET /api/appid/status
  获取AppID状态统计
  Query: ?productName=stt_billing (可选)
  Response: {"total": 20, "available": 5, "in_use": 15, "released": 0, "productName": "stt_billing"}

GET /health
  健康检查
  Response: {"status": "healthy", "timestamp": 1699000000000}
```

## 配置说明

### AppID配置
服务启动后为空状态，需要通过API初始化产品配置：

```python
# 客户端初始化产品配置
client = AppIdClient("http://localhost:8888")

# 初始化stt_billing产品
stt_appids = {
    'your_appid_1': "vid_1",
    'your_appid_2': "vid_2",
}
client.init_product("stt_billing", stt_appids)

# 初始化rtc_billing产品
rtc_appids = {
    'rtc_appid_1': "vid_3",
    'rtc_appid_2': "vid_4",
}
client.init_product("rtc_billing", rtc_appids)
```

### SKU查询配置

配置文件通过 `sku-config-init` 初始化后，位于 `.sku-template/config/` 目录。

**添加新业务配置**：

在 `.sku-template/config/businesses/` 目录下创建新的 JSON 文件，例如 `your-business.json`：

```json
{
  "appIds": {
    "appid1": "vid1",
    "appid2": "vid2"
  },
  "sku": {
    "sku_ids": ["sku1", "sku2"]
  },
  "detail": {
    "business": "your_business",
    "model": "your_model"
  }
}
```

通用配置（如 API 地址、认证信息）在 `.sku-template/config/common.json` 中配置。

## 文档索引

### 功能使用文档

- **[AppID管理和预期值存储使用指南](./USAGE_GUIDE_APPID.md)** - AppID获取、释放、初始化，以及预期值文件存储功能
- **[SKU查询和HTML报告生成使用指南](./USAGE_GUIDE_SKU_QUERY.md)** - 使用已存储的预期值文件进行SKU查询和HTML报告生成

### 参考文档

- **[API参考](./API_REFERENCE.md)** - 完整的API接口文档
- **[任务工作流程](./TASK_WORKFLOW.md)** - 详细的任务执行流程说明
- **[配置设计文档](./CONFIG_DESIGN.md)** - 配置系统设计说明
- **[故障排除](./TROUBLESHOOTING.md)** - 常见问题和解决方案

### 旧版文档（已整合）

- **[使用指南（旧版）](./USAGE_GUIDE.md)** - 完整的使用指南，已拆分为两个独立的功能文档

## 注意事项

1. **服务依赖**：运行测试前必须先启动AppID管理服务
2. **端口冲突**：确保8888端口未被占用，或使用其他端口
3. **网络连接**：确保测试环境能访问SKU查询API
4. **文件权限**：确保有权限在输出目录创建HTML报告
5. **必填参数**：所有API调用中 `productName` 都是必填参数，不能为空
6. **产品初始化**：使用前必须先调用 `/api/appid/init` 初始化产品配置
7. **配置重置**：重新调用 `/api/appid/init` 会完全重置该产品的所有数据

## 故障排除

详细故障排除请参考 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### 常见问题快速参考

**AppID服务无法启动**
- 检查端口是否被占用：`netstat -tlnp | grep 8888`
- 检查Python依赖是否安装：`pip install flask requests`

**无法获取AppID**
- 检查服务是否运行：`curl http://localhost:8888/health`
- 查看服务日志了解详细错误信息

**SKU查询失败**
- 检查网络连接和API地址
- 确认API密钥和权限
- 查看详细错误日志

**任务调度器未初始化**
- 参考 [USAGE_GUIDE.md](USAGE_GUIDE.md) 中的"通过API初始化任务调度器"章节
- 检查配置文件是否存在：`sku-config-init --check`

## 扩展开发

### 添加新的测试用例
在 `billing_example.py` 的 `run_all_tests()` 方法中添加：

```python
test_cases = [
    ("你的测试用例", 120),
    # ...
]
```

### 自定义HTML报告样式
修改 `html_report_generator.py` 中的 `_get_css_styles()` 方法。

### 添加新的业务配置
在 `sku_query_framework.py` 中注册新业务：

```python
SkuQueryFactory.register_business("new_business", sku_config, detail_config)
```
