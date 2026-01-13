# MCP AI Jerry

智能交互反馈 MCP 服务器，提供 Web UI 和桌面应用双重界面支持。

## 功能特点

- 🖥️ **双重界面**：桌面应用程序 + Web UI
- 📝 **智能工作流程**：提示词管理、自动定时提交、会话追踪
- 🎨 **现代化体验**：响应式设计、音效通知、多语言支持
- 🖼️ **图片支持**：拖拽上传、剪贴板粘贴
- 🔐 **授权系统**：月卡/年卡激活，设备绑定管理

## 快速开始

### 安装

```bash
pip install uv
```

### 配置 MCP

#### Cursor / Claude Desktop

在你的 AI 助手（如 Claude Desktop、Cursor 等）中添加 MCP 配置：

```json
{
  "mcpServers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": ["mcp-ai-jerry@latest"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

#### VS Code

在 VS Code 中，按 `Cmd+Shift+P`（Mac）或 `Ctrl+Shift+P`（Windows/Linux），输入 `MCP`???为 `100000000`，以获得更好的体验。

### 桌面应用模式（可选）

如需使用桌面应用模式而非浏览器，添加环境变量：

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

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| MCP_DEBUG | 调试模式 | false |
| MCP_WEB_HOST | Web UI 主机绑定 | 127.0.0.1 |
| MCP_WEB_PORT | Web UI 端口 | 8765 |
| MCP_DESKTOP_MODE | 桌面应用程序模式 | false |
| MCP_LANGUAGE | 界面语言 (zh-CN/zh-TW/en) | 自动检测 |

## 激活授权

首次使用时需要激活授权。请访问我们的淘宝店铺购买激活码。

- 一个激活码支持 **2 台设备**
- 每 30 天可免费解绑 1 次

## 文档

- [使用指南](docs/使用指南.md) - 详细的安装和使用教程

## 许可证

MIT License
