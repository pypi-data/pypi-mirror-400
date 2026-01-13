# MLflow Header Plugin

一个用于在MLflow请求中自动添加自定义header的插件。

## 功能

此插件会自动在所有MLflow tracking请求中添加以下header：
- `X-Target-Service-IP`: 目标服务的IP地址
- `X-Target-Service-PORT`: 目标服务的端口

## 安装

### 方式1: 从源码安装

```bash
cd wedata-mlflow-header-plugin
pip install -e .
```

### 方式2: 使用pip安装

```bash
pip install wedata-mlflow-header-plugin
```

## 配置

插件通过环境变量来配置header的值：

- `MLFLOW_TARGET_SERVICE_IP`: 设置目标服务IP（默认: "127.0.0.1"）
- `MLFLOW_TARGET_SERVICE_PORT`: 设置目标服务端口（默认: "5000"）
- `WEDATA_MLFLOW_HEADER_PLUGIN_DEBUG`: 开启debug日志输出（默认关闭；可设置为 `1/true/on`）

### 配置示例

```bash
# 设置环境变量
export MLFLOW_TARGET_SERVICE_IP="192.168.1.100"
export MLFLOW_TARGET_SERVICE_PORT="8080"
export WEDATA_MLFLOW_HEADER_PLUGIN_DEBUG="1"

# 运行你的MLflow代码
python your_mlflow_script.py
```

或者在Python代码中设置：

```python
import os
os.environ["MLFLOW_TARGET_SERVICE_IP"] = "192.168.1.100"
os.environ["MLFLOW_TARGET_SERVICE_PORT"] = "8080"
os.environ["WEDATA_MLFLOW_HEADER_PLUGIN_DEBUG"] = "1"

import mlflow

# 现在所有MLflow请求都会包含这些header
mlflow.set_tracking_uri("http://your-mlflow-server:5000")
mlflow.start_run()
# ... your MLflow code ...
mlflow.end_run()
```

## 使用示例

安装插件后，无需额外代码，MLflow会自动使用此插件：

```python
import mlflow

# 插件会自动添加header到所有请求
mlflow.set_tracking_uri("http://your-mlflow-server:5000")

with mlflow.start_run():
    mlflow.log_param("param1", 5)
    mlflow.log_metric("metric1", 0.85)
```

## 验证插件

你可以通过以下方式验证插件是否正常工作：

```python
import mlflow
from mlflow.tracking.request_header.registry import resolve_request_headers

# 检查注册的header providers
headers = resolve_request_headers()
print("Request Headers:", headers)
```

## Debug模式说明

当设置 `WEDATA_MLFLOW_HEADER_PLUGIN_DEBUG=1`（或 `true/on`）时，插件会在每次 `request_headers()` 被调用时输出调试日志到 stderr，内容包括：

- 从哪些环境变量读取 header 值（以及默认值）
- 最终返回给 MLflow 的 headers（对疑似敏感字段会做基础脱敏）

## 开发

### 项目结构

```
wedata-mlflow-header-plugin/
├── setup.py                          # 安装配置
├── README.md                         # 文档
├── requirements.txt                  # 依赖
└── wedata-mlflow-header-plugin/
    ├── __init__.py                   # 包初始化
    └── plugin.py                     # 插件实现
```

### 运行测试

```bash
pip install pytest
pytest tests/
```

## 工作原理

该插件利用MLflow的插件系统，实现了 `RequestHeaderProvider` 接口。通过在 `setup.py` 中注册 `mlflow.request_header_provider` entry point，MLflow会自动发现并加载此插件。

每次MLflow发送HTTP请求时，都会调用插件的 `request_headers()` 方法，获取需要添加的header。

## 依赖

- Python >= 3.8
- mlflow >= 2.0.0

## 许可

MIT License

