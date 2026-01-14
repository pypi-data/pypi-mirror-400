# 超级今日热点 MCP 服务器

[![PyPI version](https://badge.fury.io/py/hot-news-mcp.svg)](https://badge.fury.io/py/hot-news-mcp)
[![Python Version](https://img.shields.io/pypi/pyversions/hot-news-mcp.svg)](https://pypi.org/project/hot-news-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个功能强大的 MCP (Model Context Protocol) 服务器，用于获取全网主流平台的实时新闻热点。

## ✨ 特性

- 🌐 **20+平台支持** - 覆盖社交、新闻、科技等多个领域
- 📊 **189条数据/次** - 丰富的热点内容
- 🔍 **跨平台搜索** - 一次搜索所有平台
- 📝 **简洁格式** - 标题+链接，清晰明了
- ⚡ **异步并发** - 高效获取数据
- 🔄 **实时更新** - 每次请求最新数据

## 🌐 支持的平台

### 视频社交 (2个)
- ✅ 抖音热点 (30条)
- ✅ B站热门 (30条)

### 新闻资讯 (5个)
- ✅ 今日头条 (30条)
- ✅ 澎湃新闻 (20条)
- 微博热搜
- 知乎热榜
- 百度热搜

### 科技开发 (8个)
- ✅ **CSDN** (30条) - 技术博客
- 掘金 - 技术社区
- 开源中国 - 开源社区
- SegmentFault - 技术问答
- 博客园 - 开发者博客
- InfoQ - 技术资讯
- 简书 - 创作社区
- 前端早报 - 前端技术

### 技术社区 (5个)
- ✅ GitHub (30条) - 开源项目
- ✅ V2EX (9条) - 技术社区
- ✅ 36氪 (10条) - 科技资讯
- IT之家 - 科技新闻
- 少数派 - 效率工具

## 📦 安装

```bash
pip install hot-news-mcp
```

或使用 uv（推荐）：

```bash
uv pip install hot-news-mcp
```

## 🚀 快速开始

### 1. 配置 Claude Desktop

编辑配置文件：

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

添加配置：

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "python",
      "args": ["-m", "hot_news_mcp.server"]
    }
  }
}
```

### 2. 重启 Claude Desktop

### 3. 开始使用

在 Claude Desktop 中输入：

```
获取抖音热点前5条
获取所有平台的热点
搜索包含"AI"的热点
```

## 💡 使用示例

### 获取单个平台

```
获取抖音热点
获取B站热门视频
获取CSDN热榜
获取GitHub热门项目
```

### 获取所有平台

```
获取所有平台的热点
现在有什么热点新闻？
```

### 搜索关键词

```
搜索包含"科技"的热点
搜索包含"AI"的热点
在GitHub和CSDN上搜索"Python"
```

### 分析和对比

```
对比抖音和B站的热点
分析今天的热点趋势
生成今日热点新闻摘要
```

## 🔧 开发使用

### 作为 Python 库使用

```python
import asyncio
from hot_news_mcp import HotNewsAPI

async def main():
    api = HotNewsAPI()
    
    # 获取抖音热点
    douyin_hot = await api.get_douyin_hot()
    for item in douyin_hot[:5]:
        print(f"{item['rank']}. {item['title']}")
        print(f"   {item['url']}")
    
    # 获取所有平台
    all_hot = await api.get_all_hot()
    print(f"共获取 {sum(len(v) for v in all_hot.values())} 条数据")
    
    await api.close()

asyncio.run(main())
```

### 运行测试

```bash
# 测试所有平台
python -m hot_news_mcp.test_server

# 或使用命令
hot-news-test
```

## 📊 数据格式

所有平台返回统一格式：

```json
{
  "title": "热点标题",
  "url": "链接地址",
  "platform": "平台名称",
  "rank": 排名
}
```

## 🎯 使用场景

- 📰 **新闻工作者** - 发现新闻线索
- 📱 **内容创作者** - 寻找创作灵感
- 💼 **市场营销** - 监测品牌热度
- 🎓 **研究学者** - 数据分析研究
- 👤 **个人用户** - 了解全网热点

## 📈 版本历史

### v3.0.0 (2026-01-07)
- ✅ 新增 CSDN 平台支持
- ✅ 扩展到 20 个平台
- ✅ 总数据量达到 189 条
- ✅ 新增 7 个科技平台接口

### v2.0.0
- ✅ 优化返回格式为简洁列表
- ✅ 扩展到 13 个平台
- ✅ 增强跨平台搜索功能

### v1.0.0
- ✅ 初始版本发布
- ✅ 支持 6 大主流平台

## 🔗 链接

- 📖 [完整文档](https://github.com/yourusername/hot-news-mcp)
- 🐛 [问题反馈](https://github.com/yourusername/hot-news-mcp/issues)
- 💬 [讨论区](https://github.com/yourusername/hot-news-mcp/discussions)

## 📄 许可证

[MIT License](https://opensource.org/licenses/MIT)

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

---

**如果觉得有用，欢迎 Star ⭐ 支持！**

