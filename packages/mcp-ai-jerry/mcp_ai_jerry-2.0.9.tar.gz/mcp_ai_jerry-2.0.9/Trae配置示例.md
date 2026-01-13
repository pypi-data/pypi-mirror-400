# Trae MCP 配置示例

## 基础配置（Web 模式）

```json
{
  "mcpServers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": [
        "mcp-ai-jerry@latest"
      ],
      "timeout": 600,
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

## 桌面应用模式配置

```json
{
  "mcpServers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": [
        "mcp-ai-jerry@latest"
      ],
      "timeout": 600,
      "env": {
        "MCP_DESKTOP_MODE": "true"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

## 自定义端口配置

```json
{
  "mcpServers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": [
        "mcp-ai-jerry@latest"
      ],
      "timeout": 600,
      "env": {
        "MCP_WEB_PORT": "8888",
        "MCP_WEB_HOST": "127.0.0.1"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

## 调试模式配置

```json
{
  "mcpServers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": [
        "mcp-ai-jerry@latest"
      ],
      "timeout": 600,
      "env": {
        "MCP_DEBUG": "true"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

## 多语言配置

### 简体中文
```json
{
  "mcpServers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": [
        "mcp-ai-jerry@latest"
      ],
      "timeout": 600,
      "env": {
        "MCP_LANGUAGE": "zh-CN"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

### 繁体中文
```json
{
  "mcpServers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": [
        "mcp-ai-jerry@latest"
      ],
      "timeout": 600,
      "env": {
        "MCP_LANGUAGE": "zh-TW"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

### 英文
```json
{
  "mcpServers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": [
        "mcp-ai-jerry@latest"
      ],
      "timeout": 600,
      "env": {
        "MCP_LANGUAGE": "en"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

## 完整配置（所有选项）

```json
{
  "mcpServers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": [
        "mcp-ai-jerry@latest"
      ],
      "timeout": 600,
      "env": {
        "MCP_DEBUG": "false",
        "MCP_WEB_HOST": "127.0.0.1",
        "MCP_WEB_PORT": "8765",
        "MCP_DESKTOP_MODE": "false",
        "MCP_LANGUAGE": "zh-CN"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `command` | 启动命令，使用 uvx | `uvx` |
| `args` | 包名称 | `["mcp-ai-jerry@latest"]` |
| `timeout` | 超时时间（秒） | `600` |
| `autoApprove` | 自动批准的工具 | `["interactive_feedback"]` |
| `MCP_DEBUG` | 是否启用调试模式 | `false` |
| `MCP_WEB_HOST` | Web 服务绑定地址 | `127.0.0.1` |
| `MCP_WEB_PORT` | Web 服务端口 | `8765` |
| `MCP_DESKTOP_MODE` | 是否使用桌面应用模式 | `false` |
| `MCP_LANGUAGE` | 界面语言 | 自动检测 |

## 推荐配置

大多数用户推荐使用以下配置之一：

### 1. 简单配置（推荐新手）
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

### 2. 桌面模式（推荐高级用户）
```json
{
  "mcpServers": {
    "mcp-ai-jerry": {
      "command": "uvx",
      "args": ["mcp-ai-jerry@latest"],
      "timeout": 600,
      "env": {
        "MCP_DESKTOP_MODE": "true"
      },
      "autoApprove": ["interactive_feedback"]
    }
  }
}
```
