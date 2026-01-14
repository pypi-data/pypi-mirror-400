# 🚀 UVX 安装配置指南

## 什么是 uvx？

`uvx` 是 [uv](https://github.com/astral-sh/uv) 工具的一部分，可以直接运行 PyPI 包而无需预先安装。

### 优势
- ⚡ **无需安装** - 直接运行，自动管理依赖
- 🔄 **自动更新** - 每次运行使用最新版本
- 🧹 **干净环境** - 不污染系统 Python
- ⚡ **启动快速** - uv 比 pip 快 10-100 倍

---

## 📦 安装 uv

### MacOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 使用 pip（备选）
```bash
pip install uv
```

### 验证安装
```bash
uv --version
uvx --version
```

---

## ⚙️ Claude Desktop 配置

### 配置文件位置

**MacOS**:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows**:
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 配置内容（使用 uvx）

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "uvx",
      "args": [
        "hot-news-bachstudio"
      ]
    }
  }
}
```

### 完整配置示例（多个 MCP 服务器）

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "uvx",
      "args": [
        "hot-news-bachstudio"
      ]
    },
    "other-server": {
      "command": "uvx",
      "args": [
        "other-mcp-package"
      ]
    }
  }
}
```

---

## 🔧 高级配置

### 1. 指定版本

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "uvx",
      "args": [
        "hot-news-bachstudio==3.0.0"
      ]
    }
  }
}
```

### 2. 使用预发布版本

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "uvx",
      "args": [
        "--pre",
        "hot-news-bachstudio"
      ]
    }
  }
}
```

### 3. 从 GitHub 安装（开发版）

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/BACH-AI-Tools/hot-news-bachstudio",
        "hot-news-bachstudio"
      ]
    }
  }
}
```

### 4. 使用本地路径（开发调试）

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "uvx",
      "args": [
        "--from",
        "/Users/dengpengfei/Desktop/超级今日热点",
        "hot-news-bachstudio"
      ]
    }
  }
}
```

---

## 🆚 配置方式对比

### 方式 1: 使用 uvx（推荐）✨

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "uvx",
      "args": ["hot-news-bachstudio"]
    }
  }
}
```

**优点**:
- ✅ 无需预先安装
- ✅ 自动管理依赖
- ✅ 自动使用最新版本
- ✅ 启动快速

**缺点**:
- ⚠️ 需要先安装 uv
- ⚠️ 首次运行需要下载

---

### 方式 2: 使用可执行文件

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "hot-news-bachstudio"
    }
  }
}
```

**优点**:
- ✅ 配置简单
- ✅ 直接调用

**缺点**:
- ⚠️ 需要先 pip install
- ⚠️ 需要手动更新

---

### 方式 3: 使用 Python 模块

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "python",
      "args": ["-m", "hot_news_bachstudio.server"]
    }
  }
}
```

**优点**:
- ✅ 兼容性好
- ✅ 可控性强

**缺点**:
- ⚠️ 需要先 pip install
- ⚠️ Python 路径可能不一致

---

## 📝 快速开始

### 1. 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 复制配置

**MacOS**:
```bash
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "hot-news": {
      "command": "uvx",
      "args": ["hot-news-bachstudio"]
    }
  }
}
EOF
```

**或手动编辑**:
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 3. 重启 Claude Desktop

完全退出并重新打开 Claude Desktop

### 4. 测试使用

在 Claude Desktop 中输入：
```
获取抖音热点
```

---

## 🔍 故障排查

### 问题 1: uvx 命令未找到

**错误**: `command not found: uvx`

**解决方案**:
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载 shell 配置
source ~/.zshrc  # 或 source ~/.bashrc

# 验证安装
uvx --version
```

### 问题 2: 包下载失败

**错误**: `Failed to download hot-news-bachstudio`

**解决方案**:
```bash
# 检查网络连接
ping pypi.org

# 手动测试下载
uvx hot-news-bachstudio-test

# 清理缓存
uv cache clean
```

### 问题 3: 版本不是最新

**解决方案**:
```bash
# 清理缓存
uv cache clean

# 强制重新下载
uvx --refresh hot-news-bachstudio-test
```

### 问题 4: 权限问题

**错误**: `Permission denied`

**解决方案**:
```bash
# 检查 uv 安装位置
which uvx

# 确保有执行权限
chmod +x ~/.cargo/bin/uvx
```

---

## 💡 使用技巧

### 1. 测试包是否可用

```bash
# 运行测试命令
uvx hot-news-bachstudio-test
```

### 2. 查看 uvx 缓存

```bash
# 查看缓存位置
uv cache dir

# 查看缓存大小
uv cache clean --dry-run

# 清理缓存
uv cache clean
```

### 3. 手动运行包

```bash
# 直接运行
uvx hot-news-bachstudio

# 指定版本
uvx hot-news-bachstudio==3.0.0

# 使用 --help
uvx hot-news-bachstudio --help
```

### 4. 开发模式

在开发时使用本地路径：
```json
{
  "mcpServers": {
    "hot-news-dev": {
      "command": "uvx",
      "args": [
        "--from",
        "/path/to/your/local/hot-news-bachstudio",
        "hot-news-bachstudio"
      ]
    }
  }
}
```

---

## 🔗 相关链接

### uv 工具
- 官网: https://github.com/astral-sh/uv
- 文档: https://docs.astral.sh/uv/

### 包信息
- PyPI: https://pypi.org/project/hot-news-bachstudio/
- GitHub: https://github.com/BACH-AI-Tools/hot-news-bachstudio

---

## 📊 性能对比

| 方式 | 首次启动 | 后续启动 | 更新 | 依赖管理 |
|------|---------|---------|------|---------|
| uvx | ~2s | ~0.5s | 自动 | 自动 |
| pip install | N/A | ~1s | 手动 | 手动 |
| 源码运行 | N/A | ~1s | 手动 | 手动 |

---

## ✨ 推荐配置（最终版）

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "uvx",
      "args": [
        "hot-news-bachstudio"
      ]
    }
  }
}
```

这是最简洁、最现代化的配置方式！

---

**使用 uvx，享受快速、干净的 Python 包运行体验！** 🚀

