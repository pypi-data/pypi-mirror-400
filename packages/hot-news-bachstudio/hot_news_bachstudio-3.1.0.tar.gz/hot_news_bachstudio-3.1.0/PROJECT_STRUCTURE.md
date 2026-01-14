# 项目结构说明 📁

```
超级今日热点/
├── server.py                      # 主服务器文件（MCP服务器实现）
├── requirements.txt               # Python依赖列表
├── pyproject.toml                # 项目配置文件
├── test_server.py                # 测试脚本
├── install.sh                    # MacOS/Linux安装脚本
├── install.bat                   # Windows安装脚本
├── README.md                     # 项目说明文档
├── QUICKSTART.md                 # 快速开始指南
├── USAGE.md                      # 详细使用指南
├── EXAMPLES.md                   # 使用示例集合
├── PROJECT_STRUCTURE.md          # 本文件（项目结构说明）
├── LICENSE                       # MIT许可证
├── .gitignore                    # Git忽略文件配置
└── claude_desktop_config.json    # Claude Desktop配置示例
```

## 📄 文件说明

### 核心文件

#### `server.py`
- **作用**: MCP服务器的主要实现文件
- **功能**:
  - 实现MCP协议的Resource和Tool接口
  - 提供6大平台的热点新闻API
  - 支持异步并发数据获取
  - 实现关键词搜索功能
- **依赖**: aiohttp, mcp

#### `requirements.txt`
- **作用**: Python依赖包列表
- **内容**:
  - `aiohttp>=3.9.0` - 异步HTTP客户端
  - `mcp>=0.9.0` - MCP协议SDK

#### `pyproject.toml`
- **作用**: Python项目配置文件
- **内容**: 项目元数据、依赖管理、构建配置

### 测试和安装

#### `test_server.py`
- **作用**: 测试各平台API是否正常工作
- **用法**: `python test_server.py`
- **功能**:
  - 测试所有平台的数据获取
  - 显示前3条热点示例
  - 测试并发获取功能

#### `install.sh` (MacOS/Linux)
- **作用**: 自动化安装脚本
- **用法**: `./install.sh`
- **功能**:
  - 检查Python版本
  - 创建虚拟环境（可选）
  - 安装依赖
  - 运行测试
  - 显示配置说明

#### `install.bat` (Windows)
- **作用**: Windows自动化安装脚本
- **用法**: 双击运行或 `install.bat`
- **功能**: 与install.sh相同

### 文档文件

#### `README.md`
- **作用**: 项目主文档
- **内容**:
  - 项目介绍和特性
  - 支持的平台列表
  - 安装和配置说明
  - 数据格式说明
  - 更新日志

#### `QUICKSTART.md`
- **作用**: 快速开始指南
- **内容**:
  - 3步快速安装
  - 配置Claude Desktop
  - 验证安装
  - 常见问题解决

#### `USAGE.md`
- **作用**: 详细使用指南
- **内容**:
  - 完整安装步骤
  - 使用示例
  - API接口说明
  - 数据格式详解
  - 故障排查
  - 高级配置

#### `EXAMPLES.md`
- **作用**: 使用示例集合
- **内容**:
  - 25+种使用场景
  - 实际应用案例
  - 对话式查询示例
  - 最佳实践

#### `PROJECT_STRUCTURE.md`
- **作用**: 项目结构说明（本文件）
- **内容**: 文件组织和说明

### 配置文件

#### `claude_desktop_config.json`
- **作用**: Claude Desktop配置示例
- **用法**: 复制内容到Claude Desktop配置文件
- **位置**:
  - MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

#### `.gitignore`
- **作用**: Git版本控制忽略文件
- **内容**: 忽略Python缓存、虚拟环境、IDE配置等

#### `LICENSE`
- **作用**: MIT开源许可证
- **内容**: 项目使用条款

## 🔧 核心代码结构

### `server.py` 代码组织

```python
# 1. 导入和配置
import asyncio, aiohttp, logging
from mcp.server import Server

# 2. HotNewsAPI 类
class HotNewsAPI:
    - __init__()              # 初始化
    - ensure_session()        # 确保HTTP会话
    - close()                 # 关闭会话
    - get_weibo_hot()         # 获取微博热搜
    - get_zhihu_hot()         # 获取知乎热榜
    - get_baidu_hot()         # 获取百度热搜
    - get_douyin_hot()        # 获取抖音热点
    - get_bilibili_hot()      # 获取B站热门
    - get_toutiao_hot()       # 获取今日头条
    - get_all_hot()           # 获取所有平台

# 3. MCP 服务器实例
app = Server("hot-news-server")
api = HotNewsAPI()

# 4. MCP 接口实现
@app.list_resources()         # 列出资源
@app.read_resource()          # 读取资源
@app.list_tools()             # 列出工具
@app.call_tool()              # 调用工具

# 5. 主函数
async def main()              # 启动服务器
```

## 📊 数据流程

```
用户请求 (Claude Desktop)
    ↓
MCP 协议
    ↓
server.py (MCP Server)
    ↓
HotNewsAPI
    ↓
异步HTTP请求 (aiohttp)
    ↓
各平台API
    ↓
数据解析和格式化
    ↓
返回JSON结果
    ↓
Claude Desktop展示
```

## 🔌 MCP 接口说明

### Resources (资源)
- URI格式: `hot://platform`
- 支持的平台: weibo, zhihu, baidu, douyin, bilibili, toutiao, all
- 返回格式: JSON字符串

### Tools (工具)

#### 1. get_hot_news
- **输入**:
  - platform: 平台名称
  - limit: 数量限制
- **输出**: JSON格式的热点数据

#### 2. search_hot_news
- **输入**:
  - keyword: 搜索关键词
  - platforms: 平台列表（可选）
- **输出**: JSON格式的搜索结果

## 🌐 支持的平台API

| 平台 | API端点 | 数据格式 |
|------|---------|----------|
| 微博 | weibo.com/ajax/side/hotSearch | JSON |
| 知乎 | zhihu.com/api/v3/feed/topstory/hot-lists/total | JSON |
| 百度 | top.baidu.com/api/board | JSON |
| 抖音 | iesdouyin.com/web/api/v2/hotsearch/billboard/word/ | JSON |
| B站 | api.bilibili.com/x/web-interface/popular | JSON |
| 头条 | toutiao.com/hot-event/hot-board/ | JSON |

## 🛠️ 开发指南

### 添加新平台

1. 在 `HotNewsAPI` 类中添加新方法:
```python
async def get_newplatform_hot(self) -> List[Dict[str, Any]]:
    # 实现获取逻辑
    pass
```

2. 在 `list_resources()` 中添加资源:
```python
Resource(
    uri="hot://newplatform",
    name="新平台",
    mimeType="application/json",
    description="获取新平台热点"
)
```

3. 在 `read_resource()` 和 `call_tool()` 中添加处理逻辑

4. 更新文档

### 测试新功能

```bash
# 修改 test_server.py 添加新平台测试
python test_server.py
```

### 调试

```bash
# 直接运行服务器查看日志
python server.py
```

## 📦 依赖说明

### aiohttp (>=3.9.0)
- **用途**: 异步HTTP客户端
- **功能**: 
  - 并发请求多个平台API
  - 提高数据获取效率
  - 支持超时和错误处理

### mcp (>=0.9.0)
- **用途**: Model Context Protocol SDK
- **功能**:
  - 实现MCP协议
  - 提供Server、Resource、Tool等类
  - 处理与Claude Desktop的通信

## 🔒 安全性

- ✅ 只读操作，不修改任何数据
- ✅ 使用公开API，无需认证
- ✅ 不存储用户数据
- ✅ 不发送敏感信息

## 🚀 性能优化

1. **异步并发**: 使用asyncio同时请求多个平台
2. **会话复用**: 复用HTTP连接减少开销
3. **超时控制**: 10秒超时避免长时间等待
4. **错误处理**: 单个平台失败不影响其他平台

## 📈 扩展性

- ✅ 易于添加新平台
- ✅ 支持自定义数据格式
- ✅ 可配置的参数
- ✅ 模块化设计

## 🎯 最佳实践

1. **使用虚拟环境**: 隔离项目依赖
2. **定期更新**: 保持依赖包最新
3. **错误日志**: 查看日志排查问题
4. **测试先行**: 修改后运行测试
5. **文档同步**: 更新代码后更新文档

## 📞 技术支持

- 📖 查看文档: README.md, USAGE.md, EXAMPLES.md
- 🧪 运行测试: `python test_server.py`
- 🐛 提交Issue: GitHub Issues
- 💬 社区讨论: GitHub Discussions

---

**提示**: 这个项目结构设计清晰，易于维护和扩展。如有问题，请参考相关文档。

