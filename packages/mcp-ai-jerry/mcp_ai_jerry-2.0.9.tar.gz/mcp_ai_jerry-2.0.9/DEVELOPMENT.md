# 开发调试指南

> ⚠️ **内部文档 - 仅供开发者使用**

---

## 1. 本地开发环境设置

```bash
# 克隆项目
git clone <repo-url>
cd mcp-ai-jerry

# 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -e ".[dev]"
# 或使用 uv
uv sync
```

## 2. 启动 MCP 服务器（开发模式）

### 方式一：直接运行 Python 模块

```bash
# 设置调试模式
export MCP_DEBUG=true

# 运行 MCP 服务器
python -m mcp_ai_jerry
```

### 方式二：使用 uvx 本地开发

```bash
# 使用可编辑模式运行
uvx --no-cache --with-editable . mcp-ai-jerry
```

### 方式三：模拟 MCP 调用测试

```bash
# Web UI 测试模式
uvx --no-cache --with-editable . mcp-ai-jerry test --web

# 桌面应用测试模式  
uvx --no-cache --with-editable . mcp-ai-jerry test --desktop
```

### 方式四：启用桌面应用模式

在 MCP 配置中通过环境变量启用桌面应用模式：

```json
{
  "servers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": ["mcp-ai-jerry"],
      "timeout": 600,
      "env": {
        "MCP_DESKTOP_MODE": "true"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

> ⚠️ 注意：`--desktop` 是 `test` 子命令的参数，不能直接用于 MCP 配置。要在 MCP 中启用桌面模式，请使用 `MCP_DESKTOP_MODE` 环境变量。

## 3. 单独启动 Web UI（不通过 MCP）

如果只想调试 Web UI，可以直接运行 web 模块：

```python
# test_web.py
import asyncio
import os

# 设置调试环境变量
os.environ["MCP_DEBUG"] = "true"

from mcp_ai_jerry.web.main import launch_web_feedback_ui, stop_web_ui

async def main():
    project_dir = os.getcwd()
    summary = """# 测试摘要

这是一个 **Markdown** 格式的摘要。

- 功能1
- 功能2
"""
    
    try:
        print("启动 Web UI...")
        result = await launch_web_feedback_ui(project_dir, summary, timeout=600)
        print(f"收到反馈: {result}")
    except KeyboardInterrupt:
        print("用户取消")
    finally:
        stop_web_ui()

if __name__ == "__main__":
    asyncio.run(main())
```

运行：
```bash
python test_web.py
# Web UI 将在 http://127.0.0.1:8765 启动
```

## 4. 桌面应用开发

### 构建 Tauri 桌面应用

```bash
# 进入 Tauri 项目目录
cd src-tauri

# 安装 Rust 依赖
cargo build

# 开发模式运行（需要先启动 Web 后端）
cargo run
```

### 桌面应用与 Web 后端联调

```bash
# 终端 1: 启动 Web 后端
export MCP_DESKTOP_MODE=true
python -c "
import asyncio
from mcp_ai_jerry.web.main import get_web_ui_manager

manager = get_web_ui_manager()
manager.start_server()
manager.create_session('.', '桌面应用测试')

print(f'Web 后端运行中: {manager.get_server_url()}')
print('按 Ctrl+C 停止...')

try:
    while True:
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))
except KeyboardInterrupt:
    manager.stop()
"

# 终端 2: 启动桌面应用
cd src-tauri
cargo run
```

## 5. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_web_ui.py -v

# 运行集成测试
pytest tests/integration/ -v

# 带覆盖率报告
pytest --cov=mcp_ai_jerry --cov-report=html
```

## 6. 常用调试命令

```bash
# 查看 MCP 服务器日志
MCP_DEBUG=true python -m mcp_ai_jerry 2>&1 | tee mcp.log

# 检查端口占用
lsof -i :8765  # macOS/Linux
netstat -ano | findstr :8765  # Windows

# 清理缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## 7. 项目结构

```
mcp-ai-jerry/
├── src/mcp_ai_jerry/       # 主要源代码
│   ├── auth/               # 授权模块
│   ├── desktop_app/        # 桌面应用模块
│   ├── utils/              # 工具模块
│   └── web/                # Web UI 模块
│       ├── routes/         # API 路由
│       ├── static/         # 静态文件
│       └── templates/      # 模板文件
├── src-tauri/              # Tauri 桌面应用
├── server/                 # 授权服务器
└── tests/                  # 测试文件
```

## 8. 发布流程

```bash
# 更新版本号（在 pyproject.toml, __init__.py, tauri.conf.json）

# 构建
uv build

# 发布到 PyPI
uvx twine upload dist/* -u __token__ -p <YOUR_PYPI_TOKEN>

# 推送代码
git push origin dev
```
