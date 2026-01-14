# 超级今日热点 🔥

> 让 Claude Desktop 实时获取全网热点新闻的 MCP 服务器

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io)

## 🎯 这是什么？

**超级今日热点** 是一个 MCP 服务器，可以让你在 Claude Desktop 中用自然语言获取全网主流平台的实时热点新闻。

### 一句话体验

安装配置后，在 Claude Desktop 中输入：

```
获取微博热搜前10条
```

就能看到最新的微博热搜榜单！

## ✨ 支持的平台

| 平台 | 内容类型 | 更新频率 |
|------|----------|----------|
| 🔥 微博 | 热搜榜单 | 实时 |
| 📚 知乎 | 热门问答 | 实时 |
| 🔍 百度 | 热搜排行 | 实时 |
| 🎵 抖音 | 热门话题 | 实时 |
| 📺 B站 | 热门视频 | 实时 |
| 📰 头条 | 热点新闻 | 实时 |

## 🚀 三步开始

### 第一步：安装

```bash
cd "/Users/dengpengfei/Desktop/超级今日热点"
./install.sh
```

### 第二步：配置

编辑 Claude Desktop 配置文件：

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "python",
      "args": ["/Users/dengpengfei/Desktop/超级今日热点/server.py"]
    }
  }
}
```

### 第三步：使用

重启 Claude Desktop，然后：

```
获取所有平台的热点新闻
```

## 💡 能做什么？

### 基础功能

```
获取微博热搜
获取知乎热榜
获取B站热门视频
获取所有平台的热点
```

### 搜索功能

```
搜索包含"人工智能"的热点
在微博和知乎上搜索"科技"
```

### 分析功能

```
对比微博和知乎的热点差异
分析今天的热点趋势
生成今日热点新闻摘要
```

## 📱 使用场景

### 👤 个人用户
- 快速了解全网热点
- 发现有趣的话题
- 追踪关注的事件

### 📰 新闻工作者
- 发现新闻线索
- 追踪热点事件
- 生成新闻摘要

### 📱 内容创作者
- 寻找创作灵感
- 了解热门话题
- 把握流量密码

### 💼 市场营销
- 监测品牌热度
- 发现营销机会
- 分析竞争对手

## 📚 文档导航

| 文档 | 说明 | 推荐人群 |
|------|------|----------|
| [开始使用.md](开始使用.md) | 快速入门 | ⭐ 新手必读 |
| [配置说明.txt](配置说明.txt) | 配置步骤 | ⭐ 新手必读 |
| [EXAMPLES.md](EXAMPLES.md) | 使用示例 | ⭐ 所有用户 |
| [USAGE.md](USAGE.md) | 详细指南 | 进阶用户 |
| [README.md](README.md) | 完整说明 | 所有用户 |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | 项目结构 | 开发者 |

## 🎨 特色功能

### ⚡ 异步并发
同时获取多个平台数据，速度快

### 🔍 智能搜索
跨平台搜索关键词，一次搞定

### 📊 数据分析
AI 辅助分析热点趋势

### 🎯 自然交互
用日常语言提问，无需记命令

### 🔄 实时更新
每次请求都获取最新数据

### 🛡️ 稳定可靠
单个平台失败不影响其他平台

## 🧪 测试和演示

### 测试所有平台

```bash
python test_server.py
```

### 查看 API 演示

```bash
python demo.py
```

## ❓ 常见问题

<details>
<summary>Q: 需要什么环境？</summary>

- Python 3.10 或更高版本
- Claude Desktop 应用
- 网络连接
</details>

<details>
<summary>Q: 安装失败怎么办？</summary>

1. 检查 Python 版本：`python --version`
2. 升级 pip：`pip install --upgrade pip`
3. 重新安装：`pip install -r requirements.txt`
</details>

<details>
<summary>Q: Claude Desktop 无法连接？</summary>

1. 检查配置文件路径是否正确
2. 确保 Python 可以在终端中运行
3. 重启 Claude Desktop
4. 查看 Claude Desktop 的日志
</details>

<details>
<summary>Q: 某些平台无法获取数据？</summary>

1. 运行测试脚本：`python test_server.py`
2. 检查网络连接
3. 可能是平台 API 临时不可用
</details>

## 🔧 技术栈

- **Python 3.10+**: 主要编程语言
- **aiohttp**: 异步 HTTP 客户端
- **MCP SDK**: Model Context Protocol 实现

## 📊 项目结构

```
超级今日热点/
├── server.py              # MCP 服务器主程序
├── requirements.txt       # Python 依赖
├── test_server.py        # 测试脚本
├── demo.py              # API 演示
├── install.sh           # 安装脚本（Mac/Linux）
├── install.bat          # 安装脚本（Windows）
├── 开始使用.md          # 快速入门 ⭐
├── 配置说明.txt         # 配置步骤 ⭐
├── EXAMPLES.md         # 使用示例 ⭐
└── 其他文档...
```

## 🌟 为什么选择我们？

### vs 手动查看

| 对比项 | 超级今日热点 | 手动查看 |
|--------|-------------|----------|
| 多平台聚合 | ✅ 一次获取所有 | ❌ 需要逐个访问 |
| 关键词搜索 | ✅ 跨平台搜索 | ❌ 需要手动查找 |
| 数据分析 | ✅ AI 辅助分析 | ❌ 需要人工整理 |
| 使用便捷 | ✅ 自然语言 | ❌ 需要操作 |
| 实时更新 | ✅ 每次最新 | ⚠️ 需要刷新 |

## 🎁 使用技巧

1. **自然对话**: 用日常语言提问，不需要记住特定命令
2. **指定数量**: 可以说"前10条"、"前5个"等
3. **组合查询**: 一次请求多个平台
4. **深度分析**: 基于获取的数据继续提问
5. **格式要求**: 可以要求特定输出格式

## 📈 更新日志

### v1.0.0 (2026-01-07)

- ✅ 初始版本发布
- ✅ 支持 6 大主流平台
- ✅ 实现 Resource 和 Tool 接口
- ✅ 支持关键词搜索功能
- ✅ 异步并发获取数据
- ✅ 完整的文档体系

## 🤝 贡献

欢迎贡献！你可以：

- 🐛 报告 Bug
- 💡 提出新功能建议
- 🔧 提交代码改进
- 📝 改进文档

## 📄 许可证

[MIT License](LICENSE) - 可自由使用、修改和分发

## 💬 联系方式

- 📖 查看文档获取帮助
- 🐛 提交 Issue 报告问题
- ⭐ Star 项目表示支持

## 🎉 立即开始

```bash
# 1. 克隆或下载项目
# 2. 运行安装脚本
./install.sh

# 3. 配置 Claude Desktop
# 4. 开始使用！
```

---

**如果觉得有用，欢迎 Star ⭐ 和分享！**

Made with ❤️ by 超级今日热点团队

