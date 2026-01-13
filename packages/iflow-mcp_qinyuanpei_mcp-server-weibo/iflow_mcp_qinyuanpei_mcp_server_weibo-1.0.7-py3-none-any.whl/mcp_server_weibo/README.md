# Weibo MCP Server

这是一个基于 [Model Context Protocol](https://modelcontextprotocol.io) 的服务器，用于抓取微博用户信息、动态和搜索功能。该服务器可以帮助获取微博用户的详细信息、动态内容以及进行用户搜索。

## 安装

从源代码安装：

```json
{
    "mcpServers": {
        "weibo": {
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/qinyuanpei/mcp-server-weibo.git",
                "mcp-server-weibo"
            ]
        }
    }
}
```
从包管理器安装：

```json
{
    "mcpServers": {
        "weibo": {
            "command": "uvx",
            "args": ["mcp-server-weibo"],
        }
    }
}
```

## 组件

### 工具

- `search_weibo_users`: 用于搜索微博用户
    - **输入:** `keyword`: 搜索关键词
    - **输出:** `WeiboUsers`: 包含用户基本信息的 Pydantic 模型列表

- `extract_weibo_profile`: 获取用户详细信息
    - **输入:** `user_id`: 用户ID
    - **输出:** `WeiboProfile`: 包含用户详细信息的 Pydantic 模型

- `extract_weibo_feeds`: 获取用户动态
    - **输入:** `user_id`: 用户ID, `limit`: 获取数量限制
    - **输出:** `WeiboFeeds`: 包含用户动态信息的 Pydantic 模型列表

### 资源   

无

### 提示

无

## 依赖要求

- Python >= 3.8
- httpx >= 0.24.0
- pydantic >= 2.0.0
- fastmcp >= 0.1.0

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 免责声明

本项目与微博官方无关，仅用于学习和研究目的。
