# 使用指南

## 快速开始

### 1. 安装依赖

```bash
cd "/Users/dengpengfei/Desktop/超级今日热点"

# 使用 pip
pip install -r requirements.txt

# 或使用 uv（推荐，更快）
uv pip install -r requirements.txt
```

### 2. 测试服务器

在配置到 Claude Desktop 之前，建议先测试一下：

```bash
# 运行测试脚本
python test_server.py
```

这将测试所有平台的API是否正常工作。

### 3. 配置 Claude Desktop

#### MacOS 配置路径

```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Windows 配置路径

```bash
%APPDATA%\Claude\claude_desktop_config.json
```

#### 配置内容

打开配置文件并添加：

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "python",
      "args": [
        "/Users/dengpengfei/Desktop/超级今日热点/server.py"
      ]
    }
  }
}
```

**注意**：如果你已经有其他 MCP 服务器配置，只需要添加 "hot-news" 部分即可。

#### 使用 uv 的配置（推荐）

如果你安装了 uv：

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/dengpengfei/Desktop/超级今日热点",
        "run",
        "server.py"
      ]
    }
  }
}
```

### 4. 重启 Claude Desktop

保存配置文件后，重启 Claude Desktop 使配置生效。

## 使用示例

配置完成后，你可以在 Claude Desktop 中这样使用：

### 基础使用

#### 1. 获取单个平台热点

```
请获取微博热搜前10条
```

```
获取知乎热榜
```

```
查看B站现在有什么热门视频
```

#### 2. 获取所有平台热点

```
获取所有平台的热点新闻
```

```
现在全网都在关注什么？
```

#### 3. 搜索关键词

```
搜索包含"人工智能"的热点
```

```
在微博和知乎上搜索"春节"相关的热点
```

### 高级使用

#### 4. 分析和对比

```
对比微博和知乎上关于"AI"的热点话题有什么不同
```

```
分析今天全网热点的主要话题类型
```

#### 5. 追踪热点

```
获取微博、知乎、B站的科技类热点
```

```
帮我找出今天最热的娱乐新闻
```

#### 6. 生成报告

```
基于全网热点，生成今日热点新闻摘要
```

```
分析今天的热点趋势，哪些话题最受关注
```

## API 接口说明

### Resources（资源）

可以直接访问以下资源：

| URI | 说明 |
|-----|------|
| `hot://weibo` | 微博热搜 |
| `hot://zhihu` | 知乎热榜 |
| `hot://baidu` | 百度热搜 |
| `hot://douyin` | 抖音热点 |
| `hot://bilibili` | B站热门 |
| `hot://toutiao` | 今日头条 |
| `hot://all` | 所有平台 |

### Tools（工具）

#### 1. get_hot_news

获取指定平台的热点新闻。

**参数：**
- `platform` (必填): 平台名称
  - 可选值: `weibo`, `zhihu`, `baidu`, `douyin`, `bilibili`, `toutiao`, `all`
- `limit` (可选): 返回数量，默认30

**示例：**
```json
{
  "platform": "weibo",
  "limit": 10
}
```

#### 2. search_hot_news

在所有平台中搜索包含关键词的热点。

**参数：**
- `keyword` (必填): 搜索关键词
- `platforms` (可选): 要搜索的平台列表
  - 默认搜索所有平台
  - 可选值: `["weibo", "zhihu", "baidu", "douyin", "bilibili", "toutiao"]`

**示例：**
```json
{
  "keyword": "科技",
  "platforms": ["weibo", "zhihu"]
}
```

## 数据格式说明

### 微博热搜数据格式

```json
{
  "rank": 1,
  "title": "热搜标题",
  "hot_value": 1234567,
  "url": "https://...",
  "category": "分类",
  "label": "标签"
}
```

### 知乎热榜数据格式

```json
{
  "rank": 1,
  "title": "问题标题",
  "excerpt": "摘要",
  "hot_value": "100万热度",
  "url": "https://...",
  "type": "类型"
}
```

### 百度热搜数据格式

```json
{
  "rank": 1,
  "title": "热搜标题",
  "hot_value": 1234567,
  "url": "https://...",
  "desc": "描述",
  "img": "图片URL"
}
```

### 抖音热点数据格式

```json
{
  "rank": 1,
  "title": "话题标题",
  "hot_value": 1234567,
  "label": "标签",
  "sentence_tag": "句子标签"
}
```

### B站热门数据格式

```json
{
  "rank": 1,
  "title": "视频标题",
  "author": "UP主",
  "play": 1000000,
  "like": 50000,
  "url": "https://...",
  "desc": "视频描述"
}
```

### 今日头条数据格式

```json
{
  "rank": 1,
  "title": "新闻标题",
  "hot_value": 1234567,
  "url": "https://...",
  "img": "图片URL"
}
```

## 故障排查

### 1. 服务器无法启动

**问题**：Claude Desktop 无法连接到 MCP 服务器

**解决方案**：
- 检查 Python 是否正确安装：`python --version`
- 检查依赖是否安装：`pip list | grep mcp`
- 查看 Claude Desktop 的日志文件

### 2. 某个平台无法获取数据

**问题**：某个特定平台返回空数据或错误

**解决方案**：
- 运行测试脚本查看详细错误：`python test_server.py`
- 检查网络连接
- 可能是平台API变化，需要更新代码

### 3. 数据获取较慢

**问题**：获取数据需要较长时间

**解决方案**：
- 这是正常现象，因为需要访问多个平台
- 使用单个平台查询而不是 `all` 会更快
- 确保网络连接稳定

### 4. Python 版本问题

**问题**：提示 Python 版本不兼容

**解决方案**：
- 确保使用 Python 3.10 或更高版本
- 升级 Python：使用 pyenv 或从官网下载最新版本

## 高级配置

### 使用虚拟环境

推荐使用虚拟环境来隔离依赖：

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # MacOS/Linux
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

然后在 Claude Desktop 配置中使用虚拟环境的 Python：

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "/Users/dengpengfei/Desktop/超级今日热点/.venv/bin/python",
      "args": [
        "/Users/dengpengfei/Desktop/超级今日热点/server.py"
      ]
    }
  }
}
```

### 使用 uv（推荐）

uv 是一个更快的 Python 包管理器：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 使用 uv 安装依赖
uv pip install -r requirements.txt

# 在配置中使用 uv
```

配置文件：

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/dengpengfei/Desktop/超级今日热点",
        "run",
        "server.py"
      ]
    }
  }
}
```

## 开发和贡献

### 添加新平台

如果你想添加新的平台支持：

1. 在 `HotNewsAPI` 类中添加新方法
2. 在 `list_resources()` 中添加新资源
3. 在 `read_resource()` 中添加处理逻辑
4. 在 `call_tool()` 中添加平台支持
5. 更新 README 文档

### 测试

运行测试脚本：

```bash
python test_server.py
```

### 日志

服务器会输出日志到标准输出，你可以在 Claude Desktop 的日志中查看。

## 常见问题 (FAQ)

**Q: 数据更新频率如何？**
A: 每次请求都会实时获取最新数据。

**Q: 是否需要API密钥？**
A: 不需要，使用公开API接口。

**Q: 支持哪些操作系统？**
A: MacOS、Windows、Linux 都支持。

**Q: 可以自定义获取数量吗？**
A: 可以，使用 `limit` 参数。

**Q: 数据格式可以导出吗？**
A: 返回的是 JSON 格式，可以要求 Claude 转换为其他格式。

**Q: 如何更新服务器？**
A: 只需替换 `server.py` 文件并重启 Claude Desktop。

## 技术支持

如遇到问题：
1. 查看本文档的"故障排查"部分
2. 运行 `python test_server.py` 查看详细错误
3. 在 GitHub 项目页面提交 Issue
4. 查看 Claude Desktop 日志文件

## 许可证

MIT License - 可自由使用、修改和分发。

