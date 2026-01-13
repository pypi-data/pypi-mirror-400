# GMICLOUD-IEOPS Python SDK

> 用于构建可扩展 AI 模型推理服务的统一框架

**[English](README_EN.md)** | 中文

## 目录

- [概览](#概览)
- [安装](#安装)
- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [配置管理](#配置管理)
- [NFS 存储](#nfs-存储)
- [API 参考](#api-参考)
- [示例](#示例)
- [详细文档](#详细文档)

---

## 概览

GMICLOUD-IEOPS Python SDK 提供构建推理服务的统一框架：

- **统一服务器基础设施**: 基于 FastAPI 的服务器，支持自动路由注册
- **灵活路由**: 支持 REST API、SSE 流式和 WebSocket
- **Handler 自动检测**: 自动处理同步/异步函数和生成器
- **配置管理**: 集中式环境变量管理，支持类型安全
- **服务注册**: 自动注册到 IEOPS 代理进行负载均衡

### 架构

```
┌─────────────────────────────────────────────────────────────────┐
│  Worker 应用                                                      │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐ │
│  │    Handler    │────▶│    Server     │────▶│   FastAPI     │ │
│  │ (你的逻辑)    │     │ (RouterDef)   │     │   Application │ │
│  └───────────────┘     └───────────────┘     └───────────────┘ │
│                                                      │          │
│                                                      ▼          │
│                                              ┌───────────────┐  │
│                                              │   Uvicorn     │  │
│                                              │   (TCP/Unix)  │  │
│                                              └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  IEOPS Proxy (负载均衡器)                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 安装

### 从 PyPI (推荐)

```bash
pip install gmi-ieops
```

### 从源码 (开发)

```bash
cd sdk
pip install -e .
```

### 依赖

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic

---

## 快速开始

### 1. 创建 Handler

```python
from typing import Dict, Any, AsyncGenerator

class MyHandler:
    """你的推理模型 Handler"""
    
    async def chat_stream(self, query: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """异步生成器用于流式输出"""
        messages = query.get("messages", [])
        response = f"Hello! You said: {messages[-1]['content'] if messages else 'nothing'}"
        
        for char in response:
            yield {
                "results": [{"content": char, "role": "assistant"}],
                "stopped": False,
            }
        
        yield {"stopped": True, "stop_reasons": ["end"]}
    
    def chat_complete(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """同步函数用于单次响应"""
        return {"message": "Hello from sync handler!"}
```

### 2. 创建 Server

```python
from gmi_ieops.handler import Handler, Server, RouterDef, RouterKind
from gmi_ieops.config import env

def main():
    handler = MyHandler()
    
    server = Server(
        routers={
            "chat": [
                RouterDef(path="stream", handler=handler.chat_stream, kind=RouterKind.SSE),
                RouterDef(path="complete", handler=handler.chat_complete, kind=RouterKind.API),
            ],
        },
        app_name=env.app.name,
    )
    
    Handler(server=server).serve()

if __name__ == "__main__":
    main()
```

### 3. 运行 Server

```bash
# TCP 模式
MODEL_SERVER_HOST=0.0.0.0 MODEL_SERVER_PORT=8080 MODEL_SERVER_SOCKET="" python server.py

# Unix socket 模式 (默认)
python server.py
```

---

## 核心概念

### RouterDef

路由定义，包含路径、处理函数和类型：

```python
from gmi_ieops.handler import RouterDef, RouterKind, HTTPMethod

RouterDef(
    path="chat",                    # 路由路径 (不含前缀)
    handler=model.chat,             # 处理函数
    kind=RouterKind.SSE,            # 路由类型: API, SSE, 或 WS
    method=HTTPMethod.POST,         # HTTP 方法 (默认: POST)
    summary="Chat endpoint",        # OpenAPI 描述
    timeout=300,                    # 请求超时 (覆盖全局配置)
)
```

### RouterKind

| Kind | 说明 | 用途 |
|------|------|------|
| `RouterKind.API` | REST API，返回 JSON | 单次响应端点 |
| `RouterKind.SSE` | Server-Sent Events | 流式文本生成 |
| `RouterKind.WS` | WebSocket | 双向通信 |

### Handler 类型

SDK 自动检测 Handler 类型：

| Handler 类型 | 签名 | 行为 |
|-------------|------|------|
| 异步生成器 | `async def handler(query) -> AsyncGenerator` | 流式输出 |
| 同步生成器 | `def handler(query) -> Generator` | 线程池流式输出 |
| 异步函数 | `async def handler(query) -> Any` | 异步单次响应 |
| 同步函数 | `def handler(query) -> Any` | 线程池单次响应 |

### Server

`Server` 类管理 FastAPI 应用：

```python
server = Server(
    routers={...},                  # 路由定义
    router_config=RouterConfig(     # 全局路由配置
        timeout=600,
        sse_headers={...},
    ),
    prefix="/v1",                   # 路由前缀
    on_startup=startup_callback,    # 启动钩子
    on_shutdown=shutdown_callback,  # 关闭钩子
    enable_cors=True,               # 启用 CORS
    app_name="my-service",          # 应用名称
)
```

---

## 配置管理

### 环境变量

SDK 使用集中式环境变量管理器。通过 `env` 对象访问：

```python
from gmi_ieops.config import env

# 应用配置
env.app.name              # APP_NAME (默认: "ieops")

# 服务器配置
env.server.host           # MODEL_SERVER_HOST (默认: "127.0.0.1")
env.server.port           # MODEL_SERVER_PORT (默认: 8001)
env.server.socket         # MODEL_SERVER_SOCKET (默认: "")

# 模型配置
env.model.path            # MODEL_PATH (默认: "")
env.model.name            # MODEL_NAME (默认: "model")
env.model.timeout         # MODEL_TIMEOUT (默认: 600)
env.model.concurrency     # MODEL_THREAD_CONCURRENCY (默认: 8)

# 设备配置
env.device.cuda_visible   # CUDA_VISIBLE_DEVICES (默认: "0")
env.device.device         # DEVICE (默认: "auto")
env.device.torch_dtype    # TORCH_DTYPE (默认: "float16")

# 存储配置
env.storage.nfs_server        # IEOPS_NFS_SERVER (默认: "")
env.storage.pid               # IEOPS_STORAGE_PID (默认: "u-00000000")
env.storage.fs_name           # IEOPS_STORAGE_FS_NAME (默认: "jfs-dev")
env.storage.oid               # IEOPS_STORAGE_OID (默认: "gmicloud.ieops")
env.storage.uid               # IEOPS_STORAGE_UID (默认: "gmicloud.ieops")
env.storage.write_chunk_size  # IEOPS_NFS_WRITE_CHUNK_SIZE (默认: 524288, 即 512KB)
env.storage.read_chunk_size   # IEOPS_NFS_READ_CHUNK_SIZE (默认: 524288, 即 512KB)
env.storage.timeout           # IEOPS_NFS_TIMEOUT (默认: 30000, 即 30 秒)
```

### Socket vs TCP 模式

```bash
# Unix Socket 模式 (默认，自动生成 socket 路径)
python server.py

# Unix Socket 模式 (自定义路径)
MODEL_SERVER_SOCKET=/var/run/myapp.sock python server.py

# TCP 模式 (设置 socket 为空字符串)
MODEL_SERVER_SOCKET="" MODEL_SERVER_HOST=0.0.0.0 MODEL_SERVER_PORT=8080 python server.py
```

### 自定义环境变量

```python
from gmi_ieops.config import env

# 获取字符串
value = env.get("MY_CUSTOM_VAR", "default")

# 带类型转换
value_int = env.get_int("MY_INT_VAR", 10)
value_bool = env.get_bool("MY_BOOL_VAR", False)
value_float = env.get_float("MY_FLOAT_VAR", 0.5)
value_list = env.get_list("MY_LIST_VAR", ["a", "b"])
```

---

## NFS 存储

SDK 提供透明的 NFS 分布式存储访问，使用 `gmifs://` 协议前缀将文件写入 NFS。

### 基本用法

```python
# 设置环境变量启用 NFS
# IEOPS_NFS_SERVER=10.0.0.1:32049

# 导入 handler 模块时会自动启用 NFS（无需手动导入 storage）
from gmi_ieops.handler import Handler, Server

# 使用 gmifs:// 前缀写入 NFS
with open("gmifs://output/image.png", "wb") as f:
    f.write(image_data)

# 不带前缀的路径仍然访问本地文件系统
with open("/data/models/model.bin", "rb") as f:  # 本地文件
    data = f.read()
```

> **注意**: 如果 `IEOPS_NFS_SERVER` 设置了但 libnfs 未安装，使用 `gmifs://` 路径时会得到明确的错误提示。

### 工作原理

- `gmifs://path` → NFS: `/{pid}/{fs_name}/{oid}/{uid}/path`
- 其他路径 → 本地文件系统（不受影响）

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `IEOPS_NFS_SERVER` | "" | NFS 服务器地址 (如 `10.0.0.1:32049`) |
| `IEOPS_STORAGE_PID` | "u-00000000" | 存储 PID |
| `IEOPS_STORAGE_FS_NAME` | "jfs-dev" | 文件系统名称 |
| `IEOPS_STORAGE_OID` | "gmicloud.ieops" | 组织 ID |
| `IEOPS_STORAGE_UID` | "gmicloud.ieops" | 用户 ID |
| `IEOPS_NFS_WRITE_CHUNK_SIZE` | 524288 | 写入块大小 (字节，最大 1MB) |
| `IEOPS_NFS_READ_CHUNK_SIZE` | 524288 | 读取块大小 (字节，最大 1MB) |
| `IEOPS_NFS_TIMEOUT` | 30000 | NFS 超时时间 (毫秒) |

> **注意**: Linux NFS 内核单次读写块大小上限为 **1MB**，请勿将块大小设置超过此限制。

### 高级用法

```python
from gmi_ieops.storage import FileSystem

# 直接使用 FileSystem API
fs = FileSystem(server="10.0.0.1", port=32049)

# 创建目录
fs.mkdir("data/images", parents=True, exist_ok=True)

# 读写文件
with fs.open("data/result.json", "w") as f:
    f.write('{"status": "ok"}')

# 列出目录
for name in fs.listdir("data"):
    print(name)
```

---

## API 参考

### gmi_ieops.handler

| 类/函数 | 说明 |
|---------|------|
| `Server` | FastAPI 服务器，带路由管理 |
| `Handler` | 服务生命周期管理器 |
| `RouterDef` | 路由定义数据类 |
| `RouterConfig` | 全局路由配置 |
| `RouterKind` | 路由类型枚举 (API, SSE, WS) |
| `HTTPMethod` | HTTP 方法枚举 |
| `generate_trace_id()` | 生成唯一跟踪 ID |
| `format_error_response()` | 创建统一错误响应 |

### gmi_ieops.config

| 类/函数 | 说明 |
|---------|------|
| `env` | 全局环境变量实例 |
| `Env` | 环境变量管理器类 |
| `EnvVar` | 环境变量描述符 |
| `EnvGroup` | 环境变量分组基类 |
| `AppEnv` | 应用环境变量组 |
| `LogEnv` | 日志环境变量组 |
| `ServerEnv` | 服务器环境变量组 |
| `ModelEnv` | 模型环境变量组 |
| `DeviceEnv` | 设备环境变量组 |
| `ApiEnv` | API 环境变量组 |
| `StorageEnv` | 存储环境变量组 |
| `RegisterEnv` | 注册环境变量组 |

### gmi_ieops.utils

| 类/函数 | 说明 |
|---------|------|
| `log` | 日志工具 |
| `randstr()`, `arandstr()` | 随机字符串生成器 |
| `randint()`, `arandint()` | 随机整数生成器 |
| `SubprocessManager` | 子进程生命周期管理器 |

### gmi_ieops.storage

| 类/函数 | 说明 |
|---------|------|
| `FileSystem` | 用户隔离文件系统 |
| `GMIFS_PROTOCOL` | gmifs:// 协议常量 |
| `enable_nfs_intercept()` | 启用 NFS 拦截 (自动调用) |
| `disable_nfs_intercept()` | 禁用 NFS 拦截 |

---

## 示例

### OpenAI 兼容聊天 API

```python
from gmi_ieops.handler import Handler, Server, RouterDef, RouterKind, HTTPMethod
from gmi_ieops.config import env

class ChatHandler:
    async def chat_completions(self, query):
        """OpenAI 兼容聊天补全"""
        messages = query.get("messages", [])
        # 你的推理逻辑
        return {
            "id": "chatcmpl-xxx",
            "object": "chat.completion",
            "choices": [{"message": {"role": "assistant", "content": "Hello!"}}],
        }
    
    async def chat_completions_stream(self, query):
        """流式聊天补全"""
        async for token in self.generate_tokens(query):
            yield {
                "id": "chatcmpl-xxx",
                "object": "chat.completion.chunk",
                "choices": [{"delta": {"content": token}}],
            }
    
    async def list_models(self, query):
        """列出可用模型"""
        return {
            "object": "list",
            "data": [{"id": env.model.name, "object": "model"}],
        }

def main():
    handler = ChatHandler()
    
    server = Server(
        routers={
            "chat/completions": [
                RouterDef(path="", handler=handler.chat_completions, kind=RouterKind.API),
                RouterDef(path="stream", handler=handler.chat_completions_stream, kind=RouterKind.SSE),
            ],
            "models": [
                RouterDef(path="", handler=handler.list_models, kind=RouterKind.API, method=HTTPMethod.GET),
            ],
        },
        prefix="/v1",
        app_name=env.app.name,
    )
    
    Handler(server=server).serve()
```

### 图像生成 API

```python
class ImageHandler:
    async def txt2img(self, query):
        """文生图"""
        prompt = query.get("prompt", "")
        # 你的扩散逻辑
        return {"images": [{"base64": "..."}]}
    
    async def txt2img_stream(self, query):
        """流式进度更新"""
        for progress in range(0, 101, 10):
            yield {"progress": progress, "status": "generating"}
        yield {"progress": 100, "status": "complete", "images": [...]}

server = Server(
    routers={
        "images": [
            RouterDef(path="generate", handler=handler.txt2img, kind=RouterKind.API),
            RouterDef(path="generate/stream", handler=handler.txt2img_stream, kind=RouterKind.SSE),
        ],
    },
)
```

---

## 错误处理

SDK 提供统一错误处理：

```python
from gmi_ieops.handler import format_error_response
from fastapi import HTTPException

# 在你的 handler 中
async def my_handler(query):
    if not query.get("messages"):
        raise HTTPException(status_code=400, detail="Messages required")
    
    try:
        result = await inference(query)
        return result
    except Exception as e:
        # 会被全局异常处理器捕获
        raise

# 错误响应格式:
# {
#     "message": "错误描述",
#     "type": "error_type"
# }
```

---

## 最佳实践

### 1. Handler 设计

```python
# ✅ 好: 无状态 handler，配置来自构造函数
class Handler:
    def __init__(self, model_path: str = env.model.path):
        self.model = load_model(model_path)

# ❌ 坏: 全局状态
MODEL = None
def handler(query):
    global MODEL
    if MODEL is None:
        MODEL = load_model()
```

### 2. 流式输出

```python
# ✅ 好: 产出增量结果
async def stream_handler(query):
    async for chunk in generate():
        yield {"content": chunk, "stopped": False}
    yield {"stopped": True}

# ❌ 坏: 收集所有再产出
async def bad_stream(query):
    results = []
    async for chunk in generate():
        results.append(chunk)
    yield {"content": "".join(results)}
```

### 3. 错误处理

```python
# ✅ 好: 明确的异常
from fastapi import HTTPException

if not valid_input(query):
    raise HTTPException(status_code=400, detail="Invalid input")

# ✅ 好: 日志用于调试
from gmi_ieops.utils import log

try:
    result = inference(query)
except Exception as e:
    log.get_logger(trace_id=query.get("trace_id")).error(f"Inference error: {e}")
    raise
```

---

## 详细文档

| 文档 | 说明 |
|------|------|
| [NFS 存储指南](docs/nfs-client-guide.md) | 分布式文件系统访问、缓存、锁机制 |
| [Worker 示例](../workers/) | 参考实现 |

