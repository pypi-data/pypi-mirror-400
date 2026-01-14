# 快速开始指南 ⚡

只需 3 步，即可在 Claude Desktop 中使用全网热点新闻！

## 📋 前置要求

- ✅ Python 3.10 或更高版本
- ✅ Claude Desktop 应用

## 🚀 安装步骤

### MacOS / Linux

```bash
# 1. 进入项目目录
cd "/Users/dengpengfei/Desktop/超级今日热点"

# 2. 运行安装脚本
./install.sh

# 3. 按照提示完成安装
```

### Windows

```bash
# 1. 进入项目目录
cd "C:\Users\YourName\Desktop\超级今日热点"

# 2. 运行安装脚本
install.bat

# 3. 按照提示完成安装
```

### 手动安装

如果安装脚本无法运行，可以手动安装：

```bash
# 安装依赖
pip install -r requirements.txt

# 测试服务器
python test_server.py
```

## ⚙️ 配置 Claude Desktop

### 1. 打开配置文件

**MacOS**:
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows**:
```bash
notepad %APPDATA%\Claude\claude_desktop_config.json
```

### 2. 添加配置

复制以下内容到配置文件（如果已有其他配置，只添加 "hot-news" 部分）：

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

**注意**: 将路径替换为你的实际路径！

### 3. 重启 Claude Desktop

保存配置文件后，完全退出并重新启动 Claude Desktop。

## 🎯 开始使用

在 Claude Desktop 中尝试以下命令：

```
获取微博热搜前10条
```

```
获取所有平台的热点新闻
```

```
搜索包含"科技"的热点
```

## ✅ 验证安装

如果配置成功，你会在 Claude Desktop 的工具栏看到 MCP 服务器已连接。

你也可以询问 Claude：

```
你现在可以获取哪些平台的热点新闻？
```

## 🐛 遇到问题？

### 问题 1: 找不到 Python

**解决方案**: 安装 Python 3.10+
- MacOS: `brew install python@3.10`
- Windows: 从 [python.org](https://www.python.org) 下载安装

### 问题 2: 依赖安装失败

**解决方案**: 使用虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # MacOS/Linux
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 问题 3: Claude Desktop 无法连接

**解决方案**: 
1. 检查配置文件路径是否正确
2. 确保 Python 路径正确
3. 查看 Claude Desktop 日志
4. 重启 Claude Desktop

### 问题 4: 某些平台无法获取数据

**解决方案**: 
1. 运行测试脚本查看详情: `python test_server.py`
2. 检查网络连接
3. 可能是平台 API 临时不可用，稍后再试

## 📚 更多信息

- 📖 [完整文档](README.md)
- 📝 [详细使用指南](USAGE.md)
- 🔧 [配置示例](claude_desktop_config.json)

## 🎉 完成！

现在你可以在 Claude Desktop 中随时获取全网热点新闻了！

---

**提示**: 如果你觉得这个工具有用，欢迎分享给朋友！

