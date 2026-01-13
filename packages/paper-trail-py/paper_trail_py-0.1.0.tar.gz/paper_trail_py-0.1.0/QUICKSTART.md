# 🚀 快速启动指南

## 📋 前置要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - 现代 Python 包管理器

## 🔧 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

## 📦 项目设置

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/paper-trail-py.git
cd paper-trail-py
```

### 2. 安装依赖

```bash
# 开发环境（推荐）
make dev-install

# 或手动安装
uv pip install -e ".[dev,async,postgresql]"
```

### 3. 设置 Pre-commit

```bash
pre-commit install
```

## 🧪 运行测试

```bash
# 快速测试
make test

# 带覆盖率
make test-cov

# 观察模式（自动重新运行）
make test-watch
```

## 🎨 代码质量检查

```bash
# 运行所有检查
make lint          # Ruff + Black + isort
make type-check    # MyPy
make format        # 自动格式化

# 或运行 pre-commit
make pre-commit
```

## 🏗️ 项目结构速览

```
paper-trail-py/
├── src/paper_trail/       # 核心源码
│   ├── __init__.py        # 公共 API
│   ├── models.py          # Version 模型
│   ├── decorators.py      # @track_versions
│   ├── context.py         # Whodunnit/事务
│   ├── query.py           # 查询 API
│   ├── reify.py           # 版本恢复
│   ├── serializers.py     # 序列化
│   ├── config.py          # 配置
│   ├── async_support.py   # 异步
│   └── performance.py     # 性能优化
│
├── tests/                 # 测试套件
├── examples/              # 使用示例
└── pyproject.toml         # 项目配置
```

## 📚 快速使用

### 基础示例

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session, DeclarativeBase
from paper_trail import track_versions

class Base(DeclarativeBase):
    pass

@track_versions()
class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String(200))

# 使用
engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)
session = Session(engine)

article = Article(title="Hello")
session.add(article)
session.commit()  # ✅ 自动创建版本记录
```

### 运行完整示例

```bash
cd examples
uv run python complete_example.py
```

## 🔨 常用开发命令

```bash
# 安装
make install          # 生产安装
make dev-install      # 开发安装

# 测试
make test             # 运行测试
make test-cov         # 带覆盖率
make test-watch       # 观察模式

# 代码质量
make lint             # Lint 检查
make format           # 格式化代码
make type-check       # 类型检查
make pre-commit       # Pre-commit hooks

# 构建和发布
make build            # 构建包
make publish-test     # 发布到 TestPyPI
make publish          # 发布到 PyPI

# 清理
make clean            # 清理构建产物
```

## 🐛 调试技巧

### 查看 SQL 日志

```python
engine = create_engine('sqlite:///test.db', echo=True)
```

### 使用 IPython

```bash
uv run ipython

from paper_trail import *
# 交互式测试
```

## 📖 学习资源

1. **README.md** - 项目概览和功能介绍
2. **ARCHITECTURE.md** - 完整架构设计文档
3. **examples/** - 实际使用示例
4. **tests/** - 测试用例（学习 API 用法）

## 🤝 贡献流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### Commit 规范

```
<type>(<scope>): <subject>

types: feat, fix, docs, style, refactor, test, chore
```

示例：
```bash
git commit -m "feat(query): add time range filter"
git commit -m "fix(decorators): handle None values"
git commit -m "docs: update README examples"
```

## ❓ 常见问题

### Q: 如何切换数据库？

```python
# PostgreSQL
engine = create_engine('postgresql://user:pass@localhost/db')

# MySQL
engine = create_engine('mysql+pymysql://user:pass@localhost/db')

# SQLite
engine = create_engine('sqlite:///app.db')
```

### Q: 如何禁用版本追踪？

```python
from paper_trail import configure

configure(enabled=False)
```

### Q: 如何自定义序列化？

```python
from paper_trail.serializers import CustomFieldSerializer

serializer = CustomFieldSerializer({
    'price': lambda v: f"${v:.2f}",
})

@track_versions(serializer=serializer)
class Product(Base):
    # ...
```

## 🆘 获取帮助

- 📝 Issues: https://github.com/yourusername/paper-trail-py/issues
- 💬 Discussions: https://github.com/yourusername/paper-trail-py/discussions
- 📧 Email: support@example.com

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**准备好了吗？开始使用 PaperTrail 追踪你的数据变更吧！** 🎉
