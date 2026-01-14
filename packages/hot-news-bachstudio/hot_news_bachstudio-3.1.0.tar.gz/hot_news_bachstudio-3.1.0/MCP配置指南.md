# 🔧 Claude Desktop MCP 配置指南

## ✅ 服务器已测试成功！

当前可用的平台：
- ✅ **抖音热点** - 30 条数据
- ✅ **B站热门** - 30 条数据  
- ✅ **今日头条** - 30 条数据
- ✅ **百度热搜** - 数据可用

## 📍 配置文件位置

### MacOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### 快速打开命令
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

如果文件不存在，请先创建：
```bash
mkdir -p ~/Library/Application\ Support/Claude
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

## 📝 配置内容

### 方式一：使用 python3（推荐）

将以下内容复制到 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "python3",
      "args": [
        "/Users/dengpengfei/Desktop/超级今日热点/server.py"
      ]
    }
  }
}
```

### 方式二：使用完整 Python 路径

```json
{
  "mcpServers": {
    "hot-news": {
      "command": "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
      "args": [
        "/Users/dengpengfei/Desktop/超级今日热点/server.py"
      ]
    }
  }
}
```

### 方式三：如果已有其他 MCP 服务器

如果你的配置文件中已经有其他 MCP 服务器，只需添加 `hot-news` 部分：

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "hot-news": {
      "command": "python3",
      "args": [
        "/Users/dengpengfei/Desktop/超级今日热点/server.py"
      ]
    }
  }
}
```

## 🚀 配置步骤

### 1. 打开配置文件

```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 2. 复制配置

选择上面的任一配置方式，复制整个 JSON 内容

### 3. 保存文件

保存并关闭编辑器

### 4. 重启 Claude Desktop

完全退出 Claude Desktop（Command + Q），然后重新打开

### 5. 验证安装

在 Claude Desktop 中输入：

```
获取抖音热点前5条
```

如果能看到数据，说明配置成功！🎉

## 💡 使用示例

### 获取单个平台

```
获取抖音热点
获取B站热门视频
获取今日头条热点
```

### 获取所有平台

```
获取所有平台的热点
现在有什么热点新闻？
```

### 搜索关键词

```
搜索包含"科技"的热点
在抖音和B站上搜索"游戏"
```

### 数据分析

```
对比抖音和B站的热点差异
分析今天的热点趋势
```

## ⚠️ 注意事项

1. **路径必须正确**
   - 确保路径是完整的绝对路径
   - 路径中的中文需要正确显示

2. **JSON 格式**
   - 确保 JSON 格式正确，没有多余的逗号
   - 所有的引号必须是双引号 `"`

3. **Python 版本**
   - 需要 Python 3.10 或更高版本
   - 确保已安装依赖：`pip3 install aiohttp mcp`

4. **网络访问**
   - 需要能够访问互联网
   - 某些平台可能需要特定的网络环境

## 🐛 故障排查

### 问题1：Claude Desktop 无法连接 MCP 服务器

**解决方案：**
1. 检查配置文件路径是否正确
2. 确保 Python 可以运行：`python3 --version`
3. 确保依赖已安装：`pip3 list | grep mcp`
4. 查看 Claude Desktop 日志（菜单 -> Help -> Show Logs）

### 问题2：命令执行后没有响应

**解决方案：**
1. 重启 Claude Desktop
2. 检查服务器是否正常：`python3 /Users/dengpengfei/Desktop/超级今日热点/test_server.py`
3. 确保网络连接正常

### 问题3：某些平台无法获取数据

**解决方案：**
- 这是正常的，部分平台（微博、知乎）可能需要额外的认证
- 当前可用的平台：抖音、B站、今日头条、百度

### 问题4：JSON 格式错误

**解决方案：**
1. 使用 JSON 验证工具检查格式：https://jsonlint.com
2. 确保没有多余的逗号
3. 确保所有引号都是双引号

## 📊 配置文件示例

已为你生成了配置文件：
```
/Users/dengpengfei/Desktop/超级今日热点/claude_mcp_config.json
```

你可以直接复制这个文件的内容！

## 🎯 快速命令

### 一键配置（如果配置文件不存在）

```bash
# 创建配置文件目录
mkdir -p ~/Library/Application\ Support/Claude

# 复制配置文件
cp "/Users/dengpengfei/Desktop/超级今日热点/claude_mcp_config.json" ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 重启 Claude Desktop
```

### 查看当前配置

```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 编辑配置

```bash
open -e ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

## ✨ 成功标志

配置成功后，你会看到：
1. Claude Desktop 启动时不会报错
2. 可以成功获取热点数据
3. 搜索和分析功能正常工作

## 📞 需要帮助？

1. 查看完整文档：`README.md`
2. 查看使用示例：`EXAMPLES.md`
3. 运行测试脚本：`python3 test_server.py`

---

**配置完成后，记得重启 Claude Desktop！** 🎉

