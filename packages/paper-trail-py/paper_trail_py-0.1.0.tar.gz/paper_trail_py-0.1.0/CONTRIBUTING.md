# 🤝 贡献指南

感谢你对 PaperTrail-Py 的兴趣！本指南将帮助你快速上手项目贡献。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发设置](#开发设置)
- [代码规范](#代码规范)
- [测试要求](#测试要求)
- [提交流程](#提交流程)
- [发布流程](#发布流程)

## 🌟 行为准则

我们致力于提供一个友好、专业的开源社区环境。参与项目即表示同意遵守以下原则：

- 尊重不同观点和经验
- 接受建设性批评
- 专注于对社区最有利的事情
- 对其他社区成员保持同理心

## 🚀 如何贡献

### 报告 Bug

在提交 Bug 之前，请：

1. 检查 [Issues](https://github.com/yourusername/paper-trail-py/issues) 是否已存在
2. 使用最新版本重现问题
3. 提供详细的重现步骤

**Bug 报告应包含**：
```markdown
**描述**
简洁描述问题

**重现步骤**
1. 执行 '...'
2. 调用 '...'
3. 观察错误

**期望行为**
描述期望的正确行为

**实际行为**
描述实际发生的情况

**环境**
- OS: [macOS 13.0]
- Python: [3.11.0]
- PaperTrail: [0.1.0]
- SQLAlchemy: [2.0.0]

**额外信息**
堆栈跟踪、日志等
```

### 提出新功能

功能请求应：

1. 说明使用场景
2. 解释为什么现有功能不满足需求
3. 提供 API 设计示例（如果可能）

### 提交代码

1. **Fork 项目**
   ```bash
   git clone https://github.com/yourusername/paper-trail-py.git
   cd paper-trail-py
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/my-feature
   # 或
   git checkout -b fix/issue-123
   ```

3. **开发和测试**
   ```bash
   make dev-install
   # 开发...
   make test
   make lint
   ```

4. **提交更改**
   ```bash
   git commit -m "feat(scope): description"
   ```

5. **推送并创建 PR**
   ```bash
   git push origin feature/my-feature
   ```

## 🔧 开发设置

### 环境要求

- Python 3.10+
- uv (包管理器)
- Git

### 初始化项目

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/paper-trail-py.git
cd paper-trail-py

# 2. 运行设置脚本
./scripts/setup.sh

# 或手动设置
make dev-install
pre-commit install
```

### 开发工作流

```bash
# 创建功能分支
git checkout -b feature/amazing-feature

# 开发过程中频繁运行测试
make test

# 提交前检查
make lint
make type-check
make pre-commit

# 提交
git commit -m "feat(query): add time range filter"

# 推送
git push origin feature/amazing-feature
```

## 📝 代码规范

### 风格指南

我们使用以下工具确保代码质量：

- **Black** - 代码格式化（line-length=88）
- **isort** - 导入排序
- **Ruff** - Fast linter
- **mypy** - 类型检查（strict mode）

运行格式化：
```bash
make format
```

### 类型提示

**必须**为所有公共 API 添加类型提示：

✅ 好的示例：
```python
def get_versions(
    session: Session,
    model_class: Type,
    model_id: Any,
    limit: Optional[int] = None,
) -> List[Version]:
    """获取版本历史"""
    ...
```

❌ 不好的示例：
```python
def get_versions(session, model_class, model_id, limit=None):
    ...
```

### 文档字符串

使用 Google 风格的 docstring：

```python
def reify_version(
    session: Session,
    version: Version,
    model_class: Type,
    commit: bool = False,
) -> Any:
    """
    从版本记录恢复对象
    
    Args:
        session: SQLAlchemy 会话
        version: 版本记录
        model_class: 目标模型类
        commit: 是否立即提交
        
    Returns:
        恢复的模型实例
        
    Raises:
        ValueError: 如果版本记录没有对象快照
        
    Example:
        >>> version = get_versions(session, Article, 123)[0]
        >>> restored = reify_version(session, version, Article)
    """
    ...
```

### Commit 规范

使用 Conventional Commits：

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链更新

**示例**:
```bash
feat(query): add time range filtering

Add `between()` method to VersionQuery for filtering versions
within a specific time range.

Closes #42
```

## 🧪 测试要求

### 编写测试

- 所有新功能**必须**有测试
- Bug 修复**应该**添加回归测试
- 目标覆盖率：**95%+**

### 测试结构

```python
import pytest

class TestFeature:
    """测试功能 X"""
    
    @pytest.fixture(autouse=True)
    def setup(self, session, clean_db):
        """测试前设置"""
        ...
    
    def test_basic_functionality(self, session):
        """测试基本功能"""
        # Given
        article = Article(title="Test")
        session.add(article)
        session.commit()
        
        # When
        versions = get_versions(session, Article, article.id)
        
        # Then
        assert len(versions) == 1
        assert versions[0].event == 'create'
```

### 运行测试

```bash
# 所有测试
make test

# 特定文件
uv run pytest tests/test_query.py

# 特定测试
uv run pytest tests/test_query.py::TestVersionQuery::test_for_model

# 覆盖率报告
make test-cov
open htmlcov/index.html
```

## 📤 提交流程

### Pull Request 清单

在提交 PR 之前，确保：

- [ ] 代码通过所有测试
- [ ] 添加了新功能的测试
- [ ] 更新了相关文档
- [ ] Commit 信息符合规范
- [ ] 代码通过 lint 检查
- [ ] 类型检查通过

### PR 描述模板

```markdown
## 描述
简洁描述你的更改

## 动机和上下文
为什么需要这个更改？解决了什么问题？

Closes #(issue)

## 更改类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 破坏性更改
- [ ] 文档更新

## 测试
描述你添加的测试

## 截图（如适用）

## 清单
- [ ] 代码遵循项目规范
- [ ] 已添加测试
- [ ] 所有测试通过
- [ ] 文档已更新
```

### Review 流程

1. 自动 CI 检查必须通过
2. 至少一个维护者 approve
3. 解决所有 review 意见
4. Squash merge 到 main

## 🚢 发布流程

维护者专用：

### 版本号规范

遵循 [Semantic Versioning](https://semver.org/):

- **MAJOR**: 破坏性更改
- **MINOR**: 新功能（向后兼容）
- **PATCH**: Bug 修复

### 发布步骤

1. **更新版本号**
   ```bash
   # pyproject.toml
   version = "0.2.0"
   
   # src/paper_trail/__init__.py
   __version__ = "0.2.0"
   ```

2. **更新 CHANGELOG**
   ```markdown
   ## [0.2.0] - 2026-01-15
   
   ### Added
   - 新功能 X
   
   ### Fixed
   - Bug Y
   
   ### Changed
   - 改进 Z
   ```

3. **创建 Git Tag**
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```

4. **创建 GitHub Release**
   - 自动触发 PyPI 发布

## 💡 开发技巧

### 调试

```python
# 启用 SQL 日志
engine = create_engine('sqlite:///test.db', echo=True)

# 使用 IPython
uv run ipython
```

### 性能分析

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# 你的代码

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## 📚 学习资源

- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)
- [Python 类型提示](https://docs.python.org/3/library/typing.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

## ❓ 需要帮助？

- 💬 [Discussions](https://github.com/yourusername/paper-trail-py/discussions)
- 📧 Email: dev@example.com
- 💼 [Slack/Discord](链接)

---

**感谢你的贡献！** 🎉
