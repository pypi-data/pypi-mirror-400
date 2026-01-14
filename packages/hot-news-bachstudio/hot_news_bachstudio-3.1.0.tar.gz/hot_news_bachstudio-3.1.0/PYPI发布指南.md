# 📦 PyPI 发布指南

## 🎯 发布准备

### 1. 注册 PyPI 账号

#### TestPyPI（测试环境，推荐先测试）
- 注册地址: https://test.pypi.org/account/register/
- 用于测试发布流程

#### PyPI（正式环境）
- 注册地址: https://pypi.org/account/register/
- 正式发布使用

### 2. 生成 API Token

#### TestPyPI
1. 登录 https://test.pypi.org
2. 进入 Account Settings
3. 点击 "Add API token"
4. 设置 token 名称和权限
5. 复制生成的 token（只显示一次）

#### PyPI
1. 登录 https://pypi.org
2. 进入 Account Settings
3. 点击 "Add API token"
4. 设置 token 名称和权限
5. 复制生成的 token（只显示一次）

### 3. 配置认证

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-你的正式环境token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-你的测试环境token
```

**注意**: 
- username 必须是 `__token__`
- password 是完整的 token（包括 `pypi-` 前缀）

---

## 🚀 快速发布

### 方法一：使用发布脚本（推荐）

```bash
cd "/Users/dengpengfei/Desktop/超级今日热点"
chmod +x publish.sh
./publish.sh
```

脚本会自动：
1. ✅ 检查发布工具
2. ✅ 安装/升级依赖
3. ✅ 清理旧文件
4. ✅ 构建包
5. ✅ 检查包完整性
6. ✅ 引导上传

### 方法二：手动发布

#### 1. 安装发布工具

```bash
pip install --upgrade pip setuptools wheel twine build
```

#### 2. 清理旧文件

```bash
rm -rf build/ dist/ *.egg-info
```

#### 3. 构建包

```bash
python3 -m build
```

#### 4. 检查包

```bash
python3 -m twine check dist/*
```

#### 5. 上传到 TestPyPI（测试）

```bash
python3 -m twine upload --repository testpypi dist/*
```

#### 6. 测试安装

```bash
pip install -i https://test.pypi.org/simple/ hot-news-mcp
```

#### 7. 上传到 PyPI（正式）

```bash
python3 -m twine upload dist/*
```

---

## 📋 发布检查清单

### 发布前检查

- [ ] 更新版本号（pyproject.toml）
- [ ] 更新 CHANGELOG
- [ ] 测试所有功能
- [ ] 更新文档
- [ ] 检查依赖版本
- [ ] 运行测试脚本

### 构建检查

- [ ] 清理旧文件
- [ ] 构建成功
- [ ] 检查包完整性
- [ ] 查看生成的文件

### 上传检查

- [ ] 先上传到 TestPyPI
- [ ] 从 TestPyPI 安装测试
- [ ] 测试功能正常
- [ ] 再上传到正式 PyPI

---

## 🔧 常见问题

### 问题1: 包名已存在

**错误**: `The name 'hot-news-mcp' is already in use`

**解决方案**:
1. 修改包名（pyproject.toml 中的 name）
2. 或者联系 PyPI 管理员

### 问题2: 认证失败

**错误**: `403 Forbidden` 或 `Invalid credentials`

**解决方案**:
1. 检查 ~/.pypirc 配置
2. 确认 token 正确（包括 `pypi-` 前缀）
3. 确认 username 是 `__token__`

### 问题3: 版本号冲突

**错误**: `File already exists`

**解决方案**:
1. 更新版本号（pyproject.toml）
2. 重新构建和上传

### 问题4: 依赖问题

**错误**: 安装时依赖无法解析

**解决方案**:
1. 检查 requirements.txt
2. 确认依赖版本兼容性
3. 测试安装

---

## 📊 包信息

### 当前版本
- **版本号**: 3.0.0
- **包名**: hot-news-mcp
- **Python**: >=3.10

### 依赖
- aiohttp>=3.9.0
- mcp>=0.9.0

### 包含文件
- hot_news_mcp/
  - __init__.py
  - server.py
  - test_server.py
- README.md
- LICENSE
- pyproject.toml

---

## 🎯 发布后

### 1. 验证发布

#### TestPyPI
- 查看: https://test.pypi.org/project/hot-news-mcp/
- 安装测试:
```bash
pip install -i https://test.pypi.org/simple/ hot-news-mcp
```

#### PyPI
- 查看: https://pypi.org/project/hot-news-mcp/
- 安装:
```bash
pip install hot-news-mcp
```

### 2. 测试安装

```bash
# 创建测试环境
python3 -m venv test_env
source test_env/bin/activate

# 安装包
pip install hot-news-mcp

# 测试导入
python3 -c "from hot_news_mcp import HotNewsAPI; print('✅ 导入成功')"

# 运行测试
python3 -m hot_news_mcp.test_server
```

### 3. 更新文档

- [ ] 更新 README.md
- [ ] 添加安装说明
- [ ] 更新版本历史
- [ ] 发布 Release Notes

### 4. 宣传推广

- [ ] 在 GitHub 创建 Release
- [ ] 发布到社交媒体
- [ ] 更新项目主页
- [ ] 通知用户更新

---

## 📝 版本管理

### 版本号规则

遵循 [语义化版本](https://semver.org/lang/zh-CN/)：

- **主版本号**: 不兼容的 API 修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

示例：
- 1.0.0 → 1.0.1 (修复bug)
- 1.0.1 → 1.1.0 (新增功能)
- 1.1.0 → 2.0.0 (重大更新)

### 更新版本

1. 修改 `pyproject.toml`:
```toml
version = "3.0.1"
```

2. 修改 `hot_news_mcp/__init__.py`:
```python
__version__ = "3.0.1"
```

3. 更新 CHANGELOG

4. 提交代码

5. 创建 Git tag:
```bash
git tag v3.0.1
git push origin v3.0.1
```

---

## 🔗 有用的链接

### PyPI
- PyPI 主页: https://pypi.org
- TestPyPI: https://test.pypi.org
- 文档: https://packaging.python.org

### 工具
- setuptools: https://setuptools.pypa.io
- twine: https://twine.readthedocs.io
- build: https://pypa-build.readthedocs.io

### 教程
- Python 打包指南: https://packaging.python.org/tutorials/packaging-projects/
- PyPI 发布教程: https://realpython.com/pypi-publish-python-package/

---

## 💡 最佳实践

### 1. 版本管理
- 使用语义化版本
- 每次发布创建 Git tag
- 维护 CHANGELOG

### 2. 测试
- 先发布到 TestPyPI
- 测试安装和功能
- 确认无误后发布到 PyPI

### 3. 文档
- 保持 README 更新
- 提供清晰的安装说明
- 包含使用示例

### 4. 安全
- 不要提交 API token
- 使用 .gitignore 忽略敏感文件
- 定期更新依赖

---

## 🎉 发布成功后

恭喜！你的包已经发布到 PyPI！

### 用户可以这样安装：

```bash
pip install hot-news-mcp
```

### 在 Claude Desktop 中配置：

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

---

**祝发布顺利！** 🎊

